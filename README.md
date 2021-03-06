mxklabs - Raspberry Pi Calendar
===============================

# Introduction

The aim of this project is to turn a Raspberry Pi with a touchscreen into a combined clock/calendar. The calendar is linked to Google Calendar. The display shows events on a spiral with similar to the hour hand of a clock (i.e 00:00 and 12:00 are on top, 03:00 and 15:00 on the right, etc.). As time progresses events move closer to the centre of the spiral, with the very centre representing the here and now. The spiral updates in real time.

![Screenshot](assets/screenshot.png)

**NOTE**: *This project has been abandoned due to the purchase of a smart fridge. I've left the repository here in case it is useful to anybody. It happily downloads events from Google Calendar and displays it using Cairo. Note that whilst partly functional this code is not production quality.*

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

* Install six (a python 2/3 compatibility library):

   ```
   sudo python3 -m pip install --upgrade six
   ```

* Install dotmap (a library for dealing with dictionaries):

   ```
   sudo python3 -m pip install --upgrade dotmap
   ```

* Install Cairo:

   ```
   sudo python3 -m pip install --upgrade cairocffi
   ```

* Install the Google API Python client:

   ```
   sudo python3 -m pip install --upgrade google-api-python-client
   ```

* Install the TkInter imaging module:

   ```
   sudo apt-get install python3-pil.imagetk
   sudo apt-get install gir1.2-webkit-3.07
   ```

## Installing this software (mxklabs-pi-calendar)

The easiest way to install our this repository is to use git to clone the source
code directly from the github repository:

```
git clone https://github.com/mxklabs/mxklabs-pi-calendar.git
```

This puts the source code in `/home/pi/mxklabs-pi-calendar`. Now, you should be able to
manually start the application as follows:

```
python3 mxklabs-pi-calendar/main.py
```

## Configuring mxklabs-pi software

If you're planning to use the Google Calendar API feature then you'll need to
download a `client_secret.json` to `/home/pi/mxklabs-pi-calendar/credentials/google-api/client_secret.json`
(follow [this guide](https://developers.google.com/google-apps/calendar/quickstart/python)).
Note that this application was developed to stay within Google's free tier
quotas; there's no need to add a billing account.

## Post-Installation Tweaks

* To turn your screen upside down add the line `rotate_lcd=2` to the top of `/boot/config.txt`.
* To auto-start the application on startup add `@/usr/bin/python3 /home/pi/mxklabs-pi-calendar/main.py`
to the bottom of `/home/pi/.config/lxsession/LXDE-pi/autostart`.
* To set the brightness of the display set `/sys/class/backlight/rpi_backlight/brightness`
to a number between `0` (dark) and `255` (bright).
* To force the screen to stay on add `xserver-command=X -s 0 dpms` to `/etc/lightdm/lightdm.conf`'s
`[Seats:*]` section.
