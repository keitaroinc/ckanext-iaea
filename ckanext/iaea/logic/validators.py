import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as df
from ckan.common import _

from ckanext.iaea.helpers import get_main_organization


def package_organization_validator(value, context):
    '''Validates the organization on create/update package.
    The organization must be one of:
     - Empty value i.e. no owner organization for the package.
     - If set, then it must be set to the main organization of the portal.
     - If the package already was owned by an organization, the value must either be that old
       organization or the main portal organization (this is for compatibility with older packages).
    '''
    if not value:
        return value
    
    main_org = get_main_organization()
    package = context.get('package')

    if not package and not main_org:
        raise df.Invalid(_('Only datasets without organization are allowed'))

    if not package:
        # Check that the current owner_org is the main owner_org
        if value.lower() != main_org.get('name').lower() and value.lower() != main_org.get('id').lower():
            raise df.Invalid(_('The dataset owner organization must be {} or empty').format(main_org.get('name')))

    if package and main_org:
        new_org = _get_organization(value)
        if not new_org:
            raise df.Invalid(_('Package owner organization does not exist'))
        if new_org.get('id') != package.owner_org:
            # The owner organization was updated, so it must be set to the main organization or not at all.
            if new_org.get('id') != main_org.get('id'):
                # The new owner org is not the main org.
                raise df.Invalid(_('You can only update the package owner organization to {} or leave the old one.').format(main_org.get('name')))

    return value


def _get_organization(value):
    try:
        return tk.get_action('organization_show')({
            'ignore_auth': True,
        }, {
            'id': value,
        })
    except tk.ObjectNotFound:
        return None
