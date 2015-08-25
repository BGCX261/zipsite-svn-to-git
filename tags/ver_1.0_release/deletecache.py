#!/bin/env python
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
from DataStore import *
import logging

class AddTask(webapp.RequestHandler):
    
    def get(self):
        self.post()
        self.redirect( '/' )
    
    def post(self):
        memcache.flush_all()
        logging.info('Memcache has all flushed! ')        
        db.delete(DBCache().all())
        
        
        if (DBCache().all().count() > 1 ):
        	pQueue = taskqueue.Queue(name = 'DeleteDBCache')
        	taskurl = 'http://' + self.request.host_url
        	pTask = taskqueue.Task(url='/cacheflush', params=dict(url=taskurl))
        	
        	pQueue.add(pTask)
        else:
        	logging.info('DBcache has all flushed! ')
        	
       
        

def main():
    application = webapp.WSGIApplication([
                            ('.*', AddTask),
                           
                                ], debug=True)
                                
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
