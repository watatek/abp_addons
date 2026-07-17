# Copyright 2026
from odoo import api, fields, models


class ProductTemplate(models.Model):
    """Add the Dynamic Approval Workflow to Products (mirrors the Sales
    Order sample shipped in ``dynamic_approval_workflow``) and link products
    created from the CRM Pipeline "New Products" tab back to the
    opportunity they came from.

    This class only *extends* ``product.template`` from the ``product``
    module -- it does not touch ``dynamic_approval_workflow`` in any way.
    ``product.template`` already inherits ``mail.thread`` in Odoo core, so
    the chatter integration required by ``approval.mixin`` works out of the
    box.
    """

    _inherit = ["product.template", "approval.mixin"]

    #: Only these values are accepted by product.template.type in Odoo 19.
    _VALID_PRODUCT_TYPES = ("consu", "service", "combo")

    crm_lead_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Created From Opportunity",
        ondelete="set null",
        copy=False,
        index=True,
        help=(
            "Opportunity/lead this product was created from (via the "
            "Pipeline 'New Products' tab). Left empty for products created "
            "the normal way, e.g. from Sales > Products."
        ),
    )

    # ------------------------------------------------------------------
    # ORM overrides
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        # Guard against context leakage: when a product.template is created
        # as a nested one2many line while saving a crm.lead (e.g. from the
        # "New Products" tab), Odoo reuses the *same* env.context as the
        # parent save call. The Pipeline action sets ``default_type:
        # 'opportunity'`` in its context (so new leads default to
        # Opportunity) -- and since product.template also has a field named
        # "type", the ORM's create() default-value resolution picks up that
        # unrelated 'opportunity' value for *this* model too, which is not
        # a valid product.template.type and raises a ValueError. Sanitize
        # it here rather than relying on view-level context (which only
        # affects the client, not this server-side create()).
        for vals in vals_list:
            if vals.get("type") not in self._VALID_PRODUCT_TYPES:
                vals["type"] = "consu"
        products = super().create(vals_list)
        # Products created inline from the CRM "New Products" tab are
        # submitted to the approval workflow automatically: the salesperson
        # should not have to remember an extra "Submit for Approval" click.
        auto_submit = products.filtered(
            lambda p: p.crm_lead_id
            and p.approval_state == "draft"
            and p._get_approval_config()
        )
        if auto_submit:
            auto_submit.action_submit_for_approval()
        return products

    def write(self, vals):
        res = super().write(vals)
        # Re-activate the product automatically as soon as it is approved.
        if vals.get("approval_state") == "approved":
            self.filtered(lambda p: not p.active).write({"active": True})
        return res

    # ------------------------------------------------------------------
    # Approval workflow hooks
    # ------------------------------------------------------------------

    def action_submit_for_approval(self):
        """Archive the product while it is pending approval so it cannot be
        picked on quotations or purchase orders until Accounting signs off
        on its selling price / cost price. Re-activation happens in
        ``write()`` above once the linked approval request is approved.
        """
        res = super().action_submit_for_approval()
        self.filtered(lambda p: p.approval_state == "pending_approval").write(
            {"active": False}
        )
        return res

    def action_reset_to_draft(self):
        """Let the requester edit and resubmit a rejected/returned product."""
        self.filtered(
            lambda p: p.approval_state in ("rejected", "returned")
        ).write({"approval_state": "draft"})
