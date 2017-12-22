##
## Downloads all alerts RSS feeds as listed in feeds_list.csv
##
##  Author  : Manohar Kuse <mpkuse@connect.ust.hk>
##  Created : 12th Oct, 2017
##

import csv
import code
import urllib2
import time
import os

import TerminalColors
tcol = TerminalColors.bcolors()

# All printing functions
import utility_functions as uf

CSV_FILENAME = 'feeds_list.csv'
ALERTS_DB = 'alerts_db/alert_3' #TODO: current time as string append






def make_folder_if_not_exist(folder):
    if not os.path.exists(folder):
        print tcol.OKGREEN, 'Make Directory : ', folder, tcol.ENDC
        os.makedirs(folder)
    else:
        print tcol.WARNING, 'Directory already exists : Not creating :', folder, tcol.ENDC





uf._debug( 'Alerts DB :'+ALERTS_DB )
uf._debug( 'Open file : '+CSV_FILENAME )
make_folder_if_not_exist( ALERTS_DB )


csvReader = csv.reader( open(CSV_FILENAME) )
for row_i, row in enumerate(csvReader):
    uf._printer_('---'+str(row_i))
    uf._debug( 'row : '+str(row), lvl=2 )
    tag = row[0]
    url = row[1]

    alert_id = url.strip().split('/')[-1]
    alert_user_id = url.strip().split('/')[-2]


    uf._printer_G( 'alert_id=%s ; user=%s ; tag=%s' %(alert_id, alert_user_id, tag) )


    # Download
    uf._debug( 'URL:%s' %(url) )
    startTime = time.time()
    response = urllib2.urlopen( url )
    html = response.read()


    # Save to file
    fname = '%s/%s_%s.xml' %(ALERTS_DB, alert_user_id, alert_id)
    uf._debug( 'Save to : %s' %(fname) )
    fp = open( fname, 'w' )
    fp.write( html )
    uf._debug( 'Done')
    uf._report_time( time.time() - startTime )
