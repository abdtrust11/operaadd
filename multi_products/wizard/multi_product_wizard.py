# -*- coding: utf-8 -*-


from odoo import _, api, fields, models, _


class MultiProductWizard(models.TransientModel):
    _name = 'multi.product.wizard'
    _description = 'Multi Product Wizard'

    product_ids = fields.Many2many('product.product', string="Product's")

    def add_products(self):
        active_id = self._context.get('active_id')
        if self._context.get('request_type') == 'po':
            purchase_id = self.env['purchase.order'].browse(active_id)
            for line in self.product_ids:
                purchase_id.write({'order_line': [
                    (0, 0, {'product_id': line.id}),
                ]})
        elif self._context.get('request_type') == 'stock':
            picking_id = self.env['stock.picking'].browse(active_id)
            for line in self.product_ids:
                picking_id.write({'move_ids_without_package': [
                    (0, 0, {'product_id': line.id, 'name': line.name,
                            'product_uom': line.uom_id.id,
                            'location_id': picking_id.location_id.id,
                            'location_dest_id': picking_id.location_dest_id.id,
                            }),
                ]})
