from flask import Flask
application = Flask(__name__)

@application.route("/")
def hello():
    return "<h1>Hello Docker!</h1><a href='/static/'>A link to a meme</a>"
