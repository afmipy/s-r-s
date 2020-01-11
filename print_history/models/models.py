from odoo import models,fields,api


class PrintHistory(models.Model):
    _name = 'print.history'

    user_id = fields.Many2one('res.users')
    date = fields.Datetime()
    report_name = fields.Char()
