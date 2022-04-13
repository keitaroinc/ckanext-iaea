import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
from ckan.lib.plugins import DefaultTranslation
from ckanext.iaea.logic import action
from flask import Blueprint
from ckanext.iaea import view

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
    

class IaeaPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'iaea')

    def get_helpers(self):
        return {
            'featured_group': featured_group,
            'package_activity_html': package_activity_html,
            'suggested_filter_fields_serializer': suggested_filter_fields_serializer
        }
        
    # IActions
    def get_actions(self):
        return {
            'resource_view_create': action.resource_view_create,
            'resource_view_update': action.resource_view_update
        }
    # IBlueprint
    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'
        # Add plugin url rules to Blueprint object
        blueprint.add_url_rule(u'/dataset/metadata/<id>', view_func=view.metadata)

        return blueprint
