# Copyright 2026 Hieu Bui
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
{
    "name": "ABP Purchase",
    "version": "19.0.1.0.0",
    "summary": "Link sale orders to a purchase order and feed the source document",
    "author": "Hieu Bui",
    "website": "",
    "category": "ABP",
    "license": "LGPL-3",
    "depends": ["purchase", "sale"],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
