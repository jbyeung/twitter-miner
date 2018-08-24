# Flask main app file to run the webapp; run with python app.py to test locally

from flask import Flask, redirect, url_for, request, render_template
from flask import session, escape

from leaders import getAllLeaders, removeLeaders, addLeaders, updateLeader, setLeaderType
from crunchbase import getCrunchbaseDump, removeCrunchbaseFile
from people import processPeople
from matches import processMatchesCB, processMatchesManual, parseManualInput, appendIfNotBlank

import urllib
import os
import time
import boto3

app = Flask(__name__)

app.secret_key = '\xbc\x01\x02V+d\xddByG\xb8ux\x94U\x1fu?qY\xb4\xe4Y\x89'

### queues - AWS SQS
sqs = boto3.resource('sqs', region_name='us-west-2')

queue1 = sqs.get_queue_by_name(QueueName='t1.fifo')
queue2 = sqs.get_queue_by_name(QueueName='t2.fifo')

##### ROUTES

@app.route('/')
def index():
	if 'username' in session:

		messages = read_queue1()
		messages2 = read_queue2()

		return render_template('index.html', messages=messages, messages2=messages2)
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login(name=None):
	# puts up a login to authenticate

	error = None
	if request.method == 'POST':
		if valid_login(request.form['username'],request.form['password']):
			session['username'] = request.form['username']
			return render_template('index.html', username=session['username'])
		else:
			error = 'Invalid username/password'

	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# not used anymore
@app.route('/s3/<path:path>')
def s3_file(path):
    return redirect('https://www.amazons3.com/user/file/{}'.format(path), code=301)

# read SQS queue #1
def read_queue1():
	messages = []

	for message in queue1.receive_messages(MessageAttributeNames=['type','action', 'payload1', 'payload2', 'payload3', 'payload4'], VisibilityTimeout=1, MaxNumberOfMessages=10, WaitTimeSeconds=5):
		# Get the custom author message attribute if it was set
		if message.message_attributes is not None:
			messageType = message.message_attributes.get('type').get('StringValue')
			if messageType == 'leader':
				action = message.message_attributes.get('action').get('StringValue')

				if action == "addLeaders":
					leader = message.message_attributes.get('payload1').get('StringValue')
					messages.append("Add leader command for %s" % leader)
				elif action == "deleteLeaders":
					leader = message.message_attributes.get('payload1').get('StringValue')
					messages.append("Delete leader command for %s" % leader)
				elif action == "updateLeader":
					leader = message.message_attributes.get('payload1').get('StringValue')
					messages.append("Update leader command for %s" % leader)
				elif action == "setLeaderType":
					leader = message.message_attributes.get('payload1').get('StringValue')
					setType = message.message_attributes.get('payload2').get('StringValue')
					messages.append("Set leader type for %s to %s" % (leader, setType))

			elif messageType == 'crunchbase':
				action = message.message_attributes.get('action').get('StringValue')
				if action == "csv":
					messages.append("CSV Update")
				elif action == "matches":
					email = message.message_attributes.get('payload1').get('StringValue')
					minA = message.message_attributes.get('payload2').get('RealValue')
					filterType = message.message_attributes.get('payload3').get('StringValue')
					otherFilter = message.message_attributes.get('payload4').get('StringValue')
					regionFilter = message.message_attributes.get('payload5').get('StringValue')
					
					messages.append("CB matches for %s with %f and %s, %s, %s" % (email, minA, filterType, otherFilter, regionFilter))
	return messages

# read SQS queue #2
def read_queue2():
	messages = []
	for message in queue2.receive_messages(MessageAttributeNames=['type','action', 'payload1', 'payload2']):
		# Get the custom author message attribute if it was set
		if message.message_attributes is not None:
			messageType = message.message_attributes.get('type').get('StringValue')
			if messageType == 'matches':
				action = message.message_attributes.get('action').get('StringValue')

				if action == "matches":
					people = message.message_attributes.get('payload1').get('StringValue')
					email = message.message_attributes.get('payload2').get('StringValue')
					messages.append("Manual matches for %s with query of %s" % (email, people))
				
	return messages

###########################################################
# Leaders
@app.route('/leaders')
def leaders():
	# pulls leaders to displays
	if 'username' in session:
		leaders_list = getAllLeaders()

		return render_template('leaders.html', leaders_list=leaders_list, num_leaders=len(leaders_list))
	return redirect(url_for('login'))

