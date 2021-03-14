from odoo import http
from odoo.http import request

class Hg_Dhl_Link(http.Controller):
    """
        This class is to support a link for external systems to call a certain tracking.
        Because external systems do not know the internal record id, we provide an automated redirection.
        The external link is .../hg_dhl/nnnnnnnnnnnnnnnn and n stand for the DHL tracking number
    """
    @http.route('/hg_dhl/<track_no>', website=True, type='http', auth='user')
#    @http.route('/hg_dhl/<track_no>', type='http', auth='user')
    def hg_redirect(self, track_no, **kwargs):
        # get the record id
        hg_dhl_track = request.env['hg.tracking'].sudo().search([('tracking_no','=',track_no)])
        # assemble the autmatic redirection
        try:
            # we take first element only, in case there might be more than one
            track_id = hg_dhl_track[0].id
        except Exception:
            return '<h1>Keine Tracking Daten gefunden!</h1>'
        #finally we redirect to the tracking form with track_id
        url_string = '/web#id={track_id}&model=hg.tracking&view_type=form'
        return request.redirect(url_string.format(track_id=track_id))