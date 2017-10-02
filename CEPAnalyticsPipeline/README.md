# Motivation:

A Smart grid is an electrical grid which includes a variety of operational and energy measures from smart meters, smart appliances, renewable energy sources. 
An inherently complex system which is rapidly growing. A smart home in the present has multiple devices capable of transmitting valuable information about itself. 
As more number of homes add more devices, data will be generated fast and volume of data will continue to grow. 

The data itself will be a collection of complex events or patterns. It will be useful to detect event patterns in an endless stream of events, giving you the opportunity to quick get hold of what’s really important in your data

Example: Detection of divergence between the energy consumption and energy production

## CEP Engine

A CEP engine is a platform for building and running applications used to process and analyze large number of real time events

## Processing:
- Simple Patterns
  - Has the average energy generation fallen below a Threshold
- Iterative Patterns
  - Specify a condition that accepts subsequent events based on properties of the previously accepted events
- Looping Patterns
  - Has that happened multiple times within the last 30 seconds

## Pipeline

- AWS cluster
- 3 Node Kafka
- 3 Node Flink
- 3 Node Cassandra

![Alt text](https://github.com/ajaykrishna2013/Data-Engineering/blob/master/CEPAnalyticsPipeline/app/templates/Pipeline.png)
