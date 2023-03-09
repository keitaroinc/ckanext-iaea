CONCURRENT_USERS=( 30 50 100 )
CONCURRENT_USERS_FILES_UPLOAD=( 1 5 10 )
ORG_NAME="load_test"
SLEEP_TIME=180

echo "== Running stress and load tests =="
if [ -z "${SITE_URL}" ]; then
    echo "Please set SITE_URL to the URL of the portal."
    exit 1
fi
if [ -z "${ADMIN_TOKEN}" ]; then
    echo "Please set ADMIN_TOKEN with the token of CKAN admin user."
    exit 1
fi

echo " * Site: ${SITE_URL}"
echo " * Concurrent users: ${CONCURRENT_USERS}"
echo " * Test organization: ${ORG_NAME}"

echo ":: Updating k6.io docker image"
docker pull grafana/k6

echo ":: Generating test CSV files"
echo ":: Generating 10MiB files:"
python gen_upload_files.py --file-prefix test_file --file-size 10485760
echo ":: Generating smaller 50KiB files:"
python gen_upload_files.py --file-prefix smaller_file --file-size 51200
echo ":: Test CSV files generated."

echo ":: Testing users visiting the site"
for users_count in "${CONCURRENT_USERS[@]}"; do
    echo ":: Running scenario with ${users_count} users."
    docker run -it --network host \
        --volume $(pwd):/home/k6/run \
        grafana/k6 run --insecure-skip-tls-verify \
            --env BASE_URL="${SITE_URL}" \
            --env CKAN_ADMIN_TOKEN="${ADMIN_TOKEN}" \
            --env CKAN_TEST_USERS_ORG="${ORG_NAME}" \
            --env CONCURRENT_USERS="${users_count}" \
            run/visit-site.test.js
done
echo ":: Test users visiting the site done."
echo ""

echo ":: Testing parallel upload of files"
for users_count in "${CONCURRENT_USERS_FILES_UPLOAD[@]}"; do
    echo ":: Running scenario with ${users_count} users."
    docker run -it --network host \
        --volume $(pwd):/home/k6/run \
        grafana/k6 run --insecure-skip-tls-verify \
            --env BASE_URL="${SITE_URL}" \
            --env CKAN_ADMIN_TOKEN="${ADMIN_TOKEN}" \
            --env CKAN_TEST_USERS_ORG="${ORG_NAME}" \
            --env CONCURRENT_USERS="${users_count}" \
        run/upload-resources.test.js
    echo ":: Upload files scenario done."
    echo ":: Pausing for ${SLEEP_TIME} seconds between tests..."
    sleep ${SLEEP_TIME}
done
echo ":: Testing of parallel upload of files done."
echo ""

echo ":: Testing API calls to fetch data"
echo ":: Pausing again for ${SLEEP_TIME} to give time to recover from previous tests."
sleep ${SLEEP_TIME}
for users_count in "${CONCURRENT_USERS[@]}"; do
    echo ":: Running scenario with ${users_count} users."
    docker run -it --network host \
        --volume $(pwd):/home/k6/run \
        grafana/k6 run --insecure-skip-tls-verify \
            --env BASE_URL="${SITE_URL}" \
            --env CKAN_ADMIN_TOKEN="${ADMIN_TOKEN}" \
            --env CKAN_TEST_USERS_ORG="${ORG_NAME}" \
            --env CONCURRENT_USERS="${users_count}" \
            --env CKAN_TEST_CSV_FILE_PREFIX="smaller_file" \
            run/access-api.test.js
    echo ":: Pausing for ${SLEEP_TIME} seconds between tests..."
    sleep ${SLEEP_TIME}
done
echo ":: Test API calls to fetch data done."
