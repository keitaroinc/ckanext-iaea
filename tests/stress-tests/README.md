Stress tests for IAEA data portal
=================================

Stress tests for the following scenarios:
* Users visiting the main portal site - 30, 50 and 100 concurrent users.
* Users uploading rather large CSV files (around 10MiB) - 10 concurrent users.
* Users fetching data from the API - 30, 50 and 100 concurrent users.

# Running the tests

Tests are implemented with [k6.io](https://k6.io/) framework and the easiest way is to run them with `docker`.
There is also a script provided that runs all tests scenarios: `run_tests.sh`.

## Prerequisites

You'll need `docker` and `python` installed.

Then you need to create an organization on the data portal that will be used for the load testing.
This is due to the fact that the tests will create lot of datasets and resources, and in case of a crash of the script
the datasets might remain on the site. The datasets will be put into this organization - so even if some datasets do remain
after the load test, they could be easily purged from the load test organization.

To create the organization, login to the portal as an admin, then create new organzation by opening `/organization` page on the
site and clicking on "Add Organization".

> **NOTE:** Make sure you put `load_test` as the name for the organization. If you choose different name, please update the `ORG_NAME` variable in `run_tests.sh` script.

> **Important:** Do **not** set `ORG_NAME` to the main IAEA organization (`the-international-atomic-energy-agency`) as the load tests might pollute this organization with the test datasets created by the load test scripts.

## Run the tests

Invoke the script to run all the tests:

```bash
SITE_URL="https://data-dev.iaea.org" \
ADMIN_TOKEN="<put-your-ckan-admin-token-here>" \
./run_tests.sh
```

where:
* `SITE_URL` is the base URL of the data portal:
  * dev: `https://data-dev.iaea.org`
  * staging: `https://data-staging.iaea.org`
  * prod: `https://data.iaea.org`
* `ADMIN_TOKEN`: is the CKAN admin user API token. To obtain this token, login as a **CKAN admin**, then click on your profile and scroll down. The API token is displayed in the left panel.
* `ORG_NAME` - this could only be set in the `run_tests.sh` script. Change this **only if you create test organization which name is not `load_test`**.
* `CONCURRENT_USERS` - could only be set in the `run_tests.sh` script. Controls the number of concurrent users for the different scenarios.

> Running all tests with default configuration would take about 1h 20m.