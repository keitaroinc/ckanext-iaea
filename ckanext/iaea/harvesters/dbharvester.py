from ckan.plugins.core import SingletonPlugin, implements
from ckanext.harvest.interfaces import IHarvester

from ckanext.iaea.backend import get_backend

class DBHarvester(SingletonPlugin):
    
    implements(IHarvester)

    def info(self):
        return {
            'name': 'dbharvester',
            'title': 'DB Source Harvest',
            'Description': 'Harvest data from a database data source.'
        }
    
    def validate_config(self, config):

        return ''
    
    def gather_stage(self, harvest_job):

        return []
    
    def fetch_stage(self, harvest_object):

        return True
    
    def import_stage(self, harvest_object):

        return True