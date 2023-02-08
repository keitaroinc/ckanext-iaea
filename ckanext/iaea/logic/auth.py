from sqlalchemy.sql import exists

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

    allowed_org = config.get('ckanext.iaea.allow_dataset_create_from_organization')
    if not allowed_org or not allowed_org.strip():
        return res

    user = context.get('auth_user_obj')
    if user:
        org_id = get_organization_id(allowed_org)
        if org_id is None:
            return res
        
        if not user_has_sufficient_roles_in_org(user.id, org_id, ['editor', 'admin']):
            return {
                'success': False,
                'message': _('User {} cannot create datasets.').format(user.name),
            }

    return res

def user_has_sufficient_roles_in_org(user_id, org_id, roles):
    q = (model.Session.query(model.Member.group_id)
        .filter(model.Member.state=='active')
        .filter(model.Member.table_name=='user')
        .filter(model.Member.group_id == org_id)
        .filter(model.Member.table_id == user_id)
        .filter(model.Member.capacity.in_(roles))).exists()
    return model.Session.query(q).scalar()

def get_organization_id(org_name_id):
    q = (model.Session.query(model.Group.id)
        .filter(model.Group.id == org_name_id or model.Group.name == org_name_id)
        .filter(model.Group.state == 'active')
        .filter(model.Group.type == 'organization'))
    for org_id in q:
        return org_id
    return None
