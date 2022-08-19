#Atari8BitBot by @KaySavetz. 2020-2021.

import tweepy
import logging
from botConfig import create_api
import time
import os
from shutil import copyfile
import Emulator
from datetime import datetime
from unidecode import unidecode
import re
import GistManager

logging.basicConfig(level=logging.INFO)
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

    #if url, get code from it
    if gistUrl:
        text = GistManager.getGist(gistUrl)
        if text.startswith("Error: "): 
            logger.info(f"unable to retrieve {gistUrl}, {text}")
            config['error']=text
            return config
        else:
            basiccode = unidecode(text)
    #look for Debug command
    exp = "{\w*?D\w*(?:}|\s)" # {D\d\d  D= debug
    result = re.search(exp,basiccode)
    if result:  
        config['debug'] = True
    else:
        config['debug'] = False

    #look for start time command
    exp = "{\w*?B(\d\d?)\w*(?:}|\s)" # {B\d\d  B= Begin
    result = re.search(exp,basiccode)
    if result:  
        starttime = int(result.group(1))
        logger.info(f" Requests start at {starttime} seconds")
    else:
        starttime = 2

    #look for length of time to record command
    exp = "{\w*?S(\d\d?\d?)\w*(?:}|\s)" # {S\d\d  S= Seconds to record
    result=re.search(exp,basiccode)
    if result:
        recordtime = int(result.group(1))
        logger.info(f" Requests record for {recordtime} seconds")
    else:
        recordtime = 20
    if recordtime <1:
        recordtime=10
    if recordtime >30:
        recordtime=30
        
    exp = "{\w*?X(\d\d?\d?)\w*(?:}|\s)" # {X\d\d  X= Xelerate speed 1-20
    speed=1
    result=re.search(exp,basiccode)
    if result:
        speed = int(result.group(1))
        logger.info(f" Accelerate {speed*100} %")
    if speed>20: speed=20
    if speed<1: speed=1
    
    language = 0 # default to BASIC

    exp = "{\w*?A\w*(?:}|\s)" #{A
    if re.search(exp,basiccode): 
        language=2 #it's Assembly
        logger.info("it's ASM")
        basiccode = "ORG $8000\n" + basiccode
    
    exp = "{\w*?Z\w*(?:}|\s)" #{Z
    if re.search(exp,basiccode): 
        language=3 #it's ZX basic
        logger.info("it's ZX basic")

    movies=0
    exp = "{\w*?M\w*(?:}|\s)" #{Z
    if re.search(exp,basiccode): 
        movies=1 
        logger.info("Using new movie support")


    #remove any { command
    #exp = "{\w*(?:}|\s)" #{anything till space or }
    exp = "{\w*(?:}\s*)" #{anything till } plus trailing whitespace
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
    config['movie_support'] =movies
    return config

def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id, 
      tweet_mode='extended', include_entities=True).items():
        new_since_id = max(tweet.id, new_since_id)
        url=None
        
        logger.info(f"Tweet from {tweet.user.name}")
        #if there is an url in text, pass the firs
        if tweet.entities['urls']:
            url=tweet.entities['urls'][0]['expanded_url']
        if not GistManager.validate(url):
            url=None
        config=determine_config(tweet.full_text, url)
        
        if config['error']:
            logger.info(config['error'])
            continue

        error=Emulator.compile(api, tweet, config)
        if error:
            continue
        Emulator.run_emulator(api, tweet, config)
        logger.info("Done!")
    return new_since_id

def main():
    os.chdir('/home/zxspectrum/bot/')

    api = create_api()

    now = datetime.now()
    logger.info("START TIME:")
    logger.info(now.strftime("%Y %m %d %H:%M:%S")) 

    try:
        sinceFile = open('sinceFile.txt','r')
        since_id = sinceFile.read()
    except:
        sinceFile = open('sinceFile.txt','w')
        sinceFile.write("1")
        logger.info("created new sinceFile")
        since_id = 1

    sinceFile.close()       
    since_id = int(since_id)
    logger.info(f"Starting since_id {since_id}")
    os.environ["DISPLAY"] = ":99"

    while True:
        didatweet=0
        new_since_id = check_mentions(api, since_id)
        if new_since_id != since_id:
            since_id = new_since_id
            logger.info(f"Since_id now {since_id}")     
            sinceFile = open('sinceFile.txt','w')
            sinceFile.write(str(since_id))
            sinceFile.close()
            didatweet=1
        if didatweet==0:
            logger.info("Waiting...")
            time.sleep(120)

if __name__ == "__main__":
    main()
    
