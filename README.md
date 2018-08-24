# Project Ripple Overview

This project is designed to determine who is following certain leaders on Twitter.  Crunchbase data pulled from the API in the form of a CSV file (people.csv) is used to obtain the twitter ID, cross reference this with leader data, and determine the confidence level that this person is a Christian.  A confidence level is determined based on how many leaders they follow.

The webapp is hosted on AWS and runs on Python/Flask.  AWS SQS (simple queue service) is used to queue commands for the backend, which are processed by t1_manager and t2_manager, which run in the background on the AWS server.  These then run the scripts to process data, read/write to the databases, and send results out to the webapp or email for the user.

As you can see, the UI is pretty spartan.  There wasn't time to figure that out and make it look pretty.  But it works, most of the time.

## App Usage Overview
The app has three basic sections behind a login portal (sovereign/capital):

1) Leaders
Add, delete, update, modify type of leader
Add adds a new leader - this adds a queue to t1 and grabs the leader's followers list from twitter, which may take from minutes (small pool) to 8-12+ hours if they have half a million to a million followers.

Delete just wipes them from the database.

Update deletes and adds them to update their followers list.

Modify type just changes their type from A to B or vice versa.  This is fast.

2) Crunchbase
Grab new crunchbase file from the API - this downloads the tar zip (~1gb) and then unzips it, saves the people.csv and deletes the rest.

There is also an option to delete the file entirely.  This is in the event that the user wants to re-check everyone.  Currently, when matches are sent to the user either via email or batch, they are set to "exported = true".  This is a column in the people.sqlite.  This means they will not be exported again - ever.  SC had wanted this so they don't get a lot of noise in future batches since they were intending to just use this to check any new additions to the CB database and not wanting to see old results.  They also only export people in groupings, as in the last option.

Lastly, there is the option to do a batch result.  You can set filters for title, group type, optional filters, etc.  This is to only send out part of the total list, since there are a LOT of entries.  Matching in this fashion takes hours minimum.

3) Manual results
This is to allow them to spot check people they meet, etc.  by entering their twitter handles manually.  The script then figures out theri twitterID number (which is not public) so as to use this to check followers through the twitter API. The Twitter API only lists the ID numbers, not the handles, of a given person's followers.  This can take a while, on the order of a few minutes for a few entries.  The app is set not to time-out in that it caps the number of entries so it doesn't hit the time-out time.  This limit is 3 at a time (in app.py under manual section), you may need to adjust this.  Ideally it'd be closer to 10.  

The other option is to just add a queue in t2, and then they will get an email when it is done.  This is a better option in general.  It might be useful to add saved emails so they don't have to keep typing it.

## Setup

Use Python 2.7+ with boto3, Flask, and Tweepy (Twitter client).  

Install with PIP.

sudo pip install tweepy boto3 Flask

### API Keys
API Keys are contained in config.py.

For the Crunchbase API, https://data.crunchbase.com/v3/docs/using-the-api

For the Twitter API, use Tweepy.  http://www.tweepy.org/

### Folder Structure

/data/dump is for new Crunchbase downloads/
/data/queue is not used

/filter/confidence.csv is used to compute the confidence heuristic.
/filter/titles-1.txt and titles-2.txt are title filters lists

/log is for logs

/results/ is where processed results get written

/s3/leaders.sqlite is where leaders is stored.  Amazon S3 isn't used anymore but this could be moved.
/sqlite/people.sqlite Processed crunchbase results from the people.csv into here.

main folder houses all python scripts

## AWS

This project is housed on an AWS EC2 instance.  The EC2 URL is: http://ec2-54-244-147-34.us-west-2.compute.amazonaws.com/ .  If it changes, you can see it from the portal.

To SSH into the instance, use:
ssh -i "sc-key.pem" ec2-user@ec2-54-244-147-34.us-west-2.compute.amazonaws.com

Once the EC2 instance is setup, SSH in and run 
nohup ./monitor1.sh
nohup ./monitor2.sh 
 
to set up the scripts to monitor the SQS queues and process them to execute the commands requested by the user.  nohup starts the scripts on separate threads so they will run in background.  These scripts are setup to automatically restart the t1 and t2 manager scripts whenever they crash.  


### AWS EC2

login/pw: same as gmail.  Instance should restart automatically whenever it goes down, 

### AWS SQS

AWS Simple Queue Service is used as a request queue system from the user.  Requests for leader changes and crunchbase pulls, removals get sent to t1.  also batch processing of the crunchbase file is done on t1.  t2 processes all manual processing of twitter handles (manually entered by the user in the webapp).  This is designed such that they do not interfere with one another.

Modifications to the leaders file should not happen at the same time as a batch process of the crunchbase file, these will both lock up the system for a while.  So manual processing is done on a separate queue so as to still be runnable while this is happening.  This will also ensure that a new crunchbase file is not downloaded/processing while a batch process is happening.  

I had previously used t3 with a mutex to block action on either stack whenever there was a conflicting action (modifying leaders while reading the leaders file, or getting a new crunchbase file while manually searching for matches), but there were issues where the threads would get locked up and the app would not be usable anymore.  This didn't seem necessary since there is typically only one user at a time using this app.. so they generally know what to do and what not to do.

Ideally, a mutex should be implemented.  Or perhaps a server-side check and use a filesystem queue instead of SQS.

## Troubleshooting

### EC2
SSH into the instance and check if monitor1/t1_manager and monitor2/t2_manager are running.  Also check if the app is live.  It is run with Gunicorn in a virtualenv.  Gunicorn is then serviced by supervisor to restart it whenever it crashes.  So you will need to install these on the EC2 instance with pip install Gunicorn, and pip install supervisor --pre

Check these links for info:

https://www.matthealy.com.au/blog/post/deploying-flask-to-amazon-web-services-ec2/
https://www.matthealy.com.au/blog/post/using-supervisor-with-flask-and-gunicorn/

In a rare event, you may need to go to the AWS EC2 portal and restart the instance.  

### AWS SQS
To clear any jams on SQS, just go into the AWS portal and clear t1/t2 of all existing messages.  This should be sufficient.