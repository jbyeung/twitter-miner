from helper import *
from matches import *

from helper import parseTwitterUrl
from loggg import *
import json
import csv
import tweepy
import inspect
import time
import sqlite3
from config import consumer_key, consumer_secret, access_key, access_secret

import os.path
import tweepy
import time
import boto

consumer_key = "MUYM7WkXImlIBANo8oTA1lvfh"
consumer_secret = "LRM54284gEP9AnASZjTSWLLHz7MXDazbHzf5ieLFZAzVJWOaiR"
access_key = "18663552-frJIIahCDeiTHkUjyvHMP7PwI82p7vTYbjPbsv5Zc"
access_secret = "blw48iv1KAkcSW7gC8FkOZQqXaetGkoINvuBYF5udr2pK"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

API = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

############
# Jeffrey Yeung
# This is a set of test functions 

###############



dir = os.path.dirname(__file__)
#sqlite

sqlite_file = os.path.join(dir, 'sqlite/people.sqlite')
table_name1 = 'people'  # name of the table to be created
new_field0 = "ID"
new_field1 = "christianConfidence"
new_field2 = "indexDate"
new_field3 = 'city' # name of the column
new_field4 = 'stateCode' # name of the column
new_field5 = 'countryCode' # name of the column
new_field6 = 'name' # name of the column
new_field7 = 'title' # name of the column
new_field8 = 'company' # name of the column
new_field9 = 'companyID' # name of the column
new_field10 = 'industry' # name of the column
new_field11 = 'companyDescription' # name of the column
new_field12 = 'yearFounded' # name of the column
new_field13 = 'amountRaised' # name of the column
new_field14 = 'twitterHandle' # name of the column
new_field15 = 'twitterID' # name of the column
new_field16 = 'uuid' # name of the column
new_field17 = 'crunchbaseURL' # name of the column
new_field18 = "LinkedIn"
new_field19 = 'updatedAt' # name of the column
new_field20 = "following"
new_field21 = "exported"
textType = 'TEXT'  # column data type
intType = 'INTEGER'

people_index_indexdate = 2
people_index_city = 3
people_index_state = 4
people_index_country = 5
people_index_title = 7
people_index_company = 8
people_index_companyID = 9
people_index_twitter = 14
people_index_twitterID = 15
people_index_uuid = 16
people_index_updatedAt = 18


def testImport():
	# starts process for people - takes a while
	# imports csv file into the table and fetches twitterID for each from twitter

	logStart("Processing people")

	conn = sqlite3.connect(sqlite_file)
	conn.text_factory = sqlite3.Binary
	c = conn.cursor()

	# OAuth process, using the keys and tokens
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)

	API = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


	# import the people.csv from data dump
	reader = csv.DictReader(open(os.path.join(dir, "data/dump/people-TEST.csv")))
	users = []
	for line in reader:
		users.append(line)

	
	twitter_list = []

	for user in users:
		print user["first_name"]
		# twitter api lookup ids and put in dictionary

		# check if user alread in db
		
		c.execute('SELECT * FROM {tn} WHERE {cn}=\"{val}\"' \
					.format(tn="people", cn="uuid", val=user["uuid"]))
		userInDB = c.fetchone()
		if not userInDB:
			# print "already in db"
			# check if already exported. ignore it if exported
			# if not userInDB[people_index_indexdate]:
			# 	# if not exported, then just update the fields
			# 	c.execute('UPDATE {} SET city=?, stateCode=?, countryCode=?, title=?, company=?, companyID=?, updatedAt=? WHERE uuid=?'.format("people"),
			# 	 (user["city"], user["state_code"], user["country_code"], user["primary_affiliation_title"], 
			# 	 	user["primary_affiliation_organization"], user["primary_organization_uuid"], user["updated_at"], user["uuid"]))
			# 	conn.commit()
		# else:
			print "inserting "
			twitter_url = user["twitter_url"]
			if len(twitter_url) > 0:
				handle = parseTwitterUrl(twitter_url)
			
				try:
					r = API.get_user(handle)
					if r:
						friends = r.friends_count
						if friends < 20000:
							user["twitterID"] = r.id_str
							

							params = (0, "", user["city"], user["state_code"], user["country_code"], str(user["first_name"] + " " +  user["last_name"]), user["primary_affiliation_title"],
							user["primary_affiliation_organization"], user["primary_organization_uuid"], "", "", 0, 0, handle, user["twitterID"], user["uuid"], user["cb_url"], user["updated_at"], "", 0)
							
							try:
								c.execute('INSERT INTO people VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', params)

								conn.commit()
							except sqlite3.Error as er:
								print 'er:', er.message
							
				except tweepy.TweepError, e:
					if "Not authorized" in str(e.message):
						print "error"
						pass
					pass
	
	conn.close()
	logEnd("Done!")
		
