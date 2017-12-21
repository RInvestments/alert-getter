""" This class give access functions for google-alerts.

    This class is based on
    a) alertshtml_to_csv.py --> Give google-alerts html page returns a csv with corresponding RSS feed URLS
    b) download_alerts.py --> Given the csv file downloads all alerts and saves to file
    c) test_xml.py --> Opens the XML file


        Author  : Manohar Kuse <mpkuse@connect.ust.hk>
        Created : 8th Dec, 2017
"""

import csv
import code
import urllib2
import time
import os
import glob
import re
import urlparse

import uuid
import pymongo
import collections
import json
from bs4 import BeautifulSoup
from datetime import datetime


import TerminalColors
tcol = TerminalColors.bcolors()

# All printing functions
import utility_functions as uf


class AlertDownloader:
    def __debug( self, msg, lvl=0 ):
        if lvl in self.verbosity:
            print tcol.WARNING, '[DEBUG=%d] %s' %(lvl,msg) , tcol.ENDC

    def __error( self, msg ):
        print tcol.FAIL, msg, tcol.ENDC

    def __printerG( self, msg ):
        print tcol.OKGREEN, msg, tcol.ENDC
    def __printerB( self, msg ):
        print tcol.OKBLUE, msg, tcol.ENDC

    def __init__(self, ALERTS_DB, feeds_list_csv=None, feeds_list_html=None, verbosity=0 ):
        self.verbosity = range(verbosity)
        self.ALERTS_DB = ALERTS_DB

        # Setup DB access and file accesses
        self.client = pymongo.MongoClient()
        self.db = self.client.sun_dance

        ########
        if feeds_list_html is not None and feeds_list_csv is None:
            # Assume that html file name is provided
            self.__debug( 'Assume that html file name is provided', lvl=2 )

            self.rss_feed_list = self._alertshtml_to_list( feeds_list_html )
            return



        ########
        if feeds_list_html is None and feeds_list_csv is not None:
            # Assume a CSV file name is provided
            self.__debug( 'Assume a CSV file name is provided', lvl=2 )

            self.rss_feed_list = self._alertscsv_to_list( feeds_list_csv )
            return

        self.__error( "Need to provide alert list either as CSV or as HTML" )







    def _alertshtml_to_list( self, input_html_file ):
        """ Returns a list like : [ (tag1,url1), (tag2,url2), ..., (tagn,urln)] """
        self.__debug( 'Input File (HTML) : '+ input_html_file, lvl=1 )
        try:
            soup = BeautifulSoup( open(input_html_file).read() , "lxml")
        except IOError:
            self.__error( 'Cannot open file: %s' %(input_html_file) )
            return None

        alerts_soup = soup.find( "div", {"id": "manage-alerts-div"})
        if alerts_soup is None:
            self.__error( "No div with id:manage-alerts-div. Probably invalid html.\nhttps://www.google.com/alerts. Just Ctrl+S this page from browser " )
            return None

        all_li = alerts_soup.findAll( "li" )
        if len(all_li) < 1:
            self.__error( "No Alerts")
            return None


        # fp_out = open( output_csv, 'w' )
        out_list = []
        for li in all_li:
            tag_text = li.find( "div", {"class":"query_div"} ).get_text().strip()
            rss_url = li.find( "a" )['href']

            self.__debug( '---', lvl=2 )
            self.__debug( 'tag     : '+ tag_text, lvl=2 )
            self.__debug( 'rss_url : '+ rss_url, lvl=2 )

            out_list.append( (tag_text,rss_url) )

            # fp_out.write( "%s,%s\n" %(tag_text, rss_url) )
        # fp_out.close()
        self.__debug( 'List contains %d alert-items' %(len(out_list)) )
        return out_list

    def _alertscsv_to_list( self, input_csv_file ):
        """ Returns a list like : [ (tag1,url1), (tag2,url2), ..., (tagn,urln)] """
        self.__debug( 'Input File (CSV) : '+ input_csv_file, lvl=1 )

        try:
            csvReader = csv.reader( open(input_csv_file) )
        except IOError:
            self.__error( 'Cannot Load file: ', input_csv_file)
            return None
        except:
            self.__error( 'Invalid CSV')
            return None

        # loop on csv file, expect 2 cols in every row
        out_list = []
        for row_i, row in enumerate(csvReader):
            if len(row) != 2:
                return None
            self.__debug( str( row ), lvl=2 )
            out_list.append( (row[0], row[1]) )

        return out_list


    def _make_folder_if_not_exist(self, folder):
        if not os.path.exists(folder):
            print tcol.OKGREEN, 'Make Directory : ', folder, tcol.ENDC
            os.makedirs(folder)
        else:
            print tcol.WARNING, 'Directory already exists : Not creating :', folder, tcol.ENDC



    def download_alerts( self ):
        """ Will download all the alerts as separate XML file """
        ALERTS_DB = self.ALERTS_DB
        self.__debug( 'ALERTS_DB='+ALERTS_DB, lvl=1 )
        self._make_folder_if_not_exist( ALERTS_DB )
        for (tag,url) in self.rss_feed_list:
            alert_id = url.strip().split('/')[-1]
            alert_user_id = url.strip().split('/')[-2]

            # print tag
            # print 'download : ', url
            self.__printerG( 'alert_id=%s ; user=%s ; tag=%s' %(alert_id, alert_user_id, tag) )

            self.__debug( 'URL:%s' %(url), lvl=0 )
            startTime = time.time()
            response = urllib2.urlopen( url )
            html = response.read()


            # Save to file
            fname = '%s/%s_%s.xml' %(ALERTS_DB, alert_user_id, alert_id)
            self.__debug( 'Save to : %s' %(fname), lvl=0 )
            self.__printerB( 'Save to : %s' %(fname) )
            fp = open( fname, 'w' )
            fp.write( html )
            print 'Done in %4.2fs' %( time.time() - startTime )


    def insert_into_db( self ):
        ALERTS_DB = self.ALERTS_DB

        ntotal_fails = 0
        ntotal_success = 0
        for l in glob.glob( ALERTS_DB+'/*_*.xml' ):
            self.__debug( 'Open XML file: %s' %(l) )

            meta, alertinfo_list = self._parse_alert_xml( l )
            self.__debug( '---' )
            self.__debug( 'File contains %d ALERTs on %s' %( len(alertinfo_list),  meta['alert_title'] ), lvl=2 )

            self.__printerG( 'File contains %d ALERTs on %s' %( len(alertinfo_list),  meta['alert_title'] ) )

            n_fails = 0
            n_success = 0
            for news_item in alertinfo_list:
                R = {}

                R['alert_title'] = meta['alert_title']
                R['alert_id'] = meta['alert_id']
                R['alert_user_id'] = meta['alert_user_id']

                R['news_id'] = news_item['id']
                R['news_title'] = news_item['title']
                R['one_line'] = news_item['one_line']
                R['published'] = news_item['published']
                R['updated_on'] = news_item['updated_on']
                R['url'] = news_item['news_url']

                # code.interact( local=locals() )
                self.__debug( '- %s' %( R['news_title'] ), lvl=2 )

                # TODO
                #db.insert( R )

                status = self._add_to_db( R )
                if status is True:
                    n_success += 1
                    ntotal_success += 1
                else:
                    n_fails += 1
                    ntotal_fails += 1

            self.__printerG( 'n_success: %d; n_fails: %d' %(n_success, n_fails))
        self.__printerG( 'ntotal_success: %d; ntotal_fails: %d' %(ntotal_success, ntotal_fails))

    def _parse_alert_xml( self, XML_FILE ):
        soup = BeautifulSoup( open(XML_FILE).read() , "lxml")

        title = soup.find( 'title' ).text
        # print 'Title : ', title.split( '-')[-1].strip()

        self_url = soup.find( 'link')['href']
        alert_id = self_url.strip().split('/')[-1]
        alert_user_id = self_url.strip().split('/')[-2]
        # print 'self_url', self_url
        # print 'alert_id', alert_id
        # print 'alert_user_id', alert_user_id

        all_entries = soup.findAll( 'entry' )
        # print 'nEntries : ', len(all_entries)
        F={}
        F['alert_title'] = title.split( '-')[-1].strip()
        F['alert_url'] = self_url
        F['alert_id'] = alert_id
        F['alert_user_id'] = alert_user_id
        F['n_alerts'] = len(all_entries)


        E = []
        for entry in all_entries:
            # print '---'


            title = uf.strip_tags( entry.find( 'title').get_text() )
            news_id = entry.find( 'id').text.split(':')[-1].strip()
            published_on = entry.find( 'published' ).get_text()
            updated_on = entry.find( 'updated').get_text()
            one_line = uf.strip_tags( entry.find( 'content' ).get_text() )

            # print 'title : ', title
            # print 'id    : ', news_id
            # print 'published : ', published_on
            # print 'updated_on: ', updated_on
            # print 'one_line  : ', one_line

            raw_url = entry.find( 'link')['href']
            # print 'raw   : ', raw_url

            news_url = uf.strip_google_redirect( raw_url )
            # print '\nnews_url: ', news_url

            e = {}
            e['title'] = title
            e['id'] = news_id
            e['published'] = published_on
            e['updated_on'] = updated_on
            e['one_line'] = one_line
            e['news_url'] = news_url
            E.append( e )

        # F: Alert Info
        # E: Each alert entry
        return F, E

    def _get_uuid( self,cur_dict ):
        od = collections.OrderedDict(sorted(cur_dict.items()))

        json_data_obj =  json.dumps(od)
        digest = uuid.uuid3(uuid.NAMESPACE_DNS, json_data_obj)
        return str(digest)

    def _add_to_db( self, cur_dict ):
        cur_dict['uuid'] = self._get_uuid( cur_dict )
        ###########################
        #### MongoDB Insertion ####
        ###########################

        try:
            cur_dict['last_modified'] = datetime.now()
            self.db.news_data.insert( cur_dict )
            return True
        except pymongo.errors.DuplicateKeyError, e:
            # Dup licate'
            self.__debug( str(e), lvl=4 )
            self.__debug( tcol.FAIL + 'DuplicateKeyError' + tcol.ENDC, lvl=3 )
            return False
        except Exception as e:
            #TODO catch the `Duplicate key insertion`. This denotes this data already exists
            self.__debug( str(e)  )
            self.__debug( tcol.FAIL+ 'MOngoDB insert failed'+ tcol.ENDC, lvl=3 )
            return False


if __name__ == "__main__":
    date_str = datetime.today().strftime( '%Y%m%d' )
    ob = AlertDownloader( ALERTS_DB='alerts_db/alert_%s' %(date_str), feeds_list_html='google-alerts.html', verbosity=3 )
    # ob = AlertDownloader( feeds_list_csv='feeds_list.csv', verbosity=3 )
    # ob = AlertDownloader( feeds_list_html='/home/mpkuse/Music/a.html', verbosity=3 )

    ob.download_alerts( )
    ob.insert_into_db()
