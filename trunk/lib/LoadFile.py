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

from zipfile import ZipFile
from lib.DataStore import DBCache
from lib import LoadConfig
from lib import MimeType
import os
import logging
import time

class NoCached:

    WebsiteFilePath = LoadConfig.getStr('zipsite', 'WebsiteFilePath')

    def load(self, URLString, cache=True):
        Content = self.loadUnZipFile(URLString)
        
        if ( Content is None):
            Content = self.loadZipFile(URLString)
        
        if ( Content is None):
            raise NameError, URLString
        
        sMimeType = MimeType.get(URLString)
        CreateTime= time.time()

        if (cache):
            DBHandle = DBCache()
            DBHandle.save(URLString, Content, sMimeType)
         
            return [sMimeType, Content, CreateTime]
        
    def loadZipFile(self, URLString):
    #Load the file from zip files. This is the core function!
        lFilename = URLString.split('/')
        iPathLevel = 1
        #Loop count, The dir layers

        Content = None
        while(iPathLevel <= len(lFilename)):
        #Get the zip file name and the filename from the URL, support muli-layer    
            sFilePath = os.getcwd() + self.WebsiteFilePath
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
                    Content = ZipFileHandle.read(sFileName)
                    ZipFileHandle.close()
                    logging.info(sFileName + " in " + sZipFilename + " Loaded!")
                    break
                    
                except:
                    logging.error('No found ' + URLString + '!')
        
            iPathLevel +=1
        
        return Content
    
    def loadUnZipFile(self, URLString):
        
        sRealFileName = os.getcwd() + self.WebsiteFilePath + URLString
        Content = None
        
        if (os.path.exists(sRealFileName)):
        #If the file not be ziped, read it drictory    
            fNoZipedFile = open(sRealFileName, 'r')
            Content = fNoZipedFile.read()
            fNoZipedFile.close()
            logging.info("Load: " + URLString + " From unziped file")
            
        return Content
