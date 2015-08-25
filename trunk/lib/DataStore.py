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
##    Website: www.litrin.net
##    Example: android-sdk.appspot.com
##

from google.appengine.ext import db
from lib.MemCache import CacheURL, CacheTempData
import time

class DBCache(db.Model):
    
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    URL = db.StringProperty(multiline=False)
    BlobEntry = db.BlobProperty()
    Number = db.IntegerProperty(default = 0)
    MimeType = db.StringProperty(multiline=False)
    LoadCount = db.IntegerProperty(default = 1)
    
    def save(self, URLString, Entry, MimeType, Number=0):
        
        if (len(Entry) < 1024 * 1024): #GAE limit, 1M object
            DBHandle = DBCache()
            DBHandle.URL = URLString
            DBHandle.BlobEntry = Entry
            DBHandle.Number = Number
            DBHandle.MimeType = MimeType
            DBHandle.put()
            
        else:
            count = 0
            Number = 0
            spliteEntry = ''

            for bit in Entry:
                count += 1
                spliteEntry += str(bit)
                if ( count > 1024*1024*0.9 ):
                    count = 0
                    self.save(URLString, spliteContent, MimeType, Number)
                    
                    Number += 1
                    spliteEntry = ''
                                        
            self.SaveBlob(URLString, spliteContent, MimeType, Number)
            
            CreateTime = time.time()

            Entry = [MimeType, spliteContent, CreateTime]
            
            CacheURL().save(URLString, Entry)
    
    def load(self, URLString):
    
        Entry = CacheURL().load(URLString)
        if (Entry is not None):
            return Entry 
        
        DBHandle = DBCache.all()
        DBHandle.filter("URL = ", URLString).order('Number').fetch(1000)
    
        if(DBHandle.count() == 0):
            return None
            
        else:
            MimeType = ''
            Content = ''

            for Query in DBHandle:
                Content += str(Query.BlobEntry)
                MimeType = str(Query.MimeType)
                CreateTime = time.mktime(Query.CreateTime.timetuple())

                Query.LoadCount = Query.LoadCount + 1
                Query.put()
                
            Entry = [MimeType, Content, CreateTime]
            CacheURL().save(URLString, Entry)

            return Entry
            
    def remove(self, URLString):
        DBHandle = DBCache.all()
        DBHandle.filter("URL = ", URLString).order('Number').fetch(1000)
                
        if(DBHandle.count() == 0):
            return True
            
        else:
            CacheURL().remove(URLString)
            Entry = ''
            
            for Query in DBHandle:
                Entry += str(Query.BlobEntry)
                Query.LoadCount = Query.LoadCount + 1
                Query.delete()
                
            return True

    def flush(self):
        return db.delete(DBCache().all())            

    def getMaxHtmlLoad(self):
        LoadCount = CacheTempData().load('maxHTMLLoad')
        if (LoadCount is not None):
            return float(LoadCount)
            
        DBHandle = DBCache.all()
        DBHandle.filter("MimeType = ", 'text/html').filter('Number = ', 0).order('-LoadCount')
        
        for Query in DBHandle.fetch(1):
            CacheTempData().save('maxHTMLLoad', Query.LoadCount)
            return float(Query.LoadCount)
        
