import urllib.request as urllib2
import sys
import urllib
from unidecode import unidecode
import re


def validate(url):
    return url and "gist" in url and "raw" in url

def getGist(gistUrl):
    if not validate(gistUrl):
        return "Error: Not a valid URL, only raw gists are allowed"
    try:
        response = urllib2.urlopen(gistUrl)
        data = response.read()
    except urllib2.URLError as e:
        return "Error: "+e.reason
    if len(data) > 5000:
        return "Error: only 5k of code is allowed"
    return data.decode('utf8')
