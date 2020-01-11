from odoo import models, fields, api
import base64
import tempfile
import shutil


########################## Parent model ####################################################################


class PeriodicReportSave(models.Model):
    _name = 'periodic.report.save'
    _description = 'Periodic report saving'
    _rec_name = 'user_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, invisible=True)
    periodic_report_save_model_ids = fields.One2many('periodic.report.save.model', 'periodic_report_save_id')
    periodic_report_result_ids = fields.One2many('periodic.report.result', 'periodic_report_save_id')

    def test(self):
        print('File created ')
        result = []
        with tempfile.TemporaryDirectory() as tmpdirname:
            print('created temporary directory', tmpdirname)
        for rec in self.periodic_report_save_model_ids:
            result_reports = []
            model_description = self.env['%s' % rec.model_name]._description

            # result.append((0, 0, {'model_name': rec.model_name}))
            dir = tempfile.TemporaryDirectory()
            for line in rec.report_ids:

                print('Reports are :', rec.report_ids)
                for seq,record in enumerate(self.env['%s' % (rec.model_name)].search([]).ids,1):
                    report_render = self.env['ir.actions.report'].browse(line.id)
                    data = base64.b64encode(report_render.render_qweb_pdf([record])[0])
                    filename = rec.model_name.replace('.', '_')+'_%s'%seq+'.pdf'
                    result_reports.append((0,0,{'binary_id': data,
                                                'filename': filename}))
                    with open('%s/%s'%(dir.name,filename), 'wb') as file:
                        file.write(report_render.render_qweb_pdf([record])[0])

            binary_zip = shutil.make_archive('/tmp/exe', 'zip', '%s'%dir.name)
            with open(binary_zip, "rb",) as f:
                print(f.name)
                binary_zip_result = base64.b64encode(f.read())

            result.append((0, 0, {'model_name': model_description, 'binary_ids': result_reports,'zip':binary_zip_result,
                                  'zip_filename':str(model_description) + '.zip'}))

        # print('The result is ', result)
        # print('Before entering the var')
        self.periodic_report_result_ids = result


########################## Added periodic report  ####################################################################


class InheritIrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    periodic_report_save_id = fields.Many2one('periodic.report.save.model')


########################## Added periodic report  ####################################################################


class PeriodicReportSaveModel(models.Model):
    _name = 'periodic.report.save.model'
    _description = 'Model report saving'

    def get_allowed_models(self):
        result = []
        allowed_models = set(self.env['ir.actions.report'].search([]).mapped('model'))
        for line in allowed_models:
            result.append((line, self.env['%s'%line]._description))
        return result

    periodic_report_save_id = fields.Many2one('periodic.report.save')
    model = fields.Selection(selection=get_allowed_models)
    model_name = fields.Char()
    report_ids = fields.Many2many('ir.actions.report', relation='periodic_reports_rel', string='Reports')

    @api.onchange('model')
    def get_model_name(self):
        for line in self:
            print(line.model)
            line.model_name = line.model


########################### Result ####################################################################################


class PeriodicReportResult(models.Model):
    _name = 'periodic.report.result'

    periodic_report_save_id = fields.Many2one('periodic.report.save')
    model_name = fields.Char()
    binary_ids = fields.One2many('periodic.report.binary', 'result_id',string='PDF files')
    zip = fields.Binary(string='Zip file')
    zip_filename = fields.Char()


########################### Binary ####################################################################################


class PeriodicReportBinary(models.Model):
    _name = 'periodic.report.binary'
    _rec_name = 'filename'
    binary_id = fields.Binary()
    filename = fields.Char()
    result_id = fields.Many2one('periodic.report.result')
