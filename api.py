# coding: utf-8
from __future__ import unicode_literals

import json
import logging
import os
from flask import Flask, request, Response
from waitress import serve

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberMessageRequest


class ViberFlaskWrapper(object):
	
	# Main Flask object
	app = None
	
	# Stores session states
	sessionStorage = {}

	# Viber object for API interaction
	viber = None


	def __init__(self,name):
		self.app = Flask(name)
		self.app.add_url_rule('/message', view_func=self.message, methods=['POST'])

		bot_configuration = BotConfiguration(
			name=os.environ['VIBERBOT_NAME'],
			avatar=os.environ['VIBERBOT_AVATAR'],
			auth_token=os.environ['VIBERBOT_TOKEN']
		)

		self.viber = Api(bot_configuration)
		
	def run(self):
		self.app.run()
		
	def flask_app(self):
		return self.app
		
	def message(self):
		"""Retrieves request body and generates response"""
		logging.debug("received request. post data: {0}".format(request.get_data()))
		# every viber message is signed, you can verify the signature using this method
		if not self.viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
			return Response(status=403)

		# this library supplies a simple way to receive a request object
		viber_request = self.viber.parse_request(request.get_data())

		if not isinstance(viber_request, ViberMessageRequest):
			return Response(status=200)


		message = viber_request.message
		# lets echo back
		self.viber.send_messages(viber_request.sender.id, [
			message
		])

		return Response(status=200)


logging.basicConfig(level=logging.DEBUG)
app = ViberFlaskWrapper(__name__)
flask_app = app.flask_app()

if __name__ == "__main__":
	serve(flask_app, host="0.0.0.0", port=8080)
