FROM python:3.6-stretch
#FROM debian:stretch
#Not supported, due to bug in colors. TODO: update

ENV DEBIAN_FRONTEND=noninteractive
COPY repos/nonfree.repo /etc/apt/sources.list.d/nonfree.list

RUN useradd zxspectrum -d /home/zxspectrum
RUN apt-get update
RUN apt-get install -yq fuse-emulator-common xvfb fuse-emulator-utils spectrum-roms fuse-emulator-sdl ffmpeg zmakebas z80asm fuse 

COPY --chown=zxspectrum . /home/zxspectrum
WORKDIR /home/zxspectrum

RUN gcc -Wall -lm assets/bas2tap.c -o assets/bas2tap
RUN gcc -Wall -lm assets/bin2tap.c -o assets/bin2tap

RUN cp assets/bas2tap /usr/bin
RUN cp assets/bin2tap /usr/bin

USER zxspectrum
RUN wget -q --no-check-certificate http://www.boriel.com/files/zxb/zxbasic-1.16.3-linux64.tar.gz && tar -zxvf zxbasic-1.16.3-linux64.tar.gz 

RUN mkdir -p bot/working
RUN pip3 install -r requirements.txt

CMD ./start.sh 
