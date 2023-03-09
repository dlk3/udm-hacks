#!/usr/bin/env python

#  Copyright (C) 2023  David King <dave@daveking.com>
#
#  This Source Code Form is subject to the terms of the Mozilla Public License,
#  v. 2.0.  If a copy of the MPL was not distbuted with this file, You can
#  obtain one at https://mozilla.org/MPL/2.0/.

'''
                         An API for the Ubiquity Dream Machine

This is not an official, supported API.  It was constructed by introspecting the 
request/response exchanges between the UDM and my web browser.  As a result, this API may 
cease to function at any time, without warning.

To establish a connection with a UDM:

	import udm
	my_udm = udm.UDM(udm_url, admin_userid, admin_password)
	
	Object attributes:
	
	my_udm.devices - contains a list of network Device objects known to the UDM.
					 (/proxy/network/api/s/default/stat/sta)
	my_udm.cameras - contains a list of Camera objects known to the UDM.
					 (/proxy/protect/api/bootstrap)

A "Device" object represents one network device attached to the UDM Network Console application.
Cameras are one type of device that can be attached, as are the network switches they connect to.
POE status is controlled through the switch device, not the camera device.

Device Attributes:
	session = The requests session that contains the request headers needed to interact with 
			  the UDM that controls this device.
	url 	= The url of the UDM that controls this device.
	mac 	= This device's MAC address.
	sw_mac 	= The MAC address of the switch this device is plugged into.
	sw_port = The port number this device is plugged into.
	
A "Camera" object represents one camera attached to the UDM Protect application.  Some attributes
of the corresponding network device are copied over into this object.

Camera Attributes:
	session 	= The requests session that contains the request headers needed to interact with 
				  the UDM that controls this device.
	url 		= The url of the UDM that controls this device.
	mac 		= This device's MAC address.
	name 		= The name given to this camera in the Protect application.
	lastseen 	= When this camera was last seen by the Protect application, as a UNIX timestamp.
	switch_mac 	= The MAC address of the switch this camera is plugged into.
	switch_port = The port number this camera is plugged into.

Camera Methods:
	getPOE()		   - returns True or False, indicating the current POE state of the camera,
						 "ON" or "OFF."
	setPOE("ON"|"OFF") - turns camera power on or off.  Returns True if no errors ocurred.  If
						 the camera POE is already in the desired state, nothing is done.
'''
	
import logging
import base64
import json
import os
import datetime

#  Handle error that occurs if the requests module is not installed
try:
	import requests

	#  Turn off warnings about the use of self-signed SSL certificates.  This code may
	#  need to be modified if you are using a later version of the requests module.
	from requests.packages.urllib3.exceptions import InsecureRequestWarning
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except:
	logging.error('ERROR: Unable to import the Python "requests" module.  Is it installed?')
	exit(1)

