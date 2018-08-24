
# These functions are for exporting sqlite to CSV and also sending them as email

import os
import sqlite3
import requests
import csv
import codecs
from config import crunchbase_api_key, emailUsername, emailPassword
from helper import getCrunchbaseOrgData
from helper import getCrunchbaseLinkedinURL
from loggg import *
from datetime import datetime

import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

dir = os.path.dirname(__file__)

sqlite_file_people = os.path.join(dir, 'sqlite/people.sqlite')
table_people = 'people'  # name of the table to be created
id_column = "ID"
index_field = "christianConfidence"
company_id_field = "companyID"
index_date_field = "indexDate"
following_field = "following"

people_index_id = 0
people_index_christianConfidence = 1
people_index_name = 6
people_index_company = 8
people_index_companyID = 9
people_index_twitter = 14


def exportCSV(minConfidence = 0):
	# exports the csv file to a file

	logStart("Exporting CSV")
	# for people
	conn = sqlite3.connect(sqlite_file_people)
	c = conn.cursor()

	# fetch assets from sqlite
	c.execute('SELECT * FROM {tn} WHERE christianConfidence >= {con} AND exported=0' \
			.format(tn=table_people, con=minConfidence))
	people = c.fetchall()

	f = codecs.open(os.path.join(dir, 'results/results.csv'), 'wb')
	writer = csv.writer(f)
	#write headers to csv
	writer.writerow(["ID", "christianConfidence", "indexDate", "city", "state", "country", "name", "title", "company", "companyID", "industry", "description", "yearFounded", "amountRaised", "twitterHandle", "twittterID", "uuid", "crunchbaseURL", "LinkedIn", "updatedAt", "following"])

	count = 0

	# write items row by row to csv file
	for user in people:
		count = count + 1

		org_name = user[people_index_company]
		companyID = user[people_index_companyID]

		orgData = getCrunchbaseOrgData(org_name, companyID, crunchbase_api_key)
		
		if orgData:
			cb_industry, cb_description, cb_yearfounded, cb_amountraised = orgData[0], orgData[1], orgData[2], orgData[3]
		else:
			cb_industry, cb_description, cb_yearfounded, cb_amountraised = "", "", 0, 0

		name = user[people_index_name]
		twitterHandle = user[people_index_twitter]

		LIURL = getCrunchbaseLinkedinURL(name, twitterHandle, crunchbase_api_key)

		row = (user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8], user[9], cb_industry, cb_description, cb_yearfounded, cb_amountraised, user[14], user[15], user[16], user[17], LIURL, user[19], user[20])
		writer.writerow([unicode(s).encode("utf8") for s in row])


		try:
			c.execute('UPDATE {} SET industry=?,companyDescription=?,yearFounded=?,amountRaised=?,LinkedIn=?,exported=? WHERE ID=?'.format(table_people),
					(cb_industry,cb_description,cb_yearfounded,cb_amountraised,LIURL, 1, user[people_index_id]))
			conn.commit()
		except sqlite3.Error as er:
			print 'er:', er.message

		if count % 1000 == 0:
			print count
			conn.commit()

	f.close()
	conn.close()
	logEnd("Done exporting CSV")

def exportCSVManual(people):
	# exports the csv file to a file

	f = codecs.open(os.path.join(dir, 'results/results-manual.csv'), 'wb')
	writer = csv.writer(f)
	if len(people) > 0:
		writer.writerow(people[0].keys())
	
	for row in people:
		t = row.values()
		writer.writerow([unicode(s).encode("utf8") for s in t])
	

	f.close()


def sendFile(emailto, file = "results", text = ""):
	# emails file to emailto address with designated filepath

	logStart("Sending file to %s " % emailto)
	date = datetime.today()

	# chooses which csv file to attach
	emailfrom = "Sovereign's Capital"
	if file == "manual":
		fileToSend = os.path.join(dir, "results/results-manual.csv")
		attachmentName = "ripple-twitter-%s-%s-%s.csv" % (date.year, date.month, date.day)
	else:
		fileToSend = os.path.join(dir, "results/results.csv")
		attachmentName = "ripple-crunchbase-%s-%s-%s.csv" % (date.year, date.month, date.day)
	port = 25
	
	# MIME multipart settings to set from/to/subject
	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = emailto
	msg["Subject"] = text
	msg.preamble = None

	ctype, encoding = mimetypes.guess_type(fileToSend)
	if ctype is None or encoding is not None:
	    ctype = "application/octet-stream"

	maintype, subtype = ctype.split("/", 1)

	# options to send other assets if desired later
	if maintype == "text":
	    fp = open(fileToSend)
	    # Note: we should handle calculating the charset
	    attachment = MIMEText(fp.read(), _subtype=subtype)
	    fp.close()
	elif maintype == "image":
	    fp = open(fileToSend, "rb")
	    attachment = MIMEImage(fp.read(), _subtype=subtype)
	    fp.close()
	elif maintype == "audio":
	    fp = open(fileToSend, "rb")
	    attachment = MIMEAudio(fp.read(), _subtype=subtype)
	    fp.close()
	else:
	    fp = open(fileToSend, "rb")
	    attachment = MIMEBase(maintype, subtype)
	    attachment.set_payload(fp.read())
	    fp.close()
	    encoders.encode_base64(attachment)
	attachment.add_header("Content-Disposition", "attachment", filename=attachmentName)
	msg.attach(attachment)

	# Uses gmail smtp settings; email/password are in config
	server = smtplib.SMTP("smtp.gmail.com:587")
	server.starttls()
	server.login(emailUsername,emailPassword)
	server.sendmail(emailfrom, emailto, msg.as_string())
	server.quit()

	logEnd("Done sending file")