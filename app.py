from arcgis.gis import GIS
from arcgis.geometry import Point, filters
from arcgis.network import RouteLayer, analysis
from flask import Flask, request, jsonify

application = app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello PSDW!'


@app.route('/hello')
def hello_someone():
    who = request.args.get("who")
    return "Hello {0}".format(who)


@app.route('/api/hello')
def api_hello_someone():
    who = request.args.get("who")
    message = "Hello {0}".format(who)
    response = jsonify({ "msg": message })
    response.status_code = 200
    return response

@app.route('/api/driveToDover')
def check_time():

    # https://ps-cc.maps.arcgis.com/home/webmap/viewer.html?webmap=5589213f373c4e31a3cd2a8e7dc2b4d4
    # Boston Logan: lat=42.3656&long=-71.0096
    # Portland: lat=43.6465&long=-70.3097
    # Manchester: lat=42.9297&long=-71.4352

    # get input parameters
    long = request.args.get("long")
    lat = request.args.get("lat")

    if lat is None:
        lat = 42.3656
    if long is None:
        long = -71.0096

    # search for the feature layer
    gis = GIS()
    itemid = "119a14d182b443b8b56340433d47d7e1"
    layer = gis.content.get(itemid).layers[0]

    # query feature layer using location
    filter = filters.intersects(Point({"x": long, "y": lat, "spatialReference":{"wkid": 4326}}))
    results = layer.query(geometry_filter=filter, out_fields="FromBreak,ToBreak", return_geometry=False)

    # no results means it's outside driving distance
    if len(results) == 0:
        response_msg = "This location is more than a 60 minute drive from Dover, NH."

    # return information about smallest buffer
    else:
        closest_result = sorted(results, key = lambda f : f.attributes["FromBreak"])[0]
        response_msg = "This location is a {0} - {1} minute drive from Dover, NH.".format(closest_result.attributes["FromBreak"], closest_result.attributes["ToBreak"])

    return jsonify({"msg": response_msg}), 200

@app.route('/api/actualDriveToDover')
def calc_drivetime():

    # Boston Logan: lat=42.3656&long=-71.0096&token=
    # Portland: lat=43.6465&long=-70.3097&token=
    # Manchester: lat=42.9297&long=-71.4352&token=

    # get input parameters
    long = request.args.get("long")
    lat = request.args.get("lat")
    token = request.args.get("token")
    if lat is None or long is None or token is None:
        return jsonify({"error": "Missing input parameter"}), 400

    # get referer header
    referer = request.headers.get("referer")

    # referer should be sent, but for demo:
    if referer is None:
        referer = "http://localhost"

    # make input geometry
    search_geom = Point({"x": long, "y": lat, "spatialReference":{"wkid": 4326}})

    # Dover, NH geometry
    dover_geom = Point({"x": -70.8737, "y": 43.1979, "spatialReference": {"wkid": 4326}})

    # authenticate using token

    # This works if you have a token generated with referer = 'http':
    # gis = GIS(url="https://ps-cc.maps.arcgis.com/", username=None, password=None, token=token)

    # This works for any token as long as referer matches
    gis = GIS(url="https://ps-cc.maps.arcgis.com/")
    gis._con._referer = referer
    gis._con._token = token

    # do routing
    try:
        route_service_url = gis.properties.helperServices.route.url
        route_layer = RouteLayer(route_service_url, gis=gis)
        stops = '{0},{1}; {2},{3}'.format(search_geom.x, search_geom.y, dover_geom.x, dover_geom.y)
        result = route_layer.solve(stops=stops,
                                   return_directions=False, return_routes=True,
                                   output_lines='esriNAOutputLineNone',
                                   return_barriers=False, return_polygon_barriers=False,
                                   return_polyline_barriers=False)

        travel_time = result['routes']['features'][0]['attributes']['Total_TravelTime']
        response_msg = "This location is a {0} minute drive from Dover, NH.".format(travel_time)

        return jsonify({"msg": response_msg}), 200

    except:
        return jsonify({"error":"An error occurred"}), 500


if __name__ == '__main__':
    app.run()
