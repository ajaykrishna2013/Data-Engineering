
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
import com.google.gson.Gson;
import org.apache.flink.api.common.functions.*;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer09;
import org.apache.flink.streaming.util.serialization.SimpleStringSchema;

import java.util.Date;
import java.text.DateFormat;
import java.text.SimpleDateFormat;

//Cassandra Stuff
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.connectors.cassandra.CassandraSink;
import org.apache.flink.streaming.connectors.cassandra.ClusterBuilder;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.Cluster.Builder;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.util.Collector;


import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


public class StreamingJob {
	private static final String INSERT = "INSERT INTO smart_home.smarthome_event_usage (event_time, usage) VALUES (?, ?)";
	private static final ArrayList<Tuple2<String, Integer>> collection = new ArrayList<>(20);

	static {
		for (int i = 0; i < 20; i++) {
			collection.add(new Tuple2<>("event 1-" + i, i));
		}
	}


	public static void main(String[] args) throws Exception {
		// set up the streaming execution environment
		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		
		Properties properties = new Properties();
		properties.setProperty("bootstrap.servers", "52.24.35.74:9092");
		properties.setProperty("zookeeper.connect", "52.24.35.74:2181");
		properties.setProperty("group.id", "flink_SmartHome_Consumer");
		
		DataStream<String> stream = env.addSource(new FlinkKafkaConsumer09<>( "SmartHome_A", new SimpleStringSchema(), properties) );
		
		//writeElastic(stream);
		DataStream<Tuple2<Date,Float>> time_usage_map = stream.flatMap(new FlatMapFunction<String, Tuple2<Date, Float>>() {
            		@Override
            		public void flatMap(String s, Collector<Tuple2<Date, Float>> collector) throws Exception {
            		    Gson gson = new Gson();
            		    Map<String, String> map = new HashMap<String, String>();
            		    Map<String, String> myMap = gson.fromJson(s, map.getClass());

            		    DateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
            		    Date date = format.parse(myMap.get("time"));

            		    Float usage = Float.parseFloat(myMap.get("usage"));
            		    Tuple2<Date, Float> t_u_map = new Tuple2<>();
            		    t_u_map.setFields(date, usage);

            		    collector.collect(t_u_map);
            		}
        	});

        	CassandraSink.addSink(time_usage_map)
        	        .setQuery(INSERT)
        	        .setClusterBuilder(new ClusterBuilder() {
        	            @Override
        	            protected Cluster buildCluster(Builder builder) {
        	                return builder.addContactPoint("10.0.0.10").build();
        	            }
        	        }).build();


//        SingleOutputStreamOperator<String> time_and_usage = stream.map(new MapFunction<String, String>() {
//		  private static final long serialVersionUID = -6867736771747690202L;
//
//		  @Override
//		  public String map(String value) throws Exception {
//		      	Gson gson = new Gson();
//              	Map<String, String> map = new HashMap<String, String>();
//             	 	Map<String, String> myMap = gson.fromJson(value, map.getClass());
//
//		    return myMap.get("time")+","+myMap.get("usage");
//		  }
//		});
//
//		// Adding cassandra sink
//		DataStreamSource<Tuple2<String, Integer>> source = env.fromCollection(collection);
//
//
//
//		CassandraSink.addSink(source)
//			.setQuery(INSERT)
//			.setClusterBuilder(new ClusterBuilder() {
//				@Override
//				protected Cluster buildCluster(Builder builder) {
//					return builder.addContactPoint("10.0.0.10").build();
//				}
//			})
//			.build();

		env.execute("WriteTupleIntoCassandra");
		// Added cassandra sink



		/**
		 * Here, you can start creating your execution plan for Flink.
		 *
		 * Start with getting some data from the environment, like
		 * 	env.readTextFile(textPath);
		 *
		 * then, transform the resulting DataStream<String> using operations
		 * like
		 * 	.filter()
		 * 	.flatMap()
		 * 	.join()
		 * 	.coGroup()
		 *
		 * and many more.
		 * Have a look at the programming guide for the Java API:
		 *
		 * http://flink.apache.org/docs/latest/apis/streaming/index.html
		 *
		 */

		// execute program
		env.execute("Flink Streaming Java API Skeleton");
	}
}
