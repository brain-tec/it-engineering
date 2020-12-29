HG DHL
======

This is a DHL-Express Service tracking tool. It allows us to connect to DHL servers and retrieve relevant DHL 
tracking data for a given tracking number and store all tracking information in the Odoo database.
So you get independent from the 90 days retention period of DHL.

This module provides access to a new app called **DHL Tracking**.
In order to be able to access such an app, users must be granted the *DHL Tracking / User* security group.
Furthermore, in order for the app to work properly, the settings under *DHL Tracking / Settings* must be 
configured.

During the installation of this module, a scheduled action in charge of regularly retrieving tracking data of *open
trackings* is created.

There is no link to the Odoo delivery document yet, because it was designed as a side car for a different ERP System. 
If required, the connection to Odoo delivery documents can be provided.

The module provides an external URL with tracking number to directly access tracking data from outside Odoo.
Integration into other ERP System landscapes e.g. SAP can be easily be done.

(DHL z-account required.)
