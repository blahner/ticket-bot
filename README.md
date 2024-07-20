# ticket-bot
Implement your own ticket bot in python.
## Overview
Use this project to create your own ticket bot that sends you an email and text when tickets become available for a given event. I used this code to notify myself of when permits became available to hike Mount St. Helens. Read my blog post [here](https://medium.com/@benlahner/how-to-build-your-own-ticket-bot-63c3d0706e92) for more info.

![Mount St. Helens](images/mt_st_helens_pano.jpg)

## Setup
Create your python environment and install the required packages.
```
git clone https://github.com/blahner/ticket-bot.git
conda create -n ticket_bot python=3.10
conda activate ticket_bot
cd /your/path/to/ticket-bot
pip install -r requirements.txt
```

## Create your config file
This config file contains sensitive information, such as email addresses and your email address password. Create a directory named 'config/config.ini' and format your config.ini file like:
```
[sender_email]
sender_email = youremail@emailprovider.com
password = XXXX XXXX XXXX XXXX
[receiver_emails]
receiver_email1 = youremail@emailprovider.com
receiver_email2 = yourphonenumber@phoneprovider.com
```

Use this list of [email-to-sms addresses](https://avtech.com/articles/138/list-of-email-to-sms-addresses) to help you on the email-to-text part.

## Running the script
If you want to get notified of specifically Mount St. Helens permit availability, you will only need to edit the run_main.sh file with your desired dates, group size, etc. and, in the project root directory, run:
```
./run_main.sh
```
You will probably want to run this in a 'screen' session and configure your computer to run this script in the background without going to sleep.
Also note that ticket bot code is pretty fragile. Even a simple change to the website's html layout can break it. I likely won't keep this project up-to-date with whatever changes recreation.gov makes.

In the more likely case you want to get notified of ticket availabiltiy from a different website, you will need to make intensive edits to the main.py file. Read my [blog post](https://medium.com/@benlahner/how-to-build-your-own-ticket-bot-63c3d0706e92) for an overview of how to get started.
