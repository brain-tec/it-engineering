from odoo import api, registry, models, fields, _
from odoo.exceptions import UserError
from . import dhl_login_data

from base64 import b64encode
from datetime import date, datetime
from math import ceil
from time import sleep, time

import requests
from lxml import objectify

import logging
_logger = logging.getLogger(__name__)


SUCCESSFUL_DELIVERY_STATUS = 'Zustellung erfolgreich'


class MyWait:
    """Class aimed to provide a smart sleeping mechanism, as we can call DHL-functions only 3 times per second"""

    def __init__(self):
        self.sleep = sleep
        self.cnt = 0
        self.last_reset = time() - 1  # we start in the past because there was no call yet

    def wait(self):
        if time() - self.last_reset > 1:
            self.cnt = 0
            self.last_reset = time()

        self.cnt += 1

        if self.cnt > 3:
            sleep_time = 1.0 - ceil((time() - self.last_reset) * 10) / 10
            sleep(sleep_time)

            self.cnt = 1
            self.last_reset = time()


class HgTracking(models.Model):
    _name = 'hg.tracking'
    _description = 'DHL Tracking'
    _order = 'delivery, tracking_no'
    _rec_name = 'tracking_no'

    tracking_no = fields.Char(string='Tracking No', required=True)
    delivery = fields.Char(string='Delivery')
    raw_xml_status = fields.Text(string='Raw XML Status', readonly=True, copy=False)
    last_call = fields.Datetime('Last Call to DHL Server on', readonly=True, copy=False)
    done = fields.Boolean('Done', readonly=True, copy=False)
    error = fields.Char(string='Last Status Error', readonly=True, copy=False)
    error_image = fields.Char(string='Last Signature Error', readonly=True, copy=False)

    # All these field names come from DHL ==> do not change!
    # If we need to keep track of more tracking data, just create more fields named following DHL's lead
    product_name = fields.Char(string='Product', readonly=True, copy=False)
    pan_recipient_address = fields.Char(string='Destination Address', readonly=True, copy=False)
    dest_country = fields.Char(string='Destination Country', readonly=True, copy=False)
    recipient_name = fields.Char(string='Recipient', readonly=True, copy=False)
    recipient_id_text = fields.Char(string='Received by', readonly=True, copy=False)
    short_status = fields.Char(string='Short Status', readonly=True, copy=False)
    status = fields.Char(string='Last Status', readonly=True, copy=False)
    status_timestamp = fields.Char(string='Last Status on', readonly=True, copy=False)
    image = fields.Binary(string='Signature', readonly=True, copy=False)

    event_ids = fields.One2many('hg.tracking.event', 'tracking_id', string='Events', auto_join=True, readonly=True)

    def _update_events(self, req_content):
        event_env = self.env['hg.tracking.event']

        self.event_ids.unlink()

        for event_content in req_content.data.data.data:
            vals = {'tracking_id': self.id}

            for y in event_content.attrib:
                x = y.replace('-', '_')

                if x in event_env._fields:
                    vals[x] = event_content.attrib[y]

            event_env.create(vals)

    def get_tracking_data(self, days_for_done=30):
        icp_env = self.env['ir.config_parameter'].sudo()

        my_wait = MyWait()  # Needed to make sure that we call DHL-functions max. 3 times per second

        dhl_login_data.live = bool(self.env['ir.config_parameter'].sudo().get_param('hg_dhl.live', False))

        if dhl_login_data.live:
            login_data = dhl_login_data.DhlLogin
            # Note: DHL uses the application registration for user name and the user name for application.
            # It is strange, but it is like this. To avoid confusion in the setup screen, we cross change it here
            login_data.app_name = icp_env.get_param('hg_dhl.user')
            login_data.app_pwd = icp_env.get_param('hg_dhl.pwd')
            login_data.user = icp_env.get_param('hg_dhl.app')
            login_data.pwd = icp_env.get_param('hg_dhl.app_pwd')
        else:
            login_data = dhl_login_data.DhlLoginTest
            login_data.user = icp_env.get_param('hg_dhl.test_user')
            login_data.pwd = icp_env.get_param('hg_dhl.test_pwd')

        url_template = ('https://cig.dhl.de/services/{server}/rest/sendungsverfolgung?xml='
                        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
                        '<data'
                        ' language-code="de"'
                        ' appname="{app_name}"'
                        ' password="{app_pwd}"'
                        ' piece-code="{tracking_no}"'
                        ' request="{request}"'
                        '/>')

        for tracking in self:
            # Note that here we are not filtering out done trackings; this way, we can force the operation on
            # trackings that are already done

            tracking_no = tracking.tracking_no.zfill(20)

            url_detail = url_template.format(server=login_data.server,
                                             app_name=login_data.app_name,
                                             app_pwd=login_data.app_pwd,
                                             tracking_no=tracking_no,
                                             request="d-get-piece-detail")

            url_signature = url_template.format(server=login_data.server,
                                                app_name=login_data.app_name,
                                                app_pwd=login_data.app_pwd,
                                                tracking_no=tracking_no,
                                                request="d-get-signature")

            my_wait.wait()

            # Connects to the DHL Server and requests event details
            req = requests.get(url_detail, auth=(login_data.user, login_data.pwd))

            try:
                req_content = objectify.fromstring(req.content)
            except Exception:
                raise UserError(_('Error on getting tracking data from the DHL Server. '
                                  'Please make sure the login data in the Settings page is correct.'))

            tracking.raw_xml_status = req.content
            tracking.last_call = datetime.now()

            if req_content.attrib['code'] == '0':
                # No error; tracking data and events updated
                tracking.error = None

                for x in self._fields:
                    y = x.replace('_', '-')

                    try:
                        tracking[x] = req_content.data.attrib[y]
                    except Exception:
                        pass

                tracking._update_events(req_content)
            else:
                # There was an error with the event details request
                tracking.error = req_content.attrib['error']

            if tracking.short_status == SUCCESSFUL_DELIVERY_STATUS:
                my_wait.wait()

                # Connects to the DHL Server and requests the signature
                req = requests.get(url_signature, auth=(login_data.user, login_data.pwd))

                try:
                    req_content = objectify.fromstring(req.content)
                except Exception:
                    raise UserError(_('Error on requesting signature from the DHL Server. '
                                      'Please contact your admin.'))

                if req_content.attrib['code'] == '0':
                    # No error; tracking signature updated
                    tracking.error_img = None

                    image = bytes.fromhex(req_content.data.attrib['image'])
                    tracking.image = b64encode(image)
                else:
                    # There was an error with the signature request
                    tracking.error_image = req_content.attrib['error']

            # Marks the tracking as done if a successful delivery status was received was successful or if more
            # than <days_for_done> days have  passed since the creation of the tracking
            diff = date.today() - tracking.create_date.date()

            if diff.days > days_for_done or tracking.short_status == SUCCESSFUL_DELIVERY_STATUS:
                tracking.done = True

    @api.model
    def get_all_trackings_data(self, days_for_done=30, batch_size=5):
        """
        Function expected to be called by a cron job; it updates all open trackings in batches of <batch_size>.
        """

        logging.info('Processing open DHL Trackings...')

        open_trackings = self.search([('done', '=', False)])

        for batch in (open_trackings[i:i + batch_size] for i in range(0, len(open_trackings), batch_size)):
            with api.Environment.manage(), registry().cursor() as cr:
                batch = batch.with_env(batch.env(cr))
                batch.get_tracking_data(days_for_done)

                logging.info('Batch of DHL trackings processed: {}'.format(batch.ids))

        logging.info('Open DHL Trackings Processed!')


class HgTrackingEvent(models.Model):
    _name = 'hg.tracking.event'
    _description = 'DHL Tracking Event'
    _order = 'tracking_id, event_timestamp DESC'

    tracking_id = fields.Many2one('hg.tracking', string='Tracking Reference')

    # All these field names come from DHL ==> do not change!
    # If we need to keep track of more event data, just create more fields named following DHL's lead
    event_timestamp = fields.Char(string='Timestamp')
    event_country = fields.Char(string='Country')
    event_location = fields.Char(string='Place')
    event_short_status = fields.Char(string='Short Status')
    event_status = fields.Char(string='Status')
