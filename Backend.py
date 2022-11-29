from TwitterApi import TwitterApi
from MastodonApi import MastodonApi
import os
from types import SimpleNamespace
import logging

class Backend:
    impl=None
    api=None
    logger = logging.getLogger()
    consumer_key        = os.getenv('CONSUMER_KEY')
    consumer_secret     = os.getenv('CONSUMER_SECRET')
    access_token        = os.getenv('ACCESS_TOKEN')
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

    def get_api(Self, consumer_key, consumer_secret, access_token, access_token_secret):
        if not access_token_secret:
            Self.logger.error("Twitter access token missing from env")
            raise ValueError('Missing credentials')
        Self.api=Self.impl.get_api(consumer_key, consumer_secret, access_token, access_token_secret)
    
    def get_replies(Self,since_id):
        return Self.impl.get_replies(Self.api,since_id)

    def update_status(Self,message,id,media):
        if os.getenv('DRY_RUN'):
            Self.logger.info(f"Dry run, would post {message}" )
            return "dummy status"
        else:
            return Self.impl.update_status(Self.api,message,id,media)

    def media_upload(Self, filename):
        if os.getenv('DRY_RUN'):
            Self.logger.info(f"Dry run, would upload {filename}" )
            dummy_media=SimpleNamespace()
            dummy_media.media_id="12345"
            return dummy_media
        else:
            return Self.impl.media_upload(Self.api,filename)
   
    def reply(Self,tweet, text):
        if os.getenv('DRY_RUN'):
            Self.logger.info(f"Dry run, would post {tweet}" )
            return "dummy id"
        else:
            return Self.impl.reply(Self.api,tweet, text)

    def __init__(Self,backend):
        if backend == 'twitter':
            Self.impl = TwitterApi()
        else:
            Self.impl = MastodonApi()
        Self.get_api(Self.consumer_key, Self.consumer_secret, Self.access_token, Self.access_token_secret)
