# Copyright 2026
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("order_line")
    def _onchange_order_line_set_partner(self):
        """Adopt the cheapest supplier when a product is picked first.

        The user may fill a line before choosing a vendor. In that case the
        line is priced from the cheapest active cost, so the order simply
        follows the supplier of that cost.
        """
        if self.partner_id:
            return
        for line in self.order_line:
            if not line.product_id:
                continue
            cost = self.env["sales.cost"]._find_best_cost(
                line.product_id.product_tmpl_id
            )
            if cost:
                self.partner_id = cost.partner_id
                break


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("product_id")
    def _compute_price_unit_and_date_planned_and_name(self):
        """Let the approved cost win over the vendor pricelist.

        Runs after the standard computation so the name and planned date keep
        their usual values, then overwrites the price with the active
        sales.cost of the ordered item: the vendor's own cost when a vendor is
        set, otherwise the cheapest one across vendors.
        """
        super()._compute_price_unit_and_date_planned_and_name()
        for line in self:
            if not line.product_id or line.invoice_lines:
                continue
            # Same guard as the standard compute: never fight a manual price.
            if line.technical_price_unit != line.price_unit:
                continue
            cost = self.env["sales.cost"]._find_best_cost(
                line.product_id.product_tmpl_id,
                partner=line.order_id.partner_id,
            )
            if not cost:
                continue
            price = line._convert_sales_cost(cost)
            line.price_unit = price
            line.technical_price_unit = price

    def _convert_sales_cost(self, cost):
        """Landed cost of ``cost`` expressed in the order currency."""
        self.ensure_one()
        company = self.company_id or self.order_id.company_id or self.env.company
        target = self.order_id.currency_id or company.currency_id
        source = cost.currency_id or target
        if not source or not target or source == target:
            return cost.landed_cost
        date = self.date_order.date() if self.date_order \
            else fields.Date.context_today(self)
        return source._convert(cost.landed_cost, target, company, date)


class SalesCost(models.Model):
    _inherit = "sales.cost"

    @api.model
    def _find_best_cost(self, product_template, partner=None):
        """Return the active cost for the item: the vendor's one, or the
        cheapest across vendors when no vendor is given."""
        if not product_template:
            return self.browse()
        domain = [
            ("product_template_id", "=", product_template.id),
            ("state", "=", "active"),
        ]
        if partner:
            domain.append(("partner_id", "=", partner.id))
            return self.search(domain, limit=1)
        return self.search(domain, order="landed_cost_company asc", limit=1)
