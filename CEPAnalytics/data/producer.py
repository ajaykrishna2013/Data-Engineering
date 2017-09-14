from confluent_kafka import Producer

#p = Producer({'bootstrap.servers':'127.0.0.1:9092'})
p = Producer({'bootstrap.servers':'54.69.161.38:9092'})
for i in range(200,210,1):
	p.produce('first_topic', 'text from python proc'+str(i), str(i))
p.flush()
