# Helper functions

import re
import csv
import requests

# import the confidence values
reader = csv.DictReader(open("filter/confidence.csv"))
confidence = []
for line in reader:
	confidence.append(line)

# These are the filters used
with open("filter/titles-1.txt") as dataFile: founderTitles = dataFile.read().splitlines()
with open("filter/titles-2.txt") as dataFile: cxoTitles = dataFile.read().splitlines()
regex = re.compile('c.o')

def createManualList(filepath):
	# This is used to create a list of twitter handles from a file (filepath)
	# Splits twitter handles out from various formats of twitter handles 

	reader = csv.DictReader(open(filepath, "rb"))
	people = []
	for line in reader:
		if len(line.get("TwitterHandle")) > 0:
			s = line.get("TwitterHandle")
			if len(s.split("@/")) > 1:
				s = s.split("@/")[1]
			line["TwitterHandle"] = s
		people.append(line)
	return people

def titleFilter(title, filterType, otherFilter):
	# title is string
	# returns True or False depending on method
	# This function is used as a search filter by title types. These are defined in /filter/

	title = title.lower()
	if filterType =="other":
		strings = otherFilter.split(',')
		for s in strings:
			if s in title:
				return True
			if re.match(regex, title):
				return True
		return False
	elif filterType == "founders":
		for s in founderTitles:
			if s in title:
				return True
		return False
	elif filterType == "cxo":
		for s in cxoTitles:
			if s in title:
				return True
			if re.match(regex, title):
				return True
		return False
	elif filterType == "everyone-else":
		for s in founderTitles:
			if s in title:
				return False
		for s in cxoTitles:
			if s in title:
				return False
		return True
	elif filterType == "all":
		return True

def regionFilter(country, regionType):
	# option to filter by regions

	if regionType == "USA":
		return country == "USA"
	elif regionType == "other-regions":
		return country != "USA"
	else:
		return True

def calcConfidence(A, B):
	# confidence is calculated as A.B (as a float); A comes the whole numbers, B is after decimal

	while B >= 1.0:
		B = B / 10.0
	return float(A + B)


def parseTwitterUrl(url):
	# url is a string
	# returns the twitter handle parsed

	if not url: 
		return url
	else:
		if len(url.split("com/")) == 2:
			handle = (url.split("com/"))[1]
		elif len(url.split("@")) == 2:
			handle = (url.split("@"))[1]
		else:
			handle = url
		return handle
	
def getCrunchbaseOrgData(orgName, companyID, apiKey):
	# return tuple of industry, description, yearfounded, amount raised
	# updated for v3.1

	if companyID:
		companyID = companyID.replace("-","")

	url = "https://api.crunchbase.com/v3.1/organizations?query=%s&user_key=%s" % (orgName, apiKey)
	response = requests.get(url)
	if response.status_code == 200:
		j = response.json()

		if j["data"]["items"]:

			items = j["data"]["items"]
			permalink = ""
			for company in items:
				if company["uuid"].replace("-","") == companyID:
					permalink = company["properties"]["permalink"]
					break
			# parse items list for uuid match
			
			url2 = "https://api.crunchbase.com/v3.1/organizations/%s?user_key=%s" % (permalink, apiKey)
			response2 = requests.get(url2)
			if response2.status_code == 200:
				j2 = response2.json()

				yearFounded = ""
				amountRaised = 0
				description = ""
				industry = ""

				try:
					data = j2["data"]
					properties = data["properties"]

					if "founded_on" in properties:
						yearFounded = properties["founded_on"]
					if "total_funding_usd" in properties:
						amountRaised = properties["total_funding_usd"]
					if "short_description" in properties:
						description = properties["short_description"]

					if "categories" in data["relationships"]:
						categories = data["relationships"]["categories"]
						industry = ""
						for category in categories["items"]:
							if industry:
								industry = industry + ", "
							industry = industry + category["properties"]["name"]

					return (industry, description, yearFounded, amountRaised)
				except KeyError as err:
					# print err
					pass
			else:
				return None
		else:
			return None
	else:
		return None

def getCrunchbaseLinkedinURL(name, twitterHandle, apiKey):
	# return tuple of industry, description, yearfounded, amount raised
	# updated for v3.1

	url = "https://api.crunchbase.com/v3.1/people?query=%s&user_key=%s" % (name, apiKey)
	response = requests.get(url)
	if response.status_code == 200:

		j = response.json()

		if j["data"]["items"]:

			items = j["data"]["items"]
			for person in items:
				properties = person["properties"]
				if parseTwitterUrl(properties["twitter_url"]) == twitterHandle:
					return properties["linkedin_url"]
	return ""