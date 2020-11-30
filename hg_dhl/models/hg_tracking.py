from odoo import api, models, fields
import requests
from . import dhllogin
from lxml import objectify
from base64 import b64encode
from datetime import date, datetime
from time import sleep, time
from math import ceil



# ----------------------------------------------------------------------------------------------
# Class MyWait
# ----------------------------------------------------------------------------------------------
class MyWait():
    """ this class is a wait function as we can only call DHL up to 3 times a second """
    def __init__(self):
        self.time = time
        self.sleep = sleep
        self.cnt = 0
        self.lastreset = time() - 1  # we start in the past because there was no call yet
    def wait(self):
        if time() - self.lastreset > 1:
            self.cnt = 0
            self.lastreset = time()
        print('CNT', self.cnt, self.lastreset, time())
        self.cnt = self.cnt + 1
        if self.cnt > 3:
            x = 1.0 - ceil((time() - self.lastreset) * 10) / 10
            print('WAIT!', x)
            sleep(x)
            self.cnt = 1
            self.lastreset = time()


# ----------------------------------------------------------------------------------------------
# Class HgTracking
# ----------------------------------------------------------------------------------------------
class HgTracking(models.Model):
    _name = 'hg.tracking'
    _description = 'Tracking Daten zum Lieferschein'
    _order = 'delivery, tracking_no'
    complete = fields.Boolean('DHL Info komplett')
    lcall = fields.Datetime('Zuletzt aktualisiert am')
    delivery = fields.Char(string='Lieferung')
    tracking_no = fields.Char(string='Tracking No')
    dest_country = fields.Char(string='Empfangsland')
    pan_recipient_address = fields.Char(string='Empfängeradresse')
    product_name = fields.Char(string='Produkt')
    recipient_id_text = fields.Char(string='Entgegengenommen von')
    recipient_name = fields.Char(string='Name Empfänger')
    short_status = fields.Char(string='Status kurz')
    status = fields.Char(string='Letzter Status')
    status_timestamp = fields.Char(string='Zeitstempel')
    dhl_status = fields.Text(string='DHL Tracking', readonly='true')
    image = fields.Binary(string='Unterschrift')
    error = fields.Char(string='Fehler bei letztem Zugriff (Status)')
    error_img = fields.Char(string='Fehler bei letztem Zugriff (Unterschrift)')
    event_line = fields.One2many('hg.tracking.event', 'tracking_ref', string='Events', copy=True,
                                 auto_join=True)


    def update_events(self, content):
        """
        method to update the events that belong to this tracking number
        """
        print(self.event_line)
        self.event_line.unlink()
        dhl_obj = objectify.fromstring(content)
        for mydata in dhl_obj.data.data.data:
            vals = {
                'tracking_ref': self.id
            }
            new_event = self.env['hg.tracking.event'].create(vals)
            new_event.tracking_no = self.tracking_no
            for x in mydata.attrib:
                y = x.replace('-', '_')
                try:
                    new_event[y] = mydata.attrib[x]
                except:
                    pass


    def get_tracking(self):
        """ Method to call the DHL Server and get the tracking data """
        mysleep = MyWait()  # we need a counter because we can only call DHL 3 times a second
        dhllogin.live = self.env['ir.config_parameter'].sudo().get_param('hg_dhl.dhllive')
        if dhllogin.live == 'True':
            login = dhllogin.DhlLogin
            # note: DHL uses the application registration for user name and the user name for application
            # strange, but it is like this. To avoid confusion in the setup screen, we cross change it here
            login.appname = self.env['ir.config_parameter'].sudo().get_param('hg_dhl.dhluser')
            login.password = self.env['ir.config_parameter'].sudo().get_param('hg_dhl.dhlpwd')
            login.user = self.env['ir.config_parameter'].sudo().get_param('hg_dhl.dhlapp')
            login.pwd = self.env['ir.config_parameter'].sudo().get_param('hg_dhl.dhlapppwd')
        else:
            login = dhllogin.DhlLoginTest
            login.user = self.env['ir.config_parameter'].sudo().get_param('hg_dhl.dhltestuser')
            login.pwd = self.env['ir.config_parameter'].sudo().get_param('hg_dhl.dhltestpwd')

        for track in self:
            if not track.complete:
                # assemble the url to access dhl server
                url = "https://cig.dhl.de/services/" + login.server + "/rest/sendungsverfolgung?xml="
                url = url + '<?xml version="1.0"'
                url = url + ' encoding="UTF-8"'
                url = url + ' standalone="no"?>'
                url = url + ' <data appname="' + login.appname +'"'
                url = url + ' language-code="de"'
                url = url + ' password="' + login.password + '"'
                # prepare piece-code e.g. piece-code="00340434161094015902"'
                if len(track.tracking_no) < 20:
                    # leading zero missing, we add that
                    no = '0' * (20-len(track.tracking_no)) + track.tracking_no
                else:
                    no = track.tracking_no
                url = url + ' piece-code="' + no + '"'
                url_detail = url + ' request="d-get-piece-detail"/>'
                url_signi = url + ' request="d-get-signature"/>'

                # Call DHL Server for event details
                mysleep.wait()
                req = requests.get(url_detail, auth=(login.user, login.pwd))
                # put data into an object
                dhl_obj = objectify.fromstring(req.content)
                # we store the full reply in a text field
                track.dhl_status = req.content
                track.lcall = datetime.now()
                # check for error
                if dhl_obj.attrib['code'] == '0':
                    track.error = None
                    # fill our data base object fields
                    for x in track._fields:
                        y = x.replace('_', '-')
                        try:
                            track[x] = dhl_obj.data.attrib[y]
                        except:
                            pass
                    track.update_events(req.content)
                else:
                    # store the error, if there was any
                    track.error = dhl_obj.attrib['error']
                # Call DHL Server for signature
                if track.short_status == 'Zustellung erfolgreich':
                    mysleep.wait()
                    req = requests.get(url_signi, auth=(login.user, login.pwd))
                    # we store the image in our object
                    dhl_obj = objectify.fromstring(req.content)
                    if dhl_obj.attrib['code'] == '0':
                        track.error_img = None
                        # no error code, we store the image
                        b = bytes.fromhex(dhl_obj.data.attrib['image'])
                        track.image = b64encode(b)
                    else:
                        # store the error text
                        track.error_img = dhl_obj.attrib['error']
            # check if finally delivered
            difference = date.today() - track.create_date.date()
            if difference.days > 30 or track.short_status == 'Zustellung erfolgreich':
                # we do not check DHL again for data now
                track.complete = True

    @api.model
    def get_tracking_all(self):
        """ function to call by cron (job) to update all tracking information  """
        tracks = self.search([('complete', '=', False)])
        tracks.get_tracking()
        for rec in tracks:
            print('Lieferung: ', rec.delivery, 'complete:', rec.complete)


# ----------------------------------------------------------------------------------------------
# Class HgTrackingEvent
# ----------------------------------------------------------------------------------------------
class HgTrackingEvent(models.Model):
    """ This class contains the tracking events from DHL with timestamp and location """
    _name = 'hg.tracking.event'
    _description = 'Tracking Events zur Lieferung'
    _order = 'tracking_ref, event_timestamp'
    tracking_ref = fields.Many2one('hg.tracking', string='Tracking Ref')
    tracking_no = fields.Char(string='Tracking No')
    event_timestamp = fields.Char(string='Zeitstempel')
    event_country = fields.Char(string='Land')
    event_location = fields.Char(string='Ort')
    event_short_status = fields.Char(string='Status kurz')
    event_status = fields.Char(string='Status')


