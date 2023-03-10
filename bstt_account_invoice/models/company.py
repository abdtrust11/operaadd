#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    foreign_name = fields.Char(string="Foreign Name", help="Foreign Name")
    branch_name_e = fields.Char(string="Company Branch Name", help="Foreign Name")
    branch_name_a = fields.Char(string="Branch Name", help="Foreign Name")


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    swift_code = fields.Char('Swift Code')

