import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
from ckan.lib.plugins import DefaultTranslation
from ckanext.iaea.logic import action, validators
import ckanext.iaea.logic.auth as ia
from flask import Blueprint
from ckanext.iaea import view
import ckan.model as model
import ckanext.iaea.middleware as middleware
from ckan.model.meta import engine
from threading import Thread, Event
import signal
import sys


from ckanext.iaea.helpers import get_helpers

def package_activity_html(id):
    activity =  logic.get_action(
            'package_activity_list_html')({}, {'id': id ,'limit': 8})
    return activity
   
                   
def featured_group():
    try:
        group_list = logic.get_action('group_list')(
            {}, {'sort': 'package_count', 'all_fields': True})
        if group_list: 
            return group_list
        else:
            return logic.get_action('group_list')(
                {}, {'all_fields': True})
    except (logic.NotFound, logic.ValidationError, logic.NotAuthorized):
        return {}


def suggested_filter_fields_serializer(datapackage, view_dict):
    suggested_filter_fields = view_dict.get('suggested_filter_fields', False)
    try:
        fields = datapackage['resources'][0]['schema']['fields']
    except KeyError as e:
        fields = []
    rules = []
    date  = {}
    if suggested_filter_fields: 
        suggested_fields_with_type = [field for field in fields if field['name'] in suggested_filter_fields]
        for field in suggested_fields_with_type:
            if field['type'] in ['datetime', 'date']:
                date = {
                    'startDate': None,
                    'endDate': None,
                    'fieldName': field['name']
                }
            else:
                rules.append({
                    'combinator': 'AND',
                    'field': field['name'],
                    'operator': '=',
                    'value': ''
                })
    if rules:
        datapackage['resources'][0].update({'rules': rules})
    if date:
        datapackage['resources'][0].update({'date': date})
    return datapackage
    

def featured_view_url(pkg):
    featured_view = model.ResourceView.get(pkg['featured_view'])
    return toolkit.h.url_for(qualified=True, controller='package',
                               action='resource_view', id=pkg['name'],
                               resource_id=featured_view.resource_id,
                               view_id=featured_view.id)
                            
class IaeaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm,
                  DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IMiddleware, inherit=True)
    plugins.implements(plugins.IAuthFunctions)


    # IDatasetForm
    def update_package_schema(self):
        schema = super(IaeaPlugin, self).update_package_schema()
        schema.update({
            u'featured_view': [toolkit.get_validator(u'ignore_missing'),
                             toolkit.get_converter(u'convert_to_extras')]
        })
        return schema

    def show_package_schema(self):
        schema = super(IaeaPlugin, self).show_package_schema()
        schema.update({
            u'featured_view': [toolkit.get_converter(u'convert_from_extras'),
                             toolkit.get_validator(u'ignore_missing')],
        })
        return schema

    def is_fallback(self):
        return True

    def package_types(self):
        return []


    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'iaea')
        start_conn_pool_ping()

    def get_helpers(self):
        iaea_helpers = {
            'featured_group': featured_group,
            'package_activity_html': package_activity_html,
            'suggested_filter_fields_serializer': suggested_filter_fields_serializer,
            'featured_view_url': featured_view_url,
        }
        iaea_helpers.update(get_helpers())
        return iaea_helpers
        
    # IActions
    def get_actions(self):
        return {
            'resource_view_create': action.resource_view_create,
            'resource_view_update': action.resource_view_update,
        }

    # IValidators
    def get_validators(self):
        return {
            'iaea_owner_org_validator': validators.package_organization_validator,
        }

    # IBlueprint
    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'
        # Add plugin url rules to Blueprint object
        blueprint.add_url_rule(u'/dataset/metadata/<id>', view_func=view.metadata)
        blueprint.add_url_rule(u'/dataset/<id>/view', view_func=view.FeatureView.as_view(str(u'feature_view')))
        return blueprint


    # IAuthFunctions
    def get_auth_functions(self):
        return {'package_create': ia.package_create}

    def make_middleware(self, app, config):

        return middleware.RestrictMiddleware(app, config)


def start_conn_pool_ping():

    class ConnPoolKeepalive(Thread):

        def __init__(self, *args, **kwargs):
            super(ConnPoolKeepalive, self).__init__(*args, **kwargs)
            self._exit = Event()

        def end_keepalive(self):
            self._exit.set()

        def run(self):
            while True:
                with engine.connect() as conn:
                    conn.execute('SELECT 1').scalar()
                if self._exit.wait(1):
                    print('**Exited')
                    return

    t = ConnPoolKeepalive()
    t.start()

    handlers = {}

    def handle_signal(sig, frame):
        t.end_keepalive()
        if handlers.get(sig):
            handlers[sig](sig, frame)


    def trap_signal(*args):
        for sig in args:
            handler = signal.signal(sig, handle_signal)
            if handler:
                handlers[sig] = handler

    trap_signal(signal.SIGINT)
