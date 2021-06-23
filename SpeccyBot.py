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
    basiccode = re.sub('^(@.+?\s)+','',full_text, re.ASCII)
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
    exp = "{\w*?D\w*(?:}|\s)" # {B\d\d  D= debug
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
    exp = "{\w*?S(\d\d?)\w*(?:}|\s)" # {S\d\d  S= Seconds to record
    result=re.search(exp,basiccode)
    if result:
        recordtime = int(result.group(1))
        logger.info(f" Requests record for {recordtime} seconds")
    else:
        recordtime = 20
    if recordtime <1:
        recordtime=1
    if recordtime >30:
        recordtime=30
        
    language = 0 # default to BASIC

    exp = "{\w*?A\w*(?:}|\s)" #{A
    if re.search(exp,basiccode): 
        language=2 #it's Assembly
        logger.info("it's ASM")

        basiccode = "ORG $8000\n" + basiccode

    #remove any { command
    #exp = "{\w*(?:}|\s)" #{anything till space or }
    exp = "{\w*(?:}\s*)" #{anything till } plus trailing whitespace
    basiccode = re.sub(exp,'',basiccode)

    #whitespace
    basiccode = basiccode.strip()
    logger.info(f"Code: [{basiccode}]")
    
    #halt if string is empty
    if not basiccode:
        logger.info("!!! basiccode string is empty, SKIPPING")
        config['error']="Error: Empty code"
        return config
    
    config['starttime']  =starttime
    config['recordtime'] =recordtime
    config['language']   =language
    config['basiccode']  =basiccode
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
            
        config=determine_config(tweet.full_text, url)
        
        if config['error']:
            logger.info(config['error'])
            continue
        
        language    = config['language']
        starttime   = config['starttime']
        basiccode   = config['basiccode']
        recordtime  = config['recordtime']
        debug       = config['debug']
        
        logger.info(basiccode)
        
        if language>0: #not BASIC
            basiccode=basiccode + "\n"
            outputFile = open('working/AUTORUN.BAS','w',encoding='latin')
        else:
            outputFile = open('working/AUTORUN.BAS','w')

        outputFile.write(basiccode)
        outputFile.close()

        if language==0: #BASIC
            logger.info("Making disk image, moving tokenized BASIC")
            result = os.popen('bas2tap working/AUTORUN.BAS -a working/tape.tap 2>&1').read()

        elif language==2: #ASM
            #todo run assembler code and use bin2tap
            asmResult = os.popen('z80asm working/AUTORUN.BAS -o working/run.bin 2>&1').read()
            if "error: " in asmResult:
                logger.error("assembler code not valid")
                continue
            logger.info("Making disk image, moving text ASM")
            result = os.popen('bin2tap working/run.bin working/tape.tap 2>&1').read()

        else:
            logger.error("Yikes! Langauge not valid")
            continue

        if "ERROR" in result:
            logger.error("Not a valid BASIC program")
            logger.error(result)
            if debug:
                reply_tweet(api, tweet, result[:280])
            continue
        Emulator.run_emulator(logger, api, language, recordtime, starttime)

        logger.info("Done!")
    return new_since_id

def reply_tweet(api, tweet, text):
    msg=" "
    for line in text.split("\n"):
        if "ERROR"  in line:
            msg=msg+line+"\n"
    
    tweettext = f"@{tweet.user.screen_name} \n {msg}"
    logger.info(f"MSG: {tweettext}")
    api.update_status(auto_populate_reply_metadata=False, status=tweettext.strip(), in_reply_to_status_id=tweet.id)

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
    
