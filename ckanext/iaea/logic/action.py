import logging
from contextlib import contextmanager
import ckan.lib.datapreview as datapreview
import ckan.logic as l
import ckan.plugins as p
from ckan.logic.schema import default_create_resource_view_schema, default_update_resource_view_schema

from ckanext.iaea.helpers import get_main_organization

log = logging.getLogger(__name__)

ignore_missing = p.toolkit.get_validator('ignore_missing')

_MISSING = object()


@contextmanager
def _temporary_schema(context, schema):
    """Apply ``schema`` to ``context`` for the duration of the wrapped call only.

    ``context`` is shared with whatever called us, and several callers reuse a
    single context for a whole sequence of actions (xloader's ``xloader_hook``
    creates the default views and then updates the task status). Leaving our
    schema behind makes the next action in that sequence validate its own
    data_dict against a resource_view schema, which fails silently for the
    caller - so always put the previous value back.
    """
    previous = context.get('schema', _MISSING)
    context['schema'] = schema
    try:
        yield
    finally:
        if previous is _MISSING:
            context.pop('schema', None)
        else:
            context['schema'] = previous


@p.toolkit.chained_action
def resource_view_create(up_func, context, data_dict):
    view_plugin = datapreview.get_view_plugin(data_dict['view_type'])
    if not view_plugin:
        raise l.ValidationError(
            {"view_type": "No plugin found for view_type {view_type}".format(
                view_type=data_dict['view_type']
            )}
        )
    schema = default_create_resource_view_schema(view_plugin)
    schema.update({
        'suggested_filter_fields': [ignore_missing]
    })
    with _temporary_schema(context, schema):
        return up_func(context, data_dict)


@p.toolkit.chained_action
def resource_view_update(up_func, context, data_dict):
    model = context['model']
    resource_view = model.ResourceView.get(data_dict['id'])
    if not resource_view:
        raise l.NotFound
    view_plugin = datapreview.get_view_plugin(resource_view.view_type)
    schema = default_update_resource_view_schema(view_plugin)
    schema.update({
        'suggested_filter_fields': [ignore_missing]
    })
    with _temporary_schema(context, schema):
        return up_func(context, data_dict)
