import tweepy
import logging
import time
import os,sys
import subprocess

def run_emulator(logger, api, tweet, language, recordtime, starttime):
    logger.info("Firing up emulator")
    if language==0 or language==2: #BASIC or ASM
        cmd = '/usr/bin/fuse-sdl --fbmode 640 --graphics-filter 2x --no-confirm-actions --no-autosave-settings --auto-load --no-sound --tape working/tape.tap'.split()

    emuPid = subprocess.Popen(cmd, env={"DISPLAY": ":99","SDL_AUDIODRIVER": "dummy"})
    logger.info(f"   Process ID {emuPid.pid}")

    time.sleep(starttime)

    logger.info("Recording with ffmpeg")
    result = os.system(f'ffmpeg -y -hide_banner -loglevel warning -f x11grab -r 30 -video_size 672x440 -i :99 -q:v 0 -pix_fmt yuv422p -t {recordtime} working/OUTPUT_BIG.mp4')

    logger.info("Stopping emulator")
    emuPid.kill()

    logger.info("Converting video")
    result = os.system('ffmpeg -loglevel warning -y -i working/OUTPUT_BIG.mp4 -vcodec libx264 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -pix_fmt yuv420p -strict experimental -r 30 -t 2:20 -acodec aac -vb 1024k -minrate 1024k -maxrate 1024k -bufsize 1024k -ar 44100 -ac 2 working/OUTPUT_SMALL.mp4')
    #per https://gist.github.com/nikhan/26ddd9c4e99bbf209dd7#gistcomment-3232972

    logger.info("Uploading video")  

    media = api.media_upload("working/OUTPUT_SMALL.mp4", chunked=True)

    logger.info(f"Media ID is {media.media_id}")

    time.sleep(5)
    #TODO replace with get_media_upload_status per https://github.com/tweepy/tweepy/pull/1414

    logger.info(f"Posting tweet to @{tweet.user.screen_name}")
    tweettext = f"@{tweet.user.screen_name} "
    api.update_status(auto_populate_reply_metadata=False, status=tweettext, media_ids=[media.media_id], in_reply_to_status_id=tweet.id)
