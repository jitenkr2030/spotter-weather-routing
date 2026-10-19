from datetime import datetime,timedelta,timezone
from .providers import get_routes, weather_at, demo_routes
from .risk import checkpoint_risk,summarize_route,rank_routes
import math
def parse_dt(value):
    if not value:return datetime.now(timezone.utc)
    dt=datetime.fromisoformat(value.replace('Z','+00:00'))
    return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
def samples(coords, spacing, route_distance_miles=None):
    """
    Sample route geometry at regular road-mile intervals and always
    include the destination. Road miles are mapped proportionally
    onto the route geometry.
    """
    def hav(a, b):
        lon1, lat1 = map(math.radians, a)
        lon2, lat2 = map(math.radians, b)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        h = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )
        return 3958.8 * 2 * math.asin(
            min(1, math.sqrt(h))
        )

    if not coords:
        raise ValueError("Route geometry contains no coordinates.")

    if len(coords) == 1:
        distance = float(route_distance_miles or 0)
        return [(0.0, list(coords[0]))] if distance == 0 else [
            (0.0, list(coords[0])),
            (distance, list(coords[0])),
        ]

    segments = [
        (a, b, hav(a, b))
        for a, b in zip(coords, coords[1:])
    ]
    geometry_distance = sum(segment[2] for segment in segments)

    road_distance = float(
        route_distance_miles
        if route_distance_miles is not None
        else geometry_distance
    )

    if road_distance <= 0 or geometry_distance <= 0:
        return [(0.0, list(coords[0]))]

    # Regular intervals plus the exact destination mileage.
    targets = list(range(0, int(road_distance), spacing))
    if not targets or targets[0] != 0:
        targets.insert(0, 0)
    if not math.isclose(targets[-1], road_distance):
        targets.append(road_distance)

    output = []

    for target_mile in targets:
        geometry_target = (
            target_mile / road_distance * geometry_distance
        )
        walked = 0.0
        point = list(coords[-1])

        for a, b, segment_distance in segments:
            if walked + segment_distance >= geometry_target:
                fraction = (
                    (geometry_target - walked) / segment_distance
                    if segment_distance > 0
                    else 0.0
                )
                fraction = max(0.0, min(1.0, fraction))
                point = [
                    a[0] + fraction * (b[0] - a[0]),
                    a[1] + fraction * (b[1] - a[1]),
                ]
                break

            walked += segment_distance

        output.append((float(target_mile), point))

    # Guarantee the last checkpoint uses the exact destination coordinate.
    output[-1] = (road_distance, list(coords[-1]))

    return output

def build_trip(payload, demo_only=False):
    origin = str(payload.get("origin", "Dallas, TX")).strip()
    dest = str(payload.get("destination", "Austin, TX")).strip()
    load = float(payload.get("load_lb", 28000))
    spacing = int(payload.get("checkpoint_spacing_miles", 25))
    forecast_offset_hours = int(payload.get("forecast_offset_hours", 0))

    if not origin or not dest:
        raise ValueError("Origin and destination are required.")
    if not 0 <= load <= 100000:
        raise ValueError("Load weight must be between 0 and 100,000 lb.")
    if spacing not in (10, 25, 50):
        raise ValueError("Checkpoint spacing must be 10, 25, or 50 miles.")
    if not 0 <= forecast_offset_hours <= 48:
        raise ValueError("Forecast offset must be between 0 and 48 hours.")

    departure = parse_dt(payload.get("departure_time"))
    routes, routing_provider = (demo_routes(), "demo") if demo_only else get_routes(origin, dest)
    output = []
    weather_sources = set()

    for route_index, route in enumerate(routes):
        checkpoints = []

        for checkpoint_index, (mile, coord) in enumerate(
            samples(
                route["coordinates"],
                spacing,
                route["distance_miles"],
            )
        ):
            distance = max(float(route["distance_miles"]), 1.0)
            arrival = departure + timedelta(
                minutes=route["duration_minutes"] * mile / distance
            )
            weather_time = arrival + timedelta(
                hours=forecast_offset_hours
            )

            weather = weather_at(
                coord[0],
                coord[1],
                weather_time,
                route_index,
                checkpoint_index,
                use_live=not demo_only,
            )
            weather_sources.add(weather.get("source", "unknown"))

            risk = checkpoint_risk(
                weather["wind_mph"],
                weather["rain_in_hr"],
                weather["snow_in_hr"],
                load,
            )

            checkpoints.append({
                "id": f"{route['id']}-cp-{checkpoint_index + 1}",
                "mile": round(mile, 1),
                "coordinates": coord,
                "arrival_time": arrival.isoformat(),
                "weather_forecast_time": weather_time.isoformat(),
                "weather": weather,
                "risk": risk,
            })

        route["checkpoint_spacing_miles"] = spacing
        route["checkpoints"] = checkpoints
        route["eta"] = (
            departure + timedelta(minutes=route["duration_minutes"])
        ).isoformat()
        route["summary"] = (
            f"{route['distance_miles']} mi · "
            f"{route['duration_minutes']} min · "
            f"{len(checkpoints)} checkpoints"
        )
        output.append(summarize_route(route))

    ranked = rank_routes(output)

    for index, route in enumerate(ranked):
        route["rank"] = index + 1

    if weather_sources == {"open-meteo"}:
        weather_provider = "open-meteo"
    elif weather_sources == {"demo"}:
        weather_provider = "demo"
    else:
        weather_provider = "mixed"

    mode = (
        "demo"
        if routing_provider == "demo" or weather_provider != "open-meteo"
        else "live-routing"
    )

    disclaimer = (
        "Demo route coordinates or weather are illustrative, not dispatch "
        "guidance. Forecast coverage and official truck restrictions vary."
        if mode == "demo"
        else
        "Forecasts are estimates. Verify current road conditions and official "
        "truck restrictions before dispatch."
    )

    return {
        "trip": {
            "origin": origin,
            "destination": dest,
            "departure_time": departure.isoformat(),
            "load_lb": load,
            "checkpoint_spacing_miles": spacing,
            "forecast_offset_hours": forecast_offset_hours,
        },
        "routes": ranked,
        "recommended_route_id": ranked[0]["id"] if ranked else None,
        "providers": {
            "routing": routing_provider,
            "weather": weather_provider,
        },
        "mode": mode,
        "disclaimer": disclaimer,
    }
