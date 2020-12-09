# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'HG DHL Tracking',
    'version': '13.0.1.0',
    'category': 'Warehouse',
    'summary': 'HG DHL Tracking',
    'author': 'Harald',
    'maintainer': 'Harald',
    'website': 'https://it-gran.com',
    'depends': ['base', 'mail', 'base_setup'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hg_tracking.xml',
        'data/hg_cron.xml',
        'views/res_config_settings.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
