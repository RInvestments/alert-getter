
import TerminalColors
tcol = TerminalColors.bcolors()
import re
import urlparse

#################### Printer functions ################
MY_NAME = ''

def strip_google_redirect( raw_url ):
    parsed = urlparse.urlparse(raw_url)
    xurl=urlparse.parse_qs(parsed.query)['url']
    return xurl[0]

def strip_tags( raw_text ):
    data = re.sub( r'<.*?>', '', raw_text )
    return data

def _printer( txt ):
    print tcol.OKBLUE, 'download_alerts :', tcol.ENDC, txt

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
        print tcol.OKBLUE, 'download_alerts (Debug=%2d) :' %(lvl), tcol.ENDC, txt

def _error( txt ):
    """ """
    print tcol.FAIL, 'download_alerts (Error) :', tcol.ENDC, txt

def _report_time( txt ):
    print tcol.OKBLUE, 'download_alerts (time) :', tcol.ENDC, '%4.2f sec' %(txt)
########################################################
