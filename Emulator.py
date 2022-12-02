import logging
import time
import os
import subprocess

def compile(backend, message, config):
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
    if os.path.exists("working/movie.fmf"):
        os.remove("working/movie.fmf")
    if os.path.exists("working/OUTPUT_SMALL.mp4"):
        os.remove("working/OUTPUT_SMALL.mp4") 
    if os.path.exists("working/OUTPUT_BIG.mp4"):
        os.remove("working/OUTPUT_BIG.mp4") 
     
    if language==0: #BASIC
        logger.info("Making tape image, moving tokenized BASIC")
        result = os.popen('bas2tap working/AUTORUN -a working/dummy.tap 2>&1').read()
        if "ERROR" in result:
            logger.error("Not a valid BASIC program")
            logger.error(result)
            if debug:
                backend.reply(message, result[:280])
            return 1
        os.popen('zmakebas -a 0 -o working/tape.tap working/AUTORUN  2>&1').read()


    elif language==3: #ZX BASIC
        logger.info("Making tape image BASIC")
        zxbc='zxbasic/zxbc.py'
        if os.getenv('ZBXPATH'):
            zxbc=os.getenv("ZBXPATH") + "/" + 'zxbc'   
        result = os.popen(zxbc+' -taB -o working/tape.tap working/AUTORUN 2>&1').read()
        logger.debug(result)
        if "error:" in result:
            logger.error("Not a valid ZX BASIC program")
            logger.error(result)
            if debug:
                backend.reply(message, result[:200])
            return 1

    elif language==2: #ASM
        #todo run assembler code and use bin2tap
        asmResult = os.popen('z80asm working/AUTORUN -o working/run.bin 2>&1').read()
        if "error: " in asmResult:
            logger.error("assembler code not valid")
            logger.error(asmResult)
            if debug:
                backend.reply(message, asmResult[:200])
            return 1
        logger.info("Making disk image, moving text ASM")
        result = os.popen('bin2tap working/run.bin working/tape.tap 2>&1').read()

    else:
        logger.error("Yikes! Langauge not valid")
        return 1

def run_emulator(backend, message, config):
    starttime   = config['starttime']
    recordtime  = config['recordtime']
    speed       = config['speed']
    
    logger = logging.getLogger()
    logger.info("Firing up emulator")
    if not os.path.exists("working/tape.tap"):
        logger.error("no program to run")
        return
    
    rom="--machine 48"
    if config['128mode']==1:
        rom="--machine 128"
    
    cmd = f'fuse {rom} --fbmode 640 --graphics-filter 2x --speed {speed*100} --no-confirm-actions --no-autosave-settings --auto-load --movie-start working/movie.fmf --movie-compr None  --rate 2 --sound-freq 44100 --separation ACB --tape working/tape.tap'.split()
    
    logger.info(f"command: {cmd}")
    emuPid = subprocess.Popen(cmd)
    
    logger.info(f"waiting for {starttime+recordtime} seconds")
    time.sleep(starttime+recordtime)
    cut_time=f'0:00-{starttime//60}:{(starttime%60):02}'
    logger.info(f"cutting: {cut_time} seconds" )
    logger.info(f"killing {emuPid} ")
    emuPid.kill()
    
    if os.path.exists("working/movie.fmf"):
        logger.info("converting fmf")
        
        result = os.system(f'fmfconv -C {cut_time} working/movie.fmf | ffmpeg -y -c:v libx264 -sws_flags accurate_rnd -pix_fmt yuv420p -r 30 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -b:v 5M -t 2:20 -acodec aac -ar 44100 -ac 2 working/OUTPUT_SMALL.mp4')
        logger.debug(result)
    else:
        logger.error("Emulator was unable to run, skipping video") 
    
    if os.path.exists("working/OUTPUT_SMALL.mp4"):
        logger.info("Uploading video")  
        media = backend.media_upload("working/OUTPUT_SMALL.mp4")
        logger.info(f"Media ID is {media.media_id}")

        logger.info(f"Posting to @{message.user.screen_name}")
        msg = f"@zxspectrumbot@mastodon.cloud ran @{message.user.name} 's code and obtained: \n "
        backend.update_status(msg,message.id,media)
    else:
        logger.error("No video to post")
