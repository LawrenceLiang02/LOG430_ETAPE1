import http from 'k6/http';
import { check, sleep } from 'k6';

const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjU0NDYwOSwianRpIjoiNDRmY2U3MmYtNGVmZS00ZTZkLWEyZDgtMGQ0ZTdlNmJlYmI2IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzUyNTQ0NjA5LCJjc3JmIjoiNGEzZjA4NzktYjVkNi00N2NhLTg3OTUtMjk2MGMzMWZmZWY5IiwiZXhwIjoxNzUyNTQ1NTA5fQ.1hBtE6unxIm6cJvXuj6HfQ_AnHf5qHSC3KXR_VOeIUg"';

export let options = {
  vus: 50,
  duration: '30s',
};

const ports = [8000, 8001, 8002, 8003, 8004];

export default function () {
  const headers = {
    headers: {
      Authorization: `Bearer ${TOKEN}`,
    },
  };

  for (let i = 0; i < ports.length; i++) {
    const url = `http://localhost:${ports[i]}/api/locations/`;
    const res = http.get(url, headers);

    check(res, {
      [`${url} responded 200`]: (r) => r.status === 200,
    });

    sleep(0.2); // short pause between requests to simulate user pacing
  }
}