#  Define an object class for a UDM device		
class UDM:
	
	#  Login to UDM, creating a requests session object containing the authentication headers
	#  needed for subsequent requests.  Also get the list of known network client devices and
	#  cameras.
	def __init__(self, hostname, userid, password, camera_json_filename=os.path.expanduser('~/.config/udmcameralist.json')):
		self.url = 'https://' + hostname

		logging.debug('Logging into UDM')

		#  Create session for UDM connection
		self.session = requests.Session()

		#  Login to UDM
		_request_data = {
			'username': userid,
			'password': password,
			'rememberMe': False
		}
		try:
			_r = self.session.post(self.url + '/api/auth/login', json=_request_data, verify=False)
		except Exception as e:
			logging.exception('Unexpected exception while logging in to {}'.format(url), exc_info=True)
			exit(1)
		if _r.status_code != 200:
			logging.error('The login failed: ' + _r.text)
			exit(_r.status_code)
			
		#  Set authorization cookies for all subsequent requests
		self.session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
		for _cookie in _r.headers['Set-Cookie'].split(';'):
			if _cookie.startswith('TOKEN='):
				self.session.headers.update({'Cookie': _cookie + ';'})
				#  If the token cookie contains a x-csrf-token value, this must be decoded
				#  and passed in the request headers otherwise any attempt to change any
				#  settings will fail with a "404 Not Found" error.
				_decoded_token = base64.b64decode(_cookie.split('=')[1].split('.')[1] + '===')
				_decoded_token = json.loads(_decoded_token.decode('utf-8'))
				if 'csrfToken' in _decoded_token:
					self.session.headers.update({'x-csrf-token': _decoded_token['csrfToken']})

		logging.debug('Authentication headers:\n{}'.format(json.dumps(dict(self.session.headers), indent=4)))

		#  Add lists of devices and cameras as UDM object attributes
		self.devices = self._getDevices()
		self.cameras = self._getCameras(camera_json_filename)
	
	#  Return a list of	Device objects, one for each network device that the UDM manages
	def _getDevices(self):
		
		#  Get the list of network devices known to this UDM
		logging.debug('Getting network device list from UDM Network Console app')
		_device_list = []
		_r = self.session.get(self.url + '/proxy/network/api/s/default/stat/sta', verify=False)
		if _r.status_code == 200:
			for device in _r.json()['data']:
				_device_list.append(Device(self.session, self.url, device))
			logging.debug('Network client devices:\n{}'.format(json.dumps(_r.json()['data'], indent=4)))
		else:
			logging.error('The request for network client information failed with status code = {}'.format(_r.status_code))
			if _r.text != '':
				logging.error('Response text: {}'.format(_r.text))

		return _device_list
	
	#  Return a list of Camera objects, one for each camera that the UDM manages
	def _getCameras(self, camera_json_filename):
			
		#  When a camera is powered off for a period of time, the UDM Protect application
		#  forgets it.  In order to remember cameras that are powered off, we save the camera
		#  info in a file.  Cameras in the file are matched with those that Protect currently
		#  knows about using the camera's MAC addresses.  If a camera is permanently removed
		#  from the network, it is possible that it remains in our camera file.  We don't
		#  think this will cause any problems but who knows?
		
		#  Read in the camera list file, if it exists
		_camera_json = []
		try:
			if os.path.exists(camera_json_filename):
				logging.debug('Reading existing file {}'.format(camera_json_filename))
				with open(camera_json_filename, 'r') as _f:
					_camera_json = json.load(_f)
		except:
			logging.exception('Unexpected exception', exc_info=True)
	
		#  Get the information for all of the cameras Protect currently knows about
		logging.debug('Getting list of cameras from UDM Protect app')
		_r = self.session.get(self.url + '/proxy/protect/api/bootstrap', verify=False)
		if _r.status_code != 200:
			logging.error('The request for camera information failed with status code = {}'.format(_r.status_code))
			if _r.text != '':
				logging.error('Response text: {}'.format(_r.text))
			return
		for _camera in _r.json()['cameras']:
			_found = False
			_camera['switch_mac'] = ''
			_camera['switch_port'] = ''
			for _c in _camera_json:
				if _c['name'].upper() == _camera['name'].upper():
					_found = True
					logging.debug('Updating existing camera in the list: {}'.format(_camera['name']))
					_c = _camera
					_c['mac'] = _camera['mac'].upper()
					break
			if not _found:
				logging.debug('Adding new camera to the list: {}'.format(_camera['name']))
				_camera['mac'] = _camera['mac'].upper()
				_camera_json.append(_camera)

		#  Update the camera list with the MAC address of the switches and the 
		#  ports on those switches that the cameras are connected to.
		for _device in self.devices:
			for _c in _camera_json:
				if _device.mac == _c['mac']:
					try:
						_c['switch_mac'] = _device.sw_mac
					except:
						pass
					try:
						_c['switch_port'] = _device.sw_port
					except:
						pass
					logging.debug('Updating network switch MAC and port number for {} camera\nMAC: {} Port: {}'.format(_c['name'], _c['switch_mac'], _c['switch_port']))
					break
		
		#  Overwrite the camera list file			
		logging.debug('Writing camera details file {}'.format(camera_json_filename))
		try:
			with open(camera_json_filename, 'w') as _f:
				json.dump(_camera_json, _f)		
		except:
			logging.exception('Unexpected exception', exc_info=True)
		logging.debug('Camera details:\n{}'.format(json.dumps(_camera_json, indent=4)))	
		
		#  Return the camera list as a list of camera objects
		_camera_list = []
		for camera in _camera_json:
			_camera_list.append(Camera(self.session, self.url, camera))
		return _camera_list

#  Define object classes for network devices and cameras
class Device:
	def __init__(self, session, url, properties):
		self.session = session
		self.url = url
		self._properties = properties
		self.mac = properties['mac'].replace(":","").upper()
		try:
			self.sw_mac = properties['sw_mac'].replace(":","").upper()
		except:
			logging.debug('Device with MAC = {} does not have a "sw_mac" attribute.'.format(self.mac))
			self.sw_mac = None
		try:
			self.sw_port = properties['sw_port']
		except:
			logging.debug('Device with MAC = {} does not have a "sw_port" attribute.'.format(self.mac))
			self.sw_port = Nonew
		
