###############
# Jeffrey Yeung

# functions to create table in sqlite and process people from crunchbase into it

###############

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

def createTable():
	# creates new table file if it doesn't already exist for "people.sqlite"
	
	if os.path.isfile(sqlite_file):
		logError("Create table file", "file already exists")
	else:
		logStart("Creating new people table")
		conn = sqlite3.connect(sqlite_file)
		conn.text_factory = sqlite3.Binary
		c = conn.cursor()

		try:
			c.execute('CREATE TABLE {tn} ({nf0} {ft0} PRIMARY KEY, {nf1} {ft1}, {nf2} {ft2}, {nf3} {ft3}, {nf4} {ft4}, {nf5} {ft5}, {nf6} {ft6}, {nf7} {ft7}, {nf8} {ft8}, {nf9} {ft9}, {nf10} {ft10}, {nf11} {ft11}, {nf12} {ft12}, {nf13} {ft13}, {nf14} {ft14}, {nf15} {ft15}, {nf16} {ft16}, {nf17} {ft17}, {nf18} {ft18}, {nf19} {ft19}, {nf20} {ft20}, {nf21} {ft21})'\
		        .format(tn=table_name1, nf0=new_field0, ft0=intType, nf1=new_field1, ft1=intType, nf2=new_field2, ft2=intType, nf3=new_field3, ft3=textType
		        	, nf4=new_field4, ft4=textType, nf5=new_field5, ft5=textType, nf6=new_field6, ft6=textType, nf7=new_field7, ft7=textType, nf8=new_field8, ft8=textType
		        	, nf9=new_field9, ft9=intType, nf10=new_field10, ft10=textType, nf11=new_field11, ft11=textType, nf12=new_field12, ft12=intType, nf13=new_field13, ft13=intType,
		        	nf14=new_field14, ft14=textType, nf15=new_field15, ft15=intType, nf16=new_field16, ft16=intType,nf17=new_field17, ft17=textType,nf18=new_field18, ft18=textType,
		        	nf19=new_field19, ft19=intType, nf20=new_field20, ft20=textType, nf21=new_field21, ft21=intType))
		except sqlite3.Error as er:
			print 'er:', er.message
		c.close()
		logEnd("Done!")

#-----------------------------------------------------------------------
# load our API credentials 
#-----------------------------------------------------------------------

def processPeople():
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
	reader = csv.DictReader(open(os.path.join(dir, "data/dump/people.csv")))
	users = []
	for line in reader:
		users.append(line)

	
	# twitter_list = []
	count = 0
	for user in users:
		count = count + 1
		if count % 1000 == 0:
			print count
		# twitter api lookup ids and put in dictionary

		# check if user alread in db
		
		c.execute('SELECT * FROM {tn} WHERE {cn}=\"{val}\"' \
					.format(tn="people", cn="uuid", val=user["uuid"]))
		userInDB = c.fetchone()
		if not userInDB:

			# # check if already exported. ignore it if exported
			# if not userInDB[people_index_indexdate]:
			# 	# if not exported, then just update the fields
			# 	c.execute('UPDATE {} SET city=?, stateCode=?, countryCode=?, title=?, company=?, companyID=?, updatedAt=? WHERE uuid=?'.format("people"),
			# 	 (user["city"], user["state_code"], user["country_code"], user["primary_affiliation_title"], 
			# 	 	user["primary_affiliation_organization"], user["primary_organization_uuid"], user["updated_at"], user["uuid"]))
			# 	conn.commit()
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
							user["primary_affiliation_organization"], user["primary_organization_uuid"], "", "", 0, 0, handle, user["twitterID"], user["uuid"], user["linkedin_url"], user["cb_url"], user["updated_at"], "", 0)
							
							try:
								c.execute('INSERT INTO people VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', params)

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
