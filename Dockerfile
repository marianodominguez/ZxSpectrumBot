FROM python:3.6-stretch
#FROM debian:stretch
ENV DEBIAN_FRONTEND=noninteractive
COPY repos/nonfree.repo /etc/apt/sources.list.d/nonfree.list

RUN useradd zxspectrum -d /home/zxspectrum
RUN apt-get update
RUN apt-get install -yq fuse-emulator-common xvfb autoconf automake build-essential cmake doxygen git graphviz imagemagick libasound2-dev libass-dev libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev libavutil-dev libfreetype6-dev libgmp-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libopus-dev librtmp-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-net-dev libsdl2-ttf-dev libsnappy-dev libsoxr-dev libssl-dev libtool libv4l-dev libva-dev libvdpau-dev libvo-amrwbenc-dev libvorbis-dev libwebp-dev libx264-dev libx265-dev libxcb-shape0-dev libxcb-shm0-dev libxcb-xfixes0-dev libxcb1-dev libxml2-dev lzma-dev meson nasm pkg-config python3-dev python3-pip texinfo wget yasm zlib1g-dev libdrm-dev

RUN apt-get install -yq spectrum-roms 
COPY --chown=zxspectrum . /home/zxspectrum
WORKDIR /home/zxspectrum

RUN gcc -Wall -lm assets/bas2tap.c -o assets/bas2tap
RUN gcc -Wall -lm assets/bin2tap.c -o assets/bin2tap

RUN cp assets/bas2tap /usr/bin
RUN cp assets/bin2tap /usr/bin

#ffmpeg from source to support 8 bits per pixel
RUN cd ~ && git clone --depth 1 https://code.videolan.org/videolan/x264 && \
 cd x264 && ./configure --host=arm-unknown-linux-gnueabi --enable-static --enable-shared --disable-opencl && \
 make -j4 && make install

RUN cd ~ && git clone git://source.ffmpeg.org/ffmpeg --depth=1 && \
 cd ffmpeg && ./configure --arch=armel --target-os=linux --enable-gpl --enable-shared --enable-libx264 --enable-nonfree && \
 make -j4 && make install

USER zxspectrum
RUN mkdir -p bot/working
#get master for video upload, 4.0a+
RUN pip3 install git+https://github.com/tweepy/tweepy.git
RUN pip3 install -r requirements.txt


CMD ./start.sh 
