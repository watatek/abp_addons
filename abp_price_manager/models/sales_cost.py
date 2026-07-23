# Copyright 2026
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SalesCost(models.Model):
    _name = "sales.cost"
    _description = "Sales Cost"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Cost Name",
        required=True,
        tracking=True,
    )
    product_template_id = fields.Many2one(
        comodel_name="product.template",
        string="Item Code",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=True,
        ondelete="restrict",
        tracking=True,
    )

    exw_cost = fields.Float(string="EXW Cost", tracking=True)
    processing_cost = fields.Float(string="Processing Cost", tracking=True)
    freight_cost = fields.Float(string="Freight Cost", tracking=True)
    landed_cost = fields.Float(
        string="Landed Cost",
        compute="_compute_landed_cost",
        store=True,
        readonly=True,
        tracking=True,
        help="EXW Cost + Processing Cost + Freight Cost.",
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    exchange_rate = fields.Float(
        string="Exchange Rate",
        compute="_compute_exchange_rate",
        readonly=True,
        digits=(12, 6),
        help="Current res.currency.rate of the selected currency.",
    )

    approved_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        readonly=True,
        copy=False,
        tracking=True,
    )
    approval_date = fields.Datetime(
        string="Approval Date",
        readonly=True,
        copy=False,
        tracking=True,
        help="Moment the record was approved (effective date).",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        string="Status",
        default="draft",
        required=True,
        copy=False,
        tracking=True,
    )

    @api.depends("exw_cost", "processing_cost", "freight_cost")
    def _compute_landed_cost(self):
        for record in self:
            record.landed_cost = (
                record.exw_cost + record.processing_cost + record.freight_cost
            )

    @api.depends("currency_id", "currency_id.rate")
    def _compute_exchange_rate(self):
        for record in self:
            record.exchange_rate = record.currency_id.rate or 0.0

    def _check_state(self, expected, action):
        wrong = self.filtered(lambda r: r.state != expected)
        if wrong:
            raise UserError(
                _("%(action)s is only allowed on %(expected)s records.")
                % {"action": action, "expected": expected}
            )

    def action_submit(self):
        self._check_state("draft", _("Submit"))
        self.write({"state": "submitted"})

    def action_approve(self):
        self._check_state("submitted", _("Approve"))
        for record in self:
            # Only one cost may stay Active for a given item: deactivate the
            # previous one(s) before promoting this record.
            previous = self.search(
                [
                    ("id", "!=", record.id),
                    ("product_template_id", "=", record.product_template_id.id),
                    ("state", "=", "active"),
                ]
            )
            previous.write({"state": "inactive"})
            record.write(
                {
                    "state": "active",
                    "approved_by_id": self.env.user.id,
                    "approval_date": fields.Datetime.now(),
                }
            )
            record._apply_to_product()

    def _apply_to_product(self):
        """Push the landed cost of an active record onto the product."""
        for record in self:
            if record.state == "active" and record.product_template_id:
                record.product_template_id.write(
                    {"standard_price": record.landed_cost}
                )

    def write(self, vals):
        result = super().write(vals)
        if "landed_cost" in vals or "exw_cost" in vals \
                or "processing_cost" in vals or "freight_cost" in vals:
            self._apply_to_product()
        return result

    def action_decline(self):
        self._check_state("submitted", _("Decline"))
        self.write({"state": "inactive"})

    def action_deactivate(self):
        self._check_state("active", _("Deactivate"))
        self.write({"state": "inactive"})
