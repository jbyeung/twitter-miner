# These functions process matches by using the crunchbase sqlite file with the twitter data (pulled here)

from helper import calcConfidence, titleFilter, parseTwitterUrl, regionFilter
from loggg import *
import json
import os
import time 
import sqlite3
import csv
import tweepy
import copy
from export import exportCSV, exportCSVManual, sendFile
from config import consumer_key, consumer_secret, access_key, access_secret

dir = os.path.dirname(__file__)

#####################################################################
# import leader data 
sqlite_file_leaders = os.path.join(dir, 's3/leaders.sqlite')
table_leaders = 'leaders'  # name of the table to be created
twitter_handle_field = "twitterHandle"
type_field = "type"

leader_index_id = 0
leader_index_twitterHandle = 1
leader_index_dateUpdated = 2
leader_index_followers = 3
leader_index_type = 4

follow_index_id = 0
follow_index_followers = 1

# import people data from crunchbase
sqlite_file_people = os.path.join(dir, 'sqlite/people.sqlite')
table_people = 'people'  # name of the table to be created
id_column = "ID"
index_field = "christianConfidence"
index_date_field = "indexDate"
following_field = "following"
exported_field = "exported"

people_index_id = 0
people_index_christianConfidence = 1
people_index_indexDate = 2
people_index_country = 5
people_index_title = 7
people_index_twitter = 14
people_index_twitterID = 15
people_index_following = 21

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
# Creation of the actual interface, using authentication

API = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def processMatchesCB(targetEmail, minA = 1, filterType = "founders", otherFilter="", regionType="USA"):
	# starts process for all CB file
	# calculates confidence values for each entry and updates their followings
	# takes a while to run

	logStart("Matching CB")
	conn1 = sqlite3.connect(sqlite_file_leaders)
	conn1.text_factory = sqlite3.Binary
	c1 = conn1.cursor()

	c1.execute('SELECT * FROM {tn}' \
			.format(tn=table_leaders))
	leaders = c1.fetchall()
	
	conn2 = sqlite3.connect(sqlite_file_people)
	conn2.text_factory = sqlite3.Binary
	c2 = conn2.cursor()

	try:
		c2.execute('SELECT * FROM {tn} WHERE {cn}=\'\' AND {cn2}=0'\
			.format(tn=table_people, cn=index_date_field, cn2=exported_field))
		people = c2.fetchall()
		
		hits = 0
		tested = 0


		#####################################################################
		# see who follows who
		count = 0
		for user in people:
			count = count + 1
			if count % 2000 == 0:
				print count
			title = str(user[people_index_title])
			country = str(user[people_index_country])
			
			# use title and region filter
			if titleFilter(title, filterType, otherFilter) and regionFilter(country, regionType):
				A = 0
				B = 0
				following = []
				# get list of tables of leaders

				for leader in leaders:	# ID, twitterHandle, dateUpdated, followers, type (A or B)

					try:
						# check if person is in leader's list
						c1.execute('SELECT * FROM {tn} WHERE {cn}=\'{val}\'' \
							.format(tn=leader[leader_index_twitterHandle], cn=twitter_handle_field, val=user[people_index_twitterID]))
						results = c1.fetchall()

						# compute A and B count 
						if len(results) > 0:
							if 'A' in str(leader[leader_index_type]):
								A = A + 1
							else:
								B = B + 1
							handle = str(leader[leader_index_twitterHandle])
							following.append(handle)
						
					except sqlite3.Error as er:
						logError("Getting leaders", er)
						pass
				
				# determine confidence and if there are followers, update sqlite
				confidence = calcConfidence(A, B)
				if len(following) > 0:
					try:
						c2.execute('UPDATE {} SET christianConfidence=?,indexDate=?,following=? WHERE ID=?'.format(table_people),
									(confidence,int(time.time()),', '.join(following),user[people_index_id]))
						conn2.commit()
					except sqlite3.Error as er:
						logError("Setting confidence", er)
				else:
					try:
						c2.execute('UPDATE {} SET christianConfidence=0,indexDate=?,following=\'\' WHERE ID=?'.format(table_people),
									(int(time.time()),user[people_index_id]))
						conn2.commit()
					except sqlite3.Error as er:
						logError("Setting confidence no followers", er)
	except sqlite3.Error as er:
		logError("no unexported people", er)
			
	conn1.close()
	conn2.close()
	logEnd("Matching CB")


	exportCSV(minA)
	text = "Crunchbase export of %s \n" % filterType + "Minimum number of A's followed set to %s \n" % str(minA)
	sendFile(targetEmail, "results", text)

	logEnd("Matching manual")

