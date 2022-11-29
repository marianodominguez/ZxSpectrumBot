import logging
import BotConfig 
import time
import os
import Emulator
from datetime import datetime
import GistManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def check_mentions(backend, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for message in backend.get_replies(since_id):
        logger.info(message)
        new_since_id = max(message.id, new_since_id)
        url=None
        
        logger.info(f"Tweet from {message.user.name}")
        #if there is an url in text, pass the first
        if 'urls' in message.entities.keys():
            url=message.entities['urls'][0]['expanded_url']
        if not GistManager.validate(url):
            url=None
        config=BotConfig.determine_config(message.full_text, url)
        
        if config['error']:
            logger.info(config['error'])
            continue

        error=Emulator.compile(backend, message, config)
        if error:
            continue
        Emulator.run_emulator(backend, message, config)
        logger.info("Done!")
    return new_since_id

def main():
    os.chdir('/home/zxspectrum/bot/')

    backend = BotConfig.create_backend()

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
        new_since_id = check_mentions(backend, since_id)
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