@app.route('/leaders/add_leaders', methods=['POST'])
def add_leaders():
	# processes adding leaders from twitter handles
	leader1 = request.form['leader1']
	type1 = request.form['leader1_type']
	leader2 = request.form['leader2']
	type2 = request.form['leader2_type']
	leader3 = request.form['leader3']
	type3 = request.form['leader3_type']
	leader4 = request.form['leader4']
	type4 = request.form['leader4_type']
	leader5 = request.form['leader5']
	type5 = request.form['leader5_type']


	if leader1:
		queue1.send_message(MessageBody='addLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()), MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'addLeaders',
							'DataType':'String'
						},
						'payload1': {'StringValue':leader1,'DataType':'String'},
						'payload2': {'StringValue':type1,'DataType':'String'}
					})
	if leader2:
		queue1.send_message(MessageBody='addLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'addLeaders',
							'DataType':'String'
						},
						'payload1': {'StringValue':leader2,'DataType':'String'},
						'payload2': {'StringValue':type2,'DataType':'String'}
					})
	if leader3:
		queue1.send_message(MessageBody='addLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'addLeaders',
							'DataType':'String'
						},
						'payload1': {'StringValue':leader3,'DataType':'String'},
						'payload2': {'StringValue':type3,'DataType':'String'}
					})
	if leader4:
		queue1.send_message(MessageBody='addLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'addLeaders',
							'DataType':'String'
						},
						'payload1': {'StringValue':leader4,'DataType':'String'},
						'payload2': {'StringValue':type4,'DataType':'String'}
					})
	if leader5:
		queue1.send_message(MessageBody='addLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'addLeaders',
							'DataType':'String'
						},
						'payload1': {'StringValue':leader5,'DataType':'String'},
						'payload2': {'StringValue':type5,'DataType':'String'}
					})

	leaders_list = getAllLeaders()
	return render_template('leaders.html', leaders_list=leaders_list, messages=["added leaders"])

@app.route('/leaders/delete_leaders', methods=['POST'])
def delete_leaders():

	leader1 = {'StringValue':request.form['leader1'],'DataType':'String'}
	leader2 = {'StringValue':request.form['leader2'],'DataType':'String'}
	leader3 = {'StringValue':request.form['leader3'],'DataType':'String'}
	leader4 = {'StringValue':request.form['leader4'],'DataType':'String'}
	leader5 = {'StringValue':request.form['leader5'],'DataType':'String'}

	if leader1['StringValue']:
		queue1.send_message(MessageBody='removeLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()), MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'removeLeaders',
							'DataType':'String'
						},
						'payload1': leader1
					})
	if leader2['StringValue']:
		queue1.send_message(MessageBody='removeLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()), MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'removeLeaders',
							'DataType':'String'
						},
						'payload1': leader2
					})
	if leader3['StringValue']:
		queue1.send_message(MessageBody='removeLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'removeLeaders',
							'DataType':'String'
						},
						'payload1': leader3
					})
	if leader4['StringValue']:
		queue1.send_message(MessageBody='removeLeaders', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'removeLeaders',
							'DataType':'String'
						},
						'payload1': leader4
					})
	if leader5['StringValue']:
		queue1.send_message(MessageBody='removeLeaders', MessageGroupId='t1',MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'removeLeaders',
							'DataType':'String'
						},
						'payload1': leader5
					})
	
	
	leaders_list = getAllLeaders()
	return render_template('leaders.html', leaders_list=leaders_list, messages=["remove leaders"])

@app.route('/leaders/update_leader', methods=['POST'])
def update_leader():
	# update is to remove and re-add leader to refresh folllowers list
	leader = {'StringValue':request.form['leader'],'DataType':'String'}
	# leader = request.form['leader']
	# updateLeader(leader)

	queue1.send_message(MessageBody='updateLeader', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'updateLeader',
							'DataType':'String'
						},
						'payload1': leader
					})
	

	leaders_list = getAllLeaders()
	return render_template('leaders.html', leaders_list=leaders_list, messages=["updated leader"])

@app.route('/leaders/set_leader_type', methods=['POST'])
def set_leader_type():
	# to change leader type (A, B)
	leader = {'StringValue':request.form['leader'],'DataType':'String'}
	leader_type = {'StringValue':request.form['leader_type'],'DataType':'String'}
	# setLeaderType(leader, leader_type)

	queue1.send_message(MessageBody='setLeaderType', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'setLeaderType',
							'DataType':'String'
						},
						'payload1': leader,
						'payload2': leader_type
					})

	leaders_list = getAllLeaders()
	return render_template('leaders.html', leaders_list=leaders_list, messages=["set leader type"])


