[![CKAN](https://img.shields.io/badge/ckan-2.8-orange.svg?style=flat-square)](https://github.com/ckan/ckan)

A custom CKAN extension for International Atomic Energy Agency (IAEA) data portal.

## Requirements

Make sure you have following tools installed on your machine:

* Docker
* Docker-compose

## Installation

First, set the portal hostname in `/etc/hosts`:

```bash
echo "127.0.0.1 ckan.iaea.local" >> /etc/hosts
```

To build the images:

```bash
docker compose build
```


## Configuration

You should set CKAN auth option to allow for datasets without organization:
```
ckan.auth.create_unowned_dataset = true
```

### Optional

```
# Main organization name for the portal. Default value is 'iaea'
ckanext.iaea.main_organization=iaea
```

## Run the full portal
To start the containers:

```bash
docker compose --profile full up
```
Now you can start development of your extension.


Try to access the portal at [http://ckan.iaea.local:5000](http://ckan.iaea.local:5000).

The default user and pass are set in `.env` - variables `CKAN_SYSADMIN_NAME` and `CKAN_SYSADMIN_PASSWORD`.

## Run only the services needed for CKAN

Run the docker compose without profile:
```bash
docker compose up
```

This would provide (accessible on the host):
* PostgreSQL server at port `5432`
* Redis at port `6379`
* Solr at port `8983`
* Datapusher at port `8800`


# Development setup

## Install required extensions

### ckanext-pdfview
We need version `0.0.7` for this extension:

```
git clone https://github.com/ckan/ckanext-pdfview.git
cd ckanext-pdfview
git checkout 0.0.7
python setup.py develop
```

### ckanext-authz-service

```bash
git clone https://github.com/datopian/ckanext-authz-service.git
cd ckanext-authz-service
python setup.py develop
pip install -r requirements.py2.txt
```

### ckanext-sentry

```
git clone https://github.com/okfn/ckanext-sentry.git
cd ckanext-sentry/
python setup.py develop
pip install -r requirements.txt 
```

### ckanext-basiccharts
```
git clone https://github.com/ckan/ckanext-basiccharts.git
cd ckanext-basiccharts/
python setup.py develop
```

### ckanext-basiccharts
```
git clone https://github.com/ckan/ckanext-basiccharts.git
cd ckanext-basiccharts
python setup.py develop
```

### ckanext-visualize
```
git clone https://github.com/datopian/ckanext-visualize.git
cd ckanext-visualize
python setup.py develop
pip install -r requirements.txt
```
### ckanext-geoview
This repository is cloned, to apply a patch for IAEA:

```
git clone https://github.com/keitaroinc/ckanext-geoview
cd ckanext-geoview
git checkout iaea
python setup.py develop
```

### ckanext-pages
On tag `v0.3.7`:

```
git clone https://github.com/ckan/ckanext-pages
cd ckanext-pages
git checkout v0.3.7
python setup.py develop
pip install -r requirements.txt

# Initialize the database
paster --plugin=ckanext-pages pages initdb --config=./ckan/development.ini
```
### ckanext-dataexplorer-react
Cloned, has customization:

```
git clone https://github.com/keitaroinc/ckanext-dataexplorer-react.git
cd ckanext-dataexplorer-react
git checkout iaea
python setup.py develop
pip install -r requirements.txt
```

### ckanext-dcat

On revision `v1.3.0`:
```
git clone https://github.com/ckan/ckanext-dcat
cd ckanext-dcat
git checkout v1.3.0
python setup.py develop
pip install -r requirements-py2.txt
```

### ckanext-report

```bash
git clone https://github.com/ckan/ckanext-report.git
cd ckanext-report
python setup.py develop
pip install -r requirements.txt

# Initialize the database
paster --plugin=ckanext-report report initdb --config=./ckan/development.ini
```

### ckanext-archiver

```bash
git clone https://github.com/ckan/ckanext-archiver.git
cd ckanext-archiver
python setup.py develop
pip install -r requirements.txt

# Initialize the database for archiver and report
paster --plugin=ckanext-archiver archiver init --config=./ckan/development.ini
paster --plugin=ckanext-report report initdb --config=./ckan/development.ini
```

### ckanext-qa

```
git clone git@github.com:keitaroinc/ckanext-qa.git
cd ckanext-qa
python setup.py develop
pip install requirements.txt

# Initialize the database
paster --plugin=ckanext-qa qa init --config=./ckan/development.ini
```

# ckanext-validation
```bash
git clone git@github.com:keitaroinc/ckanext-validation.git
cd ckanext-validation/
git checkout ckan-2.8.2
python setup.py develop
pip install -r requirements.txt

# Initialize the database

paster --plugin=ckanext-validation validation init-db -c ./ckan/development.ini
```