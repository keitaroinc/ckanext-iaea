\set datastore_ro_password '\'' `echo $DATASTORE_READONLY_PASSWORD` '\''

CREATE ROLE datastore_ro SUPERUSER LOGIN PASSWORD :datastore_ro_password;
CREATE DATABASE datastore OWNER ckan ENCODING 'utf-8';
