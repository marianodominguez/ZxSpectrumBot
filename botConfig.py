# tweepy-bots/bots/config.py
import tweepy
import logging

logger = logging.getLogger()

def create_api():
    consumer_key = "tMA7JsNnVs95BU4nTmvXlLptG"
    consumer_secret = "RFBAYG9iWoWf0IHCIxBXBFvisvBLjH8dQOqRratksuLauIsyk7"
    access_token = "1392626957536284674-3ppfPG5XxXWl00vBtsIAf2Pi58w9JW"
    access_token_secret = "XqOM36dzD4E6qKjOrJJJz0A4bENv22SB4RhBoMHvqcWk2"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api

