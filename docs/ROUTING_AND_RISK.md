# Routing and Risk Analysis

## Purpose

RouteWise / SpotterAI combines route planning with weather-aware
risk information to help users compare route alternatives.

## Routing Workflow

1. The user supplies the route-planning inputs through the frontend.
2. The frontend sends the request to the Django backend.
3. The backend validates the request and obtains routing data from
   the configured routing provider.
4. Weather data is obtained from the configured weather provider
   where applicable.
5. The backend evaluates the available route information.
6. The frontend presents the resulting route information for review.

## External Integrations

### OpenRouteService

Provides routing data used by the application. Route availability
and supported vehicle options depend on the configured API and
request parameters.

### Open-Meteo

Provides weather data used in weather-aware route analysis.
Forecast availability depends on location, forecast horizon and
provider coverage.

## Route Ranking

The implemented safety-first ranking considers:

1. Severe/high-risk distance, prioritizing routes with less exposure.
2. Average route risk.
3. Travel duration.

The ranking should be understood as an application-level comparison,
not a guarantee that a route is safe.

## Weather Risk

Weather-related risk classifications depend on the rules implemented
in the backend. They should not be interpreted as official road
closures, emergency warnings or guaranteed forecasts.

Document the exact weather thresholds and category mappings here
after checking the implementation.

## Forecast Offsets

Forecast offsets determine which forecast period is considered.
The actual supported offsets and their calculation must match the
backend implementation.

## Truck and Vehicle Constraints

Document supported truck/load parameters, vehicle restrictions and
provider-specific limitations based on the actual request schema.

Do not claim that a routing provider enforces every real-world
truck restriction unless that behavior has been verified.

## Limitations

- Weather and route data depend on external provider availability.
- Forecasts may differ from actual conditions.
- Risk scores are decision-support estimates.
- Route rankings do not replace road regulations or official
  safety instructions.
