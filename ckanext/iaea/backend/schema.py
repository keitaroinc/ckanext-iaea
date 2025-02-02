"""
Copyright (c) 2018 Keitaro AB

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from ckan.plugins import toolkit

not_empty = toolkit.get_validator('not_empty')
ignore_missing = toolkit.get_validator('ignore_missing')
ignore_empty = toolkit.get_validator('ignore_empty')
positive_integer = toolkit.get_validator('is_positive_integer')


def mssql():
    return {
        'db_name': [not_empty, unicode],
        'host': [not_empty, unicode],
        'port': [not_empty, positive_integer, unicode],
        'username': [not_empty, unicode],
        'password': [not_empty, unicode],
        'sql': [not_empty, unicode]
    }
