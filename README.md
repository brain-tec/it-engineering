# it-engineering

This hg_dhl module is a stand alone tracking database for dhl express service. 
It is possible to enter or upload a delivery number and a tracking number 
and to collect all related tracking data from DHL server.
All tracking steps and the signature are stored in the Odoo DB.
This avoids that the information is lost after 90 days when DHL removes 
the data from their server.

There is no link to the odoo delivery document yet, this might be offered
at a later stage in a separate module.

Other interaction with DHL servers are not supported.
