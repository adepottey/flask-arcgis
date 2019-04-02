from arcgis.gis import GIS
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


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

@app.route('/driveToDover')
def check_time():

    # get input parameters
    long = request.args.get("long")
    lat = request.args.get("lat")

    if long is None:
        long = 43.3045
    if lat is None:
        lat = -70.9756

    # search for the feature layer
    gis = GIS()
    itemid = "119a14d182b443b8b56340433d47d7e1"
    layer = gis.content.get(itemid).layers[0]

    # query feature layer using location
    # TODO THIS IS NOT DOING A SPATIAL QUERY
    results = layer.query(geometry_filter={"x": long, "y": lat, "spatialReference":{"wkid": 4326}}, out_fields="FromBreak,ToBreak", return_geometry=False)

    # no results means it's outside driving distance
    if len(results) == 0:
        return "This location is more than a 90 minute drive from Dover, NH."

    # return information about smallest buffer
    else:
        closest_result = sorted(results, key = lambda f : f.attributes["FromBreak"])[0]
        return "This location is a {0} - {1} minute drive from Dover, NH.".format(closest_result.attributes["FromBreak"], closest_result.attributes["ToBreak"])

if __name__ == '__main__':
    app.run()
