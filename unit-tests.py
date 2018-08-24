from config import crunchbase_api_key
from helper import *
from loggg import logUnitTest

################# UNIT TESTS
def filterUnitTest():
# Tests filters based on titles

	result = ""
	strings = ("Founder", "President", "CEO", "CXO")

	for s in strings:
		if not titleFilter(s):
			result = result + "failed " + s + "\n"
	if not result:
		result = "Passed!"
	return result

def confidenceUnitTest():
	# tests confidence level heuristics
	s = ""
	if calcConfidence(3,0) != 100:
		s = s + "failed 100\n"
	if calcConfidence(2,0) != 80:
		s = s +  "failed 80\n"
	if calcConfidence(1,0) != 60:
		s = s + "failed 60\n"
	if calcConfidence(0,3) != 50:
		s = s + "failed 50\n"
	if calcConfidence(0,2) != 20:
		s = s + "failed 20\n"
	if calcConfidence(0,0) != 0:
		s = s + "failed 0\n"
	
	if not s:
		s = "Passed!"

	return s

def CBUnitTests():
	# tests Crunchbase API functions
	
	s = ""

	if not getCrunchbaseLinkedinURL("Moses Lee", "mosesklee", crunchbase_api_key):
		s = s + "CB LinkedIn failed!\n"
	if not getCrunchbaseOrgData("Seelio", "fb867477-36ec-872b-ec9f-75fe1945de35", crunchbase_api_key)
		s = s + "CB Org Data failed!\n"

	if not s:
		s = "Passed!"
	return s


logUnitTest("Filters", filterUnitTest())
logUnitTest("Confidence test", confidenceUnitTest())
logUnitTest("Crunchbase tests", CBUnitTests())