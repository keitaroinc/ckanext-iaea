import logging
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model

from ckan.common import  _, c 

log = logging.getLogger(__name__)

render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action


def metadata(id):  # noqa
    """Render this package's public activity stream page.
    """
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': c.user,
        u'for_view': True,
        u'auth_user_obj': c.userobj
    }
    
    data_dict = {u'id': id}
    try:
        pkg_dict = get_action(u'package_show')(context, data_dict)
        pkg = context[u'package']
        dataset_type = pkg_dict[u'type'] or u'dataset'
    except NotFound:
        return base.abort(404, _(u'Dataset not found'))
    except NotAuthorized:
        return base.abort(403, _(u'Unauthorized to read dataset %s') % id)

    # TODO: remove
    c.pkg_dict = pkg_dict
    c.pkg = pkg

    return base.render(
        u'package/metadata.html', {
            u'dataset_type': dataset_type,
            u'pkg_dict': pkg_dict,
            u'pkg': pkg,
            u'id': id,  # i.e. package's current name
        }
    )