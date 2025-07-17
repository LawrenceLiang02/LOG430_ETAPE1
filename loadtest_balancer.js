import http from 'k6/http';
import { check, sleep } from 'k6';

const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjcwNTE5MSwianRpIjoiYzdjYTY5ODgtZDVhNC00MDRhLWEyODktNzZkMTNjNmY5ZWNiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzUyNzA1MTkxLCJjc3JmIjoiMzE3MjFlYTMtZTgxNi00NjZiLWFkN2ItYTYyMzkyZWMwOTM2IiwiZXhwIjoxNzUyNzA2MDkxLCJyb2xlIjoiYWRtaW4ifQ.p2jfGt5XNZr1ew5_b9bIZ1a0bLo5jsrNuKOeXiBiQWk';

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
