#!/bin/env python
##
##	This is a project for Google App Engine 
##		that support create a webisite by ZIP packages!
##
##	By Litrin J. 2011/02
##	Website: www.litrin.net
##	Example: android-sdk.appspot.com
##

from google.appengine.ext import db

class DBCache(db.Model):
    
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    URL = db.StringProperty(multiline=False)
    BlobEntry = db.BlobProperty()
    Number = db.IntegerProperty(default = 0)
    MimeType = db.StringProperty(multiline=False)
    LoadCount = db.IntegerProperty(default = 1)
    
    def SaveBlob(self, URL, Entry, MimeType, Number=0):
        
        if (len(Entry) < 1024*1024):
            DBHandle = DBCache()
            DBHandle.URL = URL
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
                if (count > 1024*1024*0.9):
                    count = 0
                    self.SaveBlob(URL, spliteEntry, MimeType, Number)
                    Number += 1
                    spliteEntry = ''
                                        
            self.SaveBlob(URL, spliteEntry, MimeType, Number)
                        
    
    def Load(self, URL):
        DBHandle = DBCache.all()
        DBHandle.filter("URL = ", URL).order('Number').fetch(1000)
    
        if(DBHandle.count() == 0):
            return None
        else:
            Entry = ''
            for Query in DBHandle:
                Entry += str(Query.BlobEntry)
                Query.LoadCount = Query.LoadCount + 1
                Query.put()

        return Entry