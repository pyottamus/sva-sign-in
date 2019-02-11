#!/bin/bash
# Startup script for the SVA Sign In Application
#
#@reboot sh /home/pi/SVA_Sign_In/startup.sh

#
cd $HOME/SVA_Sign_In

#
if [ "$DISPLAY" = "" ]
then
	export DISPLAY=:0
fi

# wait for Xwindows and the desktop to start up
MSG="echo Waiting 45 seconds before starting"
DELAY="sleep 45"
if [ "$1" = "-n" -o "$1" = "--no-sleep" -o "$1" = "--no-delay" ]
then
	MSG=""
	DELAY=""
	shift
fi
if [ "$1" = "-d" -o "$1" = "--delay" ]
then
	MSG="echo Waiting $2 seconds before starting"
	DELAY="sleep $2"
	shift
	shift
fi
if [ "$1" = "-m" -o "$1" = "--message-delay" ]
then
	MSG="echo Waiting $2 seconds for response before starting"
	#DELAY="xmessage -buttons Now:0,Cancel:1 -default Now -timeout $2 Starting SVA Sign In Application in $2 seconds"
	DELAY='zenity --question --title Student Veterans Sign In --ok-label=Now --cancel-label=Cancel --timeout '$2' --text "Starting SVA Sign In Application in '$2' seconds" >/dev/null 2>&1'
	shift
	shift
fi

$MSG
eval $DELAY
if [ $? -eq 1 ]
then
	
	echo "SVA Sign In Application Cancelled"
	exit 0
fi

#xmessage -timeout 5 Starting PiClock....... &
zenity --info --timeout 3 --text "Starting PiClock......." >/dev/null 2>&1 &

# stop screen blanking
echo "Disabling screen blanking...."
xset s off
xset -dpms
xset s noblank

# get rid of mouse cursor
pgrep unclutter >/dev/null 2>&1
if [ $? -eq 1 ]
then
	unclutter >/dev/null 2>&1 &
fi

# the main app
cd Clock
echo "Starting SVA Sign In..."
python -u SVA_Sign_In.py