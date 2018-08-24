## This script manages messages coming in regarding leader attributes and crunchbase functions

from leaders import addLeaders, removeLeaders, setLeaderType, getLeaderType
from people import processPeople
from crunchbase import getCrunchbaseDump
from matches import processMatchesCB

import time
import boto3

### queues - AWS SQS
sqs = boto3.resource('sqs', region_name='us-west-2')

queue1 = sqs.get_queue_by_name(QueueName='t1.fifo')
queue2 = sqs.get_queue_by_name(QueueName='t2.fifo')
#queue3 = sqs.get_queue_by_name(QueueName='t3.fifo')

while(1):
	# Process messages by printing out body and optional author name


	for message in queue1.receive_messages(MessageAttributeNames=['type','action', 'payload1', 'payload2', 'payload3', 'payload4', 'payload5'], VisibilityTimeout=1, MaxNumberOfMessages=10, WaitTimeSeconds=5):
		# Get the custom author message attribute if it was set
		if message.message_attributes is not None:
			messageType = message.message_attributes.get('type').get('StringValue')
			if messageType == 'leader':

				# Let the queue know that the message is processed
				message.delete()
				
				action = message.message_attributes.get('action').get('StringValue')



				if action == "addLeaders":
					handle = message.message_attributes.get('payload1').get('StringValue')
					leaderType = message.message_attributes.get('payload2').get('StringValue')
					leader = {"handle" : handle, "type" : leaderType}
					addLeaders(leader)
				elif action == "removeLeaders":
					leader = message.message_attributes.get('payload1').get('StringValue')
					removeLeaders(leader)
				elif action == "updateLeader":
					leader = message.message_attributes.get('payload1').get('StringValue')
					leaderType = getLeaderType(leader)
					removeLeaders(leader)
					addLeaders(({"handle": leader, "type":leaderType}))
				elif action == "setLeaderType":
					leader = message.message_attributes.get('payload1').get('StringValue')
					setType = message.message_attributes.get('payload2').get('StringValue')
					setLeaderType(leader, setType)


			elif messageType == 'crunchbase':
				# Let the queue know that the message is processed
				message.delete()

				action = message.message_attributes.get('action').get('StringValue')
				if action == "csv":
					if getCrunchbaseDump():
						processPeople()
				elif action == "matches":

					email = message.message_attributes.get('payload1').get('StringValue')
					minA = message.message_attributes.get('payload2').get('StringValue')
					filterType = message.message_attributes.get('payload3').get('StringValue')
					otherFilter = message.message_attributes.get('payload4').get('StringValue')
					region = message.message_attributes.get('payload5').get('StringValue')
					processMatchesCB(email, int(minA), filterType, otherFilter, region)

