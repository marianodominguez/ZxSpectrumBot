# ZxSpectrumBot

This is a port from the Atari 8-bit Twitter bot at https://twitter.com/Atari8BitBot


Documentation for using the bot will be in this readme

The main twitter posting code is based on what I learned from "The Reply to Mentions Bot" at https://realpython.com/twitter-bot-python-tweepy/#the-config-module

Dependencies. So many dependencies:
- A Twitter account, and API keys for it https://developer.twitter.com/en/products/twitter-api
- Tweepy. Specifically the fork that allows video uploads. https://github.com/tweepy/tweepy/pull/1414 They plan on folding that feature into the main program but as of this writing, haven't.
- zxspectrum emulator fuse: fuse-emulator-common spectrum-roms fuse-emulator-utils
- Spectrum Basic parser (TBD)
- zmakebas: utility to create tap files https://github.com/z00m128/zmakebas
- ffmpeg, for processing video files: https://ffmpeg.org
- Tapes: 
- An X Virtual Frame Buffer running on display 99 (/usr/bin/Xvfb :99 -ac -screen 0 1024x768x24)
