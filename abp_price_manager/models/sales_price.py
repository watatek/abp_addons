# Copyright 2026
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


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
        help="Inherited from the selected Cost Name; can be overridden. "
             "Expressed in the cost currency.",
    )
    cost_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Cost Currency",
        related="cost_id.currency_id",
        store=True,
        readonly=True,
    )
    landed_cost_converted = fields.Float(
        string="Landed Cost (Price Currency)",
        compute="_compute_landed_cost_converted",
        store=True,
        readonly=True,
        tracking=True,
        help="Landed Cost converted from the cost currency into the price "
             "currency at the current rate.",
    )
    landed_cost_display = fields.Char(
        string="Landed Cost",
        compute="_compute_landed_cost_display",
        help="Landed Cost in the cost currency and, when they differ, its "
             "equivalent in the price currency.",
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
    selling_price_company = fields.Float(
        string="Selling Price (Company Currency)",
        compute="_compute_selling_price_company",
        store=True,
        readonly=True,
        help="Selling Price converted into the company currency at the "
             "current rate.",
    )
    selling_price_display = fields.Char(
        string="Selling Price",
        compute="_compute_selling_price_display",
        help="Selling Price in the price currency and, when they differ, its "
             "equivalent in the company currency.",
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

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
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

    @api.depends("currency_id", "currency_id.rate")
    def _compute_exchange_rate(self):
        for record in self:
            record.exchange_rate = record.currency_id.rate or 0.0

    @api.depends("landed_cost", "cost_currency_id", "currency_id",
                 "cost_currency_id.rate", "currency_id.rate")
    def _compute_landed_cost_converted(self):
        for record in self:
            source = record.cost_currency_id or record.currency_id
            target = record.currency_id
            if not record.landed_cost or not source or not target \
                    or source == target:
                record.landed_cost_converted = record.landed_cost
                continue
            record.landed_cost_converted = source._convert(
                record.landed_cost,
                target,
                record.company_id or self.env.company,
                fields.Date.context_today(record),
            )

    @api.depends("landed_cost", "landed_cost_converted",
                 "cost_currency_id", "currency_id")
    def _compute_landed_cost_display(self):
        for record in self:
            source = record.cost_currency_id or record.currency_id
            target = record.currency_id
            base = formatLang(
                self.env, record.landed_cost, currency_obj=source
            ) if source else formatLang(self.env, record.landed_cost)
            if source and target and source != target:
                converted = formatLang(
                    self.env, record.landed_cost_converted, currency_obj=target
                )
                record.landed_cost_display = "%s = %s" % (base, converted)
            else:
                record.landed_cost_display = base

    @api.depends("selling_price", "currency_id", "currency_id.rate",
                 "company_id")
    def _compute_selling_price_company(self):
        for record in self:
            company = record.company_id or self.env.company
            target = company.currency_id
            source = record.currency_id
            if not record.selling_price or not source or source == target:
                record.selling_price_company = record.selling_price
                continue
            record.selling_price_company = source._convert(
                record.selling_price,
                target,
                company,
                fields.Date.context_today(record),
            )

    @api.depends("selling_price", "selling_price_company", "currency_id",
                 "company_id")
    def _compute_selling_price_display(self):
        for record in self:
            company = record.company_id or self.env.company
            source = record.currency_id
            target = company.currency_id
            base = formatLang(
                self.env, record.selling_price, currency_obj=source
            ) if source else formatLang(self.env, record.selling_price)
            if source and target and source != target:
                converted = formatLang(
                    self.env, record.selling_price_company, currency_obj=target
                )
                record.selling_price_display = "%s = %s" % (base, converted)
            else:
                record.selling_price_display = base

    @api.depends("selling_price", "landed_cost_converted")
    def _compute_gross_margin(self):
        for record in self:
            cost = record.landed_cost_converted
            if cost:
                record.gross_margin = (record.selling_price - cost) / cost
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
