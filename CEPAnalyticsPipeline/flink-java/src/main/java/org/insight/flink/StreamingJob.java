
package org.insight.flink;
/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.util.Properties;
import java.util.List;
import java.util.Map;
import java.util.Date;
import java.io.InputStream;
import java.io.FileInputStream;
import java.io.IOException;
//time and gson modules
import com.google.gson.Gson;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.text.ParseException;
//CEP modules
import org.apache.flink.api.java.tuple.*;
import org.apache.flink.cep.CEP;
import org.apache.flink.cep.PatternSelectFunction;
import org.apache.flink.cep.PatternStream;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.SimpleCondition;
import org.apache.flink.streaming.api.TimeCharacteristic;

//Streaming modules
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.functions.timestamps.BoundedOutOfOrdernessTimestampExtractor;
import org.apache.flink.streaming.api.functions.timestamps.AscendingTimestampExtractor;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;

//Kafka modules
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer09;
import org.apache.flink.streaming.util.serialization.SimpleStringSchema;


//Cassandra Stuff
import org.apache.flink.streaming.connectors.cassandra.CassandraSink;
import org.apache.flink.streaming.connectors.cassandra.ClusterBuilder;
import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.Cluster.Builder;


public class StreamingJob {
	
	//Insert Query
	private static final String INSERT_CEP = "INSERT INTO cep_analytics.smarthome_cep_table " +
						 "(home_id, event_start_time, event_end_time, event_description, event_severity, latitude, longitude) " +
						 "VALUES (?, ?, ?, ?, ?, ?, ?)";

	//Define Pattern Classes
	public static class OverLowThreshold extends SimpleCondition<Tuple8<Integer, Date, String, String, Float, Float, Float, Float>> {
		@Override
		public boolean filter(Tuple8<Integer, Date, String, String, Float, Float, Float, Float> event1) throws Exception {
			Float overLowThreshold = 0.6f * event1.f7;
			if (event1.f6 >= overLowThreshold)
				return true;
			else
				return false;
		}
	}

	public static class OverHighThreshold extends SimpleCondition<Tuple8<Integer, Date, String, String, Float, Float, Float, Float>> {
		@Override
		public boolean filter(Tuple8<Integer, Date, String, String, Float, Float, Float, Float> event2) throws Exception {
			Float overHighThreshold = 0.8f * event2.f7;
			if (event2.f6 >= overHighThreshold)
				return true;
			else
				return false;
		}
	}

	public static Properties getConfig(String filename) {
	    	Properties cfg = new Properties();
	    
	    	try {
	    	  InputStream input = new FileInputStream(filename);
	    	  cfg.load(input);
	    	} catch (IOException e) {
	    	  System.out.println("Could not load config file.");
	    	  System.out.println(e.getMessage());
	    	}
	    	
	    	return cfg;
	  }


	public static void main(String[] args) throws Exception {
		// set up the streaming execution environment
		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
		env.setParallelism(4);
		env.enableCheckpointing(5000);
		
		//retrieve configuration
		Properties cfg = getConfig("config.properties");
    		final String kafkaConnect = cfg.getProperty("bootstrap.servers");
    		final String zookeeperConnect = cfg.getProperty("zookeeper.connect");
    		final String cassandraConnect = cfg.getProperty("cassandra.connect");
		
		Properties properties = new Properties();
		properties.setProperty("bootstrap.servers", kafkaConnect);
		properties.setProperty("zookeeper.connect", zookeeperConnect);
		properties.setProperty("group.id", "flinkSmartHomeConsumer");


		FlinkKafkaConsumer09<String> kafkaSource = new FlinkKafkaConsumer09<>("SHMeterTopic2", new SimpleStringSchema(), properties);
	
		//Extract Ascending timestamp from kafka source
		kafkaSource.assignTimestampsAndWatermarks(new AscendingTimestampExtractor<String>() {
			@Override
			public long extractAscendingTimestamp(String s) {
				Gson gson = new Gson();
				Map<String, String> map = new HashMap<String, String>();
				Map<String, String> myMap = gson.fromJson(s, map.getClass());

				DateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSSSS");
				
				try {
					Date date = format.parse(myMap.get("time"));
					System.out.print(date);
					return date.getTime();
				} catch (ParseException e) {
					e.printStackTrace();
				}
				return (long) 1.0;
			}
		});


		//Add Kafka Source to env
		DataStream<String> stream = env.addSource(kafkaSource);

		//Unpack the Event Stream
		DataStream<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> cepMap = stream
			.flatMap(new UnpackEventStream());

		
		//cepMap.print();

		DataStream<Tuple8<Integer,Date,String,String,Float,Float,Float, Float>> cepMapByHomeId = cepMap.keyBy(0);

		cepMapByHomeId.print();

		//Define Chained Pattern
		Pattern<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>, ?> detectThresholdPattern =
				Pattern.<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>>begin("start")
						.where(new OverLowThreshold())
						.followedBy("end")
						.where(new OverHighThreshold())
						.within(Time.seconds(30));

		//Apply pattern
		PatternStream<Tuple8<Integer, Date, String, String, Float, Float, Float, Float>> patternStream = CEP.pattern(cepMapByHomeId, detectThresholdPattern);


		DataStream<Tuple7<Integer, Date, Date, String, String, Float, Float>> alerts = patternStream.select(new PackageCapturedEvents());

		alerts.print();

		//Send to Cassandra
		CassandraSink.addSink(alerts)
				.setQuery(INSERT_CEP)
				.setClusterBuilder(new ClusterBuilder() {
					@Override
					protected Cluster buildCluster(Builder builder) {
						return builder.addContactPoint("10.0.0.10").build();
					}
				}).build();


		// execute program
		env.execute("Flink Streaming");
	}
}
