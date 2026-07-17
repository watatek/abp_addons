# Copyright 2026
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    product_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="crm_lead_id",
        string="New Products",
        help=(
            "Products created directly from this opportunity's Pipeline "
            "form. They are automatically sent through the product "
            "approval workflow as soon as they are created."
        ),
    )
    stage_create_product = fields.Boolean(
        string="Stage Allows Product Creation",
        related="stage_id.create_product",
        help=(
            "Technical field used to show/hide the 'New Products' tab "
            "based on the current stage's configuration."
        ),
    )
