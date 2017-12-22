""" Downloads article contents given an URL

        The main will query mongodb to get list of urls, where I do not
        have full article. I use the popular goose package
        to download and parse articles.

        https://github.com/grangier/python-goose

"""

from goose import Goose
import pymongo
import code
import time

import utility_functions as uf


# url = 'http://eng.belta.by/society/view/belarusian-buyers-of-geely-cars-promised-subsidies-107864-2017/'
# url = 'https://weekherald.com/2017/12/20/somewhat-favorable-media-coverage-somewhat-unlikely-to-impact-huaneng-power-international-hnp-stock-price.html'
# g = Goose()
# article = g.extract( url=url )
#
# article.title
# article.cleaned_text
# code.interact( local=locals() )
# quit()
#
# Setup MongoDB
try:
    conn = pymongo.MongoClient()
    print 'MongoDB Connected!'
except e:
    print 'Failured: ', str(e)
    quit()

db = conn.sun_dance


#
# Setup Parser (Goose)
g = Goose({'http_timeout': 5, 'browser_user_agent': 'Mozilla'})

total_items =db.news_data.find({ "full_article_text": {"$exists": False} } ).count()
print 'Total Items: ', total_items

i=1
for d in db.news_data.find({ "full_article_text": {"$exists": False} } ):
    # print d
    # code.interact( local=locals() )

    print '---%d of %d---' %(i,total_items)
    i+= 1
    startTime = time.time()
    print 'Alert on   :', d['alert_title']
    print '_id        :', str(d['_id'])
    print 'news_id    :', d['news_id']
    print 'uuid       :', d['uuid']
    print 'Downloading: ', d['url']

    try:
        with uf.Timeout(5):
            article = g.extract( url=d['url'])
            print 'article.title       :', article.title
            print 'article.domain      :', article.domain
            # print article.cleaned_text
            print 'article.publish_date:', article.publish_date

            new_data = {}
            new_data['full_article_title'] = article.title
            new_data['full_article_text'] = article.cleaned_text
            new_data['full_article_domain'] = article.domain
            new_data['full_article_publish_date'] = article.publish_date
            # code.interact( local=locals() )
    except uf.Timeout.Timeout:
        print '[ERROR] Timeout. This item (uuid=%s) will be empty' %( d['uuid'] )
        new_data = {}
        new_data['full_article_title'] = ""
        new_data['full_article_text'] = ""
        new_data['full_article_domain'] = ""
        new_data['full_article_publish_date'] = ""

    db.news_data.find_one_and_update( {"_id": d['_id']}, { "$set": new_data } )
    print 'Done in %4.2fs' %(time.time() - startTime)
