Intercom - Indoor part
======================

RASPBERRY Pi 2 Model B:
 - Python Kivy
 - linphone python wrapper
 - omxplayer


#pip install Flask
#pip install pyscreenshot
#pip install Pillow
#apt-get install python-gtk2


USB audio:
 - upravit:
(http://raspberrypi.stackexchange.com/questions/40831/how-do-i-configure-my-sound-for-jasper-on-raspbian-jessie)
/etc/modprobe.d/alsa-base.conf

# This sets the index value of the cards but doesn't reorder.
options snd_usb_audio index=0
options snd_bcm2835 index=1

# Does the reordering.
options snd slots=snd_usb_audio,snd_bcm2835