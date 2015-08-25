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

from google.appengine.api import memcache
import logging
import pickle
from lib import LoadConfig

class MemCache():
    
    Lable = ''
    Time = 0

    def save(self, key, Entry):
        memcacheKey = self.getKeyName(key)
    
        if(Entry == None):
            logging.info('Entry is None!')
            
            return True
        
        else:
            Entry = pickle.dumps(Entry)
            if(len(Entry) < 1024*1024):
                memcache.add( memcacheKey, Entry, self.Time )
                logging.info(memcacheKey + ' cached!')

                return True
            else:
                logging.info(memcacheKey + ' too big to save in memcache!')
        
                return False
        
    def load(self, key):
        memcacheKey = self.getKeyName(key)
        Value = memcache.get(memcacheKey)
        if (Value == None):
            return None
            
        return pickle.loads(memcache.get(memcacheKey))

    def remove(self, key):
        memcache.delete(self.getKeyName(key))
        
    def removeAll(self):
        memcache.flush_all()
        
    def getKeyName(self, key):
        return self.Lable + key
        


class CacheURL(MemCache):
    Lable = 'URL_Cache:'
    Time = LoadConfig.getInt('zipsite', 'MemcacheTime')

    
class CacheTempData(MemCache):
    Lable = 'TempValue:'
    Time = 900

    
class CacheSiteMap:
    Lable = ''
    
    Time = LoadConfig.getInt('sitemap', 'MemcacheTime')
    PartCount = 1
    
    def __init__(self):
        self.getCount()
        
    def save(self, Data):
        key = self.Lable + '_' + str(self.PartCount)
        
        try:
            memcache.add( key, Data, self.Time )
            logging.info(key + ':' + Data)
            self.countAdd()
            return True
        except:
            return False
            
    def load(self):
        loop = 0
        sitemapBody = ''
        
        while (loop <= self.PartCount):
            print str(loop) + '<= ' + str(self.PartCount)
            key = self.Lable + '_' + str(loop)
            print key
            sitemapPart = memcache.get(key)
            
            if (sitemapPart is None):
                sitemapPart = ''
                
            sitemapBody += sitemapPart
            loop += 1
        return sitemapBody

        
    def getCount(self):
        key = self.Lable + '_part_count:'
        count = memcache.get(key)
        
        if (count is not None):
            self.PartCount = int(count)
            return self.PartCount
        else:
            return None
            
    def countAdd(self):
        count = self.PartCount + 1
        memcache.add( self.Lable + '_part_count:', count, self.Time )
        
    def remove(self, Part = 0 ):
        if (Part == 0 ):
            loop = 1
            sitemapBody = ''
            while (loop < self.PartCount):
                key = self.Lable + str(loop)
                loop += 1
                memcache.delete(key)
        else:
            key = self.Lable + str(Part)
            memcache.delete(key)
    
    def finish(self):
        memcache.delete(self.Lable + '_part_count:')

class CacheXMLSiteMap(CacheSiteMap):
    Lable = 'sitemap.xml'
    
class CacheTXTSiteMap(CacheSiteMap):
    Lable = 'sitemap.txt'
