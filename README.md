Intercom - Indoor part
======================

RASPBERRY Pi 2 Model B:
 - Python Kivy
 - omxplayer


Install:
- add root
- install kivy:
  https://kivy.org/docs/installation/installation-rpi.html
- install PJSIP:
  !!! netreba FFMPEG ani ASTERISK !!!
  apt-get install -y alsa-base alsa-utils alsa-tools libasound-dev
  apt-get install -y libasound2-plugins libasound2 libasound2-dev mpg321

  wget http://www.libsdl.org/release/SDL2-2.0.5.tar.gz
   tar xvzf SDL2-2.0.5.tar.gz
   ./autogen
   ./configure
   make -j4 && make install

  http://www.pjsip.org/download.htm:
   wget http://www.pjsip.org/release/2.6/pjproject-2.6.tar.bz2
   tar xvf pjproject-2.6.tar.bz2
   cd pjproject-2.6
   ./configure --disable-floating-point --disable-speex-aec --disable-large-filter --disable-l16-codec --disable-ilbc-codec --disable-g722-codec --disable-g7221-codec --disable-ffmpeg --disable-v4l2 --disable-openh264 --disable-video
   make dep -i && make -j4 -i (&& make install)




USB audio:
 - upravit:
(http://raspberrypi.stackexchange.com/questions/40831/how-do-i-configure-my-sound-for-jasper-on-raspbian-jessie)
/etc/modprobe.d/alsa-base.conf

# This sets the index value of the cards but doesn't reorder.
options snd_usb_audio index=0
options snd_bcm2835 index=1

# Does the reordering.
options snd slots=snd_usb_audio,snd_bcm2835