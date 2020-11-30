from odoo import api, fields, models


class HgDhlTrackSettings(models.TransientModel):
    """This class contains the setup for HG DHL Tracking module
       dhluser = user provided from DHL for partners, a so called ZT-user
       dhlpwd = the password for the user"""
    _inherit = 'res.config.settings'

    dhltestuser = fields.Char(string="DHL User des Entwicklers")
    dhltestpwd = fields.Char(string="DHL Password des Entwicklers")
    dhllive = fields.Boolean(string="Zugriff auf produktiven DHL Server")
    dhluser = fields.Char(string="DHL User")
    dhlpwd = fields.Char(string="DHL Password")
    dhlapp = fields.Char(string="DHL Applikations-Registrierung")
    dhlapppwd = fields.Char(string="DHL Applikations-Password")

    def set_values(self):
        super(HgDhlTrackSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('hg_dhl.dhltestuser', self.dhltestuser)
        self.env['ir.config_parameter'].set_param('hg_dhl.dhltestpwd', self.dhltestpwd)
        self.env['ir.config_parameter'].set_param('hg_dhl.dhluser', self.dhluser)
        self.env['ir.config_parameter'].set_param('hg_dhl.dhlpwd', self.dhlpwd)
        self.env['ir.config_parameter'].set_param('hg_dhl.dhllive', self.dhllive)
        self.env['ir.config_parameter'].set_param('hg_dhl.dhlapp', self.dhlapp)
        self.env['ir.config_parameter'].set_param('hg_dhl.dhlapppwd', self.dhlapppwd)



    @api.model
    def get_values(self):
        res = super(HgDhlTrackSettings, self).get_values()

        sudo = self.env['ir.config_parameter'].sudo()
        dhltestuser = sudo.get_param('hg_dhl.dhltestuser')
        dhltestpwd = sudo.get_param('hg_dhl.dhltestpwd')
        dhluser = sudo.get_param('hg_dhl.dhluser')
        dhlpwd = sudo.get_param('hg_dhl.dhlpwd')
        dhllive = sudo.get_param('hg_dhl.dhllive')
        dhlapp = sudo.get_param('hg_dhl.dhlapp')
        dhlapppwd = sudo.get_param('hg_dhl.dhlapppwd')

        res.update(
            dhluser=dhluser, dhlpwd=dhlpwd, dhllive=dhllive, dhltestuser=dhltestuser, dhltestpwd=dhltestpwd,
            dhlapp=dhlapp, dhlapppwd=dhlapppwd
        )
        return res