def processMatchesManual(listPeople, targetEmail = "", convertFromString = False):
	# assumes listPeople is list of people, twitter handles as "TwitterHandle"
	# gets twitter ID numbers then checks leaders list to see who is following who

	conn1 = sqlite3.connect(sqlite_file_leaders)
	conn1.text_factory = sqlite3.Binary
	c1 = conn1.cursor()

	c1.execute('SELECT * FROM {tn}' \
			.format(tn=table_leaders))
	leaders = c1.fetchall()


	# get ids
	people = []
	redo_list = []
	arr = []

	if convertFromString:
		# list People is just a string, need to convert into array of dict
		arr = parseManualInput(listPeople)
		logStart("Matching manual string with %d people entered" % len(arr))
#		logStart("Matching manual string %s" % listPeople)
	else:
		arr = listPeople
		logStart("Matching manual %d people entered" % len(listPeople))

	# check each person in list to get twitter ID numbers
	for person in arr:

		# make copy and redo list in case this API fails
		redo_list.append(person)
		user = copy.deepcopy(person)
		try:
			parsed = parseTwitterUrl(user['TwitterHandle'])

			# get the results from twitter API
			results = API.user_timeline(parsed)

			if len(results) > 0:

				# remove from redo_list since we found some result
				redo_list.pop()
				result = results[0]

				# get twitter ID
				user['TwitterID'] = result.user.id_str
				user['TwitterHandle'] = parsed
				people.append(user)
		except tweepy.TweepError, e:
			if "Not authorized" in str(e.message):
				print e.message
				pass
			# elif e.message[0]['code'] == 88:
			# 	time.sleep(60 * 15)
			# 	results = API.user_timeline(handle)
			# 	if len(results) > 0:
			# 		result = results[0]
			# 		user['TwitterID'] = result.user.id_str
			# 	pass

	# check people that weren't found with the first API method
	for person in redo_list:
		user = copy.deepcopy(person)
		try:
			parsed = parseTwitterUrl(user['TwitterHandle'])
			result = API.get_user(parsed)
			
			redo_list.pop()
			user['TwitterID'] = result.id_str

		except tweepy.TweepError, e:
			if "Not authorized" in str(e.message):
				print e.message
				pass
			# elif e.message[0]['code'] == 88:
			# 	time.sleep(60 * 15)
			# 	result = API.user_timeline(handle)	
			# 	user['TwitterID'] = result.id_str
			# 	user['TwitterHandle'] = parsed
			# 	pass
		people.append(user)


	# find matches

	for user in people:
		A = 0
		B = 0
		following = []
		# get list of tables of leaders

		if "TwitterID" in user:
			# if the leader has the twitter ID in the followers list
			for leader in leaders:	# ID, twitterHandle, dateUpdated, followers, type (A or B)
				try:
					c1.execute('SELECT * FROM {tn} WHERE {cn}=\'{val}\'' \
						.format(tn=leader[leader_index_twitterHandle], cn=twitter_handle_field, val=user["TwitterID"]))
					results = c1.fetchall()

					if len(results) > 0:
						if 'A' in str(leader[leader_index_type]):
							A = A + 1
						else:
							B = B + 1
						handle = str(leader[leader_index_twitterHandle])
						following.append(handle)
					
				except sqlite3.Error as er:
					pass

			confidence = calcConfidence(A, B)
			user['Confidence'] = str(confidence)
			user['Following'] = ', '.join(following)

	# then export the CSV file manually
	exportCSVManual(people)
	text = "Manual twitter check of %s users" % str(len(arr))
	if targetEmail:
		# sends the emailasset if requested
		sendFile(targetEmail, "manual", text)
	logEnd("Matching manual")

	return people

def parseManualInput(handlesString):
	# splits the input string into processable components
	people = []
	handlesString = handlesString.replace(",", " ")
	array = handlesString.splitlines()
	for s in array:
		arr = s.split(' ')
		for s1 in arr:
			appendIfNotBlank(people, s1)
	return people

def appendIfNotBlank(arr, s):
	if s:
		arr.append({"TwitterHandle" : s})
