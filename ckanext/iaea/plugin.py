import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
from ckanext.iaea.helpers import get_helpers
from ckanext.iaea.logic import action, validators


class IaeaPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IValidators)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "iaea")

    # ITemplateHelpers
        
    def get_helpers(self):
        iaea_helpers = {
            # 'featured_group': featured_group,
            # 'package_activity_html': package_activity_html,
            # 'suggested_filter_fields_serializer': suggested_filter_fields_serializer,
            # 'featured_view_url': featured_view_url,
        }
        iaea_helpers.update(get_helpers())
        return iaea_helpers

    # IValidators
    def get_validators(self):
        return {
            'iaea_owner_org_validator': validators.package_organization_validator,
        }
