# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SetMessage(models.TransientModel):
    _name = 'set.message.wizard'
    _description = ' Pop up Message is Generated'


    set_message = fields.Char(string='message',required=True)
    set_message_count = fields.Integer(string='set message count', required=True)

    @api.model
    def default_get(self, fields):
        res = super(SetMessage, self).default_get(fields)
        purchase_id = self.env['purchase.order'].browse(self.env.context.get('active_id'))
        if purchase_id:
            data = purchase_id.filtered(lambda l: not l.set_name)
            count_ds = len(data.ids)
            for rec in purchase_id:

                if not rec.set_name:
                    if rec.partner_id:
                        rec.set_name = rec.partner_id.name
                        rec.street = rec.partner_id.street
                        rec.street2 = rec.partner_id.street2
                        rec.zip = rec.partner_id.zip
                        rec.city = rec.partner_id.city
                        rec.state_id = rec.partner_id.state_id.id
                        rec.country_id = rec.partner_id.country_id.id
                else:
                    pass

            if count_ds == 0:
                raise UserError(
                    'Already Initial Address Updated. ')
            res = {
                'set_message_count': count_ds,
                'set_message': "Successfully " + str(count_ds) + " Purchase Records update the Initial address."
            }
            return res


        return res



class SetMessageBill(models.TransientModel):
    _name = 'set.message.bill.wizard'
    _description = ' Bill Pop up Message is Generated'

    set_message = fields.Char(string='message', required=True)
    set_message_count = fields.Integer(string='set message count', required=True)

    @api.model
    def default_get(self, fields):
        res = super(SetMessageBill, self).default_get(fields)
        bill_id = self.env['account.move'].browse(self._context.get('active_id'))
        if bill_id:
            data = bill_id.filtered(lambda l: not l.set_name)
            count_ds = len(data.ids)
            for rec in bill_id:
                if rec.move_type == 'out_invoice':
                    raise UserError(' In Customer Invoice Do Not Add Initial Address. ')
                if not rec.set_name:
                    if rec.partner_id:
                        rec.set_name = rec.partner_id.name
                        rec.street = rec.partner_id.street
                        rec.street2 = rec.partner_id.street2
                        rec.zip = rec.partner_id.zip
                        rec.city = rec.partner_id.city
                        rec.state_id = rec.partner_id.state_id.id
                        rec.country_id = rec.partner_id.country_id.id
                else:
                    pass
            if count_ds == 0:
                raise UserError(
                    'Already Initial Address Updated. ')
            res = {
                'set_message_count': count_ds,
                'set_message': "Successfully " + str(count_ds) + " Bill Records update the Initial address."
            }
            return res

        return res