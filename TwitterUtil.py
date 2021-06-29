import tweepy
import logging

def reply_tweet(api, tweet, text):
    logger = logging.getLogger()
    msg=" "
    for line in text.split("\n"):
        if "ERROR"  in line:
            msg=msg+line+"\n"
    
    tweettext = f"@{tweet.user.screen_name} \n {msg}"
    logger.info(f"MSG: {tweettext}")
    api.update_status(auto_populate_reply_metadata=False, status=tweettext.strip(), 
        in_reply_to_status_id=tweet.id)
