####################################################################################################
#	This plugin will act as an embedded webserver for other channels
#
#	Made by 
#	dane22....A Plex Community member
#
####################################################################################################

# To find Work in progress, search this file for the word ToDo

import os
import posixpath
import urllib
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import threading
import ast

VERSION = ' V0.0.0.1'
NAME = 'WebChannels'
ART = 'art-default.jpg'
ICON = 'icon-WebChannel.png'
PREFIX = '/applications/WebChannels'
APPGUID = '7608cf36-742b-11e4-8b39-00089be320f4'
DESCRIPTION = 'Acts as a webserver for other channels/bundles'
ROUTES = {}

####################################################################################################
# Start function
####################################################################################################
def Start():
	print("********  Started %s on %s  **********" %(NAME  + VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME  + VERSION, Platform.OS))
	global myWeb
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME  + VERSION
	ObjectContainer.view_group = 'List'
	DirectoryObject.thumb = R(ICON)
	HTTP.CacheTime = 0
	GetRoutes()
	# Start WebServer
	myWeb = WebServer()
	myWeb.start()

####################################################################################################
# Get Routes to valid document roots
####################################################################################################
@route(PREFIX + '/GetRoutes')
def GetRoutes():
	global ROUTES	
	ROUTES = ast.literal_eval('{' + Prefs['Routes'] + '}')

####################################################################################################
# Main menu
####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
@route(PREFIX + '/MainMenu')
def MainMenu():
	Log.Debug("**********  Starting MainMenu  **********")
	oc = ObjectContainer()
	try:
		oc.add(DirectoryObject(key=Callback(backgroundScan, title=title, sectiontype=sectiontype, key=key, random=time.clock(), paths=',,,'.join(paths)), title='Look in section "' + title + '"', summary='Look for unmatched files in "' + title + '"'))
		print 'ged'
	except:
		Log.Critical("Exception happened in MainMenu")
		raise
	oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
	Log.Debug("**********  Ending MainMenu  **********")
	return oc

#***********************************************************************
# ValidatePrefs
#***********************************************************************
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
	Log.Debug('Validating Prefs')
	GetRoutes()
	myWeb.restart()

#***********************************************************************
# WebServer
#***********************************************************************
class WebServer(HTTPServer):
	def __init__(self):
		self.server_address = '0.0.0.0'
		self.HandlerClass = RequestHandler
		Log.Debug('* http deamon init okay')

	def start(self):
		Log.Debug('* Starting httpd deamon')
		self.server_port = int(Prefs['Port'])
		self.server = HTTPServer((self.server_address, self.server_port), self.HandlerClass)	
		thread = threading.Thread(target = self.server.serve_forever)
		thread.deamon = True
		thread.start()
		sa = self.server.socket.getsockname()
		print "* Serving HTTP on", sa[0], "port", sa[1], "..."
		Log.Debug('* Serving HTTP on %s port %s ....' %(sa[0],sa[1]))

	def stop(self):
		print 'Stopping httpd deamon.....Please wait'
		Log.Debug('Shutting down httpd deamon')
		self.server.shutdown()

	def restart(self):
		Log.Debug('Restarting WebServer')
		self.stop()
		self.start()

#***********************************************************************
# RequestHandler
#***********************************************************************
class RequestHandler(SimpleHTTPRequestHandler):
	# Request Handler for bundle paths
	def translate_path(self, path):
		"""translate path given routes"""

		# set default root to this bundles http directory
		root = os.path.join(Core.app_support_path, 'Plug-ins', 'WebChannel.bundle', 'http-root')
	      
		# look up routes and set root directory accordingly to the request
		for pattern, rootdir in ROUTES.items():
			if path.startswith(pattern):
				# found match!
				path = path[len(pattern):]  # consume path up to pattern len
				root = rootdir
				break
	      
		# normalize path and prepend root directory
		path = path.split('?',1)[0]
		path = path.split('#',1)[0]
		path = posixpath.normpath(urllib.unquote(path))
		words = path.split('/')
		words = filter(None, words)				  
		path = root
		for word in words:
			drive, word = os.path.splitdrive(word)
			head, word = os.path.split(word)
			if word in (os.curdir, os.pardir):
				continue
			path = os.path.join(path, word)
		return path

