import os
import requests
import math
from datetime import datetime, timezone


def demo_routes():
    start = (-96.7970, 32.7767)
    end = (-97.7431, 30.2672)
    mids = [
        [(-96.9, 32.5), (-97.1, 32.1), (-97.35, 31.7)],
        [(-97.0, 32.7), (-97.25, 32.0), (-97.5, 31.2)],
        [(-96.7, 32.4), (-97.3, 31.9), (-97.6, 31.0)],
    ]
    vals = [
        ("Route A · Direct", 196, 190),
        ("Route B · Weather detour", 224, 225),
        ("Route C · Alternate corridor", 238, 245),
    ]
    return [
        {
            "id": f"route-{i + 1}",
            "name": v[0],
            "coordinates": [list(start)] + m + [list(end)],
            "distance_miles": v[1],
            "duration_minutes": v[2],
            "source": "demo",
        }
        for i, (m, v) in enumerate(zip(mids, vals))
    ]


def _coordinates(value):
    """Accept 'latitude,longitude' strings, if supplied explicitly."""
    try:
        lat, lon = map(float, value.split(","))
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return [lon, lat]
    except (ValueError, AttributeError):
        pass
    return None


def geocode_location(location):
    """Resolve a city/address with Geoapify, returning [longitude, latitude]."""
    key = os.getenv("GEOAPIFY_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEOAPIFY_API_KEY is not configured.")

    # Allow explicit coordinate inputs without spending a geocoding request.
    coords = _coordinates(location)
    if coords:
        return coords

    response = requests.get(
        "https://api.geoapify.com/v1/geocode/search",
        params={
            "text": location,
            "format": "json",
            "limit": 1,
            "apiKey": key,
        },
        timeout=12,
    )
    response.raise_for_status()
    results = response.json().get("results", [])

    if not results:
        raise ValueError(f"Geoapify could not find a location: {location}")

    result = results[0]
    return [float(result["lon"]), float(result["lat"])]



def get_routes(origin, destination):
    """Return distinct real HGV routes, using waypoint requests when needed."""
    ors_key = os.getenv("OPENROUTESERVICE_API_KEY", "").strip()
    geo_key = os.getenv("GEOAPIFY_API_KEY", "").strip()

    if not ors_key or not geo_key:
        return demo_routes(), "demo"

    try:
        start = geocode_location(origin)
        end = geocode_location(destination)

        url = (
            "https://api.heigit.org/openrouteservice/v2/directions/"
            "driving-hgv/geojson"
        )
        headers = {
            "Authorization": ors_key,
            "Content-Type": "application/json",
        }

        routes = []
        signatures = set()

        def add_features(features):
            for feature in features:
                if len(routes) >= 3:
                    break

                geometry = feature.get("geometry") or {}
                summary = (feature.get("properties") or {}).get("summary") or {}
                coords = geometry.get("coordinates") or []

                if len(coords) < 2 or not summary:
                    continue

                # Compare several points along each geometry to reject duplicates.
                sample_indices = {
                    round(i * (len(coords) - 1) / 4)
                    for i in range(5)
                }
                signature = tuple(
                    (round(coords[i][0], 3), round(coords[i][1], 3))
                    for i in sorted(sample_indices)
                )

                if signature in signatures:
                    continue

                try:
                    distance = float(summary["distance"])
                    duration = float(summary["duration"])
                except (KeyError, TypeError, ValueError):
                    continue

                signatures.add(signature)
                index = len(routes)
                routes.append({
                    "id": f"route-{index + 1}",
                    "name": f"Live route {chr(65 + index)}",
                    "coordinates": coords,
                    "distance_miles": round(distance / 1609.344, 1),
                    "duration_minutes": round(duration / 60),
                    "source": "openrouteservice",
                })

        def request_route(coordinates, alternatives=False):
            payload = {"coordinates": coordinates}
            if alternatives:
                payload["alternative_routes"] = {
                    "target_count": 3,
                    "share_factor": 0.6,
                    "weight_factor": 1.4,
                }

            return requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=40,
            )

        # First try the provider's native alternative-route support.
        response = request_route([start, end], alternatives=True)
        needs_waypoints = False

        if response.status_code == 400:
            try:
                error = response.json().get("error", {})
            except ValueError:
                error = {}

            if error.get("code") == 2004:
                # The alternatives algorithm does not support this trip length.
                needs_waypoints = True
            else:
                response.raise_for_status()
        else:
            response.raise_for_status()
            add_features(response.json().get("features", []))
            needs_waypoints = len(routes) < 3

        # For long routes, request real HGV road routes via distinct intermediate
        # waypoints. The provider supplies every returned road geometry.
        if needs_waypoints and len(routes) < 3:
            mid_lat = (start[1] + end[1]) / 2
            cos_lat = max(abs(math.cos(math.radians(mid_lat))), 0.01)

            east_km = (end[0] - start[0]) * 111.32 * cos_lat
            north_km = (end[1] - start[1]) * 111.32
            length_km = math.hypot(east_km, north_km)

            if length_km > 1:
                perp_east = -north_km / length_km
                perp_north = east_km / length_km

                # Try both sides of the corridor at several positions.
                candidates = [
                    (0.33, 20), (0.50, -20), (0.50, 20),
                    (0.67, -20), (0.33, -35), (0.67, 35),
                ]

                for fraction, offset_km in candidates:
                    if len(routes) >= 3:
                        break

                    base_lon = start[0] + (end[0] - start[0]) * fraction
                    base_lat = start[1] + (end[1] - start[1]) * fraction

                    waypoint = [
                        base_lon + (
                            perp_east * offset_km
                            / (111.32 * max(
                                abs(math.cos(math.radians(base_lat))), 0.01
                            ))
                        ),
                        base_lat + perp_north * offset_km / 111.32,
                    ]

                    try:
                        candidate_response = request_route(
                            [start, waypoint, end]
                        )
                        if candidate_response.ok:
                            add_features(
                                candidate_response.json().get("features", [])
                            )
                    except (requests.RequestException, ValueError, KeyError,
                            TypeError):
                        # One failed waypoint must not discard valid routes.
                        continue

        if routes:
            return routes, "openrouteservice"

        return demo_routes(), "demo"

    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        routes = demo_routes()
        for route in routes:
            route["fallback_reason"] = str(exc)[:200]
        return routes, "demo"


