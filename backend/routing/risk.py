RISK_ORDER = {
    "low": 0,
    "moderate": 1,
    "high": 2,
    "severe": 3,
    "no_travel": 4,
}


def checkpoint_risk(wind_mph, rain_in_hr, snow_in_hr, load_lb):
    wind = (
        "low" if wind_mph < 25 else
        "moderate" if wind_mph < 35 else
        "high" if wind_mph < 45 else
        "severe" if wind_mph < 55 else
        "no_travel"
    )

    rain = (
        "low" if rain_in_hr < 0.10 else
        "moderate" if rain_in_hr < 0.25 else
        "high" if rain_in_hr < 0.50 else
        "severe" if rain_in_hr <= 1.00 else
        "no_travel"
    )

    snow = (
        "low" if snow_in_hr < 0.5 else
        "moderate" if snow_in_hr < 1.0 else
        "high" if snow_in_hr < 2.0 else
        "severe" if snow_in_hr <= 3.0 else
        "no_travel"
    )

    if 45 <= wind_mph < 55 and load_lb > 30000:
        wind = "no_travel"
    elif 35 <= wind_mph < 45 and load_lb > 40000:
        wind = "severe"

    overall = max(
        (wind, rain, snow),
        key=lambda risk: RISK_ORDER[risk],
    )

    return {
        "wind": wind,
        "rain": rain,
        "snow": snow,
        "overall": overall,
        "risk_score": RISK_ORDER[overall],
    }


def summarize_route(route):
    checkpoints = sorted(
        route["checkpoints"],
        key=lambda checkpoint: checkpoint["mile"],
    )

    distance = float(route["distance_miles"])

    severe_miles = 0.0
    high_miles = 0.0
    weighted_risk = 0.0
    covered_miles = 0.0
    has_no_travel = False

    for index, checkpoint in enumerate(checkpoints):
        risk = checkpoint["risk"]["overall"]
        score = checkpoint["risk"]["risk_score"]

        if risk == "no_travel":
            has_no_travel = True

        # A checkpoint represents the segment up to the next
        # checkpoint. The final endpoint represents zero miles.
        start = max(0.0, float(checkpoint["mile"]))

        if index + 1 < len(checkpoints):
            end = min(
                distance,
                float(checkpoints[index + 1]["mile"]),
            )
        else:
            end = distance

        segment_miles = max(0.0, end - start)

        if risk in ("severe", "no_travel"):
            severe_miles += segment_miles
        elif risk == "high":
            high_miles += segment_miles

        weighted_risk += score * segment_miles
        covered_miles += segment_miles

    route["severe_miles"] = round(severe_miles, 1)
    route["high_miles"] = round(high_miles, 1)
    route["average_risk"] = round(
        weighted_risk / covered_miles, 2
    ) if covered_miles else 0

    route["max_risk"] = max(
        checkpoints,
        key=lambda checkpoint: checkpoint["risk"]["risk_score"],
    )["risk"]["overall"] if checkpoints else "low"

    route["has_no_travel"] = has_no_travel
    return route


def rank_routes(routes):
    return sorted(
        routes,
        key=lambda route: (
            route["severe_miles"],
            route["high_miles"],
            route["average_risk"],
            route["duration_minutes"],
        ),
    )
