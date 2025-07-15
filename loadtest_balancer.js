import http from 'k6/http';
import { check, sleep } from 'k6';

const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjU1NjQ5NiwianRpIjoiOTRmYTY1ZjctZmJlZS00ZjRjLWExY2YtY2Y5YWY2ODVhZWIzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzUyNTU2NDk2LCJjc3JmIjoiNGQ2YmM0NzYtNGVkMS00NzZkLWJjNTEtMTEyMWI5NzFmNDM4IiwiZXhwIjoxNzUyNTU3Mzk2fQ.14_fV1HENa7d2jOmfwchAx3X6R3hlZ8dPuLPoQeM4K4';

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
