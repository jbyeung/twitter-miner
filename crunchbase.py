# These functions are for fetching a new crunchbase datafile from the API

import urllib
import tarfile
from loggg import *
from config import *
import os
import shutil


dir = os.path.dirname(__file__)

def getCrunchbaseDump():
	# return tuple of industry, description, yearfounded, amount raised
	# fetches from crunchbase API, updated for v3.1
	
	logStart("Fetch new crunchbase dump")
	url = "https://api.crunchbase.com/v3.1/csv_export/csv_export.tar.gz?user_key=%s" % crunchbase_api_key
	fileName = os.path.join(dir, "data/dump/csv_export.tar.gz")
	file = urllib.URLopener()
	file.retrieve(url, fileName)		

	# unzips tar
	if fileName.endswith("tar.gz"):
		tar = tarfile.open(fileName, "r:gz")

		# only grabs the people.csv, deletes the rest
		for filename in ['people.csv']:
			try:
				f = tar.extract(filename, os.path.join(dir, "data/dump/"))
			except KeyError:
				print 'ERROR: Did not find %s in tar archive' % filename

		tar.close()

		# remove extra files
		os.remove(fileName)

	logEnd("Done successfully!")
	logCrunchbaseUpdate()
	return True	

def removeCrunchbaseFile():
	# clears crunchbase file to allow for clean update

	logStart("Trying to remove crunchbase file")
	try:
		shutil.move('sqlite/people.sqlite', 'sqlite/archive/people%s.sqlite' % strftime('%Y-%m-%d', gmtime()))
		logEnd("Success!")
		logCrunchbaseDeletion()
	except OSError:
		logEnd("Error removing file, does not exist")
		pass