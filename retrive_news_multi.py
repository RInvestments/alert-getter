""" This script is the main handle to retrive google-alerts. After all the alerts
    are retrived, this script will also fetch the text data (cleaned with py-goose)
    from the URLs. It is all stored inside a mongodb

    Runs the code every day auto-magically

    Author  : Manohar Kuse <mpkuse@connect.ust.hk>
    Created : 22nd Dec, 2017 (Winter Solstice)
"""
import time
import pymongo
import json
from datetime import datetime
import shutil
import os

from goose import Goose
import code

from AlertDownloader import AlertDownloader
import TerminalColors
tcol = TerminalColors.bcolors()

# All printing functions
import utility_functions as uf

### PARAMS
ALERTS_DB_BASE = 'alerts_db/alert'
feeds_list_html = 'google-alerts.html'
repeat_every_sec = 86400 # 86400 = 24 * 60 * 60 (sec in 1 day)
### END PARAMS

def init_mongodb():
    # Setup MongoDB
    try:
        mongodb_uri = os.environ['MONGODB_NEWSRETRIVER_URI']
        conn = pymongo.MongoClient()
        print 'MongoDB Connected!', mongodb_uri
        db = conn.sun_dance
        return db
    except Exception as e:
        print 'Failed to connect to mongodb: ', str(e)
        quit()



def get_news_from_url():
    """ This function finds all news items from mongodb which do not have a
        full text. It then downloads full text for all such items"""

    # Parser setup
    g = Goose({ 'browser_user_agent': 'Mozilla'})

    total_items =db.news_data.find({ "full_article_text": {"$exists": False} } ).count()
    uf._printer_G( 'Total Items to retrive: %d' %( total_items ) )
    i=1
    for d in db.news_data.find({ "full_article_text": {"$exists": False} } ):
        # print d
        # code.interact( local=locals() )

        uf._printer_G( '---%d of %d---' %(i,total_items) )
        i+= 1
        startTime = time.time()
        #TODO, only print _id and uuid. As we add more alert sources in addition
        #       to google-alerts. We may or may not have titles from them. Possibly
        #       only have the urls
        print '_id        :', str(d['_id'])
        print 'uuid       :', d['uuid']
        print 'Downloading: ', d['url']
        print 'Alert on   :', d['alert_title'] #consider not printering this
        print 'news_id    :', d['news_id'] #consider not printering

        new_data = {}
        new_data['full_article_title'] = ""
        new_data['full_article_text'] = ""
        new_data['full_article_domain'] = ""
        new_data['full_article_publish_date'] = ""
        try:
            with uf.Timeout(5):
                article = g.extract( url=d['url'])
                print 'article.title       :', article.title
                print 'article.domain      :', article.domain
                # print article.cleaned_text
                print 'article.publish_date:', article.publish_date


                new_data['full_article_title'] = article.title
                new_data['full_article_text'] = article.cleaned_text
                new_data['full_article_domain'] = article.domain
                new_data['full_article_publish_date'] = article.publish_date
                # code.interact( local=locals() )
        except uf.Timeout.Timeout:
            print '[ERROR] Timeout. This item (uuid=%s) will be empty' %( d['uuid'] )
        except:
            print 'py-goose retrival failed!'


        db.news_data.find_one_and_update( {"_id": d['_id']}, { "$set": new_data } )
        uf._printer_( 'Done in %4.2fs' %(time.time() - startTime) )



db = init_mongodb()
run = 0
while True:
    startTimerun = time.time()

    #
    # Retrive google-alerts
    #
    date_str = datetime.today().strftime( '%Y%m%d' )
    storage_folder = '%s_%s' %(ALERTS_DB_BASE, date_str)
    ob = AlertDownloader( ALERTS_DB=storage_folder, feeds_list_html=feeds_list_html, verbosity=1 )
    ob.download_alerts( )
    ob.insert_into_db( db )


    #
    # More Alert Sources (future work)
    #   As we have more sources for alerts, they will go here. These will basically
    #   put urls in mongodb in db.sun_dance.news_data. Try and have similar interface to
    #   google-alerts
    #



    #
    # URL Loop - Loop over all the items in mongodb which do not have full text of
    #   articles
    #
    uf._printer_G( '+++++\n +++++ Start www crawl\n +++++')
    get_news_from_url()
    run_done_in = time.time() - startTimerun
    uf._printer_( 'Run#%d completed in %4.2f sec on %s' %(run, run_done_in, str(datetime.now()) ) )
    run = run + 1
    sleep_for = repeat_every_sec - run_done_in
    if sleep_for > 0:
        uf._printer_( 'Sleeping....zZzz for %4.2f sec' %(sleep_for))
        time.sleep( sleep_for )


    #
    # Delete Raw files
    #
    uf._printer_( 'rm -rf %s' %(storage_folder) )
    shutil.rmtree( storage_folder )
