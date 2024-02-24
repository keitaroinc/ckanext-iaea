from sqlalchemy.sql import exists
from sqlalchemy import or_

import ckan.model as model
import ckan.plugins as p
from ckan.common import config, g, _


@p.toolkit.chained_auth_function
def package_create(next_auth, context, data_dict):
    return _check_dataset_write_actions_restricted(next_auth, context, data_dict)


def _check_dataset_write_actions_restricted(next_auth, context, data_dict):
    res = next_auth(context, data_dict)
    if not res.get('success'):
        return res

    allowed_orgs = config.get('ckanext.iaea.allow_dataset_create_from_organization') or ''
    allowed_orgs = [o.strip() for o in allowed_orgs.strip().split(',') if o.strip()]

    if not allowed_orgs:
        return res

    user = context.get('auth_user_obj')
    if user:
        org_ids = get_organization_ids(allowed_orgs)
        if not org_ids:
            return res
        
        if not user_has_sufficient_roles_in_org(user.id, org_ids, ['editor', 'admin']):
            return {
                'success': False,
                'message': _('User {} cannot create datasets.').format(user.name),
            }

    return res

def get_allowed_organizations_ids():
    allowed_orgs = config.get('ckanext.iaea.allow_dataset_create_from_organization') or ''
    allowed_orgs = [o.strip() for o in allowed_orgs.strip().split(',') if o.strip()]

    if not allowed_orgs:
        return []
    return get_organization_ids(allowed_orgs)

def user_has_sufficient_roles_in_org(user_id, org_ids, roles):
    q = (model.Session.query(model.Member.group_id)
        .filter(model.Member.state=='active')
        .filter(model.Member.table_name=='user')
        .filter(model.Member.group_id.in_(org_ids))
        .filter(model.Member.table_id == user_id)
        .filter(model.Member.capacity.in_(roles))).exists()
    return model.Session.query(q).scalar()

def get_organization_ids(org_names_ids):
    q = (model.Session.query(model.Group.id)
        .filter(or_(model.Group.id.in_(org_names_ids), model.Group.name.in_(org_names_ids)))
        .filter(model.Group.state == 'active')
        .filter(model.Group.type == 'organization'))
    return [org_id[0] for org_id in q]
