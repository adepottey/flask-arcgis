from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/hello')
def hello_someone():
    who = request.args.get("who")
    return "Hello {0}".format(who)


if __name__ == '__main__':
    app.run()
