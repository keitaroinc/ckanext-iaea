import logging
import ckan.lib.datapreview as datapreview
import ckan.logic as l
import ckan.plugins as p

from ckan.logic.schema import default_create_resource_view_schema, default_update_resource_view_schema

log = logging.getLogger(__name__)

ignore_missing = p.toolkit.get_validator('ignore_missing')


@p.toolkit.chained_action
def resource_view_create(up_func, context, data_dict):
    log.warn(data_dict)
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
    context['schema'] = schema
    result = up_func(context, data_dict)
    return result


@p.toolkit.chained_action
def resource_view_create(up_func, context, data_dict):
    log.warn(data_dict)
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
    context['schema'] = schema
    result = up_func(context, data_dict)
    return result


@p.toolkit.chained_action
def resource_view_update(up_func, context, data_dict):
    print(data_dict)
    model = context['model']
    resource_view = model.ResourceView.get(data_dict['id'])
    if not resource_view:
        raise l.NotFound
    view_plugin = datapreview.get_view_plugin(resource_view.view_type)
    schema = default_update_resource_view_schema(view_plugin)
    schema.update({
        'suggested_filter_fields': [ignore_missing]
    })
    context['schema'] = schema
    result = up_func(context, data_dict)
    print(result)
    return result
