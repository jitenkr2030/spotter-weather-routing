from django.core.management.base import BaseCommand
from routing.engine import build_trip
class Command(BaseCommand):
 help='Validate built-in demo scenario.'
 def handle(self,*args,**kwargs):
  result=build_trip({'origin':'Dallas, TX','destination':'Austin, TX','load_lb':28000,'checkpoint_spacing_miles':25,'departure_time':'2026-10-19T14:00:00Z'})
  self.stdout.write(self.style.SUCCESS(f"Demo ready: {len(result['routes'])} routes; recommended={result['recommended_route_id']}"))
