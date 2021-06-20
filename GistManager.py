import url2

def getGist(url):
    if not "https://gist.githubusercontent.com" in url:
        return "Error: Not a valid URL"
