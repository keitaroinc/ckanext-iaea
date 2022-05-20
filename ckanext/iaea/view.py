import logging
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
from flask.views import MethodView
import ckan.lib.dictization.model_dictize as model_dictize
from itertools import groupby
import ckan.lib.helpers as h

from ckan.common import _, c, request

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


class FeatureView(MethodView):
    """ feature selected view on dataset page
    """

    def _prepare(self, id):
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': c.user,
            u'auth_user_obj': c.userobj,
            u'save': u'save' in request.form
        }
        try:
            check_access(u'package_update', context, {u'id': id})

        except NotFound:
            return base.abort(404, _(u'Dataset not found'))
        except NotAuthorized:
            return base.abort(
                403,
                _(u'Unauthorized to edit %s') % u''
            )

        return context

    def post(self, id):
        context = self._prepare(id)

        featured_view = request.form.get('featured_view', False)
        data_dict = {u'id': id}
        if request.form['submit'] == 'submit':
            if not featured_view:
                h.flash_error('Please select view from the list.')
                data_dict['featured_view'] = ''
            else:
                data_dict['featured_view'] = featured_view
        else:
            data_dict['featured_view'] = ''

        # update package with selected featured view
        try:
            pkg_dict = get_action(u'package_patch')(context, data_dict)
        except NotFound:
            return base.abort(404, _(u'Dataset not found'))
        except NotAuthorized:
            return base.abort(403, _(u'Unauthorized to read dataset %s') % id)

        try:
            pkg_dict = get_action(u'package_show')(context, data_dict)
            pkg = context[u'package']
            dataset_type = pkg_dict[u'type'] or u'dataset'
        except NotFound:
            return base.abort(404, _(u'Dataset not found'))
        except NotAuthorized:
            return base.abort(403, _(u'Unauthorized to read dataset %s') % id)

        package_views = model.Session.query(
            model.ResourceView
        ).join(model.Resource).filter(model.Resource.package_id == pkg_dict['id']).all()

        package_views_list = model_dictize.resource_view_list_dictize(
            package_views, context)

        package_views_dict = []
        package_views_list = sorted(package_views_list, key=lambda k: k['resource_id'])
        for k, v in groupby(package_views_list, key=lambda x: x['resource_id']):
            resource_name = model.Session.query(model.Resource.name).filter(
                model.Resource.id == k).first()[0]
            view_dict = {
                'resource_name': resource_name,
                'resource_id': k,
                'views': list(v)
            }

            package_views_dict.append(view_dict)

        c.pkg_dict = pkg_dict
        c.pkg = pkg

        return base.render(
            u'package/features_view.html', {
                u'dataset_type': dataset_type,
                u'pkg_dict': pkg_dict,
                u'pkg': pkg,
                u'id': id,  # i.e. package's current name
                u'package_views': package_views_dict
            })

    def get(self, id):
        context = self._prepare(id)
        data_dict = {u'id': id}
        try:
            pkg_dict = get_action(u'package_show')(context, data_dict)
            pkg = context[u'package']
            dataset_type = pkg_dict[u'type'] or u'dataset'
        except NotFound:
            return base.abort(404, _(u'Dataset not found'))
        except NotAuthorized:
            return base.abort(403, _(u'Unauthorized to read dataset %s') % id)

        package_views = model.Session.query(
            model.ResourceView
        ).join(model.Resource).filter(model.Resource.package_id == pkg_dict['id']).all()

        package_views_list = model_dictize.resource_view_list_dictize(
            package_views, context)

        package_views_dict = []
        package_views_list = sorted(package_views_list, key=lambda k: k['resource_id'])
        for k, v in groupby(package_views_list, key=lambda x: x['resource_id']):
            resource_name = model.Session.query(model.Resource.name).filter(
                model.Resource.id == k).first()[0]
            view_dict = {
                'resource_name': resource_name,
                'resource_id': k,
                'views': list(v)
            }

            package_views_dict.append(view_dict)

        c.pkg_dict = pkg_dict
        c.pkg = pkg

        return base.render(
            u'package/features_view.html', {
                u'dataset_type': dataset_type,
                u'pkg_dict': pkg_dict,
                u'pkg': pkg,
                u'id': id,  # i.e. package's current name
                u'package_views': package_views_dict
            })