#########################################################
# CRUNCHBASE #
@app.route('/crunchbase')
def crunchbase():
	if 'username' in session:
		status = getCrunchbaseStatus()
		if status:
			return render_template('crunchbase.html', messages=[status])
		else:
			return render_template('crunchbase.html')
	return redirect(url_for('login'))

@app.route('/crunchbase/update_crunchbase_file', methods=['POST'])
def update_crunchbase():
	# if getCrunchbaseDump():
	# 	processPeople()
	queue1.send_message(MessageBody='crunchbaseCSV', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'crunchbase',
							'DataType':'String'
						},
						'action': {
							'StringValue':'csv',
							'DataType':'String'
						}
					})
	return render_template('crunchbase.html', messages=["Updating crunchbase file"])

@app.route('/crunchbase/delete_crunchbase_file', methods=['POST'])
def delete_crunchbase():
	removeCrunchbaseFile()
	return render_template('crunchbase.html', messages=["Deleted crunchbase file"])

@app.route('/crunchbase/process_export_matches', methods=['POST'])
def process_export_matches():
	f = request.form

	if 'email' in f.keys():
		email = {'StringValue':request.form['email'],'DataType':'String'}
	else:
		email = {'StringValue':"",'DataType':'String'}
	if 'minA' in f.keys():
		minA = {'StringValue':request.form['minA'],'DataType':'String'}

	# confidence = request.form['confidence']
	filterType = {'StringValue':request.form['type'],'DataType':'String'}
	if request.form['other-filter']:
		otherFilter = {'StringValue':request.form['other-filter'],'DataType':'String'}
	else:
		otherFilter = {'StringValue':"empty",'DataType':'String'}
	if request.form['region']:
		region = {'StringValue':request.form['region'],'DataType':'String'}
	queue1.send_message(MessageBody='crunchbaseMatches', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'crunchbase',
							'DataType':'String'
						},
						'action': {
							'StringValue':'matches',
							'DataType':'String'
						},
						'payload1': email,
						'payload2': minA,
						'payload3': filterType,
						'payload4': otherFilter,
						'payload5': region,
					})

	return render_template('crunchbase.html', messages=["processing matches, will email you when complete"])

def getCrunchbaseStatus():
	if os.path.isfile("log/cb-status.txt"):
		with open("log/cb-status.txt") as dataFile: 
			s = dataFile.read()
			return s

#########################################################
# manual processing of twitter handles
@app.route('/manual')
def manual():
	if 'username' in session:

		return render_template('manual.html')
	return redirect(url_for('login'))

@app.route('/manual/process_manual', methods=['POST'])
def process_manual():
	f = request.form
	userInput = request.form['people']

	
	if 'sendEmail' in f.keys() and 'email' in f.keys() and len(userInput) > 0:
		people = {'StringValue':userInput,'DataType':'String'}
		sendEmail = {'StringValue':request.form['sendEmail'],'DataType':'String'}
		email = {'StringValue':request.form['email'],'DataType':'String'}

		if 'people' in f.keys():
			queue2.send_message(MessageBody='matches', MessageGroupId='t2', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'matches',
							'DataType':'String'
						},
						'action': {
							'StringValue':'matches',
							'DataType':'String'
						},
						'payload1': people,
						'payload2': email
					})
			return render_template('manual.html', messages=["processing matches, will email you when complete"])	
	else:
		email = ''
		if 'people' in f.keys():
			people = parseManualInput(userInput)
			if len(people) < 4:
				matches = processMatchesManual(people, email)
				return render_template('manual.html', matches=matches)
			else:
				return render_template('manual.html', messages=["Too many handles for results in browser.  Please add an email address to send the results to."])
	return render_template('manual.html')

#########################################################
# helpers
def valid_login(username, password):
	if username=="sovereign" and password=="capital":
		return True
	return False

if __name__ == "__main__":

	# dir = os.path.dirname(__file__)

	# url = "https://proj-ripple-assets.s3.amazonaws.com/asdf.txt"
	# fileName = os.path.join(dir, "data/sqlite/test.txt")
	# file = urllib.URLopener()
	# file.retrieve(url, fileName)	
	# port = int(os.environ.get('PORT', 5000))
	# app.run(host='0.0.0.0', port=port)
	app.run(threaded=True)