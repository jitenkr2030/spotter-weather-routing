from django.test import SimpleTestCase
from .risk import checkpoint_risk,rank_routes
from .engine import build_trip
from .providers import demo_routes
class RiskTests(SimpleTestCase):
 def test_wind_55_no_travel(self):self.assertEqual(checkpoint_risk(55,0,0,1000)['overall'],'no_travel')
 def test_heavy_load_wind_45_no_travel(self):self.assertEqual(checkpoint_risk(45,0,0,30001)['wind'],'no_travel')
 def test_very_heavy_load_wind_35_severe(self):self.assertEqual(checkpoint_risk(40,0,0,40001)['wind'],'severe')
 def test_rain_above_one_no_travel(self):self.assertEqual(checkpoint_risk(10,1.01,0,1000)['rain'],'no_travel')
 def test_lexicographic_ranking(self):
  routes=[{'id':'a','severe_miles':25,'high_miles':0,'average_risk':0,'duration_minutes':100},{'id':'b','severe_miles':0,'high_miles':25,'average_risk':2,'duration_minutes':200}]
  self.assertEqual(rank_routes(routes)[0]['id'],'b')
 def test_demo_has_three_routes(self):self.assertEqual(len(demo_routes()),3)


class RiskBoundaryTests(SimpleTestCase):
    def test_rain_boundaries(self):
        self.assertEqual(
            checkpoint_risk(0, 0.10, 0, 1000)["rain"],
            "moderate",
        )
        self.assertEqual(
            checkpoint_risk(0, 0.25, 0, 1000)["rain"],
            "high",
        )
        self.assertEqual(
            checkpoint_risk(0, 0.50, 0, 1000)["rain"],
            "severe",
        )
        self.assertEqual(
            checkpoint_risk(0, 1.00, 0, 1000)["rain"],
            "severe",
        )
        self.assertEqual(
            checkpoint_risk(0, 1.01, 0, 1000)["rain"],
            "no_travel",
        )

    def test_wind_boundaries(self):
        self.assertEqual(checkpoint_risk(25, 0, 0, 1000)["wind"], "moderate")
        self.assertEqual(checkpoint_risk(35, 0, 0, 1000)["wind"], "high")
        self.assertEqual(checkpoint_risk(45, 0, 0, 1000)["wind"], "severe")
        self.assertEqual(checkpoint_risk(55, 0, 0, 1000)["wind"], "no_travel")

    def test_route_risk_miles_do_not_exceed_distance(self):
        from .risk import summarize_route

        route = {
            "distance_miles": 50,
            "checkpoint_spacing_miles": 25,
            "duration_minutes": 60,
            "checkpoints": [
                {"mile": 0, "risk": {"overall": "high", "risk_score": 2}},
                {"mile": 25, "risk": {"overall": "severe", "risk_score": 3}},
                {"mile": 50, "risk": {"overall": "low", "risk_score": 0}},
            ],
        }

        summarize_route(route)

        self.assertEqual(route["high_miles"], 25)
        self.assertEqual(route["severe_miles"], 25)
        self.assertLessEqual(
            route["high_miles"] + route["severe_miles"],
            route["distance_miles"],
        )


class CheckpointSamplingTests(SimpleTestCase):
    def test_sampling_includes_exact_destination(self):
        from .engine import samples

        coordinates = [
            [-96.0, 32.0],
            [-97.0, 31.0],
            [-98.0, 30.0],
        ]

        checkpoints = samples(
            coordinates,
            spacing=25,
            route_distance_miles=196,
        )

        self.assertEqual(checkpoints[0][0], 0.0)
        self.assertEqual(checkpoints[-1][0], 196.0)
        self.assertEqual(checkpoints[-1][1], coordinates[-1])

    def test_sampling_includes_short_final_interval(self):
        from .engine import samples

        coordinates = [[-96.0, 32.0], [-97.0, 31.0]]

        checkpoints = samples(
            coordinates,
            spacing=25,
            route_distance_miles=238,
        )

        miles = [checkpoint[0] for checkpoint in checkpoints]

        self.assertEqual(miles[-1], 238.0)
        self.assertEqual(miles[-2], 225.0)
        self.assertEqual(miles[-1] - miles[-2], 13.0)


class AssessmentComplianceTests(SimpleTestCase):
    def test_snow_threshold_boundaries(self):
        self.assertEqual(
            checkpoint_risk(0, 0, 0.49, 1000)["snow"], "low"
        )
        self.assertEqual(
            checkpoint_risk(0, 0, 0.50, 1000)["snow"], "moderate"
        )
        self.assertEqual(
            checkpoint_risk(0, 0, 1.00, 1000)["snow"], "high"
        )
        self.assertEqual(
            checkpoint_risk(0, 0, 2.00, 1000)["snow"], "severe"
        )
        self.assertEqual(
            checkpoint_risk(0, 0, 3.00, 1000)["snow"], "severe"
        )
        self.assertEqual(
            checkpoint_risk(0, 0, 3.01, 1000)["snow"], "no_travel"
        )

    def test_load_rule_strict_boundaries(self):
        # Above 30,000 lb, wind of 45–54 mph triggers no-travel.
        self.assertEqual(
            checkpoint_risk(45, 0, 0, 30000)["wind"], "severe"
        )
        self.assertEqual(
            checkpoint_risk(45, 0, 0, 30001)["wind"], "no_travel"
        )

        # Above 40,000 lb, wind of 35–44 mph becomes severe.
        self.assertEqual(
            checkpoint_risk(40, 0, 0, 40000)["wind"], "high"
        )
        self.assertEqual(
            checkpoint_risk(40, 0, 0, 40001)["wind"], "severe"
        )

    def test_route_ranking_priority_order(self):
        from .risk import rank_routes

        routes = [
            {
                "id": "fast-but-severe",
                "severe_miles": 10,
                "high_miles": 0,
                "average_risk": 0,
                "duration_minutes": 100,
            },
            {
                "id": "no-severe",
                "severe_miles": 0,
                "high_miles": 20,
                "average_risk": 2,
                "duration_minutes": 200,
            },
            {
                "id": "less-high",
                "severe_miles": 0,
                "high_miles": 10,
                "average_risk": 3,
                "duration_minutes": 300,
            },
            {
                "id": "lower-average",
                "severe_miles": 0,
                "high_miles": 10,
                "average_risk": 1,
                "duration_minutes": 400,
            },
            {
                "id": "shorter-time",
                "severe_miles": 0,
                "high_miles": 10,
                "average_risk": 1,
                "duration_minutes": 200,
            },
        ]

        ranked = rank_routes(routes)

        self.assertEqual(
            [route["id"] for route in ranked],
            [
                "shorter-time",
                "lower-average",
                "less-high",
                "no-severe",
                "fast-but-severe",
            ],
        )

    def test_no_travel_miles_count_as_severe_miles(self):
        from .risk import summarize_route

        route = {
            "distance_miles": 50,
            "duration_minutes": 100,
            "checkpoints": [
                {
                    "mile": 0,
                    "risk": {"overall": "no_travel", "risk_score": 4},
                },
                {
                    "mile": 25,
                    "risk": {"overall": "low", "risk_score": 0},
                },
                {
                    "mile": 50,
                    "risk": {"overall": "low", "risk_score": 0},
                },
            ],
        }

        summarize_route(route)

        self.assertEqual(route["severe_miles"], 25.0)
        self.assertTrue(route["has_no_travel"])
