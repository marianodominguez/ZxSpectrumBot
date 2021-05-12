FROM raspbian/wheezy

RUN useradd zxspectrum -d /home/zxspectrum
RUN apt install -q fuse-emulator-common spectrum-roms ffmpeg python python-pip

COPY . /home/zxspectrum
USER zxspectrum
WORKDIR /home/zxspectrum
RUN python -r requirements.txt
COPY assets/bas2tap /usr/bin
COPY assets/code2tap /usr/bin

CMD python SpeccyBot.py 
