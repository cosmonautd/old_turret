import urllib2
import socket

def internet_on():
    try:
        response=urllib2.urlopen('https://duckduckgo.com',timeout=0.5)
        return True
    except: pass
    return False
