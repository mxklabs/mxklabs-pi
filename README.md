Touchscreen Home
================

# Installation

This code is designed to run on a Raspberry Pi with the official touchscreen
display. We recommend using these products:

* [Raspberry Pi 3 Model B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
* [Raspberry Pi Touch Display](https://www.raspberrypi.org/products/raspberry-pi-touch-display/)
* [Raspberry Pi Universal Power Supply](https://www.raspberrypi.org/products/raspberry-pi-universal-power-supply/)

You will also need a micro SD card with the latest
[Raspbian](https://www.raspberrypi.org/downloads/raspbian/) image as well as
a HDMI display, keyboard, mouse and a HDMI cable for initially configuring your
Pi.

This guide assumes you already have a Raspberry Pi up and running with a
Raspbian Stretch image with a working official Touch Display and with access to
the internet. If this is not the case, follow these guides first:

* [Setup Raspbian](https://www.imore.com/how-get-started-using-raspberry-pi)
* [Setup WiFi](https://www.digikey.com/en/maker/blogs/raspberry-pi-3-how-to-configure-wi-fi-and-bluetooth/03fcd2a252914350938d8c5471cf3b63)
* [Setup Raspberry Pi Touch Display](https://thepihut.com/blogs/raspberry-pi-tutorials/45295044-raspberry-pi-7-touch-screen-assembly-guide)



# Troubleshooting

## The screen is upside down.
* Add the line `rotate_lcd=2` to the top of `/boot/config.txt`.
