# Copyright 2026
from odoo import fields, models


class CrmStage(models.Model):
    _inherit = "crm.stage"

    create_product = fields.Boolean(
        string="Create Product",
        help=(
            "When enabled, opportunities currently in this stage display an "
            "extra 'New Products' tab (next to Contacts) on the Pipeline "
            "form, where salespeople can create new products inline. "
            "Products created there are automatically submitted to the "
            "Product Approval workflow."
        ),
    )
