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
##    By Litrin J. 2011/03
##    Website: http://code.google.com/p/zipsite
##    Example: android-sdk.appspot.com
##

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
from lib.DataStore import *
import logging

class AddTask(webapp.RequestHandler):
    
    def get(self):
        self.post()
        self.redirect( '/' )
    
    def post(self):
        DBCache().flush()
        
        pQueue = taskqueue.Queue(name = 'DeleteDBCache')
        
        if (DBCache().all().count() > 1 ):
            taskurl = 'http://' + self.request.host_url
            pTask = taskqueue.Task(url='/cacheflush', params=dict(url=taskurl))
            pQueue.add(pTask)
            
        else:
            memcache.flush_all()
            pQueue.purge()
            
            logging.info('DBcache has all flushed! ')
            

def main():
    application = webapp.WSGIApplication([
                            ('.*', AddTask),
                           
                                ], debug=True)
                                
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
