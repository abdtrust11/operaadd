# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, api,fields, _
from datetime import datetime
import random
import barcode
from barcode.writer import ImageWriter
import base64

import os
class ProductTemplatese(models.Model):
    _inherit = 'product.template'
    barcode_new = fields.Char(store=True)
    @api.model
    def create(self, vals):
        res = super(ProductTemplatese, self).create(vals)
        if res:
            barcode_str =self.env['ir.sequence'].get('product.number')
            res.write({'barcode_new': barcode_str })
        return res

class productproduct(models.Model):
    _inherit = "product.product"

    check_barcode_setting= fields.Boolean('Check Barcode Setting')
    barcode_img = fields.Binary('Barcode Image')

    @api.model
    def default_get(self,field_lst):
        res = super(productproduct, self).default_get(field_lst)
        if not self.env['res.config.settings'].search([], limit=1, order="id desc").gen_barcode:
            res['check_barcode_setting'] = True
        return res

    @api.model
    def create(self, vals):
        res = super(productproduct, self).create(vals)
        number_random = 0
        if res:
            if not vals.get('barcode') and self.env['res.config.settings'].sudo().search([], limit=1, order="id desc").gen_barcode:
                if self.env['res.config.settings'].search([], limit=1, order="id desc").generate_option == 'date':
                    barcode_str = self.env['barcode.nomenclature'].sanitize_ean("%s%s" % (res.id, datetime.now().strftime("%d%m%y%H%M")))

                elif self.env['res.config.settings'].search([], limit=1, order="id desc").generate_option == 'default':

                    product = self.env['product.template'].search([('id','=',vals['product_tmpl_id'])])
                    barcode_str = str(product.year_id.code) + str(product.barcode_new)+ '-' + self.env['ir.sequence'].get('product.code')
                    # barcode_str = self.env['barcode.nomenclature'].sanitize_ean("%s" % (new_bar))
                else:
                    number_random = int("%0.13d" % random.randint(0,999999999999))
                    barcode_str = self.env['barcode.nomenclature'].sanitize_ean("%s" % (number_random))

                # ean = barcode.get('ean13', barcode_str, writer=ImageWriter())
                path  =  os.path.abspath('bi_generate_product_ean13')
                # filename = ean.save(path+'ean13')
                # f = open(filename, 'rb')
                # jpgdata = f.read()
                # imgdata = base64.encodebytes(jpgdata)
                res.write({'barcode' : barcode_str,})
                # os.remove(filename)

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
