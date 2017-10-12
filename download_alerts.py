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

CSV_FILENAME = 'feeds_list.csv'
ALERTS_DB = 'alerts_db/alert_' #TODO: current time as string append



#################### Printer functions ################
MY_NAME = 'download_alerts'
def _printer( txt ):
    print tcol.OKBLUE, MY_NAME,' :', tcol.ENDC, txt

def _printer_Y( txt ):
    print tcol.WARNING, txt, tcol.ENDC
def _printer_G( txt ):
    print tcol.OKGREEN, txt, tcol.ENDC
def _printer_( txt ):
    print txt


def _debug( txt, lvl=0 ):
    """ """
    to_print = [0,1]
    if lvl in to_print:
        print tcol.OKBLUE, MY_NAME,'(Debug=%2d) :' %(lvl), tcol.ENDC, txt

def _error( txt ):
    """ """
    print tcol.FAIL, MY_NAME,'(Error) :', tcol.ENDC, txt

def _report_time( txt ):
    print tcol.OKBLUE, MY_NAME,'(time) :', tcol.ENDC, '%4.2f sec' %(txt)
########################################################



def make_folder_if_not_exist(folder):
    if not os.path.exists(folder):
        print tcol.OKGREEN, 'Make Directory : ', folder, tcol.ENDC
        os.makedirs(folder)
    else:
        print tcol.WARNING, 'Directory already exists : Not creating :', folder, tcol.ENDC





_debug( 'Alerts DB :'+ALERTS_DB )
_debug( 'Open file : '+CSV_FILENAME )
make_folder_if_not_exist( ALERTS_DB )


csvReader = csv.reader( open(CSV_FILENAME) )
for row in csvReader:
    _printer_('---')
    _debug( 'row : '+str(row), lvl=2 )
    tag = row[0]
    url = row[1]

    alert_id = url.strip().split('/')[-1]


    _printer_G( 'alert_id=%s ; tag=%s' %(alert_id, tag) )


    # Download
    _debug( 'URL:%s' %(url) )
    startTime = time.time()
    response = urllib2.urlopen( url )
    html = response.read()


    # Save to file
    fname = '%s/%s.xml' %(ALERTS_DB, alert_id)
    _debug( 'Save to : %s' %(fname) )
    fp = open( fname, 'w' )
    fp.write( html )
    _debug( 'Done')
    _report_time( time.time() - startTime )
