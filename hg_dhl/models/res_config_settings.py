from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dhl_live = fields.Boolean(string='DHL Productive Server', config_parameter='hg_dhl.live')
    dhl_app = fields.Char(string='DHL App Name', config_parameter='hg_dhl.app')
    dhl_app_pwd = fields.Char(string='DHL App Password', config_parameter='hhg_dhl.app_pwd')
    
    dhl_test_user = fields.Char(string='DHL Developer\'s User', config_parameter='hg_dhl.test_user')
    dhl_test_pwd = fields.Char(string='DHL Developer\'s Password', config_parameter='hg_dhl.test_pwd')
    
    dhl_user = fields.Char(string='DHL Productive User', config_parameter='hg_dhl.user')
    dhl_pwd = fields.Char(string='DHL Productive Password', config_parameter='hg_dhl.pwd')
