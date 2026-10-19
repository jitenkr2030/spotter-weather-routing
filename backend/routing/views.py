import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .engine import build_trip
@api_view(['GET'])
def health(request):return Response({'status':'ok','service':'spotter-weather-routing'})
@api_view(['GET'])
def providers(request):return Response({'routing':'openrouteservice' if os.getenv('OPENROUTESERVICE_API_KEY') else 'demo','weather':'open-meteo-enabled' if os.getenv('OPEN_METEO_ENABLED','false').lower()=='true' else 'demo','demo_available':True})
@api_view(['GET'])
def demo(request):
    try:return Response(build_trip({'origin':'Dallas, TX','destination':'Austin, TX','departure_time':'2026-10-19T14:00:00Z','load_lb':28000,'checkpoint_spacing_miles':25}, demo_only=True))
    except ValueError as e:return Response({'error':str(e)},status=400)
@api_view(['POST'])
def route(request):
    try:return Response(build_trip(request.data))
    except (ValueError,TypeError) as e:return Response({'error':str(e)},status=400)
