# Copyright 2026 Hieu Bui
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        string="Sale Orders",
        help="Sale orders this purchase order is sourced from.",
    )

    @api.onchange("sale_order_ids")
    def _onchange_sale_order_ids_set_origin(self):
        """Write the linked sale order names into the source document."""
        for order in self:
            order.origin = ", ".join(
                order.sale_order_ids.mapped("name")
            )
