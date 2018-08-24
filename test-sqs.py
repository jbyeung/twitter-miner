import time
import boto3

## This tests the AWS SQS system by sending a message to each queue, then check it in portal

### queues - AWS SQS
sqs = boto3.resource('sqs', region_name='us-west-2')

queue1 = sqs.get_queue_by_name(QueueName='t1.fifo')
queue1.send_message(MessageBody='addLeader', MessageGroupId='t1', MessageDeduplicationId=str(time.time()),  MessageAttributes={
						'type': {
							'StringValue':'leader',
							'DataType':'String'
						},
						'action': {
							'StringValue':'addLeader',
							'DataType':'String'
						},
						'payload1': {
							'StringValue':'jbyeung',
							'DataType':'String'
						},
						'payload2': {
							'StringValue':'A',
							'DataType':'String'
						}
					})


queue2 = sqs.get_queue_by_name(QueueName='t2.fifo')
people = {'StringValue':'jbyeung','DataType':'String'}
email = {'StringValue':'jbyeung@gmail.com','DataType':'String'}

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
queue3 = sqs.get_queue_by_name(QueueName='t3.fifo')
queue3.send_message(MessageBody='mutex', MessageGroupId='t3', MessageDeduplicationId=str(time.time()),  MessageAttributes={
				'type': {
					'StringValue':'mutex',
					'DataType':'String'
				},
				'action': {
					'StringValue':'block2',
					'DataType':'String'
				}
			})