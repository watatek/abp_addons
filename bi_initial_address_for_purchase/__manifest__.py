# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': "Manage Purchase Initial Address | Keep Vendor Bill Address",
    'version': '19.0.0.0',
    'category': 'Purchase',
    'summary':"Purchase Order Initial Address Keep Initial Address on Vendor Bill Update PO Initial Address Request for Quotation Change Purchase Original Address Vendor Initial Address Keep RFQ Initial Address Update Purchase Shipping Address Purchase Billing Address",
    'description': """
      
        Keep Vendor Bill Address Odoo App helps users to update initial address for single or multiple record of purchase order and vendor bill with single click. When address are changes for purchase order and vendor bill, Initial address should be there to managing the order with there original or initial address. User can also view initial address in generated purchase order report and vendor bill report.

    """,
    'author': 'BROWSEINFO',
    'website': 'https://www.browseinfo.com/demo-request?app=bi_initial_address_for_purchase&version=19&edition=Community',
    'depends': ['base','purchase','account','stock'],
    'data': [
        'security/ir.model.access.csv',
        'report/purchase_order_report.xml',
        'report/account_move_report.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'wizard/set_message_wizard_views.xml',
    ],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://www.browseinfo.com/demo-request?app=bi_initial_address_for_purchase&version=19&edition=Community',
    "images":['static/description/Initial-Address-Banner.gif'],
}
