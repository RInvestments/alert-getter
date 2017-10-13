## Given an XML file (from google alerts RSS) print out its data

from bs4 import BeautifulSoup
import urlparse
import re

def strip_google_redirect( raw_url ):
    parsed = urlparse.urlparse(raw_url)
    xurl=urlparse.parse_qs(parsed.query)['url']
    return xurl[0]

def strip_tags( raw_text ):
    data = re.sub( r'<.*?>', '', raw_text )
    return data

XML_FILE = 'alerts_db/alert_2/12484028930340680223_1652318492771626812.xml'

soup = BeautifulSoup( open(XML_FILE).read() , "lxml")

title = soup.find( 'title' ).text
print 'Title : ', title.split( '-')[-1].strip()

all_entries = soup.findAll( 'entry' )
print 'nEntries : ', len(all_entries)

for entry in all_entries:
    print '---'
    title = strip_tags( entry.find( 'title').get_text() )
    news_id = entry.find( 'id').text.split(':')[-1].strip()
    published_on = entry.find( 'published' ).get_text()
    updated_on = entry.find( 'updated').get_text()
    one_line = strip_tags( entry.find( 'content' ).get_text() )

    print 'title : ', title
    print 'id    : ', news_id
    #print 'published : ', published_on
    #print 'updated_on: ', updated_on
    #print 'one_line  : ', one_line

    raw_url = entry.find( 'link')['href']
    # print 'raw   : ', raw_url

    news_url = strip_google_redirect( raw_url )
    #print '\nnews_url: ', news_url
