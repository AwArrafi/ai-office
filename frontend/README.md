# AI Office — frontend

Dashboard Next.js untuk backend AI Office (`../backend`).

1. Jalankan backend di `127.0.0.1:8010` (lihat `../backend`).
2. `npm install`
3. `npm run dev -- -H 127.0.0.1` lalu buka http://127.0.0.1:3000

Semua request ke `/api/*` diteruskan ke backend (`BACKEND_URL`, default `http://127.0.0.1:8010`).
Status agent diperbarui dengan polling tiap 2 detik.
