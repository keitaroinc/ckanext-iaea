from ckan.plugins.core import SingletonPlugin, implements
from ckanext.harvest.interfaces import IHarvester
import ckan.plugins.toolkit as tk
from ckan.common import _
from ckan import lib

from ckanext.iaea.backend import get_backend


_df = lib.navl.dictization_functions


ValidationError = tk.ValidationError
_validator = tk.get_validator


ConfigSchema = {
    'db_type': [_validator('not_empty'), _validator('one_of')(['mssql', 'postgresql'])],
    'db_host': [_validator('not_empty'), unicode],
    'db_port': [_validator('not_empty'), _validator('is_positive_integer'), unicode],
    'db_user': [_validator('not_empty'), unicode],
    'db_password': [_validator('not_empty'), unicode],
    'db_database_name': [_validator('not_empty'), unicode],
    'datasets_query': [_validator('not_empty'), unicode],
    'fetch_data_query': [_validator('not_empty'), unicode],
    'paginate_fetch_data': [_validator('boolean_validator')],
    'paginate_size': [_validator('int_validator')],
}

DEFAULT_PAGINATION_SIZE = 250
MAX_PAGINATION_SIZE = 500


class DBHarvester(SingletonPlugin):
    
    implements(IHarvester)

    def info(self):
        return {
            'name': 'dbharvester',
            'title': 'Harvest from database',
            'Description': 'Harvest data from a database data source.'
        }
    
    def validate_config(self, config):
        '''
        Required config for the harvester?
        DB needed config properties:
         - db_url: url to the database in the form: dialect+driver://username:password@host:port/database
            - maybe some additional properties for the db driver?
        - datasets_query: SQL query to select the list of datasets.
            - this query must return the following columns:
                - id text, the dataset ID
                - name text, the name of the dataset
                - any additional columns would also be available in the harvest object
            - an example query: 'SELECT id::text, username as name from users' - generate 1 dataset for each user
        - resources_query: SQL query to get the resources metadata for each dataset.
            - must return:
                - name: the name of the resource
            - if not supplied, a default 1 resource will be created with the name of the given dataset
            - the dataset ID would be available in the resource_query
                - the additional parameters would also be available in the query
        - fetch_data_query: the SQL query that would fetch the data for a particular resource.
            - dataset ID will be available
            - resource ID will be available
            - other attributes fetched in the dataset/resource are also available
            - if 'paginate_data_fetch' is set to true, then :offset and :limit would be available
        - paginate_fetch_data: boolean, if true, then the fetch_data_query will be paginated
        - pagination_size: int, the size of the :limit for the pagination
        '''

        if not config:
            return config

        data, errors = _df.validate(config, ConfigSchema, {})
        if errors:
            raise ValidationError(errors)
        
        if 'resources_query' in config:
            data['resources_query'] = str(config['resources_query']).strip()
        
        if data.get('paginate_fetch_data'):
            if not data.get('pagination_size'):
                data['pagination_size'] = DEFAULT_PAGINATION_SIZE
            data['pagination_size'] = min(data['pagination_size'], MAX_PAGINATION_SIZE)

        return data
    
    def gather_stage(self, harvest_job):
        '''
        This stage collects the datasets and the resources for the datasets
        Executes:
        1. run datasets_query against the database to collect the datasets metadata
        2. for each collected dataset run resources_query (if available)
        3. store all of these in the harvest_object
        '''
        config = harvest_job.source.config
        print('config =>', config)

        backend = get_backend({
            'db_type': config['db_type']
        })

        

        return []
    
    def fetch_stage(self, harvest_object):
        '''
        Doesn't actually do the fetch, but creates the datasets and the resources collected in the gather_stage.
        Actual CKAN package IDs and resource IDs are updated in the harvest object.
        '''
        return True
    
    def import_stage(self, harvest_object):
        '''Does the actual data fetch.
        For each resource (all datasets) created in the previous stage, do:
            1. Run fetch_data_query with the dataset and resource parameters.
                - if paginated, run the query with :offset and :limit until no more rows are returned.
            2. For each fetched batch, call datastore_upsert action and push the data into datastore
        '''
        return True