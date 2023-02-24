import http from "k6/http";
import { sleep, fail } from "k6";
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';
import { FormData } from 'https://jslib.k6.io/formdata/0.0.2/index.js';

export class CKANAdmin {
    constructor(apiBase, apiToken, usersOrg) {
      this.apiBase = apiBase;
      this.apiToken = apiToken;
      this.usersOrg = usersOrg;
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
      this.addUserToOrg(userName, this.usersOrg)
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
  
  export class CKANUser extends CKANAdmin{
    createDataset() {
      const resp = http.post(this.getActionUrl('package_create'), JSON.stringify({
        name: `dataset-${uuidv4()}`,
        private: false,
        owner_org: `${this.usersOrg}`,
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

    listDatasets() {
      const resp = http.post(this.getActionUrl('package_list'), JSON.stringify({}), {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.apiToken,
        }
      })
      if (resp.status != 200) {
        fail(`failed to read datasets: ${resp.body}`)
      }
      return resp.json('result');
    }
    packageShow(pkgId) {
      const resp = http.post(this.getActionUrl('package_show'), JSON.stringify({
        id: pkgId,
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.apiToken,
        }
      })
      if (resp.status != 200) {
        fail(`failed to read datasets: ${resp.body}`)
      }
      return resp.json('result');
    }
    resourceShow(resourceId) {
      const resp = http.post(this.getActionUrl('resource_show'), JSON.stringify({
        id: resourceId,
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.apiToken,
        }
      })
      if (resp.status != 200) {
        fail(`failed to read datasets: ${resp.body}`)
      }
      return resp.json('result');
    }
    datastoreSearch(resourceId) {
      const resp = http.post(this.getActionUrl('datastore_search'), JSON.stringify({
        resource_id: resourceId,
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.apiToken,
        }
      })
      if (resp.status != 200) {
        fail(`failed search datastore: ${resp.body}`)
      }
      return resp.json('result');
    }
    downloadResource(downloadUrl) {
      const resp = http.get(downloadUrl, {
        headers: {
          'Authorization': this.apiToken,
        }
      })
      if (resp.status != 200) {
        fail(`failed to download resource: ${resp.body}`)
      }
      return resp.body;
    }
  }