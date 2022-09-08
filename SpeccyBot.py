import tweepy
import logging
from BotConfig import create_api,determine_config
import time
import os
import Emulator
from datetime import datetime
import GistManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

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