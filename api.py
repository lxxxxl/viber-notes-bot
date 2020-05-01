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
from viberbot.api.messages import TextMessage

from YadiskWrapper import YadiskWrapper


class ViberFlaskWrapper(object):
	
	# Main Flask object
	app = None
	
	# Stores session states
	sessionStorage = {}

	# Viber object for API interaction
	viber = None

	# Yandex Disk object for API interaction
	disk = None

	# List of users allowed to use bot
	allowedUsers = None


	def __init__(self,name):
		self.app = Flask(name)
		self.app.add_url_rule('/message', view_func=self.message, methods=['POST'])

		bot_configuration = BotConfiguration(
			name=os.environ['VIBERBOT_NAME'],
			avatar=os.environ['VIBERBOT_AVATAR'],
			auth_token=os.environ['VIBERBOT_TOKEN']
		)

		self.viber = Api(bot_configuration)
		self.allowedUsers = os.environ['VIBERBOT_ALLOWED_USERS']

		self.disk = YadiskWrapper(os.environ['YADISK_TOKEN'])


		
	def run(self):
		self.app.run()
		
	def flask_app(self):
		return self.app
		
	def message(self):
		"""Retrieves request body and generates response"""
		logging.debug("received request. post data: {0}".format(request.get_data()))
		# verify message signature
		if not self.viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
			return Response(status=403)

		# this library supplies a simple way to receive a request object
		viber_request = self.viber.parse_request(request.get_data())

		# process only message requests
		if not isinstance(viber_request, ViberMessageRequest):
			return Response(status=200)

		# check if user allowed to iteract with bot
		if not viber_request.sender.id in self.allowedUsers:
			message = TextMessage(text="403")
			self.viber.send_messages(viber_request.sender.id, [
				message
			])
			return Response(status=200)


		if not isinstance(viber_request.message, TextMessage):
			message = TextMessage(text="Not supported yet")
			self.viber.send_messages(viber_request.sender.id, [
				message
			])
			return Response(status=200)

		request_text = viber_request.message.text
		response_text = 'Saved.'
		if not self.disk.save_note(request_text):
			response_text = 'Not saved.'

		message = TextMessage(text=response_text)
		self.viber.send_messages(viber_request.sender.id, [
			message
		])

		return Response(status=200)


logging.basicConfig(level=logging.DEBUG)
app = ViberFlaskWrapper(__name__)
flask_app = app.flask_app()

if __name__ == "__main__":
	serve(flask_app, host="0.0.0.0", port=8080)
