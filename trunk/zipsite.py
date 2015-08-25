#!/bin/env python
#
# Copyright (c) 2011, Zipsite Project Group All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     # Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     # Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     # Neither the name of the Zipsite Project nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE GROUP AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE GROUP AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##
##    This is a project for Google App Engine 
##        that support create a webisite by ZIP packages!
##
##    By Litrin J. 2011/06
##    Website: http://code.google.com/p/zipsite
##

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import db
from zipfile import ZipFile
from lib.DataStore import DBCache
from lib import LoadConfig
from lib.MemCache import CacheURL
from lib.LoadFile import NoCached
import os
import logging
import time


class MainHandler(webapp.RequestHandler):

    URLString = ''
    IndexPage = LoadConfig.getStr('zipsite', 'DefaultPage')
    CacheControl = LoadConfig.getInt('zipsite', 'Cache-Control')
    HttpStatus  = 200

    def get(self):
    
        self.URLString=self.request.path
        
        if ( self.URLString[-1:] == '/'):
        #Get the defaule file for the path
            self.URLString += self.IndexPage       
            
        DBHandle = DBCache()
        Entry = DBHandle.load(self.URLString) 
        
        if (Entry is not None):
            logging.info("Load: " + self.URLString + " From Cached!")
            
        else:
            try:
                Entry = NoCached().load(self.URLString)
                
            except NameError:
                logging.info('404 Page no found at ' + self.URLString)
		
                Entry = ('text/html', '<h1>404 Page No Found!</h1>', time.time())
                self.HttpStatus = 404
            
        self.httpHandle(Entry)
    
    def httpHandle(self, Entry):
        
        sMimeType = Entry[0]
        Content   = Entry[1]
        CreateTime = Entry[2]
        
        if (self.request.if_modified_since is not None):
            localCachedTime = time.mktime(time.strptime( self.request.headers['If-Modified-Since'], "%a, %d %b %Y %H:%M:%S GMT"))
            
            if(abs( localCachedTime - CreateTime ) < 60 ):
                self.HttpStatus = 304
                
        self.response.set_status(self.HttpStatus)
        self.response.headers['Content-Type'] = sMimeType
        
        sModifyTime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(CreateTime))
        self.response.headers.add_header('Last-Modified', sModifyTime)

        sExpireTime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time() + self.CacheControl * 24 * 3600))
        self.response.headers.add_header('Expires', sExpireTime)

        self.response.headers['Cache-Control'] = 'max-age=' + str(self.CacheControl * 24 * 3600)
        
        
        self.response.out.write(Content)
        
def main():
    application = webapp.WSGIApplication([
                            ('.*', MainHandler),
                                ], 
                                                    debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