def testDups():
	# prints duplicates in the sqlite file

	conn = sqlite3.connect(sqlite_file)
	conn.text_factory = sqlite3.Binary
	c = conn.cursor()

	c.execute('SELECT * FROM people ORDER BY twitterHandle')
	results = c.fetchall()

	print "duplicates:"
	count = 0
	prevResult = results[0]
	for result in results:
		if result[people_index_twitter] == prevResult[people_index_twitter]:
			count = count + 1
			print result[people_index_twitter]
		prevResult = result

	print count

		

		
def testFile():
	AWS_KEY = 'AKIAJ3DT42YEYKNVYN4Q'
	AWS_SECRET_KEY = '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'
	BUCKET_NAME = 'elasticbeanstalk-us-west-2-026227230054'
	# fileName = "asdf.txt"
	fileName = 'leaders.sqlite'

	conn = boto.s3.connect_to_region('us-west-2',aws_access_key_id = AWS_KEY,
			aws_secret_access_key = AWS_SECRET_KEY,
			is_secure=False,host='s3-us-west-2.amazonaws.com'
			)
	source_bucket = conn.lookup(BUCKET_NAME)

	''' Download the file '''
	for name in source_bucket.list():
		if name.name in fileName:
			print("DOWNLOADING",fileName)
			name.get_contents_to_filename('sqlite/' + fileName)
			print name

def test(name):
	try:
		c = tweepy.Cursor(API.followers_ids, id = name)
		# print "type(c)=", type(c)
		ids = []
		for page in c.pages():
			ids.append(page)
			print "ids=", ids
			print "ids[0]=", ids[0]
			print "len(ids[0])=", len(ids[0])	
		
	except tweepy.TweepError:
		print "tweepy.TweepError="#, tweepy.TweepError
	except:
		e = sys.exc_info()[0]
		print "Error: %s" % e
		
def runManual(email):
	# create a manual CSV file to test a small batch of users
	people = createManualList("data/queue/manual-users.csv")
	processMatchesManual(people, email)

def recalcConfidence():
	# starts process for people - takes a while
	# imports csv file into the table and fetches twitterID for each from twitter

	conn = sqlite3.connect(sqlite_file)
	conn.text_factory = sqlite3.Binary
	c = conn.cursor()

	c.execute('SELECT * FROM {tn} WHERE {cn}=\"{val}\"' \
					.format(tn="people", cn="uuid", val=user["uuid"]))
	users = c.fetchall()

	for user in users:


		c.execute('UPDATE {} SET christianConfidence=?'.format(table_people),
									(confidence))
	c.commit()
	
	conn.close()

def clearExtraLeaders():
	# this clears extra leaders if there are duplicates
	leaders_sqlite = os.path.join(dir, 's3/leaders.sqlite')

	conn = sqlite3.connect(leaders_sqlite)
	conn.text_factory = sqlite3.Binary
	c = conn.cursor()

	c.execute('SELECT * FROM leaders')
	leaders = c.fetchall()

	leader_names = []
	for leader in leaders:
		name = leader[leader_index_twitterHandle]
		leader_names.append(name)


	table_names = []
	c.execute("""SELECT name 
    FROM sqlite_master 
    WHERE type='table';
	""")
	tables = c.fetchall()
	for table in tables:
		table_names.append(table[0])


	for name in leader_names:
		if name in table_names:
			continue
		else:
			print name
			c.execute('DELETE FROM {} WHERE twitterHandle=?'.format("leaders"), (name,))
			conn.commit()


	conn.commit()

	
	conn.close()

clearExtraLeaders()
# s = raw_input("enter handle:")
# test(s)

# email = raw_input("Please enter email to send results to:\n")
# runManual(email)

# testImport()
# testDups()
# testMatches()