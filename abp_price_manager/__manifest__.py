# Copyright 2026 Hieu Bui
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
{
    "name": "ABP Price Manager",
    "version": "19.0.1.0.0",
    "summary": "Approve item costs and selling prices and push them to products",
    "author": "Hieu Bui",
    "website": "",
    "category": "ABP",
    "license": "LGPL-3",
    "depends": ["product", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/sales_cost_views.xml",
        "views/sales_price_views.xml",
        "views/abp_price_manager_actions.xml",
        "views/abp_price_manager_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
