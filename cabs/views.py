import requests
from django.http import JsonResponse
from .models import Cab

def find_nearest_cab(request):
    if request.method == 'POST':
        print(request.POST.get('start_lat'))
        start_lat = request.POST.get('start_lat')
        start_lng = request.POST.get('start_lng')
        print(start_lat, start_lng)

        all_cabs = Cab.objects.all()

        cab_distances = []

        for cab in all_cabs:
            distance_matrix_api_base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                'origins': f'{start_lat},{start_lng}',
                'destinations': f'{cab.cab_latitude},{cab.cab_longitude}',
                'key': 'AIzaSyDejcaC0mWkEDpXgwJSmkMf-_CVqbDxPdg'
            }

            response = requests.get(distance_matrix_api_base_url, params=params)
            data = response.json()
            print(data)

            if data['status'] == 'OK':
                print(data['rows'][0]['elements'][0])
                distance = data['rows'][0]['elements'][0]['distance']['value']
                print(distance)
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
