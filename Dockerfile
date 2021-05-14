FROM python:3.6-stretch
#FROM debian:stretch
ENV DEBIAN_FRONTEND=noninteractive
COPY repos/nonfree.repo /etc/apt/sources.list.d/nonfree.list

RUN useradd zxspectrum -d /home/zxspectrum
RUN apt-get update
RUN apt-get install -yq fuse-emulator-common xvfb fuse-emulator-utils spectrum-roms fuse-emulator-sdl ffmpeg

#ffmpeg from source to support 8 bits per pixel
# RUN cd ~ && git clone --depth 1 https://code.videolan.org/videolan/x264 && \
#  cd x264 && ./configure --host=arm-unknown-linux-gnueabi --enable-static --enable-shared --disable-opencl && \
#  make -j4 && make install

# RUN cd ~ && git clone git://source.ffmpeg.org/ffmpeg --depth=1 && \
#  cd ffmpeg && ./configure --arch=armel --target-os=linux --enable-gpl --enable-shared --enable-libx264 --enable-nonfree && \
#  make -j4 && make install

COPY --chown=zxspectrum . /home/zxspectrum
WORKDIR /home/zxspectrum

RUN gcc -Wall -lm assets/bas2tap.c -o assets/bas2tap
RUN gcc -Wall -lm assets/bin2tap.c -o assets/bin2tap

RUN cp assets/bas2tap /usr/bin
RUN cp assets/bin2tap /usr/bin

USER zxspectrum
RUN mkdir -p bot/working
#get master for video upload, 4.0a+
RUN pip3 install git+https://github.com/tweepy/tweepy.git
RUN pip3 install -r requirements.txt


CMD ./start.sh 
