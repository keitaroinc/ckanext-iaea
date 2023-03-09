import { fail } from "k6";
import {CKANAdmin, CKANUser} from './ckan.js';

const BASE_URL = __ENV.BASE_URL || 'https://data-dev.iaea.org';
const POLITENESS_DELAY = __ENV.POLITENESS_DELAY ? parseInt(__ENV.POLITENESS_DELAY) : 0;
const CKAN_ADMIN_TOKEN = __ENV.CKAN_ADMIN_TOKEN;
const CKAN_TEST_USERS_PREFIX = __ENV.CKAN_TEST_USERS_PREFIX || 'test_user';
const CKAN_TEST_USERS_NUMBER = __ENV.CKAN_TEST_USERS_NUMBER ? parseInt(__ENV.CKAN_TEST_USERS_NUMBER) : 10;
const CKAN_TEST_USERS_ORG = __ENV.CKAN_TEST_USERS_ORG || 'load_test_org';
const CKAN_TEST_CSV_FILE_PREFIX = __ENV.CKAN_TEST_CSV_FILE_PREFIX || 'test_file';
const CKAN_TEST_CSV_FILE_NUMBER = __ENV.CKAN_TEST_CSV_FILE_PREFIX ? parseInt(__ENV.CKAN_TEST_CSV_FILE_PREFIX) : 10;
const CONCURRENT_USERS = __ENV.CONCURRENT_USERS ? parseInt(__ENV.CONCURRENT_USERS) : 10;

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
  scenarios: {
    stress: {
      executor: "ramping-vus",
      startVUs: 0,
      gracefulRampDown: "5m",
      stages: [
        { duration: "1m", target: CONCURRENT_USERS }, // Ramp up to all concurrent users
        { duration: "9m", target: CONCURRENT_USERS }, // Hold
        { duration: "1m", target: 0 },                // scale down. Recovery stage.
      ],
    },
  },
};

export function setup() {
  console.log(`Testing URL: ${BASE_URL} with ${CONCURRENT_USERS} concurrent users (politeness delay: ${POLITENESS_DELAY || 'none'}).`)
  const admin = new CKANAdmin(BASE_URL, CKAN_ADMIN_TOKEN, CKAN_TEST_USERS_ORG);

  console.log("Creating test users")
  const users = [];
  for (let i = 0; i < CKAN_TEST_USERS_NUMBER; i++) {
    const user = admin.getOrCreateUser(`${CKAN_TEST_USERS_PREFIX}_${i + 1}`);
    console.log(`Created user: ${user.id}`);
    users.push(user);
  }
  return {
    users: users,
    //organization: org,
  };
}

export function teardown(data) {
  const admin = new CKANAdmin(BASE_URL, CKAN_ADMIN_TOKEN, CKAN_TEST_USERS_ORG);
  console.log("Clearing users")
  data.users.forEach(user => {
    admin.deleteUser(user.id);
    console.log(`Deleted: ${user.id}`)
  })
}

export default function (data) {
  const user = data.users[Math.floor(Math.random()*data.users.length)];
  const ckanUser = new CKANUser(BASE_URL, user.apikey, CKAN_TEST_USERS_ORG);
  const admin = new CKANAdmin(BASE_URL, CKAN_ADMIN_TOKEN, CKAN_TEST_USERS_ORG);
  const dataset = ckanUser.createDataset();
  console.log(`Created dataset: ${dataset.id}`);
  
  try{
    for(let i = 0; i < 5; i++) {
      ckanUser.createResource(dataset.id, `resource-${i+1}.csv`, FILES[Math.floor(Math.random()*CKAN_TEST_CSV_FILE_NUMBER)].fileData);
    }
  }catch(e) {
    console.error(e);
  }

  admin.deleteDataset(dataset.id);
  admin.purgeDataset(dataset.id);
  console.log(`Purged dataset: ${dataset.id}`);
}
