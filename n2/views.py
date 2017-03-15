from django.views import generic
from django.http.response import HttpResponse
import requests
import json

class n2Request(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            def chkCityBound(latitude, longitude):
                # Check bounds within Taipei City
                try:
                    if latitude <= 24.964533 or latitude >= 25.209921 or longitude <= 121.456860 \
                        or longitude >= 121.663599:
                        raise ValueError

                    resp = requests.get('http://maps.googleapis.com/maps/api/geocode/' +
                        'json?latlng=' + str(latitude) + ',' + str(longitude) + '&sensor=falsea')

                    addrJson = resp.json()['results'][0]['address_components']
                    def chkCity(addrJson):
                        lenList = len(addrJson)
                        i = 0
                        for addrIter in addrJson:
                            i += 1
                            for addrKey, addrValue in addrIter.items():
                                if addrKey == 'types' and 'administrative_area_level_1' in addrValue:
                                    return addrIter['long_name']
                                if i == lenList:
                                    print('administrative_area_level_1 is not is addr Json')
                                    raise ValueError

                    inputCity = chkCity(addrJson)

                    if inputCity != 'Taipei City':
                        print('not ' + inputCity)
                        raise ValueError

                    message = {}

                except ValueError:
                    message = -2 # given location not in Taipei City

                finally:
                    return message


            def findStation(latitude, longitude):
                try:
                    iLocation = [longitude, latitude]
                    stationId = []
                    stationDist = []
                    stationName = []
                    stationSbi = []
                    numStationCand = 2 # number of nearest station chosen
                    stationPicked = []

                    resp = requests.get('http://data.taipei/youbike')
                    for i, j in resp.json()['retVal'].items():
                        if j['act'] != '0' and j['sbi'] != '0':
                            stationId.append(i)
                            stationDist.append((float(j['lng']) - iLocation[0])**2 +
                                               (float(j['lat']) - iLocation[1])**2)
                            stationName.append(j['sna'])
                            stationSbi.append(j['sbi'])

                    if len(stationId) == 0:
                        message = 1 # all ubike stations are full'
                        return stationPicked, message
                    else:
                        message = {}

                    sortedInx = sorted(range(len(stationDist)), key=lambda k: stationDist[k])

                    for i in range(numStationCand):
                        stationPicked.append({"station":stationName[sortedInx[i]], \
                            "num_ubike":int(stationSbi[sortedInx[i]])})

                except:
                    message = -3 # system error

                finally:
                    return stationPicked, message


            # Validate latitude and longitude
            lat = request.GET['lat']
            lng = request.GET['lng']

            try:
                latitude = float(lat)
                longitude = float(lng)

                if latitude <= -85 or latitude >= 85 or longitude <= -180 \
                        or longitude >= 180:
                    raise ValueError

                message = chkCityBound(latitude, longitude)

                if message == {}:
                    stationPicked, message = findStation(latitude, longitude)

            except ValueError:
                message = -1 # invalid latitude or longitude

        except:
            message = -3 # system error

        finally:
            if bool(message):
                payBack = {"code": message, "result": []}
                return HttpResponse(json.dumps(payBack, ensure_ascii=False))
            else:
                payBack = {"code": 0, "result": stationPicked}
                return HttpResponse(json.dumps(payBack, ensure_ascii=False))
