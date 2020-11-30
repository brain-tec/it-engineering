# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'HG DHL Tracking Modul',
    'version' : '13.0.1.0',
    'category' : 'Sales',
    'summary': 'DHL Tracking Infos',
    'sequence': 10,
    'description': """
This is a DHL-Express Service Tracking Tool.
It reads DHL Tracking information and make it available in Odoo.
It is independant from any Odoo object like order or delivery and can be used stand alone.
    """,
    'author' : 'Harald',
    'maintainer': 'Harald',
    'website': 'https://it-gran.com',
    'images' : ['images/journal_entries.jpeg'],
    'depends' : ['base', 'mail', 'base_setup'],
    'data': [
        # 'security/hg_dhl_groups.xml',
        'security/ir.model.access.csv',
        'views/hg_tracking.xml',
        'data/hg_cron.xml',
        'views/hg_settings.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
