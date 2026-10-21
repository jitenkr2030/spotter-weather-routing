# RouteWise / SpotterAI API Reference

## Overview

The Django REST backend provides health checks, provider status,
demo functionality and route analysis.

**Base URL:** https://spotter-weather-routing-f4wz9.faable.link

## Endpoints

### 1. Health Check

`GET /api/health/`

Purpose:
- Check whether the backend is responding.
- Use for deployment verification and service monitoring.

Example request:

```bash
curl -i \
  https://spotter-weather-routing-f4wz9.faable.link/api/health/
```

### 2. Provider Status

`GET /api/providers/`

Purpose:
- Inspect the routing and weather provider configuration.
- Verify the availability or enabled status reported by the application.

Example request:

```bash
curl -i \
  https://spotter-weather-routing-f4wz9.faable.link/api/providers/
```

### 3. Demo Endpoint

`GET /api/demo/`

Purpose:
- Access the application's demonstration functionality.
- Useful for evaluating the interface without manually preparing
  every route-analysis input.

Example request:

```bash
curl -i \
  https://spotter-weather-routing-f4wz9.faable.link/api/demo/
```

### 4. Route Analysis

`POST /api/route/`

Purpose:
- Submit route-planning inputs to the backend.
- Obtain route-analysis results for presentation in the frontend.

Example request template:

```bash
curl -i -X POST \
  https://spotter-weather-routing-f4wz9.faable.link/api/route/ \
  -H 'Content-Type: application/json' \
  -d '{}'
```

The empty JSON object is a connectivity template, not a valid
route request. Replace it with the request body required by the
implemented serializer or view.

## Request and Response Contracts

For the exact POST parameters, validation rules, status codes and
response fields, consult the Django route view, serializer and
provider implementations.

Do not assume that every provider or route option is available
for every request.

## Error Handling

Check the HTTP status code and response body when a request fails.
Document the application's actual validation and provider error
responses after inspecting the implementation.

## Integration Notes

- Routing: OpenRouteService.
- Weather: Open-Meteo.
- Backend: Django.
- Frontend: React and TypeScript.

Provider configuration and external service availability can affect
the returned results.
