import os
import shutil
from time import gmtime, strftime

# Logs to write to the /log folder

def logUnitTest(testName, result):
	with open("log/log.txt", "a") as log:
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))
		log.write(testName + ": \n")
		log.write(result)
		log.write("\n\n")

def logError(scriptName, error):
	with open("log/log.txt", "a") as log:
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))
		log.write("Error in %s, %s" % (scriptName, error))
		log.write("\n\n")

def logStart(scriptName):
	statinfo = os.stat('log/log.txt')
	if statinfo.st_size > 10000:
		shutil.move('log/log.txt', 'log/archive/log%s.txt' % strftime('%Y-%m-%d %H:%M:%S', gmtime()))
	with open("log/log.txt", "a") as log:
		log.write("----------------------------------\n")
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))
		log.write("Started %s \n " % scriptName)
		log.write("\n")

def logEnd(scriptName):
	with open("log/log.txt", "a") as log:
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))
		log.write("Ended %s \n " % scriptName)
		log.write("\n\n")
		log.write("----------------------------------\n")

def logEdit(factor, edit):
	with open("log/log.txt", "a") as log:
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))
		log.write("edited %s to %s \n" % (factor, edit))
		log.write("\n\n")

def logCrunchbaseUpdate():
	with open("log/cb-log.txt", "a") as log:
		log.write("Crunchbase fetch initiated\n")
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))
		log.write("\n\n")
	with open("log/cb-status.txt", "w") as log:
		log.write("Crunchbase fetched on:\n")
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))

def logCrunchbaseDeletion():
	with open("log/cb-log.txt", "a") as log:
		log.write("Crunchbase file deleted\n")
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))
		log.write("\n\n")
	with open("log/cb-status.txt", "w") as log:
		log.write("Crunchbase file deleted on:\n")
		log.write(strftime('%Y-%m-%d %H:%M:%S\n', gmtime()))