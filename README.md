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