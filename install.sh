#!/bin/bash

set -e

# PWD_TRIGGER=$(pwd)
# SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

help() {
    echo "Usage $0"
    echo "    -y    Skip inputs and only install deps"
    echo "    -s    Configure secrets"
    echo "    -p    Configure personalization"
    echo "    -h    Print this help"
    if [ $# -gt 0 ] && [ $1 = "abort" ]; then
        exit 1
    else
        exit 0
    fi
}

privacy_disclaimer() {
    echo "------------------------------------------------[Privacy Information]--"
    echo "Usage of this tool will require some of your basic personal information"
    echo "such as phone number, age, pin codes and district IDs you wish to look"
    echo "up for. This information does not leave your machine and is only used"
    echo "to support purposes restricted to the means of this application."
    echo "The application requires the OTP issued via CoWin which it will request"
    echo "on your specified Telegram channel. Ensure you use this with your personal"
    echo "Telegram Channel and your own Telegram Bot. OTP will need to be posted"
    echo "on the channel when asked for by your bot."
    echo "----------------------------------------------------------------------"
    echo ""
}

FULL_AUTOMATE=0
NEEDS_PERSONALIZATION=0
NEEDS_SECRET_SETUP=0
NEEDS_HELP=0

while [ ! "$1" = "" ]; do
    case $1 in
        "-y" )
            FULL_AUTOMATE=1
            shift
            ;;
        "-s" )
            NEEDS_SECRET_SETUP=1
            shift
            ;;
        "-p" )
            NEEDS_PERSONALIZATION=1
            shift
            ;;
        "-h" )
            NEEDS_HELP=1
            shift
            ;;
    esac
done

if [ $NEEDS_HELP -eq 1 ]; then
    help
fi

privacy_disclaimer
echo "[Vax]: Starting installation"

# Install package requirements
cd "$SCRIPT_DIR"
# sudo -H pip install --ignore-installed -U -r requirements.txt

if [ $NEEDS_SECRET_SETUP -eq 1 ]; then
    echo "[Vax]: Setting up secrets"
    echo "  [Vax]: Looking for previous instances of secret"
    WIPE_SECRET=0

    if [ -f "secrets_telegram.json" ]; then
        echo "[!] Secrets file already exists. Overwrite? (y/*): "
        read WIPE_SECRET
        if [ "$WIPE_SECRET" = "y" ]; then
            echo "[Vax]: Wiping old secrets"
            rm -f "secrets_telegram.json"
            WIPE_SECRET=1
        else
            echo "[!] Unknown option, skipping secret setup"
            WIPE_SECRET=2
        fi
    fi

    if [ ! $WIPE_SECRET = 2 ] && [ ! -f "secrets_telegram.json" ]; then
        echo "[Vax]: Installing telegram secrets"
        echo "-----------------------------------------------"
        echo "Creating telegram secrets, please ensure you have bot token and channel id ready.."
        echo "Note:"
        echo " || To crete and obtain your BOT TOKEN, contact BotFather at https://web.telegram.org/#/im?p=@BotFather"
        echo " || To obtain your channel id, simply create a channel and add the bot. Open your channel in Telegram web"
        echo "    and follow these instructions:"
        echo "    https://gist.github.com/mraaroncruz/e76d19f7d61d59419002db54030ebe35"
        echo "-----------------------------------------------"
        echo ""
        echo "Enter Bot token: "
        read BOT_TOKEN
        echo "Enter Channel ID: "
        read CHANNEL_ID
        echo "Generating at base path.."
        cat > "secrets_telegram.json" <<EOF
{
    "PI_BOT_TOKEN": "$BOT_TOKEN",
    "PI_CHANNEL_ID": "$CHANNEL_ID"
}
EOF
    fi
fi


if [ $NEEDS_PERSONALIZATION -eq 1 ]; then
    echo "[Vax]: Setting up user personalization"
    echo "  [Vax]: Looking for previous instances of user preferences"
    WIPE_PREF=0

    if [ -f "user_preferences.json" ]; then
        echo "[!] Preferences file already exists. Overwrite? (y/*): "
        read WIPE_PREF
        if [ "$WIPE_PREF" = "y" ]; then
            echo "[Vax]: Wiping old preferences"
            rm -f "user_preferences.json"
            WIPE_PREF=1
        else
            echo "[!] Unknown option, skipping preferences setup."
            WIPE_PREF=2
        fi
    fi

    if [ ! $WIPE_PREF = 2 ] && [ ! -f "user_preferences.json" ]; then
        echo "[Vax]: Setting up user preferences"
        echo ""
        echo "Enter Mobile Number: "
        read MOBILE_NUMER
        echo "Enter your age: "
        read AGE
        echo "Enter pin codes (specify as Python lists even if one): "
        read PIN_CODES
        echo "Enter district codes [faster] (specify as Python lists even if one): "
        read DIST_CODES
        echo "Generating at base path.."
        cat > "user_preferences.json" <<EOF
{
    "MOBILE": $MOBILE_NUMER,
    "AGE": $AGE,
    "PIN_CODES": $PIN_CODES,
    "DIST_CODES": $DIST_CODES
}
EOF
    fi
fi
echo "[Vax]: Complete."