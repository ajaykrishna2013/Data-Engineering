from confluent_kafka import Consumer, KafkaError

#c = Consumer({'bootstrap.servers':'127.0.0.1:9092', 'group.id':'mygroup', 'default.topic.config':{'auto.offset.reset':'smallest'}})
c = Consumer({'bootstrap.servers':'54.69.161.38:9092', 'group.id':'mygroup', 'default.topic.config':{'auto.offset.reset':'smallest'}})
c.subscribe(['first_topic', 'second_topic'])

running = True
while running:
	msg = c.poll()
	if not msg.error():
		print('Received message %s' % (msg.value().decode('utf-8')))
	elif msg.error().code() != KafkaError._PARTITION_EOF:
		print(msg.error())
		running = False
c.close()
