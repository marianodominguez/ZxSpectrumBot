# tweepy-bots/bots/config.py
import tweepy
import logging

logger = logging.getLogger()

def create_api():
    consumer_key = "vWBluZ27yi9jqoJACeKv1FY8d"
    consumer_secret = "ASBE7Cs01DbA25NSpJOeFJWGtsMc4YsYjPdFSBqLSjVfu3ZDo0"
    access_token = "1392626957536284674-4g8bRbXCYMlI3sAVMzeUcIbNNxiKVm"
    access_token_secret = "bvXBEBGge7PTCZRqD5XNqM5CICMvB7jNqtIJ8243mEjhX"

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

