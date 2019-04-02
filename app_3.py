from flask import Flask, request, Response, jsonify

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


if __name__ == '__main__':
    app.run()
