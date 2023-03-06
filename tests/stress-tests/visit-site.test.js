import http from "k6/http";
import { sleep, fail } from "k6";

const BASE_URL = __ENV.BASE_URL || 'https://data-dev.iaea.org';
const POLITENESS_DELAY =  __ENV.POLITENESS_DELAY ? parseInt(__ENV.POLITENESS_DELAY) : 0;
const CONCURRENT_USERS = __ENV.CONCURRENT_USERS || 10;

export const options = {
  scenarios: {
    stress: {
      executor: "ramping-vus",
      startVUs: 0,
      gracefulRampDown: "20s",
      stages: [
        { duration: "1m", target: CONCURRENT_USERS }, // Ramp up to all concurrent users
        { duration: "9m", target: CONCURRENT_USERS }, // Hold
        { duration: "1m", target: 0 },                // scale down. Recovery stage.
      ],
    },
  },
};

export function setup() {
  console.log(`Testing URL: ${BASE_URL}, concurrent users: ${CONCURRENT_USERS} (politeness delay: ${POLITENESS_DELAY || 'none'}).`)

  const resp = http.get(`${BASE_URL}/api/action/current_package_list_with_resources`)
  if (resp.status != 200) {
    fail('Unable to call CKAN')
  }
  const data = resp.json('result')
  return {
    packages: data.map(pkg => pkg.id)
  }
}

export default function (data) {
  // Walk around the portal
  [
    `${BASE_URL}`,
    `${BASE_URL}/dataset`,
    `${BASE_URL}/organization`,
    `${BASE_URL}/group`,
    //`${BASE_URL}/organization/the-international-atomic-energy-agency`
  ].forEach(url => {
    http.get(url)
    if(POLITENESS_DELAY) {
      sleep(Math.random()*POLITENESS_DELAY)
    }
  })
  
  // Now check out the public datasets
  if(data.packages) {
    data.packages.forEach(pkgId => {
      http.get(`${BASE_URL}/dataset/${pkgId}`)
      if(POLITENESS_DELAY) {
        sleep(Math.random()*POLITENESS_DELAY)
      }
    })
  }
}
