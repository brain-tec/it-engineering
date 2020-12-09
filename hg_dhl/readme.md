HG DHL
======

This is a DHL-Express Service tracking tool. It allows us to connect to DHL servers and retrieve relevant DHL 
tracking data for a given tracking number.

This module provides access to a new app called **DHL Tracking**.
In order to be able to access such an app, users must be granted the *Manage DHL Tracking* security group.
Furthermore, in order for the app to work properly, the settings under *DHL Tracking / Settings* must be 
configured.

During the installation of this module, a scheduled action in charge of regularly retrieving tracking data of *open
trackings* is created.

(DHL z-account required.)
