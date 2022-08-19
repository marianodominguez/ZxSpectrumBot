import tweepy
import logging
import time
import os,sys
import subprocess
import TwitterUtil

def compile(api, tweet, config):
    
    language    = config['language']
    basiccode   = config['basiccode']
    debug       = config['debug']
    
    logger = logging.getLogger()
    if language>0: #not BASIC
        basiccode=basiccode + "\n"
        outputFile = open('working/AUTORUN','w',encoding='latin')
    else:
        outputFile = open('working/AUTORUN','w')

    outputFile.write(basiccode)
    outputFile.close()
    
    if os.path.exists("working/tape.tap"):
        os.remove("working/tape.tap") 

    if language==0: #BASIC
        logger.info("Making tape image, moving tokenized BASIC")
        result = os.popen('bas2tap working/AUTORUN -a working/dummy.tap 2>&1').read()
        if "ERROR" in result:
            logger.error("Not a valid BASIC program")
            logger.error(result)
            if debug:
                TwitterUtil.reply_tweet(api, tweet, result[:280])
            return 1
        os.popen('zmakebas -a 0 -o working/tape.tap working/AUTORUN  2>&1').read()


    elif language==3: #ZX BASIC
        logger.info("Making tape image BASIC")
        result = os.popen('zxbasic/zxbc.py -taB -o working/tape.tap working/AUTORUN 2>&1').read()
        if "error:" in result:
            logger.error("Not a valid ZX BASIC program")
            logger.error(result)
            if debug:
                TwitterUtil.reply_tweet(api, tweet, result[:280])
            return 1

    elif language==2: #ASM
        #todo run assembler code and use bin2tap
        asmResult = os.popen('z80asm working/AUTORUN -o working/run.bin 2>&1').read()
        if "error: " in asmResult:
            logger.error("assembler code not valid")
            logger.error(asmResult)
            if debug:
                TwitterUtil.reply_tweet(api, tweet, asmResult[:280])
            return 1
        logger.info("Making disk image, moving text ASM")
        result = os.popen('bin2tap working/run.bin working/tape.tap 2>&1').read()

    else:
        logger.error("Yikes! Langauge not valid")
        return 1




def run_emulator(api, tweet, config):
    
    starttime   = config['starttime']
    recordtime  = config['recordtime']
    speed       = config['speed']
    movie_support = config['movie_support']
    
    logger = logging.getLogger()
    logger.info("Firing up emulator")
    if not os.path.exists("working/tape.tap"):
        logger.error("no program to run")
        return
    
    if movie_support:
        cmd = f'/usr/bin/fuse-sdl --fbmode 640 --graphics-filter 2x --speed {speed*100} --no-confirm-actions --no-autosave-settings --auto-load --movie-start working/movie.fmf --rate 2 --sound-freq 44100  --separation ACB --tape working/tape.tap'.split()
        time.sleep(starttime)
        
        emuPid = subprocess.Popen(cmd, env={"DISPLAY": ":99"})
        emuPid.kill()
        
        result = os.system('fmfconv working/movie.fmf | ffmpeg -loglevel warning -y -i -vcodec libx264 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -pix_fmt yuv420p -strict experimental -r 30 -t 2:20 -acodec aac -vb 1024k -minrate 1024k -maxrate 1024k -bufsize 1024k -ar 44100 -ac 2 working/OUTPUT_SMALL.mp4')
    else:
        cmd = f'/usr/bin/fuse-sdl --fbmode 640 --graphics-filter 2x --speed {speed*100} --no-confirm-actions --no-autosave-settings --auto-load --no-sound --tape working/tape.tap'.split()

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
