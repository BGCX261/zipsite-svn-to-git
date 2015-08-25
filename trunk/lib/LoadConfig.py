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
##	This is a project for Google App Engine 
##		that support create a webisite by ZIP packages!
##
##	By Litrin J. 2011/03
##	Website: www.litrin.net
##	Example: android-sdk.appspot.com
##

import ConfigParser, os

CONFIG_FILE = 'zipSite.cfg'

def Get (ConfigTitle, Setting):
    global CONFIG_FILE
    ConfigFile = open(CONFIG_FILE, 'r')

    config = ConfigParser.ConfigParser()
    config.readfp(ConfigFile)
    value = config.get(ConfigTitle, Setting)
    ConfigFile.close()
    return value
        
def getStr(ConfigTitle, Setting):
    return str(Get(ConfigTitle, Setting))
        
def getInt(ConfigTitle, Setting):
    return int(Get(ConfigTitle, Setting))
