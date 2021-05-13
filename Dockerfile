FROM python:3.6-stretch
#FROM debian:stretch
ENV DEBIAN_FRONTEND=noninteractive
COPY repos/nonfree.repo /etc/apt/sources.list.d/nonfree.list

RUN useradd zxspectrum -d /home/zxspectrum
RUN apt-get update
RUN apt-get install -yq fuse-emulator-common ffmpeg  xvfb
RUN apt-get install -yq spectrum-roms
COPY --chown=zxspectrum . /home/zxspectrum
WORKDIR /home/zxspectrum

RUN gcc -Wall -lm assets/bas2tap.c -o assets/bas2tap
RUN gcc -Wall -lm assets/bin2tap.c -o assets/bin2tap

RUN cp assets/bas2tap /usr/bin
RUN cp assets/bin2tap /usr/bin

RUN cd ~ && git clone git://source.ffmpeg.org/ffmpeg --depth=1 && \
 cd ffmpeg && ./configure --arch=armel --target-os=linux --enable-gpl --enable-nonfree && \
 make -j4 && make install

USER zxspectrum
RUN mkdir -p bot/working
#get master for video upload, 4.0a+
RUN pip3 install git+https://github.com/tweepy/tweepy.git
RUN pip3 install -r requirements.txt


CMD ./start.sh 
