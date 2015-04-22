import urllib2
import socket

def internet_on():
    try:
        response=urllib2.urlopen('https://duckduckgo.com',timeout=0.2)
        return True
    except urllib2.URLError as err: pass
    except socket.timeout as err: pass
    return False
