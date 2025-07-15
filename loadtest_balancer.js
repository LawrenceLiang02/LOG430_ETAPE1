import http from 'k6/http';
import { check, sleep } from 'k6';

const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjU0NDgwNywianRpIjoiMDgzYTg2MjQtNGIxZC00NWMwLWFlNzctMGRlZjkyYmFkM2RhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzUyNTQ0ODA3LCJjc3JmIjoiNTFjZmY2YzMtMWJjMi00YmY3LTgxMTktMzZlMzQ3MWRhZTBjIiwiZXhwIjoxNzUyNTQ1NzA3fQ.r114y9ywOUGPhGMi0Y1SyAnltxkpool3-ThMIVxfxlU';

export let options = {
  vus: 50,
  duration: '30s',
};

export default function () {
  const headers = {
    headers: {
      Authorization: `Bearer ${TOKEN}`,
    },
  };

  let res = http.get('http://localhost:8080/api/products/', headers);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
