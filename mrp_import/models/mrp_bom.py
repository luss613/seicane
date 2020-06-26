# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import xlrd


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def update_bom_from_attachment(self, attachment_ids=[]):
        ''' Update the BOM from files.
         :return: A action redirecting to bom tree/form view.
        '''
        attachments = self.env['ir.attachment'].browse(attachment_ids)
        if not attachments:
            raise UserError(_("No attachment was provided"))

        bom_ids = self.env['mrp.bom']
        for attachment in attachments:
            bom_ids += self._import_bom(attachment.datas)

        action_vals = {
            'name': _('Updated Documents'),
            'domain': [('id', 'in', bom_ids.ids)],
            'res_model': 'mrp.bom',
            'views': [[False, "tree"], [False, "form"]],
            'type': 'ir.actions.act_window',
            'context': self._context
        }
        if len(bom_ids) == 1:
            action_vals.update({'res_id': bom_ids[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals

    def _import_bom(self, xls_file):
        wb = xlrd.open_workbook(file_contents=base64.decodebytes(xls_file))
        bom_ids = self.env['mrp.bom']
        for sheet in wb.sheets():
            external_id = ref = product_name = quantity = bom_type_name = ""
            for row in range(sheet.nrows):
                # skip title
                if row == 0:
                    continue
                if sheet.cell(row, 0).value != '':
                    external_id = sheet.cell(row, 0).value
                    ref = sheet.cell(row, 1).value
                    product_name = sheet.cell(row, 2).value
                    quantity = sheet.cell(row, 3).value
                    bom_type_name = sheet.cell(row, 4).value
                line_product_name = sheet.cell(row, 5).value
                line_quantity = sheet.cell(row, 6).value
                bom = self.env.ref(external_id)
                bom_ids += bom
                product_tmpl_id = self.env['product.template'].search([('name', '=', product_name)])
                bom.write({'code': ref,
                           'product_tmpl_id': product_tmpl_id.id,
                           'product_qty': float(quantity),
                           'type': 'phantom' if bom_type_name == 'Kit' else 'normal'})
                line_product_ids = self.env['product.product'].search([('name', '=', line_product_name)])
                for product_id in line_product_ids:
                    bom.bom_line_ids.filtered(lambda r:r.product_id == product_id).product_qty = float(line_quantity)
        return bom_ids
