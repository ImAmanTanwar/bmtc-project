from django.shortcuts import render
from .models import BusStops
import json, requests, time
from django.http import HttpResponse
import re
from utilities import BusData
from django.views.decorators.csrf import csrf_exempt

def index(request):
    context={}
    bus_data = BusStops.objects.values_list('stop_name',flat=True)
    bus_stops=[]
    for i in range(0,len(bus_data)):
        bus_stops.append(str(bus_data[i]))
    context["bus_stops"]=bus_stops
    if request.method == 'POST':
        src = request.POST.get('source')
        dest = request.POST.get('destination')
        context["src"] = src
        context["dest"] = dest
        context["src_lat"] = BusStops.objects.get(stop_name=src).latitude
        context["src_lon"] = BusStops.objects.get(stop_name=src).longitude
        src_loc = context["src_lat"]+", "+context["src_lon"]
        context["dest_lat"] = BusStops.objects.get(stop_name=dest).latitude
        context["dest_lon"] = BusStops.objects.get(stop_name=dest).longitude
        dest_loc = context["dest_lat"]+", "+context["dest_lon"]
        url = "https://maps.googleapis.com/maps/api/directions/json"
        headers = {'Content-Type':'application/json'}
        data = {"origin":src_loc,
	       "destination":dest_loc,
	       "key":'AIzaSyDCdSpDXOO-i-DW7-Az6PO7toRnykIE7vA',
	       "mode":'transit',
	       "transit_mode":'bus'}
        resp = ""
        resp = requests.post(url,params=data,headers=headers)
        resp_json = resp.json()
        respon = json.loads(json.dumps(resp_json))
        routes_array = json.loads(json.dumps(respon["routes"]))
        route = routes_array[0]
        legs = json.loads(json.dumps(route["legs"]))
        leg = legs[0]
        steps = json.loads(json.dumps(leg["steps"]))
        bus_obj=""
        buses=[]
        for i in range(0,len(steps)):
            if steps[i]["travel_mode"]=="TRANSIT":
                bus_obj = steps[i]
                bus_data=BusData()
                if "short_name" in bus_obj["transit_details"]["line"]:
                    bus_data.route_no = str(bus_obj["transit_details"]["line"]["short_name"])
                else:
                    bus_data.route_no=""
                bus_data.stops = str(bus_obj["transit_details"]["num_stops"])
                bus_data.bus_name = str(bus_obj["transit_details"]["line"]["name"])
                bus_data.arrival_stop=str(bus_obj["transit_details"]["arrival_stop"]["name"])
                bus_data.departure_stop=str(bus_obj["transit_details"]["departure_stop"]["name"])
                bus_data.departure_time = str(bus_obj["transit_details"]["departure_time"]["text"])
                bus_data.arrival_time = str(bus_obj["transit_details"]["arrival_time"]["text"])
                bus_data.arrival_epoch = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str(bus_obj["transit_details"]["departure_time"]["value"]))))
                buses.append(bus_data)
        if len(buses)==0:
            context["no_bus"]=True
        elif len(buses)>1:
            context["multi_route"]=True
            context["buses"]=buses
            context["start_route"]=buses[0].route_no
            context["bus_wait_time"]=buses[0].arrival_epoch
        else:
            context["buses"]=buses
            if buses[0].route_no == "":
                context["start_route"]=buses[0].bus_name
            else:
                context["start_route"]=buses[0].route_no
            context["bus_wait_time"]=buses[0].arrival_epoch
        #for i in range(0,len(bmtc_data)):

        #print "Bus Route No. "+str(bus_obj["transit_details"]["line"]["short_name"])+" from "+str(bus_obj["transit_details"]["line"]["name"])+" will arrive at "
        #print str(bus_obj["transit_details"]["departure_time"]["text"])
    return render(request,"home.html",context)

@csrf_exempt
def get_data_map(request):
    context={}
    if request.method=='POST':
        route_data = request.POST['route']
        bmtc_url = "http://bmtcmob.hostg.in/api//itsroutewise/details"
        #route_number =
        temp = route_data.split("-")
        if len(temp)==1:
            route_no=re.split('(\d+)',route_data)
            route = route_no[1]+"-"+route_no[2]
        else:
            route=route_data
        params = {'direction': 'DN', 'routeNO': route}
        r = requests.post(bmtc_url, data=params)
        bmtc_data = r.json()
        buses_lat = [None]*len(bmtc_data)
        buses_lon = [None]*len(bmtc_data)
        buses_number = [None]*len(bmtc_data)
        direction = [None]*len(bmtc_data)
        for i in range(0,len(bmtc_data)):
            buses_lat[i] = str(bmtc_data[i][2]).split(":")[1]
            buses_lon[i] = str(bmtc_data[i][3]).split(":")[1]
            buses_number[i] = str(bmtc_data[i][0]).split(":")[1]
            direction[i] = "Down"
        params = {'direction': 'UP', 'routeNO': route}
        r = requests.post(bmtc_url, data=params)
        bmtc_data = r.json()
        for i in range(0,len(bmtc_data)):
            buses_lat.append(str(bmtc_data[i][2]).split(":")[1])
            buses_lon.append(str(bmtc_data[i][3]).split(":")[1])
            buses_number.append(str(bmtc_data[i][0]).split(":")[1])
            direction.append("UP")
        if route=="356-CW":
            route="356-CW-FLY"
            params = {'direction': 'UP', 'routeNO': route}
            r = requests.post(bmtc_url, data=params)
            bmtc_data = r.json()
            for i in range(0,len(bmtc_data)):
                buses_lat.append(str(bmtc_data[i][2]).split(":")[1])
                buses_lon.append(str(bmtc_data[i][3]).split(":")[1])
                buses_number.append(str(bmtc_data[i][0]).split(":")[1])
                direction.append("UP")
            params = {'direction': 'DN', 'routeNO': route}
            r = requests.post(bmtc_url, data=params)
            bmtc_data = r.json()
            for i in range(0,len(bmtc_data)):
                buses_lat.append(str(bmtc_data[i][2]).split(":")[1])
                buses_lon.append(str(bmtc_data[i][3]).split(":")[1])
                buses_number.append(str(bmtc_data[i][0]).split(":")[1])
                direction.append("Down")
        context["buses_lat"] = buses_lat
        context["buses_lon"] = buses_lon
        context["buses_number"] = buses_number
        context["direction"]=direction
        # print str(str(bmtc_data[0][0]).split(":")[1])
        return HttpResponse(str(json.dumps(context)))
