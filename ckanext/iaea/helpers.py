import logging

import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h


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


def get_available_organizations(data_dict):
    '''Returns a list of available organizations for the UI Create and Update dataset.
    The organizations are restricted to:
     - No organization
     - The main configured organization (default 'iaea')
     - Any organization that the package currently has, for compatibility
       with datasets that are already created on different organizations.
    '''
    available = h.organizations_available('create_dataset')
    organizations = []

    curr_org = data_dict.get('organization')
    main_org = get_main_organization()

    if not available:
        available = []

    for org in available:
        if main_org and org.get('name').lower() == main_org.get('name').lower():
            organizations.append(org)
        elif curr_org and curr_org.get('name').lower() == org.get('name').lower():
            organizations.append(org)

    return organizations


def get_main_organization():
    '''Returns the main organization for the portal.
    The is read from configuration property: ckanext.iaea.main_organization
    Returns the Organization data dict or None if there is no such organization.
    '''
    org_name = tk.config.get('ckanext.iaea.main_organization', 'iaea')
    try:
        return tk.get_action('organization_show')({
            'ignore_auth': True,
        }, {
            'id': org_name,
        })
    except tk.ObjectNotFound:
        return None

##The code from line 76 to line 77 has to be added for the data portal style for the Arabic group of languages

def is_rtl_language():
    return lang() in config.get('ckan.i18n.rtl_languages', 'he ar fa_IR').split()


# Raw resource-dict fields we allow into the resource "Additional Information"
# table, mapped to their display labels. Keys are as returned by CKAN's core
# format_resource_items(), i.e. underscores already replaced with spaces.
RESOURCE_ITEM_LABELS = {
    'package id': 'Package id',
    'id': 'Resource id',
    'resource id': 'Resource id',
    'size': 'Size',
}


def format_resource_items(items):
    '''Overrides the core helper of the same name to whitelist and relabel the
    raw resource fields shown in the resource "Additional Information" table.

    This deliberately lives in the plugin rather than in the theme's
    scheming/package/resource_read.html, because that template only wins when
    ckanext-iaea outranks ckanext-scheming in `ckan.plugins` (earlier in the
    list == higher template precedence). When it loses, ckanext-scheming's copy
    renders instead and any whitelist kept in our template is bypassed, which
    silently drops Package id / Resource id / Size from the page. Every copy of
    resource_read.html -- core's, scheming's and ours -- feeds its rows from
    this helper, so filtering here holds regardless of which one renders.

    Callers other than those three templates: none (checked across ckan and all
    bundled extensions).
    '''
    output = []
    for key, value in h.format_resource_items(items):
        label = RESOURCE_ITEM_LABELS.get(key)
        if label:
            # Translate at call time so the active request locale is used.
            output.append((tk._(label), value))
    return output


def get_helpers():
    return {
        "iaea_ga_header": googleanalytics_header,
        'iaea_get_available_organizations': get_available_organizations,
        'format_resource_items': format_resource_items,
    }
