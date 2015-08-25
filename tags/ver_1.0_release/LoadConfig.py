#!/bin/env python
##
##	This is a project for Google App Engine 
##		that support create a webisite by ZIP packages!
##
##	By Litrin J. 2011/03
##	Website: www.litrin.net
##	Example: android-sdk.appspot.com
##

import ConfigParser, os

class Config:

    ConfigFilename = "website.cfg"
    ConfigTitle = "zipsite"
    
    __configFile = None
    
    def __init__ (self, FileName = None, Title = None, Setting = None):

        if (os.path.exists(FileName)):
            self.ConfigFilename = FileName
        if (Title is not None):
            self.ConfigTitle = Title

        self.__configFile = open(self.ConfigFilename, 'r')		
     
        
    def __del__(self):
        self.__configFile.close()
        

    def Get (self, Setting):

        config = ConfigParser.ConfigParser()
        config.readfp(self.__configFile)

        value = config.get(self.ConfigTitle, Setting)
        return value
        
    def getStr(self, Setting):
        return str(self.Get(Setting))
        
    def getInt(self, Setting):
        return int(self.Get(Setting))