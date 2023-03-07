import { fail } from "k6";
import { CKANAdmin, CKANUser } from './ckan.js';

const BASE_URL = __ENV.BASE_URL || 'https://data-dev.iaea.org';
const POLITENESS_DELAY = __ENV.POLITENESS_DELAY ? parseInt(__ENV.POLITENESS_DELAY) : 0;
const CKAN_ADMIN_TOKEN = __ENV.CKAN_ADMIN_TOKEN;
const CKAN_TEST_USERS_PREFIX = __ENV.CKAN_TEST_USERS_PREFIX || 'test_user';
const CKAN_TEST_USERS_NUMBER = __ENV.CKAN_TEST_USERS_NUMBER ? parseInt(__ENV.CKAN_TEST_USERS_NUMBER) : 10;
const CKAN_TEST_USERS_ORG = __ENV.CKAN_TEST_USERS_ORG || 'load_test_org';
const CKAN_TEST_CSV_FILE_PREFIX = __ENV.CKAN_TEST_CSV_FILE_PREFIX || 'test_file';
const CKAN_TEST_CSV_FILE_NUMBER = __ENV.CKAN_TEST_CSV_FILE_NUMBER ? parseInt(__ENV.CKAN_TEST_CSV_FILE_NUMBER) : 10;
const CONCURRENT_USERS = __ENV.CONCURRENT_USERS || 10;


if (!CKAN_ADMIN_TOKEN) {
  fail('Please set the CKAN_ADMIN_TOKEN')
}

const FILES = [];
for(let i = 0; i < CKAN_TEST_CSV_FILE_NUMBER; i++) {
  const fileName = `/home/k6/run/${CKAN_TEST_CSV_FILE_PREFIX}_${i+1}.csv`;
  FILES.push({
    fileName: fileName,
    fileData: open(fileName, 'b'),
  })
}

export const options = {
  setupTimeout: "10m",
  scenarios: {
    stress: {
      executor: "ramping-vus",
      startVUs: 0,
      gracefulRampDown: "5m",
      stages: [
        { duration: "1m", target: CONCURRENT_USERS }, // Ramp up to all concurrent users
        { duration: "9m", target: CONCURRENT_USERS }, // Hold
        { duration: "1m", target: 0 },  // scale down. Recovery stage.
      ],
    },
  },
};

export function setup() {
  console.log(`Testing URL: ${BASE_URL}, concurrent users: ${CONCURRENT_USERS} (politeness delay: ${POLITENESS_DELAY || 'none'}).`)
  const admin = new CKANAdmin(BASE_URL, CKAN_ADMIN_TOKEN, CKAN_TEST_USERS_ORG);

  console.log("Creating test users")
  const users = [];
  for (let i = 0; i < CKAN_TEST_USERS_NUMBER; i++) {
    const user = admin.getOrCreateUser(`${CKAN_TEST_USERS_PREFIX}_${i + 1}`);
    console.log(`Created user: ${user.id}`);
    users.push(user);
  }

  const datasets = users.map(user => {
    const ckanUser = new CKANUser(BASE_URL, user.apikey, CKAN_TEST_USERS_ORG);
    const dataset = ckanUser.createDataset();
    for(let i = 0; i < 2; i++) {
      // choose random file
      const file = FILES[Math.floor(Math.random() * FILES.length)];
      ckanUser.createResource(dataset.id, `${user.name}-${i+1}.csv`, file.fileData);
    }
    console.log(`Created dataset: ${dataset.id}`)
    return dataset;
  })

  console.log('Tests setup complete.')
  return {
    users: users,
    datasets: datasets,
  };
}

export function teardown(data) {
  const admin = new CKANAdmin(BASE_URL, CKAN_ADMIN_TOKEN, CKAN_TEST_USERS_ORG);
  console.log('Clearing datasets')
  data.datasets.forEach(dataset => {
    admin.purgeDataset(dataset.id);
    console.log(`Purged: ${dataset.id}`)
  })
  
  console.log("Clearing users")
  data.users.forEach(user => {
    admin.deleteUser(user.id);
    console.log(`Deleted: ${user.id}`)
  })
}

export default function (data) {
  const user = data.users[Math.floor(Math.random() * data.users.length)];
  const ckanUser = new CKANUser(BASE_URL, user.apikey, CKAN_TEST_USERS_ORG);

  ckanUser.listDatasets();

  for(let i = 0; i < data.datasets.length/2; i++) {
    // choose random dataset to visit
    const dataset = data.datasets[Math.floor(Math.random() * data.datasets.length)];
    const resultDataset = ckanUser.packageShow(dataset.id);
    resultDataset.resources.forEach(rc => {
      const resultResource = ckanUser.resourceShow(rc.id);
      if (resultResource.datastore_active) {
        // Get the data from datastore
        ckanUser.datastoreSearch(resultResource.id);
      } else {
        // Data is not yet in the datastore, so fetch the data directly as download.
        ckanUser.downloadResource(resultResource.url);
      }
    })
  }
}