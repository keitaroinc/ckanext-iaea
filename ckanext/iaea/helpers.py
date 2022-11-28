import logging

import ckan.plugins.toolkit as tk


CONFIG_GA_ID='ckanext.iaea.googleanalytics.id'
log = logging.getLogger(__name__)


def googleanalytics_header():
    '''Renders the Googleanalytics head snippet adding basic tracking to CKAN.

    Please set 'ckanext.iaea.googleanalytics.id' in your ckan.ini file with the
    GA id from your Googleanalytics account.

    '''
    ga_id = tk.config.get(CONFIG_GA_ID)
    if not ga_id:
        log.error('Googleanalytics ID is missing in config. Please set %s.', CONFIG_GA_ID)
        return ''

    data = {
        'ga_id': ga_id,
    }

    return tk.render_snippet(
        'iaea/googleanalytics/snippets/gtag.html',
        data
    )


def get_helpers():
    return {
        "iaea_ga_header": googleanalytics_header,
    }
