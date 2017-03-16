from django.shortcuts import render
from .models import BusStops
import json, requests, time
from django.http import HttpResponse

def home(request):
    context={}
    if request.method == 'POST':
        src = request.POST.get('source')
        dest = request.POST.get('destination')
        context["src"] = src
        context["dest"] = dest
        src_lat = BusStops.objects.get(stop_name=src).latitude
        src_lon = BusStops.objects.get(stop_name=src).longitude
        src_loc = src_lat+", "+src_lon
        dest_lat = BusStops.objects.get(stop_name=dest).latitude
        dest_lon = BusStops.objects.get(stop_name=dest).longitude
        dest_loc = dest_lat+", "+dest_lon
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
        for i in range(0,len(steps)):
            if steps[i]["travel_mode"]=="TRANSIT":
                bus_obj = steps[i]
                break
        context["route_no"] = str(bus_obj["transit_details"]["line"]["short_name"])
        context["stops"] = str(bus_obj["transit_details"]["num_stops"])
        context["bus_name"] = str(bus_obj["transit_details"]["line"]["name"])
        context["arrival_time"] = str(bus_obj["transit_details"]["departure_time"]["text"])
        #print "Bus Route No. "+str(bus_obj["transit_details"]["line"]["short_name"])+" from "+str(bus_obj["transit_details"]["line"]["name"])+" will arrive at "
        #print str(bus_obj["transit_details"]["departure_time"]["text"])
    return render(request,"home.html",context)

def get_bus_stops(request):
    buses = ['ABCDEF','LAJDLA',"JSJHJHSDJH",'KHSJKDJS']
    print(buses)
    return HttpResponse(str(buses))
