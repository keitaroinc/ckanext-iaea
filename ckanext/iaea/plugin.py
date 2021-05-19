import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
 

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

    
class IaeaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'iaea')

    def get_helpers(self):
        return {
            'featured_group': featured_group
        }
        