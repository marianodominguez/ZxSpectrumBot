import urllib.request as urllib2
import sys
import urllib
from unidecode import unidecode
import re


def validate(url):
    return "https://gist.githubusercontent.com" in url

def getGist(gistUrl):
    if not validate(gistUrl):
        return "Error: Not a valid URL"
    try:
        response = urllib2.urlopen(gistUrl)
        data = response.read()
    except urllib2.URLError as e:
        return "Error: "+e.reason
    if len(data) > 5000:
        return "Error: only 5k of code is allowed"
    return data.decode('utf8')

if __name__ == "__main__":
    result = getGist('https://gist.githubusercontent.com/marianodominguez/b4e4cf03b821d4e48bea064c4fa73574/raw/da7dd97991cec4f7aaa3496dcf2b09693c0b749d/moire2.bas')
    exp = "{\w*(?:}\s*)" #{anything till } plus trailing whitespace
    basicode = re.sub(exp,'',result)
    print(basicode)