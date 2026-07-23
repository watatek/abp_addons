# Copyright 2026
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SalesPrice(models.Model):
    _name = "sales.price"
    _description = "Sales Price"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Price Name",
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
    cost_id = fields.Many2one(
        comodel_name="sales.cost",
        string="Cost Name",
        ondelete="restrict",
        tracking=True,
    )
    landed_cost = fields.Float(
        string="Landed Cost",
        compute="_compute_landed_cost",
        store=True,
        readonly=False,
        tracking=True,
        help="Inherited from the selected Cost Name; can be overridden.",
    )

    exw_price = fields.Float(string="EXW Price", tracking=True)
    processing_price = fields.Float(string="Processing Price", tracking=True)
    freight_price = fields.Float(string="Freight Price", tracking=True)
    selling_price = fields.Float(
        string="Selling Price",
        compute="_compute_selling_price",
        store=True,
        readonly=True,
        tracking=True,
        help="EXW Price + Processing Price + Freight Price.",
    )
    gross_margin = fields.Float(
        string="Gross Margin",
        compute="_compute_gross_margin",
        store=True,
        readonly=True,
        digits=(16, 4),
        help=(
            "(Selling Price - Landed Cost) / Landed Cost, stored as a ratio "
            "and displayed with the percentage widget."
        ),
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

    @api.onchange("product_template_id")
    def _onchange_product_template_id(self):
        """Costs are item specific: changing the item drops the cost."""
        for record in self:
            record.cost_id = False

    @api.depends("cost_id", "cost_id.landed_cost")
    def _compute_landed_cost(self):
        for record in self:
            record.landed_cost = record.cost_id.landed_cost

    @api.depends("exw_price", "processing_price", "freight_price")
    def _compute_selling_price(self):
        for record in self:
            record.selling_price = (
                record.exw_price + record.processing_price + record.freight_price
            )

    @api.depends("selling_price", "landed_cost")
    def _compute_gross_margin(self):
        for record in self:
            if record.landed_cost:
                record.gross_margin = (
                    record.selling_price - record.landed_cost
                ) / record.landed_cost
            else:
                record.gross_margin = 0.0

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
            # Only one price may stay Active for a given item: deactivate the
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
        """Push the selling price of an active record onto the product."""
        for record in self:
            if record.state == "active" and record.product_template_id:
                record.product_template_id.write(
                    {"list_price": record.selling_price}
                )

    def write(self, vals):
        result = super().write(vals)
        if "selling_price" in vals or "exw_price" in vals \
                or "processing_price" in vals or "freight_price" in vals:
            self._apply_to_product()
        return result

    def action_decline(self):
        self._check_state("submitted", _("Decline"))
        self.write({"state": "inactive"})

    def action_deactivate(self):
        self._check_state("active", _("Deactivate"))
        self.write({"state": "inactive"})
