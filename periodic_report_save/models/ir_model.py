from odoo import models,api,fields


class InheritIrModelPeriodic(models.Model):
    _inherit = 'ir.model'

    has_report = fields.Boolean(compute='check_if_has_report')

    def check_if_has_report(self):
        for line in self:
            line.has_report = bool(self.env['ir.actions.report'].search([('model','=',line.model)],limit=1))