class Camera:
	def __init__(self, session, url, properties):
		self.session = session
		self.url = url
		self._properties = properties
		self.name = properties['name']
		self.mac = properties['mac'].replace(":","").upper()
		self.lastseen = properties['lastSeen']
		self.switch_mac = properties['switch_mac'].replace(":","").upper()
		self.switch_port = properties['switch_port']

	#  Return the current POE status of the switch port this camera instance is
	#  plugged into.  Returns True for "ON" and False for "OFF"
	def getPOE(self):
		logging.debug('Searching for the switch this camera is connected to, MAC = {}'.format(self.switch_mac))
		#  Get the switch configuration details
		_r = self.session.get(self.url + '/proxy/network/api/s/default/stat/device', verify=False)
		if _r.status_code != 200:
			logging.error('The request for switch configuration information failed with status code = {}'.format(_r.status_code))
			if _r.text != '':
				logging.error('Response text: {}'.format(_r.text))
			return
		#  Find the switch this camera is connected to
		for _device in _r.json()['data']:
			_mac = _device['mac'].replace(":","").upper()
			if _mac == self.switch_mac:
				#  Find the port on this switch the camera is connected to
				logging.debug('Found the switch')
				logging.debug('Searching for the port this camera is plugged into, port #: {}'.format(self.switch_port))
				for _port in _device['port_table']:
					if _port['port_idx'] == self.switch_port:
						logging.debug('Found the port for {} camera.  Port details:\n{}'.format(self.name, json.dumps(_port, indent=4)))
						try:
							#  Add the POE status and device_id as attributes
							self.switch_id = _device['_id']
							self.poe_status = _port['poe_enable']
							
							#  Prepopulate the POST data structure we'll need to
							#  include if we send a PUT request to change the POE
							#  mode on this camera's switch port
							self.port_override = {
								'autoneg': _port['autoneg'],
								'full_duplex': _port['full_duplex'],
								'port_idx': _port['port_idx'],
								'port_security_mac_address': [],
								'portconf_id': _port['portconf_id'],
								'speed': _port['speed']
							}
							
							#  Return the current POE status
							return self.poe_status
						except KeyError as e:
							logging.exception('Missing port attribute: {}'.format(e), exc_info=True)
							return
						except Exception as e:
							logging.exception('Unexpected exception: {}'.format(e), exc_info=True)
							return
	
	#  Set the POE "ON" or "OFF" on the switch port this camera instance is plugged into.
	#  Will check to see what state the port is currently in and will not send a 
	#  request if the port is already in the desired state.
	def setPOE(self, desired_state):
		
		#  Flag that indicates whether or not a PUT request needs to be sent
		_request_pending = False
		
		#  Get the current POE state from an object attribute, or by querying
		#  the switch.  True = "ON", False = "OFF"
		logging.debug('Getting current state of {} camera'.format(self.name))
		try:
			_current_state = self.poe_status
			logging.debug('Current state: {}, from object property'.format(_current_state))
		except:
			_current_state = self.getPOE()		
			logging.debug('Current state: {}, from getPOE method'.format(_current_state))
			
		#  If the POE state needs to be changed, prepare the PUT data
		if _current_state and desired_state == 'OFF':
			logging.debug('{} camera is currently on, turning it off'.format(self.name))
			self.port_override['poe_mode'] = 'off'
			_request_pending = True
		elif not _current_state and desired_state == 'ON':
			logging.debug('{} camera is currently off, turning it on'.format(self.name))
			self.port_override['poe_mode'] = 'auto'
			_request_pending = True
		else:
			logging.debug('{} camera is already in the desired state, doing nothing'.format(self.name))

		#  Send a PUT request to change the POE state
		if _request_pending:
			_data = {
				'port_overrides': [self.port_override]
			}
			logging.debug('Sending POE request for {} camera:\n{}'.format(self.name, json.dumps(_data, indent=4)))
			_r = self.session.put(self.url + '/proxy/network/api/s/default/rest/device/' + self.switch_id, json=_data, verify=False)
			if _r.status_code != 200:
				logging.error('POE {} request failed with status code = {}'.format(desired_state, _r.status_code))
				logging.error('Response text: {}'.format(_r.text))
				return False
			else:
				logging.info('{} camera powered {}'.format(self.name, desired_state.lower()))
				return True
		
		return False