def weather_at(lon, lat, arrival, route_index, checkpoint_index, use_live=True):
    fallback_reason = None

    if use_live and os.getenv("OPEN_METEO_ENABLED", "false").lower() == "true":
        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": (
                        "wind_speed_10m,precipitation,rain,snowfall"
                    ),
                    "wind_speed_unit": "mph",
                    "precipitation_unit": "inch",
                    "forecast_days": 3,
                    "timezone": "UTC",
                },
                timeout=8,
            )
            response.raise_for_status()
            hourly = response.json()["hourly"]
            times = hourly["time"]

            if not times:
                raise ValueError("Weather provider returned no hourly data.")

            available_times = [
                datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
                for value in times
            ]

            if arrival < available_times[0] or arrival > available_times[-1]:
                raise ValueError(
                    "Selected forecast time is outside provider coverage."
                )

            index = min(
                range(len(available_times)),
                key=lambda i: abs((available_times[i] - arrival).total_seconds()),
            )

            rain_values = hourly.get("rain")
            if rain_values is None:
                rain_values = hourly["precipitation"]

            # Open-Meteo snowfall is reported in cm; convert to inches
            # because the application's risk thresholds use inches/hour.
            snowfall_inches = float(hourly["snowfall"][index]) / 2.54

            return {
                "wind_mph": float(hourly["wind_speed_10m"][index]),
                "rain_in_hr": float(rain_values[index]),
                "snow_in_hr": snowfall_inches,
                "source": "open-meteo",
            }

        except Exception as exc:
            fallback_reason = str(exc)

    # Deterministic illustrative data: change the sample by forecast hour.
    hour_bucket = int(arrival.timestamp() // 3600)

    winds = [22, 38, 47, 31, 56, 28, 41, 19, 34, 49, 26, 36]
    rains = [.02, .14, .31, .06, .55, .19, .04, .72, .12, .28]
    snows = [0, 0, .1, .6, 0, 1.2, 0, .2]

    result = {
        "wind_mph": winds[
            (checkpoint_index * 3 + route_index * 4 + hour_bucket) % len(winds)
        ],
        "rain_in_hr": rains[
            (checkpoint_index * 2 + route_index + hour_bucket) % len(rains)
        ],
        "snow_in_hr": snows[
            (checkpoint_index + route_index * 2 + hour_bucket) % len(snows)
        ],
        "source": "demo",
    }

    if fallback_reason:
        result["fallback_reason"] = fallback_reason[:200]

    return result
