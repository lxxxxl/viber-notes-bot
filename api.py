# coding: utf-8
from __future__ import unicode_literals

import json
import logging
import threading
import os
import urllib.request
from urllib.parse import urlparse
from flask import Flask, request, Response

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.messages import (
	TextMessage,
	PictureMessage,
	VideoMessage,
	FileMessage,
	LocationMessage)

from YadiskWrapper import YadiskWrapper


class ViberFlaskWrapper(Flask):
	
	# Stores session states
	sessionStorage = {}

	# Viber object for API interaction
	viber = None

	# Yandex Disk object for API interaction
	disk = None

	# List of users allowed to use bot
	allowedUsers = None


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.add_url_rule('/message', view_func=self.message, methods=['POST'])

		bot_configuration = BotConfiguration(
			name=os.environ['VIBERBOT_NAME'],
			avatar=os.environ['VIBERBOT_AVATAR'],
			auth_token=os.environ['VIBERBOT_TOKEN']
		)

		self.viber = Api(bot_configuration)
		self.allowedUsers = os.environ['VIBERBOT_ALLOWED_USERS']

		self.disk = YadiskWrapper(os.environ['YADISK_TOKEN'])
		
	def message(self):
		"""Retrieves request body and generates response"""
		logging.debug("Processing new request")
		# verify message signature
		if not self.viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
			logging.debug("User invalid signature: %s", request.headers.get('X-Viber-Content-Signature'))
			return Response(status=403)

		# this library supplies a simple way to receive a request object
		viber_request = self.viber.parse_request(request.get_data())

		# process only message requests
		if not isinstance(viber_request, ViberMessageRequest):
			logging.debug("Message is not ViberMessageRequest")
			return Response(status=200)

		# check if user allowed to iteract with bot
		if not viber_request.sender.id in self.allowedUsers:
			logging.debug("Unknown user: %s", viber_request.sender.id)
			message = TextMessage(text="403")
			self.viber.send_messages(viber_request.sender.id, [
				message
			])
			return Response(status=200)


		# Process Text message
		if isinstance(viber_request.message, TextMessage):
			logging.debug("Processing TextMessage")
			request_text = viber_request.message.text
			response_text = 'Saving...'
			message = TextMessage(text=response_text)
			self.viber.send_messages(viber_request.sender.id, [
				message
			])
			# Create saving thread
			logging.debug("Starting Saving Thread")
			save_thread = threading.Thread(
				target=self.thread_save_to_disk, 
				args=(
					viber_request.sender.id,
					request_text,
					None))
			save_thread.start()


		# Process Picture, Video and File messages
		elif isinstance(viber_request.message, PictureMessage)	\
		 or isinstance(viber_request.message, VideoMessage)		\
		 or isinstance(viber_request.message, FileMessage):
			logging.debug("Processing FileMessage")
			url = viber_request.message.media	# URL of sent file
			response_text = 'Saving...'
			message = TextMessage(text=response_text)
			self.viber.send_messages(viber_request.sender.id, [
				message
			])
			# Create saving thread
			logging.debug("Starting Saving Thread")
			save_thread = threading.Thread(
				target=self.thread_save_to_disk, 
				args=(
					viber_request.sender.id,
					None,
					url))
			save_thread.start()


		# Process Location message
		elif isinstance(viber_request.message, LocationMessage):
			logging.debug("Processing LocationMessage")
			request_text = str(viber_request.message.location)
			response_text = 'Saving...'
			message = TextMessage(text=response_text)
			self.viber.send_messages(viber_request.sender.id, [
				message
			])
			# Create saving thread
			logging.debug("Starting Saving Thread")
			save_thread = threading.Thread(
				target=self.thread_save_to_disk, 
				args=(
					viber_request.sender.id,
					request_text,
					None))
			save_thread.start()

		# Process other messages
		else:
			logging.debug("Received unsupported message")
			response_text = 'Not supported yet'
			message = TextMessage(text=response_text)
			self.viber.send_messages(viber_request.sender.id, [
				message
			])

		return Response(status=200)

	def thread_save_to_disk(self, user_id, note, file_url):
		"""Saves data to Yandex Disk and sends report to user_id"""
		logging.debug("Saving Thread started")
		response_text = 'Saved'
		# if text note provided
		if note:
			logging.debug("Saving note")
			if not self.disk.save_note(note):
				response_text = 'Cannot save note.'
		# if file provided
		if file_url:
			logging.debug("Saving file")
			# extract filename from URL
			url_parsed = urlparse(file_url)
			filename = os.path.basename(url_parsed.path)
			# download file to temp directory
			with urllib.request.urlopen(file_url) as response:
				logging.debug("Downloading file from Viber server")
				data = response.read()
				logging.debug("Uploading file to Disk")
				# upload file to Disk
				if not self.disk.save_file(filename, data):
					response_text = 'Cannot save file.'

		message = TextMessage(text=response_text)
		self.viber.send_messages(user_id, [
			message
		])
		return


app = ViberFlaskWrapper(__name__)
logging.basicConfig(level=logging.INFO)
