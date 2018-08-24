
# This script manages manual calls to process matches

from matches import processMatchesManual
import time
import boto3


### queues - AWS SQS
sqs = boto3.resource('sqs', region_name='us-west-2')

queue1 = sqs.get_queue_by_name(QueueName='t1.fifo')
queue2 = sqs.get_queue_by_name(QueueName='t2.fifo')
#queue3 = sqs.get_queue_by_name(QueueName='t3.fifo')


while(1):
	# Process messages by printing out body and optional author name

			
	for message in queue2.receive_messages(MessageAttributeNames=['type','action', 'payload1', 'payload2'], VisibilityTimeout=1, MaxNumberOfMessages=10, WaitTimeSeconds=5):
		# Get the custom author message attribute if it was set
		
		if message.message_attributes is not None:
			messageType = message.message_attributes.get('type').get('StringValue')
			if messageType == 'matches':

				action = message.message_attributes.get('action').get('StringValue')


				if action == "matches":
					people = message.message_attributes.get('payload1').get('StringValue')
					email = message.message_attributes.get('payload2').get('StringValue')
					message.delete()
					processMatchesManual(people, email, True)
					
