# tweepy-bots/bots/config.py
from Backend import Backend
import logging
import re
import os
from unidecode import unidecode
import GistManager

logger = logging.getLogger()

def determine_config(full_text, gistUrl):
    config={}
    config['error']=None
    #remove all @ mentions, leaving just the BASIC code
    basiccode = re.sub('(@.+?\s)+','',full_text, re.ASCII)
    basiccode = unidecode(basiccode)
    #unescape >, <, and &
    basiccode = basiccode.replace("&lt;", "<")
    basiccode = basiccode.replace("&gt;", ">")
    basiccode = basiccode.replace("&amp;", "&")
    #replace typogrphical quotes
    lead_double = u"\u201c"
    follow_double = u"\u201d"
    lead_single = u"\u2018"
    follow_single = u"\u2019"
    basiccode = basiccode.replace(lead_double, '"')
    basiccode = basiccode.replace(follow_double, '"')
    basiccode = basiccode.replace(lead_single, "'")
    basiccode = basiccode.replace(follow_single, "'")

    #if url, get code from it
    if gistUrl:
        text = GistManager.getGist(gistUrl)
        if text.startswith("Error: "):
            logger.info(f"unable to retrieve {gistUrl}, {text}")
            config['error']=text
            return config
        else:
            basiccode = unidecode(text)
    #by default, debug this does not spam as we are using hashtag
    config['debug'] = True

    #look for start time command
    exp = "{.*[Bb](\d\d?).*}" # {B\d\d  B= Begin
    result = re.search(exp,basiccode)
    if result:
        starttime = int(result.group(1))
        logger.info(f" Requests start at {starttime} seconds")
    else:
        starttime = 0

    #look for length of time to record command
    exp = "{.*[Ss](\d\d?).*}" # {S\d\d  S= Seconds to record
    result=re.search(exp,basiccode)
    if result:
        recordtime = int(result.group(1))
        logger.info(f" Requests record for {recordtime} seconds")
    else:
        recordtime = 30 #it seems shorter times kill the video
        logger.info(f" default for {recordtime} seconds")
    if recordtime <=1:
        recordtime=5

    exp = "{.*[Xx](\d\d?\d?).*}" # {X\d\d  X= Xelerate speed 1-20
    speed=1
    result=re.search(exp,basiccode)
    if result:
        speed = int(result.group(1))
        logger.info(f" Accelerate {speed*100} %")
    if speed>999: speed=999
    if speed<1: speed=1

    language = 0 # default to BASIC

    exp = "{.*[Aa].*}" #{A
    if re.search(exp,basiccode):
        language=2 #it's Assembly
        logger.info("it's ASM")
        basiccode = "ORG $8000\n" + basiccode

    exp = "{.*[Zz].*}" #{Z
    if re.search(exp,basiccode):
        language=3 #it's ZX basic
        logger.info("it's ZX basic")

    mode128=0
    exp = "{.*\+.*}" #{+ for 128 k mode
    if re.search(exp,basiccode):
        mode128=1
        logger.info("Using 128k mode")

    #remove any { command
    exp = "{[\w+]*}\s*" #{anything till } plus trailing whitespace
    basiccode = re.sub(exp,'',basiccode)

    #whitespace
    basiccode = basiccode.strip()
    logger.debug(f"Code: [{basiccode}]")

    #halt if string is empty
    if not basiccode:
        logger.info("!!! basiccode string is empty, SKIPPING")
        config['error']="Error: Empty code"
        return config

    config['starttime']  =starttime
    config['recordtime'] =recordtime
    config['language']   =language
    config['basiccode']  =basiccode
    config['speed']      =speed
    config['128mode']    =mode128
    return config

def create_backend():
    backend_name  = os.getenv('BACKEND')

    if backend_name  != 'twitter' and backend_name !='mastodon':
        logger.error("No backend configured in environment")
        raise ValueError('Missing backend')

    backend=None
    try:
        backend=Backend(backend_name)
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    return backend