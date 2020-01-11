from odoo import models,api,fields
import datetime


class IrActionsReportInheritPrintHistory(models.Model):
    _inherit = 'ir.actions.report'
    _rec_name = 'report_name'

    @api.noguess
    def report_action(self, docids, data=None, config=True):
        """Inherit report_Action to add a process that creates who printed the report"""
        self.env['print.history'].create({'user_id':self.env.user.id,'date':datetime.datetime.today(),'report_name':self.name})
        return super(IrActionsReportInheritPrintHistory,self).report_action(docids)
