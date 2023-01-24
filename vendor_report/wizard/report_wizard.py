# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _
import pytz
import xlwt
import odoo.osv.osv
import re
import base64
from io import BytesIO
import datetime
from datetime import date, time
import pytz

from pytz import timezone

class VendortReportWizard(models.TransientModel):
    _name = 'vendor.report.wizard'



    product_id = fields.Many2many(comodel_name="product.product", string="Product")
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    type = fields.Selection([('per_product', 'Product'),
									('per_vendor', 'Vendor'),
                                  ('per_product_verient', 'Product Verient'),
                                  ('per_location', 'Location'),
									], string='view type', required=True,
									default='per_vendor')
    excel_sheet = fields.Binary('Download Report')
    excel_sheet_name = fields.Char(string='Name', size=64)

    @api.onchange('product_id')
    def onchange_template_id(self):
        product_obj = self.env['product.product']
        domain = ['|', ('active', '=', True), ('active', '=', False)]
        products = product_obj.sudo().search(domain)
        if self.product_id:
            products = self.env['product.product']
            for rec in self.product_id:
                products += rec
        return {'domain': {'product_id': [('id', 'in', products.ids)]}}

    def get_report_data(self):
        data = []
        product_obj = self.env['product.product']
        domain = ['|', ('active', '=', True), ('active', '=', False)]

        # if self.vendor_id:
        #     domain += [('purchase_line_id.partner_id.id', '=', self.vendor_id.id)]

        products = product_obj.sudo().search(domain)
        if self.product_id:
            products = self.env['product.product']
            for rec in self.product_id:
                products += rec
        if not self.vendor_id:
            if self.product_id:
                for pro in products:
                    total_qty_in = 0.0
                    total_sale_qty = 0.0
                    print('11111111111111',pro.id)
                    move_purchase = self.env['stock.move'].sudo().search([
                        ('product_id', '=', pro.id),
                        ('state','=','done'),
                        ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming')
                    ])

                    move_sales_in = self.env['stock.move'].sudo().search([
                        ('product_id', '=', pro.id),
                        ('state', '=', 'done'),
                        ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
                    ])
                    avalible_qty = pro.qty_available

                    for move in move_purchase:
                        total_qty_in += move.product_uom_qty

                    for sale in move_sales_in:
                        total_sale_qty += sale.product_uom_qty
                    if total_qty_in > 0.0:
                        sales_per = total_sale_qty / total_qty_in * 100
                    else:
                        sales_per = 0.0
                    print('$$$$$$',move_purchase)
                    print('$$$$$$',total_qty_in)
                    data.append(
                        {
                            'vendor':False,
                            'product':pro.name,
                            'avalible_qty':avalible_qty,
                            'qty':total_qty_in,
                            'sale_qty':total_sale_qty,
                            'sales_per': round(sales_per, 2),
                        })
            else:
                total_qty_in = 0.00
                total_sale_qty = 0.00

                move_purchase = self.env['stock.move'].sudo().search([
                    ('purchase_line_id', '!=', False), ('state','=','done'),('picking_code', '=', 'incoming')
                ])

                vendor_id = move_purchase.mapped('purchase_line_id.partner_id')
                for line in vendor_id:
                    for move in move_purchase:
                        if line.id == move.purchase_line_id.partner_id.id:
                            total_qty_in += move.product_uom_qty
                    data.append(
                        {
                            'vendor':line.name,
                            'product': False,
                            'avalible_qty': False,
                            'qty': total_qty_in,
                            'sale_qty': False,
                            'sales_per':False
                        })
                print('1111111111111')
                print('vendor_id',vendor_id)

        elif self.vendor_id and self.product_id:
            for pro in products:
                total_qty_in = 0.0
                total_sale_qty = 0.00
                move_purchase = self.env['stock.move'].sudo().search([
                    ('product_id', '=', pro.id),
                    ('state', '=', 'done'),
                    ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming'),
                    ('purchase_line_id.partner_id.id', '=', self.vendor_id.id)
                ])

                move_sales_in = self.env['stock.move'].sudo().search([
                    ('product_id', '=', pro.id),
                    ('state', '=', 'done'),
                    ('sale_line_id', '!=', False), ('picking_code', '=', 'outgoing')
                ])
                for move in move_purchase:
                    total_qty_in += move.product_uom_qty

                for sale in move_sales_in:
                    total_sale_qty += sale.product_uom_qty
                if total_qty_in > 0.0:
                    sales_per = total_sale_qty / total_qty_in * 100
                else:
                    sales_per = 0.0
                avalible_qty = pro.qty_available
                data.append(
                    {
                        'vendor':self.vendor_id.name,
                        'product':pro.name,
                        'avalible_qty':avalible_qty,
                        'qty':total_qty_in,
                        'sale_qty':total_sale_qty,
                        'sales_per': round(sales_per, 2),
                    })
        elif self.vendor_id and not self.product_id:
            total_qty_in = 0.00
            total_sale_qty = 0.00
            move_purchase = self.env['stock.move'].sudo().search([
                ('picking_code', '=', 'incoming'),
                ('state', '=', 'done'),
                ('purchase_line_id.partner_id', '=', self.vendor_id.id)
            ])

            move_sales_in = self.env['stock.move'].sudo().search([
                ('sale_line_id', '!=', False),('state','=','done'), ('picking_code', '=', 'outgoing')
            ])

            for move in move_purchase:
                total_qty_in += move.product_uom_qty

            for sale in move_sales_in:
                total_sale_qty += sale.product_uom_qty

            data.append(
                {
                    'vendor': self.vendor_id.name,
                    'product':False,
                    'avalible_qty': False,
                    'qty': total_qty_in,
                    'sale_qty':False,
                    'sales_per':False,
                })

        return data

    def generate_report(self):
        self.ensure_one()
        workbook = xlwt.Workbook()
        TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 200;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour tan, pattern_back_colour tan'
        )
        TABLE_HEADER_batch = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour light_green, pattern_back_colour light_green'
        )
        TABLE_HEADER_payslib = xlwt.easyxf(
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour silver_ega, pattern_back_colour silver_ega'
        )
        TABLE_HEADER_Data = TABLE_HEADER
        TABLE_HEADER_Data.num_format_str = '#,##0.00_);(#,##0.00)'
        STYLE_LINE = xlwt.easyxf(
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin; '
            'pattern: pattern solid, pattern_fore_colour silver_ega, pattern_back_colour silver_ega'
        )
        STYLE_Description_LINE = xlwt.easyxf(
            'borders:   top thin;'
            'font: bold 1, name Tahoma, color-index black,height 160;'
            'align: vertical center, horizontal center, wrap off;'
            'pattern: pattern solid, pattern_fore_colour tan, pattern_back_colour tan'
        )
        TABLE_data = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index black,height 150;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour white, pattern_back_colour white'
        )
        TABLE_data.num_format_str = '#,##0.00'
        TABLE_HEADER_batch.num_format_str = '#,##0.00'
        xlwt.add_palette_colour("gray11", 0x11)
        workbook.set_colour_RGB(0x11, 222, 222, 222)
        TABLE_data_tolal_line = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index white,height 200;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour blue_gray, pattern_back_colour blue_gray'
        )

        TABLE_data_tolal_line.num_format_str = '#,##0.00'
        STYLE_Description_LINE.num_format_str = '#,##0.00'
        TABLE_data_o = xlwt.easyxf(
            'font: bold 1, name Aharoni, color-index black,height 150;'
            'align: vertical center, horizontal center, wrap off;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'pattern: pattern solid, pattern_fore_colour gray11, pattern_back_colour gray11'
        )
        STYLE_LINE_Data = STYLE_LINE
        STYLE_LINE_Data.num_format_str = '#,##0.00_);(#,##0.00)'

        worksheet = workbook.add_sheet(_('Payment Plan'))
        lang = self.env.user.lang
        # if lang == "ar_SY":
        worksheet.cols_right_to_left = 1

        worksheet.col(0).width = 256 * 20
        worksheet.col(1).width = 256 * 20
        worksheet.col(2).width = 256 * 15
        worksheet.col(3).width = 256 * 15
        worksheet.col(4).width = 256 * 15
        worksheet.col(5).width = 256 * 15
        worksheet.col(6).width = 256 * 15
        worksheet.col(7).width = 256 * 15
        worksheet.col(8).width = 256 * 15
        worksheet.col(9).width = 256 * 15
        worksheet.col(10).width = 256 * 15
        worksheet.col(11).width = 256 * 15
        worksheet.col(13).width = 256 * 15
        worksheet.col(13).width = 256 * 15
        row = 0
        col = 0
        worksheet.write_merge(row, row + 1, col, col + 8, _('تقرير الموردين'), TABLE_HEADER_Data)

        row += 3
        data_lines = self.get_report_data()
        col = 0
        # if self.vendor_id:
        worksheet.write(row, col, _("المورد"), TABLE_HEADER_payslib)
        col += 1
        # if self.product_id:
        worksheet.write(row, col, _("المنتج"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("الكمية المتوفرة"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("الكمية المشتراه"), TABLE_HEADER_payslib)
        col += 1
        worksheet.write(row, col, _("الكمية المباعة"), TABLE_HEADER_payslib)
        col +=1
        worksheet.write(row, col, _("معدل البيع من الوارد"), TABLE_HEADER_payslib)
        print("data_lines ==> ", data_lines)
        row += 1
        for line in data_lines:
            col = 0
            # if self.vendor_id:
            worksheet.write(row, col, line['vendor'] or '', TABLE_HEADER_batch)
            col += 1
            # if self.product_id:
            worksheet.write(row, col, line['product']  or '', TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['avalible_qty'] or '', TABLE_HEADER_batch)
            col += 1

            worksheet.write(row, col, line['qty'] or '', TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['sale_qty'] or '', TABLE_HEADER_batch)
            col += 1
            worksheet.write(row, col, line['sales_per'] or '', TABLE_HEADER_batch)
            col += 1


            row += 1

        row += 1

        if data_lines:
            output = BytesIO()
            workbook.save(output)
            self.excel_sheet_name = 'Vendor Report'

            self.excel_sheet = base64.b64encode(output.getvalue())
            self.excel_sheet_name = str(self.excel_sheet_name) + '.xls'
            output.close()
            return {
                'type': 'ir.actions.act_url',
                'name': 'Vendor Report',
                'url': '/web/content/vendor.report.wizard/%s/excel_sheet/Vendor Report.xls?download=true' % (
                    self.id),
                'target': 'self'
            }
        else:
            view_action = {
                'name': _('Vendor Report'),
                'view_mode': 'form',
                'res_model': 'vendor.report.wizard',
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new',
                'context': self.env.context,
            }

            return view_action