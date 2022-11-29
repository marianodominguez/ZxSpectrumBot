import tweepy
import logging

class TwitterApi:

    logger = logging.getLogger()

    def get_api(Self, consumer_key, consumer_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        api.verify_credentials()
        Self.logger.info("API created")
        return api

    def media_upload(Self,api,filename):
        media = api.media_upload(filename, chunked=True, media_category='tweet_video')
        return media

    def update_status(Self, api,tweettext,id, media):
        status = api.update_status(auto_populate_reply_metadata=False, status=tweettext.strip(), media_ids=[media.media_id], in_reply_to_status_id=id)
        return status

    def reply(Self,api,tweet,text):
        logger = logging.getLogger()
        msg=" "
        for line in text.split("\n"):
            if "ERROR"  in line or "error:" in line:
                msg=msg+line+"\n"
        
        tweettext = f"@{tweet.user.screen_name} \n {msg}"
        logger.info(f"MSG: {tweettext}")
        status = {}
        try: 
            status = Self.update_status(api,tweettext.strip(),tweet.id)
        except:
            logger.error(f"Unable to post message: {status}")

    def get_replies(Self, api, since_id):
        return tweepy.Cursor(api.mentions_timeline, since_id=since_id, tweet_mode='extended', include_entities=True).items()