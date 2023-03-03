import http from "k6/http";
import { sleep, fail } from "k6";
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';
import { FormData } from 'https://jslib.k6.io/formdata/0.0.2/index.js';

const BASE_URL = __ENV.BASE_URL || 'https://data-dev.iaea.org';
const POLITENESS_DELAY = __ENV.POLITENESS_DELAY ? parseInt(__ENV.POLITENESS_DELAY) : 0;
const CKAN_ADMIN_TOKEN = __ENV.CKAN_ADMIN_TOKEN;
const CKAN_TEST_USERS_PREFIX = __ENV.CKAN_TEST_USERS_PREFIX || 'test_user';
const CKAN_TEST_USERS_NUMBER = __ENV.CKAN_TEST_USERS_NUMBER ? parseInt(__ENV.CKAN_TEST_USERS_NUMBER) : 10;
const CKAN_TEST_USERS_ORG = __ENV.CKAN_TEST_USERS_ORG || 'load_test_org';
const CKAN_TEST_CSV_FILE_PREFIX = __ENV.CKAN_TEST_CSV_FILE_PREFIX || 'test_file';
const CKAN_TEST_CSV_FILE_NUMBER = __ENV.CKAN_TEST_CSV_FILE_PREFIX ? parseInt(__ENV.CKAN_TEST_CSV_FILE_PREFIX) : 10;


if (!CKAN_ADMIN_TOKEN) {
  fail('Please set the CKAN_ADMIN_TOKEN')
}

class CKANAdmin {
  constructor(apiBase, apiToken) {
    this.apiBase = apiBase;
    this.apiToken = apiToken;
  }

  getActionUrl(action) {
    return `${this.apiBase}/api/action/${action}`;
  }

  createUser(user) {
    const resp = http.post(this.getActionUrl('user_create'), JSON.stringify(user), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.apiToken,
      }
    })
    if (resp.status != 200) {
      fail(`Failed to create user: ${resp.body}`)
    }
    return resp.json('result');
  }

  showUser(userName) {
    const resp = http.post(this.getActionUrl('user_show'), JSON.stringify({
      id: userName,
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.apiToken,
      }
    })
    if (resp.status != 200) {
      if (resp.status == 404) {
        return null;
      }
      fail(`Failed to get user: ${resp.body}`)
    }
    return resp.json('result');
  }

  updateUser(user) {
    const resp = http.post(this.getActionUrl('user_update'), JSON.stringify(user), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.apiToken,
      }
    })
    if (resp.status != 200) {
      fail(`Failed to update user: ${resp.body}`)
    }
    return resp.json('result');
  }

  addUserToOrg(userName, orgName) {
    const resp = http.post(this.getActionUrl('organization_member_create'), JSON.stringify({
      id: orgName,
      username: userName,
      role: 'admin',
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.apiToken,
      }
    })
    if (resp.status != 200) {
      fail(`Failed add user to organization: ${resp.body}`)
    }
  }

  getOrCreateUser(userName) {
    const user = this._getOrCreateUser(userName);
    this.addUserToOrg(userName, CKAN_TEST_USERS_ORG)
    return user;
  }

  _getOrCreateUser(userName) {
    let user = this.showUser(userName);
    if (!user) {
      return this.createUser({
        name: userName,
        email: `${userName}@example.com`,
        password: "test1234",
      })
    }
    if (user.state != "active") {
      // reactivate this user
      user.state = "active";
      return this.updateUser(user);
    }
    return user;
  }

  deleteUser(userId) {
    const resp = http.post(this.getActionUrl('user_delete'), JSON.stringify({
      id: userId,
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.apiToken,
      }
    })
    if (resp.status != 200) {
      fail(`Failed to delete user: ${resp.body}`)
    }
    return resp.json('result');
  }

  deleteDataset(pkgId) {
    const resp = http.post(this.getActionUrl('package_delete'), JSON.stringify({
      id: pkgId,
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.apiToken,
      }
    })
    if (resp.status != 200) {
      fail(`Failed to delete package: ${resp.body}`)
    }
    return resp.json('result');
  }

  purgeDataset(pkgId) {
    const resp = http.post(this.getActionUrl('dataset_purge'), JSON.stringify({
      id: pkgId,
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.apiToken,
      }
    })
    if (resp.status != 200) {
      fail(`Failed to purge dataset: ${resp.body}`)
    }
    return resp.json('result');
  }
}

class CKANUser extends CKANAdmin{
  createDataset() {
    const resp = http.post(this.getActionUrl('package_create'), JSON.stringify({
      name: `dataset-${uuidv4()}`,
      private: false,
      owner_org: `${CKAN_TEST_USERS_ORG}`,
      license_id: 'gfdl',
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': this.apiToken,
      }
    })
    if (resp.status != 200) {
      fail(`Failed to create dataset: ${resp.body}`)
    }
    return resp.json('result');
  }

  createResource(pkgId, fileName, fileData) {
    const fd = new FormData();
    fd.append('package_id', pkgId);
    fd.append('name', fileName)
    fd.append('upload', http.file(fileData, fileName));

    http.post(this.getActionUrl('resource_create'), fd.body(), {
      headers: {
        'Content-Type': 'multipart/form-data; boundary=' + fd.boundary,
        'Authorization': this.apiToken,
      }
    })
  }
}

const TEST_USERS = [];
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
        { duration: "1s", target: 1 }, // Ramp up to all concurrent users
        { duration: "1m", target: 1 }, // Hold
        { duration: "1m", target: 0 },  // scale down. Recovery stage.
      ],
    },
  },
};

export function setup() {
  console.log(`Testing URL: ${BASE_URL}, (politeness delay: ${POLITENESS_DELAY || 'none'}).`)
  const admin = new CKANAdmin(BASE_URL, CKAN_ADMIN_TOKEN);

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
  const admin = new CKANAdmin(BASE_URL, CKAN_ADMIN_TOKEN);
  console.log("Clearing users")
  data.users.forEach(user => {
    admin.deleteUser(user.id);
    console.log(`Deleted: ${user.id}`)
  })
  // console.log('Clearing org')
  // admin.clearOrg(data.organization.id);
}

export default function (data) {
  const user = data.users[Math.floor(Math.random()*data.users.length)];
  const ckanUser = new CKANUser(BASE_URL, user.apikey);
  const admin = new CKANAdmin(BASE_URL, CKAN_ADMIN_TOKEN);
  const dataset = ckanUser.createDataset();
  console.log(`Created dataset: ${dataset.id}`);
  
  try{
    for(let i = 0; i < 5; i++) {
      ckanUser.createResource(dataset.id, `resource-${10}.csv`, FILES[Math.floor(Math.random()*CKAN_TEST_CSV_FILE_NUMBER)].fileData);
    }
  }catch(e) {
    console.error(e);
  }

  admin.deleteDataset(dataset.id);
  admin.purgeDataset(dataset.id);
  console.log(`Purged dataset: ${dataset.id}`);
}
