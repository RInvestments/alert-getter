##
## Given the html page https://www.google.com/alerts. Just Ctrl+S this page from browser (I used chrome).
## This script creates the CSV file with alert URLs, similar to:
##          1211.HK,https://www.google.com/alerts/feeds/12484028930340680223/18373879088255811446
##                      .
##                      .
##          2333.HK,https://www.google.com/alerts/feeds/12484028930340680223/4808286786322570403
##          BYD,https://www.google.com/alerts/feeds/12484028930340680223/13893697923936634468
##
##
##  Author  : Manohar Kuse <mpkuse@connect.ust.hk>
##  Created : 13th Oct, 2017
##
from bs4 import BeautifulSoup
import utility_functions as uf

input_html_file = 'google-alerts.html'
output_csv = input_html_file+'.csv' #'feed_list_ejcbsdhansbn.csv'
uf._printer_Y( 'Input File  : '+ input_html_file )
uf._printer_Y( 'Output File : '+ output_csv )


soup = BeautifulSoup( open(input_html_file).read() , "lxml")
alerts_soup = soup.find( "div", {"id": "manage-alerts-div"})
if alerts_soup is None:
    uf._error( "No div with id:manage-alerts-div.\nQuit---" )
    quit()

all_li = alerts_soup.findAll( "li" )
if len(all_li) < 1:
    uf._error( "No Alerts\nQuit-----")
    quit()


fp_out = open( output_csv, 'w' )

for li in all_li:
    tag_text = li.find( "div", {"class":"query_div"} ).get_text().strip()
    rss_url = li.find( "a" )['href']

    uf._printer_( '---' )
    uf._printer_( ' tag     : '+ tag_text )
    uf._printer_G( 'rss_url : '+ rss_url )

    fp_out.write( "%s,%s\n" %(tag_text, rss_url) )
fp_out.close()

uf._printer_G( "Done!")
