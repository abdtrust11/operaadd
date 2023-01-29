from odoo import models,fields,api
import time
import datetime

class ReportVendor(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.vendor_report.vendor_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        product_id = data['from']['product_id']
        vendor_id = data['from']['vendor_id']
        type = data['from']['type']
        docs = []
        product_obj = self.env['product.product'].browse(product_id)
        vendor_obj = self.env['res.partner'].browse(vendor_id)
        print('11111111111111111',product_obj)
        if not vendor_obj:
            if product_obj:
                for pro in product_obj:
                    total_qty_in = 0.0
                    total_sale_qty = 0.0

                    move_purchase = self.env['stock.move'].sudo().search([
                        ('product_id', '=', pro.id),
                        ('state', '=', 'done'),
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

                    docs.append(
                        {
                            'vendor': False,
                            'product': pro.name,
                            'avalible_qty': avalible_qty,
                            'qty': total_qty_in,
                            'sale_qty': total_sale_qty,
                            'sales_per': round(sales_per, 2),
                        })
            else:
                total_qty_in = 0.00
                total_sale_qty = 0.00

                move_purchase = self.env['stock.move'].sudo().search([
                    ('purchase_line_id', '!=', False), ('state', '=', 'done'), ('picking_code', '=', 'incoming')
                ])

                vendor_id = move_purchase.mapped('purchase_line_id.partner_id')
                for line in vendor_id:
                    for move in move_purchase:
                        if line.id == move.purchase_line_id.partner_id.id:
                            total_qty_in += move.product_uom_qty
                    docs.append(
                        {
                            'vendor': line.name,
                            'product': False,
                            'avalible_qty': False,
                            'qty': total_qty_in,
                            'sale_qty': False,
                            'sales_per': False
                        })
                print('1111111111111')
                print('vendor_id', vendor_id)

        elif vendor_obj and product_obj:
            for pro in product_obj:
                total_qty_in = 0.0
                total_sale_qty = 0.00
                move_purchase = self.env['stock.move'].sudo().search([
                    ('product_id', '=', pro.id),
                    ('state', '=', 'done'),
                    ('purchase_line_id', '!=', False), ('picking_code', '=', 'incoming'),
                    ('purchase_line_id.partner_id.id', '=', vendor_obj.id)
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
                docs.append(
                    {
                        'vendor': vendor_obj.name,
                        'product': pro.name,
                        'avalible_qty': avalible_qty,
                        'qty': total_qty_in,
                        'sale_qty': total_sale_qty,
                        'sales_per': round(sales_per, 2),
                    })
        elif vendor_obj and not product_obj:
            if type == 'per_vendor':
                total_qty_in = 0.00
                total_sale_qty = 0.00
                move_purchase = self.env['stock.move'].sudo().search([
                    ('picking_code', '=', 'incoming'),
                    ('state', '=', 'done'),
                    ('purchase_line_id.partner_id', '=', vendor_obj.id)
                ])

                move_sales_in = self.env['stock.move'].sudo().search([
                    ('sale_line_id', '!=', False), ('state', '=', 'done'), ('picking_code', '=', 'outgoing')
                ])

                for move in move_purchase:
                    total_qty_in += move.product_uom_qty

                for sale in move_sales_in:
                    total_sale_qty += sale.product_uom_qty

                docs.append(
                    {
                        'vendor': vendor_obj.name,
                        'product': False,
                        'avalible_qty': False,
                        'qty': total_qty_in,
                        'sale_qty': False,
                        'sales_per': False,
                    })
            else:

                move_purchase = self.env['stock.move'].sudo().search([
                    ('picking_code', '=', 'incoming'),
                    ('state', '=', 'done'),
                    ('purchase_line_id.partner_id', '=', vendor_obj.id)
                ])

                move_sales_in = self.env['stock.move'].sudo().search([
                    ('sale_line_id', '!=', False), ('state', '=', 'done'), ('picking_code', '=', 'outgoing')
                ])
                product_map = move_purchase.mapped('product_id')
                for pro in product_map:
                    total_qty_in = 0.00
                    total_sale_qty = 0.00
                    avalible_qty = 0.00
                    for move in move_purchase:
                        if pro.id == move.product_id.id:
                            total_qty_in += move.product_uom_qty
                            avalible_qty += move.product_id.qty_available
                            for sale in move_sales_in:
                                if pro.id == sale.product_id.id:
                                    total_sale_qty += sale.product_uom_qty

                    if total_qty_in > 0.0:
                        sales_per = total_sale_qty / total_qty_in * 100
                    else:
                        sales_per = 0.0
                    docs.append(
                        {
                            'vendor': vendor_obj.name,
                            'product': pro.name,
                            'avalible_qty': avalible_qty,
                            'qty': total_qty_in,
                            'sale_qty': total_sale_qty,
                            'sales_per': round(sales_per, 2),
                        })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,

        }