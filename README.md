# Spotter AI — Weather-Aware Truck Routing

React + TypeScript + Vite frontend and Django REST Framework backend for the Full Stack Developer assessment. Includes deterministic demo routes/weather, checkpoint sampling, risk classification, load rules, route ranking, an interactive MapLibre map, 0–48 hour slider, and backend tests.

## Run on Ubuntu / Termux proot

Backend:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py test
python manage.py runserver 0.0.0.0:8000
```
Frontend in another terminal:
```bash
cd frontend
npm install
cp .env.example .env
npm run dev -- --host 0.0.0.0
```

Open the Vite URL printed in the terminal. API defaults to `http://127.0.0.1:8000/api`.

## API
- `GET /api/health/`
- `GET /api/demo/`
- `POST /api/route/`
- `GET /api/providers/`

## Optional providers
Set `OPENROUTESERVICE_API_KEY` for OpenRouteService (coordinates as `lat, lon` required for live routing). Set `OPEN_METEO_ENABLED=true` to attempt Open-Meteo forecast data. Without keys, the app works with deterministic demo routes/weather and labels them as demo. Demo coordinates are a sample Dallas–Austin corridor even if different city names are entered; don't treat demo output as real routing or dispatch advice.

## Production checklist
Set a strong `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, allowed hosts, HTTPS, restricted CORS, PostgreSQL, logging/monitoring, and provider timeout/error handling before public use. Validate weather units, API terms, route coverage, official truck restrictions, and forecast availability. The demo data is illustrative, not operational safety guidance.
