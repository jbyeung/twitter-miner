###############
# Jeffrey Yeung
# get-leader-followers.py
# Gets the followers of all leaders in QUEUE, adds to the database
# This script can take a long time... due to API limits (can only read 75000 followers per 15 minutes)
###############

# from twitter import *
import json
import csv
import sqlite3
import time
from loggg import *
import os
import tweepy
from helper import parseTwitterUrl
from config import consumer_key, consumer_secret, access_key, access_secret

dir = os.path.dirname(__file__)

sqlite_file = os.path.join(dir, 's3/leaders.sqlite')
table_name1 = 'leaders'  # name of the table to be created
new_field0 = "ID"
new_field1 = 'twitterHandle' # name of the column
textType = 'TEXT'  # column data type
intType = 'INTEGER'

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
# Creation of the actual interface, using authentication

#tweepy parameters - wait_on_rate_limit automatically waits when API limit is hit
# wait_on_rate_limit_notify will print to console when this happens
API = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def getAllLeaders():
	# returns all leaders in the db in array

	conn = sqlite3.connect(sqlite_file)
	c = conn.cursor()
	
	results = []
	try:
		c.execute('SELECT * FROM {}'.format(table_name1))
		results = c.fetchall()
		
	except sqlite3.Error as er:
		logError("Get leaders", er)

	conn.close()
	return results

def setLeaderType(handle, setType):
	# updates db entry of handle to the setType type (A or B)

	if setType.lower() == "a" or setType.lower() == "b":
		logStart("Setting %s to %s" % (handle, setType))

		conn = sqlite3.connect(sqlite_file)
		c = conn.cursor()

		try:
			c.execute('UPDATE {} SET type=? WHERE twitterHandle=?'.format(table_name1), (setType, handle))
			conn.commit()
			logEdit("type of %s" % handle, setType)
		except sqlite3.Error as er:
			logError("Set leader type", er)

		conn.close()

def getLeaderType(handle):
	# returns A or B for the handle's type in db

	conn = sqlite3.connect(sqlite_file)
	c = conn.cursor()

	results = []
	try:
		c.execute('SELECT type FROM {} WHERE twitterHandle=?'.format(table_name1), (handle,))
		results = c.fetchone()
		
	except sqlite3.Error as er:
		logError("Get leader type", er)

	conn.close()

	if results:
		return results[0]
	else:
		return None

def removeLeaders(user):
	# removes [] or handles from the database, from table 'leaders' and the individual tables
	logStart("removing %s" % user)

	conn = sqlite3.connect(sqlite_file)
	c = conn.cursor()
	
	# uses parsetwitterurl to get the handle in the right format
	handle = parseTwitterUrl(user)
	try:
		c.execute('DELETE FROM {} WHERE twitterHandle=?'.format(table_name1), (handle,))
		conn.commit()

		c.execute('DROP TABLE {}'.format(handle))
		conn.commit()

		logEdit("removal of %s" % handle, "entirety")
	except sqlite3.Error as er:
		logError("remove leader %s" % handle, er)

	conn.close()

	logEnd("removing leaders")


def updateLeader(handle):
	# removes the handle and then re-adds it
	logStart("updating leader %s" % handle)

	conn = sqlite3.connect(sqlite_file)
	c = conn.cursor()

	leaderType = getLeaderType(handle)
	if leaderType:
		removeLeaders([handle])
		addLeaders({"handle": handle, "type":leaderType})

	conn.close()

	logStart("done updating %s" % handle)


def addLeaders(user):
	# input is array of dictionary of "handle" and "type"
	# adds all the leaders to the table 'leaders' and makes new tables for each

	logStart("Adding %s" % user["handle"])

	conn = sqlite3.connect(sqlite_file)
	c = conn.cursor()
	i = 0
		

	handle = parseTwitterUrl(user["handle"])

	# don't repeat existing entries
	c.execute('SELECT * FROM {} WHERE twitterHandle=?'.format(table_name1), (handle,))
	results = c.fetchone()
	if results != None:
		logError("adding leader", "exists already")
		

	ids = []
	# results = []

	try:
		t = tweepy.Cursor(API.followers_ids, id = handle)
		for page in t.pages():
			for twitterID in page:
				ids.append(twitterID)
	except tweepy.TweepError:
		print "tweepy.TweepError="#, tweepy.TweepError
	except:
		e = sys.exc_info()[0]
		print "Error: %s" % e

	
	print "%s: %s" % (time.strftime('%a %H:%M:%S'), handle)


	newUser = {}
	newUser[handle] = ids
	newUser["timestamp"] = int(time.time())

	
	# insert into leaders table
	params = (handle, newUser["timestamp"], len(ids), user["type"])
	try:
		c.execute('INSERT INTO leaders VALUES (NULL, ?, ?, ?, ?)', params)
	except sqlite3.Error as er:
		logError("Add leader", er.message)

	# ### create new sqlite table for the leader with the followers
	try:
		c.execute('CREATE TABLE {tn} ({nf0} {ft0} PRIMARY KEY, {nf1} {ft1})'\
    		.format(tn=handle, nf0=new_field0, ft0=intType, nf1=new_field1, ft1=intType))
	except sqlite3.Error as er:
		logError("Add leader", er.message)

	# insert the follower values
	count = 0
	for twitterID in newUser[handle]:
		try:
			c.execute('INSERT INTO %s VALUES (?, ?)' % handle, (count, twitterID))
			count = count + 1
		except sqlite3.Error as er:
			logError("Add leader", er.message)

	conn.commit()

	# need to only do 15 in 15 mins
	if (i > 14):
		time.sleep(60 * 15)
		i = 0

	conn.close()

	logEnd("adding leaders")