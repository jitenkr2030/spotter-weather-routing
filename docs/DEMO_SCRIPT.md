# RouteWise / SpotterAI — Assessment Demo

Suggested duration: 5–10 minutes.

## 1. Introduction — 30 seconds

"RouteWise / SpotterAI is a weather-aware route-planning application.
It combines a React frontend with a Django backend to help users
evaluate routes using routing, weather and risk information."

## 2. Show the Live Application — 1 minute

Open:

https://frontend-ten-kappa-22.vercel.app/

Explain the main interface and identify the available route inputs.

## 3. Demonstrate Route Planning — 2 minutes

1. Enter valid route details.
2. Submit a route request.
3. Show the returned route information.
4. Explain how route alternatives are presented.

Use a working example that has been tested against the live deployment.

## 4. Explain Weather and Risk — 1–2 minutes

Explain how the application uses Open-Meteo weather data and its
implemented risk rules.

Describe the safety-first route ranking:
- Severe/high-risk distance
- Average risk
- Travel duration

Explain that these are decision-support estimates, not guarantees.

## 5. Explain the Architecture — 1 minute

Describe the main components:

- React and TypeScript frontend
- Django backend and API
- OpenRouteService routing integration
- Open-Meteo weather integration

Refer to docs/ARCHITECTURE.md for further detail.

## 6. Demonstrate Engineering Verification — 1 minute

Show the backend test command and frontend build command.

Mention the previously recorded 15 passing backend tests and
successful frontend build and browser verification.

## 7. Closing — 30 seconds

"RouteWise / SpotterAI demonstrates full-stack development,
third-party API integration, route analysis, weather-aware risk
evaluation and automated testing. The documentation describes
the architecture, API, testing process and known limitations."

## Before Recording

- Verify the live application is available.
- Prepare a valid route example.
- Avoid exposing API keys or other secrets.
- Confirm the displayed results match the deployed implementation.
