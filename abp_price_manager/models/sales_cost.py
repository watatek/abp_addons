# Copyright 2026
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


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
    landed_cost_company = fields.Float(
        string="Landed Cost (Company Currency)",
        compute="_compute_landed_cost_company",
        store=True,
        readonly=True,
        help="Landed Cost converted into the company currency at the current "
             "rate.",
    )
    landed_cost_display = fields.Char(
        string="Landed Cost",
        compute="_compute_landed_cost_display",
        help="Landed Cost in the cost currency and, when they differ, its "
             "equivalent in the company currency.",
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

    @api.depends("exw_cost", "processing_cost", "freight_cost")
    def _compute_landed_cost(self):
        for record in self:
            record.landed_cost = (
                record.exw_cost + record.processing_cost + record.freight_cost
            )

    @api.depends("landed_cost", "currency_id", "currency_id.rate", "company_id")
    def _compute_landed_cost_company(self):
        for record in self:
            company = record.company_id or self.env.company
            source = record.currency_id
            target = company.currency_id
            if not record.landed_cost or not source or source == target:
                record.landed_cost_company = record.landed_cost
                continue
            record.landed_cost_company = source._convert(
                record.landed_cost,
                target,
                company,
                fields.Date.context_today(record),
            )

    @api.depends("landed_cost", "landed_cost_company", "currency_id",
                 "company_id")
    def _compute_landed_cost_display(self):
        for record in self:
            company = record.company_id or self.env.company
            source = record.currency_id
            target = company.currency_id
            base = formatLang(
                self.env, record.landed_cost, currency_obj=source
            ) if source else formatLang(self.env, record.landed_cost)
            if source and target and source != target:
                converted = formatLang(
                    self.env, record.landed_cost_company, currency_obj=target
                )
                record.landed_cost_display = "%s = %s" % (base, converted)
            else:
                record.landed_cost_display = base

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
            # Only one cost may stay Active per item and supplier pair:
            # deactivate the previous one(s) before promoting this record.
            previous = self.search(
                [
                    ("id", "!=", record.id),
                    ("product_template_id", "=", record.product_template_id.id),
                    ("partner_id", "=", record.partner_id.id),
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
