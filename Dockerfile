FROM raspbian/stretch
#FROM debian:stretch
ENV DEBIAN_FRONTEND=noninteractive
#COPY repos/nonfree.repo /etc/apt/sources.list.d/nonfree.list

RUN useradd zxspectrum -d /home/zxspectrum
RUN apt-get update
RUN apt-get install -yq fuse-emulator-common ffmpeg python3 python3-pip xvfb
RUN apt-get install -yq spectrum-roms
COPY --chown=zxspectrum . /home/zxspectrum
WORKDIR /home/zxspectrum

RUN gcc -Wall -lm assets/bas2tap.c -o assets/bas2tap
RUN gcc -Wall -lm assets/bin2tap.c -o assets/bin2tap

RUN cp assets/bas2tap /usr/bin
RUN cp assets/bin2tap /usr/bin

USER zxspectrum

RUN pip3 install -r requirements.txt

CMD python3 SpeccyBot.py 
