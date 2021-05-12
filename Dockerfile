#FROM raspbian/stretch
FROM debian:stretch
ENV DEBIAN_FRONTEND=noninteractive
COPY repos/nonfree.repo /etc/apt/sources.list.d/

RUN useradd zxspectrum -d /home/zxspectrum
RUN apt-get update
RUN apt-get install -yq fuse-emulator-common ffmpeg python python-pip
RUN apt-get install -yq spectrum-roms
COPY . /home/zxspectrum
USER zxspectrum
WORKDIR /home/zxspectrum
RUN python -r requirements.txt
COPY assets/bas2tap /usr/bin
COPY assets/code2tap /usr/bin

CMD python SpeccyBot.py 
