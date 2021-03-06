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
##	By Litrin J. 2011/02
##	Website: www.litrin.net
##	Example: android-sdk.appspot.com
##

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
from lib.DataStore import DBCache
from lib.MemCache import CacheXMLSiteMap, CacheTempData, CacheTXTSiteMap
from lib import LoadConfig 
import logging


class xml(webapp.RequestHandler):
    
    def get(self):
        totalPart = CacheXMLSiteMap().getCount()
        
        if (totalPart is None):
            
            pQueue = taskqueue.Queue(name = 'CreateSitemap')
            taskurl = 'http://' + self.request.host_url
            pTask = taskqueue.Task(url='/sitemap.xml/Create', params=dict(url=taskurl))
        
            pQueue.add(pTask)
            logging.info('Task queue started!')
            
            xml = ''
            
        else:
            xml = self.xmlHeader()
            xml += CacheXMLSiteMap().load()
            print x
            xml += "</urlset>\n"
        
        self.response.headers['Content-Type'] = 'application/xml'
        self.response.out.write(xml)
            
    
    def xmlHeader(self):
    
        header = "<?xml version='1.0' encoding='UTF-8'?>\n"
        header += "<?xml-stylesheet type=\"text/xsl\" href=\"/sitemap.xsl\"?>\n"
        header += "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"\n"
        header += "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
        header += "xsi:schemaLocation=\"http://www.sitemaps.org/schemas/sitemap/0.9"
        header += "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd\">\n"
        
        return header

class xmlCreate(webapp.RequestHandler):
    
    PreLoad = 500
    sitemapCacheTime = 60*60*24
    
    def post(self):
        self.get()
    
    def get(self):
        
        self.PreLoad = LoadConfig.getInt('sitemap', 'CountPreLoad')
        finishedCount = CacheTempData().load('tmp_sitemap_finished_count')
        
        if (finishedCount is None):
            finishedCount = 0
        
        print finishedCount
        self.buildTask(int(finishedCount))

    
    def buildTask(self, offSet):

        count = self.buildElement(offSet)
        
        finishedCount = offSet + count
        CacheTempData().save('tmp_sitemap_finished_count', finishedCount)
        
        pQueue = taskqueue.Queue(name = 'CreateSitemap')

        if (count == self.PreLoad):            
            taskurl = 'http://' + self.request.host_url
            pTask = taskqueue.Task(url='/sitemap.xml/Create', params=dict(url=taskurl))
        
            pQueue.add(pTask)
            logging.info('Task queue added!')
            
        else:
            CacheXMLSiteMap().finish()
            pQueue.purge()
            
            logging.info('Purged all temp values.')
            
        #return count

        
    def buildElement(self, offSet):
        
        XMLBody = ''
        
        maxLoadCount = memcache.get('tmp_sitemap_maxload')
        
        if (maxLoadCount is None):
            maxLoadCount = float(DBCache().getMaxHtmlLoad())
            logging.info('Max load count is: ' + str(maxLoadCount))
            
        DBHandle = DBCache.all()
        
        DBHandle.filter("MimeType = ", 'text/html').filter('Number = ', 0).order('-LoadCount')

        i = 0 
        for Query in DBHandle.fetch(self.PreLoad, offSet):
            i += 1
            line="<url>\n"
            line+="\t<loc>" + self.request.host_url + Query.URL + "</loc>\n"

            timeString = str(Query.CreateTime.strftime('%Y-%m-%dT%H:%M:%S-08:00')) 
            line+="\t<lastmod>" + timeString + "</lastmod>\n"
            
            line+="\t<changefreq>weekly</changefreq>\n"
            
            priority = round( Query.LoadCount / maxLoadCount, 2 ) 
            
            if priority < 0.01 :
                priority = 0.01
            
            line+="\t<priority>" + str(priority) + "</priority>\n"
            
            line+="</url>\n"
            
            XMLBody += line
        CacheXMLSiteMap().save(XMLBody)
        return i
        
