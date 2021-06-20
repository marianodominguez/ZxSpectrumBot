import urllib2
import sys
import urllib

def getGist(gistUrl):
    if not "https://gist.githubusercontent.com" in gistUrl:
        return "Error: Not a valid URL"
    try:
        response = urllib2.urlopen(gistUrl)
        data = response.read()
    except urllib2.URLError, e:
        return "Error: "+e.reason
    if len(data) > 2000:
        return "Error: only 2k of code is allowed"
    return data
    
if __name__ == "__main__":
    print getGist(sys.argv[1])
