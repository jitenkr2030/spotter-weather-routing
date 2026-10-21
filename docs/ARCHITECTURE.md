# RouteWise / SpotterAI — Architecture

## 1. Project Overview

RouteWise is a weather-aware truck routing application.
It compares route alternatives and evaluates weather risks
at checkpoints along each route.

The application uses a React frontend and a Django backend.

## 2. Technology Stack

- Frontend: React, TypeScript and Vite
- Map: MapLibre
- Backend: Python, Django and Django REST Framework
- Routing: OpenRouteService HGV routing API
- Geocoding: Geoapify API
- Weather: Open-Meteo hourly forecast API
- Testing: Django automated tests

## 3. System Architecture

The application follows a frontend-backend architecture.

1. The user enters the origin, destination, departure time,
   truck load weight, checkpoint spacing and forecast offset.
2. The React frontend sends trip data to the Django API.
3. Django validates the trip parameters.
4. The routing service obtains route alternatives when the
   required provider credentials are configured.
5. The backend samples each route at 10, 25 or 50-mile intervals.
6. The engine estimates arrival time at each checkpoint.
7. The weather service retrieves forecast data when enabled.
8. The risk engine evaluates wind, rain, snow and load rules.
9. Routes are ranked using their calculated risk metrics.
10. The frontend displays route alternatives and results.

## 4. Backend Components

### Routing API

The Django REST Framework API exposes these endpoints:

- GET /api/health/
- GET /api/providers/
- GET /api/demo/
- POST /api/route/

### Routing Engine

The routing engine is responsible for:

- Validating trip inputs
- Sampling route coordinates
- Estimating checkpoint arrival times
- Applying the selected forecast offset
- Collecting checkpoint weather data
- Generating route summaries
- Ranking route alternatives

### Risk Engine

The risk engine classifies wind, rain and snow conditions.
It also applies load-dependent wind restrictions and calculates
route-level risk metrics.

### Provider Integrations

OpenRouteService provides truck route geometry when configured.
Geoapify resolves city names and addresses into coordinates.
Open-Meteo provides hourly weather forecasts when enabled.

## 5. Frontend Responsibilities

The React frontend provides the user interface for trip inputs,
route alternatives, map visualization and risk information.

The frontend communicates with Django through HTTP API requests.
The API base URL is configurable using VITE_API_BASE_URL.

## 6. Demo and Fallback Behavior

The application supports demonstration data when live providers
are unavailable or are not configured.

Demo routes use illustrative Dallas-to-Austin coordinates and
sample weather values. These values must not be represented as
live routing or live weather results.

Check the API response fields named mode and providers to identify
whether live or demo data was used.

## 7. Configuration

Backend configuration examples are stored in:

backend/.env.example

Frontend configuration examples are stored in:

frontend/.env.example

Required provider settings for live routing include:

- OPENROUTESERVICE_API_KEY
- GEOAPIFY_API_KEY

Set OPEN_METEO_ENABLED=true to enable Open-Meteo weather requests.

Never commit real API keys, passwords or production secrets.

## 8. Important Limitations

This application is an assessment prototype and is not a
certified truck dispatch or safety system.

Weather forecasts, route availability and provider coverage
may vary. Always verify official weather alerts, road conditions
and truck restrictions before making real dispatch decisions.
