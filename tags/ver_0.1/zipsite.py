#!/bin/env python
##
##	This is a project for Google App Engine 
##		that support create a webisite by ZIP packages!
##
##	By Litrin J. 2011/01
##	Website: www.litrin.net
##

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import db
from zipfile import ZipFile
import os
import logging
import mimetypes


class MainHandler(webapp.RequestHandler):
	'''
This is a project for Google App Engine that support create a webisite by ZIP packages!
	'''
	URL = ''
	CACHEDTIME = 60*60*24
	#setting memcaching time (seconds)
	WebsitePath = '/Website'

	def get(self):
	
		self.URL=self.request.path
		
		if ( self.URL[-1:] == '/'):
		#Get the defaule file for the path
			self.URL+='index.html'		
				
		self.buildMimeType()
		#Set the Mime type in header
			
		Entry = self.loadFromMemcach()
		if (Entry is not None):
                        
			logging.info("Load: " + self.URL + " From Memcached!")
			
		else:
			DBHandle = DBCache()
			Entry = DBHandle.Load(self.URL) 
			
			if (Entry is not None):
				logging.info("Load: " + self.URL + " From Database!")
						
			else:
				sRealFileName = os.getcwd() + self.WebsitePath + self.URL
                                
				if (os.path.exists(sRealFileName)):
				#If the file not be ziped, read it drictory	
					fNoZipedFile = open(sRealFileName,'r')
					Entry = fNoZipedFile.read()
					fNoZipedFile.close()
					
					Entry = self.saveCacheFile(Entry, self.response.headers['Content-Type'])
					
					logging.info("Load: " + self.URL + " From unziped file!")

				else:
					Entry = self.loadZipFile()
					logging.info("Load: " + self.URL + " From ziped file!")

		self.response.out.write(Entry)
		#Response building finished!

	def loadZipFile(self):
	#Load the file from zip files. This is the core function!
		lFilename = self.URL.split('/')

		iPathLevel = 1
		#Loop count, The dir layers

		Entry = None
		while(iPathLevel <= len(lFilename)):
		#Get the zip file name and the filename from the URL, support muli-layer	
			sFilePath = os.getcwd() + self.WebsitePath
			sFileName = ''


			iElementCount = 1
			for sElement in lFilename:
			#Set or reset the Zip filename
				if ( iElementCount <= iPathLevel):
					sFilePath += sElement + '/'
					
				if ( iElementCount >= iPathLevel ):
					sFileName += sElement + '/'
					
				iElementCount += 1
				
			sFileName = sFileName[0:-1]
			sZipFilename = sFilePath[0:-1] + '.zip'
			
			if (os.path.exists(sZipFilename)):
			#Found the Zip file
				ZipFileHandle = ZipFile(sZipFilename)
				try:
					Entry = ZipFileHandle.read(sFileName)
					ZipFileHandle.close()
					logging.info(sFileName + " in " + sZipFilename + " Loaded!")

					break
				except:
					logging.error('No found ' + self.request.path + '' +sZipFilename+' !')
                                
		
			iPathLevel +=1

		if (Entry is not None ):
                        Entry = self.saveCacheFile(Entry, self.response.headers['Content-Type'])
                        return Entry
                else:
		#Can't file the file in Zip packages
			self.error(404)

			return '<h1> 404 No Found! </h1>'
		

	def loadFromMemcach(self):
		memcachkey = self.URL
		#The cache key is URL
		
		Entry = memcache.get(memcachkey)		
		if Entry is not None:
			return Entry

		else:
			return None

	def writeToMemcache(self, data):		
		memcachkey = self.URL
		#set the URL as the key
		memcache.add(memcachkey, data, 0)
		
		logging.info(memcachkey + ' cached!')
		return True

	def buildMimeType(self):
	#Building the MimeType in Http header
		sFilename = os.path.basename(self.URL)
		lFileName = sFilename.split(".")
		sExFilename = lFileName.pop()
		#Get the file ex-filename
		
		mimetypes.init()
		mimetypes.add_type('image/ico', '.ico')
		try:
			sMimeType = mimetypes.types_map['.'+sExFilename]
		except:
			sMimeType = 'text/html'
		
		self.response.headers['Content-Type'] = sMimeType
		#Send Content-type
		
	def saveCacheFile(self, Entry, MimeType):

		if( MimeType == 'text/html'):

			try:
			#Loading Plugin
				from Plugin import HtmlReplace
				Entry = HtmlReplace.main(Entry)
				logging.info('The pluging HtmlReplace executed!')

			except:
				logging.error('No found plugin HtmlReplace')

				
		if( #MimeType == 'image/png' or MimeType == 'image/x-png'
			#MimeType == 'image/jpeg' or MimeType == 'image/pjpeg'
			#or MimeType == 'image/gif' 
			False):

			try: 
			#Loading Plugin
                                
				from Plugin import ImageOptimizer
				Entry = ImageOptimizer.main(Entry, MimeType)
				logging.info('The pluging OptimizeImage executed!')

			except:
				logging.error('No plugin! ')
		
		if ( MimeType == 'text/css'):
			try:
				from Plugin import CSSMinify
				Entry = CSSMinify.main(Entry)
				logging.info('The pluging CSSMinify executed!')
				
			except:
				logging.error('No found plugin CSSMinify')
						
		DBHandle = DBCache()
		DBHandle.SaveBlob(self.URL, Entry, MimeType)
				
		self.writeToMemcache(Entry)

		return Entry


	
class DBCache(db.Model):
	
	CreateTime = db.DateTimeProperty(auto_now_add=True)
	URL = db.StringProperty(multiline=False)
	BlobEntry = db.BlobProperty()
	MimeType = db.StringProperty(multiline=False)
	LoadCount = db.IntegerProperty(default = 1)
	
	def SaveBlob(self, URL, Entry, MimeType):
		DBHandle = DBCache()
		DBHandle.URL = URL
		DBHandle.BlobEntry = Entry
		DBHandle.MimeType = MimeType
		DBHandle.put()
		
	def Load(self, URL):
		DBHandle = DBCache.all()
		DBHandle.filter("URL = ", URL).fetch(1)
		
		if(DBHandle.count() == 0):
			return None
		else:
			for Query in DBHandle:
				if(Query.BlobEntry is not None):
					Entry = Query.BlobEntry
				else:
					Entry = None
				
				Query.LoadCount = Query.LoadCount + 1
				Query.put()
			
			return Entry

class clean(webapp.RequestHandler):
	
	def get(self):
		memcache.flush_all()
		logging.info('Memcache has all flushed! ')
		
		db.delete(DBCache().all())
		
		self.redirect( '/' )
		


def main():
	application = webapp.WSGIApplication([
							('/memcacheflush', clean), 
							('.*', MainHandler),
								], 
													debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()
