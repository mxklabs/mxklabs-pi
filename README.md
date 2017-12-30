mxklabs - Raspberry Pi Touchscreen Application
==============================================

# Installation

## Hardware & setup

This code is designed to run on a Raspberry Pi with the official touchscreen
display. We recommend using these products:

* [Raspberry Pi 3 Model B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
* [Raspberry Pi Touch Display](https://www.raspberrypi.org/products/raspberry-pi-touch-display/)
* [Raspberry Pi Universal Power Supply](https://www.raspberrypi.org/products/raspberry-pi-universal-power-supply/)

You will also need a variety of other things to get up and running (like a
micro SD card with the latest [Raspbian Stretch](https://www.raspberrypi.org/downloads/raspbian/)
image, a display, a keyboard, etc.). This guide assumes you already have a
[Raspberry Pi](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
up and running with a [Raspbian Stretch](https://www.raspberrypi.org/downloads/raspbian/)
OS and the official [Touch Display](https://www.raspberrypi.org/products/raspberry-pi-touch-display/).
If this is not the case you find some basic guides
[here](https://www.imore.com/how-get-started-using-raspberry-pi),
[here](https://www.digikey.com/en/maker/blogs/raspberry-pi-3-how-to-configure-wi-fi-and-bluetooth/03fcd2a252914350938d8c5471cf3b63) and
[here](https://thepihut.com/blogs/raspberry-pi-tutorials/45295044-raspberry-pi-7-touch-screen-assembly-guide).

## Installing software dependencies

Our application requires [Python 3](https://www.python.org/downloads/) (already
installed on [Raspbian Stretch](https://www.raspberrypi.org/downloads/raspbian/))
with some additional dependencies:

* Install [Cairo](https://cairographics.org/) as follows:
 pi@raspberrypi:~$ sudo python3 -m pip install cairocffi

* Install the TkInter imaging module:
 pi@raspberrypi:~$ sudo apt-get install python3-pil.imagetk


## Installing mxklabs-pi software (i.e. this repository):

The easiest way to install our this repository is to use git to clone the source
code directly from the github repository:

 pi@raspberrypi:~$ git clone https://github.com/mxklabs/mxklabs-pi.git

This puts the source code in `/home/pi/mxklabs-pi`. Now, you should be able to
manually start the application as follows:

 pi@raspberrypi:~$ python3 mxklabs-pi/main.py


## Post-Installation Tweaks

* If your screen is upside down (depends on the case) you can add the
line `rotate_lcd=2` to the top of `/boot/config.txt`.
* To auto-start the application on startup add the following line to the bottom
of ~/.config/lxsession/LXDE-pi/autostart
 @/usr/bin/python3 /home/pi/mxklabs-pi/main.py
* Set the brightness of the backlight of your display by changing `/sys/class/backlight/rpi_backlight/brightness`
to have a number between `0` (dark) and `255` (bright).