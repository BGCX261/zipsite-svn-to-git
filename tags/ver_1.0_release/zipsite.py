#!/bin/env python
##
##    This is a project for Google App Engine 
##        that support create a webisite by ZIP packages!
##
##    By Litrin J. 2011/02
##    Website: http://code.google.com/p/zipsite
##

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import db
from zipfile import ZipFile
from DataStore import *
from LoadConfig import Config
import os
import logging
import mimetypes


class MainHandler(webapp.RequestHandler):

    URL = ''

    def get(self):
    
        self.loadSetting()
        self.URL=self.request.path
        
        if ( self.URL[-1:] == '/'):
        #Get the defaule file for the path
            self.URL += self.IndexPage       
                
        self.buildMimeType()
        #Set the Mime type in header
            
        Entry = self.loadFromMemcach()
        if (Entry is not None):
                        
            logging.info("Load: " + self.URL + " From Memcache")
            
        else:
            DBHandle = DBCache()
            Entry = DBHandle.Load(self.URL) 
            
            if (Entry is not None):
                self.writeToMemcache(Entry)
                logging.info("Load: " + self.URL + " From Database")
                        
            else:
                sRealFileName = os.getcwd() + self.WebsitePath + self.URL
                                
                if (os.path.exists(sRealFileName)):
                #If the file not be ziped, read it drictory    
                    fNoZipedFile = open(sRealFileName,'r')
                    Entry = fNoZipedFile.read()
                    fNoZipedFile.close()
                    
                    Entry = self.saveCacheFile(Entry, self.response.headers['Content-Type'])
                    self.writeToMemcache(Entry)

                    logging.info("Load: " + self.URL + " From unziped file")

                else:
                    Entry = self.loadZipFile()
                    if (Entry is not None):
                        Entry = self.saveCacheFile(Entry, self.response.headers['Content-Type'])
                        
                        self.writeToMemcache(Entry)
                    
                        logging.info("Load: " + self.URL + " From ziped file")

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
            return Entry
        else:
        #Can't file the file in Zip packages
            self.error(404)
            self.response.out.write('<h1> 404 No Found! </h1>')
            #exit()
        

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
        if (len(data) < 1024*1024):
        #limit for GAE
            memcache.add(memcachkey, data, 0)
            logging.info(memcachkey + ' cached!')
        else:
            logging.info(memcachkey + ' too big to save in memcache!')
            

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
                        
        DBHandle = DBCache()
        DBHandle.SaveBlob(self.URL, Entry, MimeType)
                
        return Entry
        
    def loadSetting(self):
        Config(FileName='website.cfg', Title='zipsite')
        
        self.CACHEDTIME = Config(FileName='website.cfg', Title='zipsite').getInt('MemcacheTime')
        self.WebsitePath = Config(FileName='website.cfg', Title='zipsite').getStr('WebsiteFilePath') 
        self.IndexPage = Config(FileName='website.cfg', Title='zipsite').getStr('DefaultPage')
       

def main():
    application = webapp.WSGIApplication([
                            ('.*', MainHandler),
                                ], 
                                                    debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