class txt(webapp.RequestHandler):
    sitemapBody = ''
    def get(self):

        self.PreLoad = LoadConfig.getInt('sitemap', 'CountPreLoad')
        sitemap = CacheTXTSiteMap().load()

        if (sitemap is not None) :
            txt = sitemap
        else:
            txt = self.buildTxt()
            
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(txt)

    
    def buildTxt(self):
       
        offSet = 0
        count = self.buildTxtElement(offSet)
        
        while (count == self.PreLoad):
            offSet += self.PreLoad
            count = self.buildTxtElement(offSet)
            
        CacheTXTSiteMap().finish()
        return self.sitemapBody
        
        
    def buildTxtElement(self, offSet):
        DBHandle = DBCache.all()
        DBHandle.filter("MimeType = ", 'text/html').filter('Number = ', 0).order('-LoadCount').fetch(1000, offSet)
        
        i = 0 
        for Query in DBHandle:
            self.sitemapBody += self.request.host_url + Query.URL  + '\n'
            CacheTXTSiteMap().save(self.sitemapBody)
            
        
        return i
        
class xsl(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/xml'
        
        xsl = '''<xsl:stylesheet version="2.0" xmlns:html="http://www.w3.org/TR/REC-html40" xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
		<html xmlns="http://www.w3.org/1999/xhtml">
			<head>
				<title>XML Sitemap</title>
				<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
				<style type="text/css">

					body {
						font-family:"Lucida Grande","Lucida Sans Unicode",Tahoma,Verdana;
						font-size:13px;
					}
					
					#intro {
						background-color:#CFEBF7;
						border:1px #2580B2 solid;
						padding:5px 13px 5px 13px;
						margin:10px;
					}
					
					#intro p {
						line-height:	16.8667px;
					}
					
					td {
						font-size:11px;
					}
					
					th {
						text-align:left;
						padding-right:30px;
						font-size:11px;
					}
					
					tr.high {
						background-color:whitesmoke;
					}
					
					#footer {
						padding:2px;
						margin:10px;
						font-size:8pt;
						color:gray;
					}
					
					#footer a {
						color:gray;
					}
					
					a {
						color:black;
					}
				</style>
			</head>
			<body>
				<h1>XML Sitemap</h1>
				<div id="intro">
					<p>
						This is a XML Sitemap which is supposed to be processed by search engines like <a href="http://www.google.com">Google</a>, <a href="http://www.bing.com">Bing</a> and <a href="http://www.yahoo.com">YAHOO</a>.<br />

						It was generated using <a href="http://code.google.com/p/zipsite/">zipSite</a> by <a href="http://www.litrin.net/">Litrin Jiang</a>.<br />
						You can find more information about XML sitemaps on <a href="http://sitemaps.org">sitemaps.org</a> and Google's <a href="http://code.google.com/sm_thirdparty.html">list of sitemap programs</a>.
					</p>

				</div>
				<div id="content">
					<table cellpadding="5">
						<tr style="border-bottom:1px black solid;">
							<th>URL</th>
							<th>Priority</th>
							<th>Change Frequency</th>

							<th>LastChange (GMT)</th>
						</tr>
						<xsl:variable name="lower" select="'abcdefghijklmnopqrstuvwxyz'"/>
						<xsl:variable name="upper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
						<xsl:for-each select="sitemap:urlset/sitemap:url">
							<tr>
								<xsl:if test="position() mod 2 != 1">
									<xsl:attribute  name="class">high</xsl:attribute>

								</xsl:if>
								<td>
									<xsl:variable name="itemURL">
										<xsl:value-of select="sitemap:loc"/>
									</xsl:variable>
									<a href="{$itemURL}">
										<xsl:value-of select="sitemap:loc"/>
									</a>
								</td>

								<td>
									<xsl:value-of select="concat(sitemap:priority*100,'%')"/>
								</td>
								<td>
									<xsl:value-of select="concat(translate(substring(sitemap:changefreq, 1, 1),concat($lower, $upper),concat($upper, $lower)),substring(sitemap:changefreq, 2))"/>
								</td>
								<td>
									<xsl:value-of select="concat(substring(sitemap:lastmod,0,11),concat(' ', substring(sitemap:lastmod,12,5)))"/>
								</td>

							</tr>
						</xsl:for-each>
					</table>
				</div>
				<div id="footer">
					Generated with <a href="http://code.google.com/p/zipsite/" title="zipsite">zipsite</a> by <a href="http://www.litrin.net/">Litrin Jiang</a>. This XSLT template is released under GPL.
				</div>

			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>'''
        self.response.out.write(xsl)

def main():
    application = webapp.WSGIApplication([
                ('/sitemap.xsl', xsl),
                ('/sitemap.xml', xml),
                ('/sitemap.xml/Create', xmlCreate),
                ('/sitemap.txt', txt),
                                    
            ], 
        debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
