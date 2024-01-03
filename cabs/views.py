import requests, json
from django.http import JsonResponse
from .models import Cab
from decouple import config

def find_nearest_cab(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start_lat = data.get('start_lat')
        start_lng = data.get('start_lng')

        all_cabs = Cab.objects.all()

        cab_distances = []

        for cab in all_cabs:
            distance_matrix_api_base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                'origins': f'{start_lat},{start_lng}',
                'destinations': f'{cab.cab_latitude},{cab.cab_longitude}',
                'key': config('GOOGLE_MAPS_API_KEY', cast=str)
            }

            response = requests.get(distance_matrix_api_base_url, params=params)
            data = response.json()

            if data['status'] == 'OK':
                distance = data['rows'][0]['elements'][0]['distance']['value']
                cab_distances.append({'cab_id': cab.id, 'distance': distance})

        cab_distances.sort(key=lambda x: x['distance'])

        nearest_cab_id = cab_distances[0]['cab_id']
        nearest_cab = Cab.objects.get(id=nearest_cab_id)

        return JsonResponse({
            'nearest_cab': nearest_cab.number_plate,
            'distance_to_nearest_cab': cab_distances[0]['distance']
        })
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
