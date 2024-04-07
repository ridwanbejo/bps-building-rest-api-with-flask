#!/usr/bin/python3

"""
export YOURAPPLICATION_SETTINGS=./settings.cfg
"""

from flask import Flask, jsonify, request


app = Flask(__name__)

app.config.from_envvar('YOURAPPLICATION_SETTINGS')

@app.route('/')
def get_home():
	response = {
		"message": "Welcome visitor",
		"app_port": app.config['APP_PORT'],
		"debug": app.config['DEBUG'],
		"remark": "We use Python config file"
	}

	return jsonify(response)

@app.route('/hello')
def get_hello():
	response = {
		"message": "Hello world!"
	}

	return jsonify(response)


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['APP_PORT'])