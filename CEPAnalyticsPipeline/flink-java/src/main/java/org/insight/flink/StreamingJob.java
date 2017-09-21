
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


import org.apache.flink.api.java.tuple.*;
import org.apache.flink.cep.CEP;
import org.apache.flink.cep.PatternSelectFunction;
import org.apache.flink.cep.PatternFlatSelectFunction;
import org.apache.flink.cep.PatternFlatTimeoutFunction;
import org.apache.flink.cep.PatternStream;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.SimpleCondition;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.types.Either;

import java.util.Properties;
import com.google.gson.Gson;
import org.apache.flink.api.common.functions.*;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.streaming.api.functions.timestamps.AscendingTimestampExtractor;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
//import org.apache.flink.streaming.api.functions.sink;
import org.apache.flink.streaming.api.datastream.DataStreamSink;
import org.apache.flink.streaming.api.functions.sink.PrintSinkFunction;
import org.apache.flink.streaming.api.functions.IngestionTimeExtractor;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer09;
import org.apache.flink.streaming.util.serialization.SimpleStringSchema;

import java.util.Date;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Random;
//Cassandra Stuff
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
	private static final String INSERT_SMART_HOME_USAGE_GENERATION = "INSERT INTO cep_analytics.smarthome_usage_gen_table (home_id, generation, usage, event_time) VALUES (?, ?, ?, ?)";
	private static final String INSERT_CEP = "INSERT INTO cep_analytics.smarthome_cep_table (home_id, event_time, event_description, event_severity, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)";

	public class CepTuple extends Tuple8<Integer,Date,String,String,Float,Float,Float,Float> {
		public CepTuple (Integer _0, Date _1, String _2, String _3, Float _4, Float _5, Float _6, Float _7) {
			super(_0, _1, _2, _3, _4, _5, _6, _7);
		}
	}


	public static class ConvertToGson implements FlatMapFunction<String, Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> {

		@Override
		public void flatMap(String s, Collector<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> collector) throws Exception {
			Gson gson = new Gson();
			Map<String, String> map = new HashMap<String, String>();
			Map<String, String> myMap = gson.fromJson(s, map.getClass());

			String[] event_class = {"Medium", "Low", "High", "Non-event"};
			Random random = new Random();
			int index = random.nextInt(event_class.length);

			DateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
			Date date = format.parse(myMap.get("time"));

			Integer home_id = Integer.parseInt(myMap.get("home_id"));
			Float latitude = Float.parseFloat(myMap.get("LAT"));
			Float longitude = Float.parseFloat(myMap.get("LONG"));
			Float usage = Float.parseFloat(myMap.get("usage"));
			Float generation = Float.parseFloat(myMap.get("generation"));
			String event_descr = "complex event";
			String event_severity = event_class[index];

			Tuple8<Integer,Date,String,String,Float,Float,Float,Float> t_u_map = new Tuple8<>();
			t_u_map.setFields(home_id, date, event_descr, event_severity, latitude, longitude, usage, generation);


			collector.collect(t_u_map);
		}
	}

	public static class CaptureEvents implements 
		PatternSelectFunction<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>, Tuple6<Integer, Date, String, String, Float, Float>> {
		@Override
		public Tuple6<Integer, Date, String, String, Float, Float> select(Map<String, List<Tuple8<Integer, Date, String, String, Float, Float, Float, Float>>> pattern) 
			throws Exception {

			Tuple8<Integer, Date, String, String, Float, Float, Float, Float>	startEvent = pattern.get("start").get(0);
			Tuple8<Integer, Date, String, String, Float, Float, Float, Float>	endEvent = pattern.get("end").get(0);
			Tuple6<Integer, Date, String, String, Float, Float> outEvent = new Tuple6<>();

			outEvent.setField(endEvent.getField(0), 0);
			outEvent.setField(endEvent.getField(1), 1);
			outEvent.setField(endEvent.getField(2), 2);
			outEvent.setField(endEvent.getField(3), 3);
			outEvent.setField(endEvent.getField(4), 4);
			outEvent.setField(endEvent.getField(5), 5);

			return outEvent;
		}
	}



	public static void main(String[] args) throws Exception {
		// set up the streaming execution environment
		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
		env.enableCheckpointing(1000);
		
		Properties properties = new Properties();
		properties.setProperty("bootstrap.servers", "52.24.35.74:9092");
		properties.setProperty("zookeeper.connect", "52.24.35.74:2181");
		properties.setProperty("group.id", "flink_SmartHome_Consumer");


		DataStream<String> stream = env.
			addSource(new FlinkKafkaConsumer09<>( 
				"SmartHomeMeterTopic", 
				new SimpleStringSchema(), 
				properties));

//		DataStream<Tuple6<Integer,Date,String,String,Float,Float>> cepMap = stream.flatMap(new FlatMapFunction<String, Tuple6<Integer,Date,String,String,Float,Float>>() {
//			@Override
//			public void flatMap(String s, Collector<Tuple6<Integer,Date,String,String,Float,Float>> collector) throws Exception {
//				Gson gson = new Gson();
//				Map<String, String> map = new HashMap<String, String>();
//				Map<String, String> myMap = gson.fromJson(s, map.getClass());
//
//			    	String[] event_class = {"Medium", "Low", "High", "Non-event"};
//			    	Random random = new Random();
//			    	int index = random.nextInt(event_class.length);
//
//				DateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
//				Date date = format.parse(myMap.get("time"));
//
//				Integer home_id = Integer.parseInt(myMap.get("home_id"));
//				Float latitude = Float.parseFloat(myMap.get("LAT"));
//				Float longitude = Float.parseFloat(myMap.get("LONG"));
//				//Float usage = Float.parseFloat(myMap.get("usage"));
//				//Float generation = Float.parseFloat(myMap.get("generation"));
//			    	String event_descr = "complex event";
//			   	String event_severity = event_class[index];
//            		    
//			    	Tuple6<Integer,Date,String,String,Float,Float> t_u_map = new Tuple6<>();
//				t_u_map.setFields(home_id, date, event_descr, event_severity, latitude, longitude);
//				collector.collect(t_u_map);
//			}
//		});

		
		DataStream<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> cepMap = stream
			.flatMap(new ConvertToGson());		


		//DataStream<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> cepMap = stream
		//	.flatMap(new FlatMapFunction<String, Tuple8<Integer,Date,String,String,Float,Float,Float,Float>>() {
		//	
		//	@Override
		//	public void flatMap(String s, Collector<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> collector) throws Exception {
		//		Gson gson = new Gson();
		//		Map<String, String> map = new HashMap<String, String>();
		//		Map<String, String> myMap = gson.fromJson(s, map.getClass());

		//	    	String[] event_class = {"Medium", "Low", "High", "Non-event"};
		//	    	Random random = new Random();
		//	    	int index = random.nextInt(event_class.length);

		//		DateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
		//		Date date = format.parse(myMap.get("time"));

		//		Integer home_id = Integer.parseInt(myMap.get("home_id"));
		//		Float latitude = Float.parseFloat(myMap.get("LAT"));
		//		Float longitude = Float.parseFloat(myMap.get("LONG"));
		//		Float usage = Float.parseFloat(myMap.get("usage"));
		//		Float generation = Float.parseFloat(myMap.get("generation"));
		//	    	String event_descr = "complex event";
		//	   	String event_severity = event_class[index];
            	//	    
		//	    	Tuple8<Integer,Date,String,String,Float,Float,Float,Float> t_u_map = new Tuple8();
		//		t_u_map.setFields(home_id, date, event_descr, event_severity, latitude, longitude, usage, generation);
		//		

		//		collector.collect(t_u_map);
		//	}
		//});

		DataStream<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> cepMapTimedValue = 
			cepMap.assignTimestampsAndWatermarks(new AscendingTimestampExtractor<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>>() {
        		@Override
        		public long extractAscendingTimestamp(Tuple8<Integer,Date,String,String,Float,Float,Float,Float> element) {
				long timeMs = element.f1.getTime();
        		    	return timeMs;
        		}
		});


		DataStream<Tuple8<Integer,Date,String,String,Float,Float,Float, Float>> cepMapByHomeId = cepMapTimedValue.keyBy(0);

		//cepMapByHomeId.print();


		Pattern<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>, ?> cep1 =
				Pattern.<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>>begin("start")
				.where(new SimpleCondition<Tuple8<Integer, Date, String, String, Float, Float, Float, Float>>() {
					@Override
					public boolean filter(Tuple8<Integer, Date, String, String, Float, Float, Float, Float> event1) throws Exception {
						//return event1.f6 > 8.0f;
						Float overLowThreshold = 0.6f * event1.f7;
						if (event1.f6 >= overLowThreshold)
							return true;
						else
							return false;
					}
				})
				.followedBy("end")
				.where(new SimpleCondition<Tuple8<Integer, Date, String, String, Float, Float, Float, Float>>() {
					@Override
					public boolean filter(Tuple8<Integer, Date, String, String, Float, Float, Float, Float> event2) throws Exception {
						Float overHighThreshold = 0.8f * event2.f7;
						if (event2.f6 >= overHighThreshold)
							return true;
						else
							return false;
					}
				});

		PatternStream<Tuple8<Integer, Date, String, String, Float, Float, Float, Float>> patternStream = CEP.pattern(cepMapByHomeId, cep1);


		DataStream<Tuple6<Integer, Date, String, String, Float, Float>> alerts = patternStream.select(new CaptureEvents());

		//alerts.print();

		CassandraSink.addSink(alerts)
				.setQuery(INSERT_CEP)
				.setClusterBuilder(new ClusterBuilder() {
					@Override
					protected Cluster buildCluster(Builder builder) {
						return builder.addContactPoint("10.0.0.10").build();
					}
				}).build();



		
		//DataStream<Tuple4<Integer,Float,Float,Date>> time_usage_map = stream.flatMap(new FlatMapFunction<String, Tuple4<Integer,Float,Float,Date>>() {
            	//	@Override
            	//	public void flatMap(String s, Collector<Tuple4<Integer,Float,Float,Date>> collector) throws Exception {
            	//	    Gson gson = new Gson();
            	//	    Map<String, String> map = new HashMap<String, String>();
            	//	    Map<String, String> myMap = gson.fromJson(s, map.getClass());

            	//	    DateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
            	//	    Date date = format.parse(myMap.get("time"));

            	//	    Integer home_id = Integer.parseInt(myMap.get("home_id"));
            	//	    Float usage = Float.parseFloat(myMap.get("usage"));
            	//	    Float generation = Float.parseFloat(myMap.get("generation"));
            	//	    
		//	    Tuple4<Integer,Float,Float,Date> t_u_map = new Tuple4<>();
            	//	    t_u_map.setFields(home_id, usage, generation, date);

            	//	    collector.collect(t_u_map);
            	//	}
        	//});

        	// CassandraSink.addSink(time_usage_map)
        	//         .setQuery(INSERT_SMART_HOME_USAGE_GENERATION)
        	//         .setClusterBuilder(new ClusterBuilder() {
        	//             @Override
        	//             protected Cluster buildCluster(Builder builder) {
        	//                 return builder.addContactPoint("10.0.0.10").build();
        	//             }
        	//         }).build();


		//  SingleOutputStreamOperator<String> time_and_usage = stream.map(new MapFunction<String, String>() {
		//	  private static final long serialVersionUID = -6867736771747690202L;
		//
		//	  @Override
		//	  public String map(String value) throws Exception {
		//	      	Gson gson = new Gson();
		//        	Map<String, String> map = new HashMap<String, String>();
		//       	 	Map<String, String> myMap = gson.fromJson(value, map.getClass());
		//
		//	    return myMap.get("time")+","+myMap.get("usage");
		//	  }
		//	});
		//
		//	// Adding cassandra sink
		//	DataStreamSource<Tuple2<String, Integer>> source = env.fromCollection(collection);
		//
		//
		//
		//	CassandraSink.addSink(source)
		//		.setQuery(INSERT)
		//		.setClusterBuilder(new ClusterBuilder() {
		//			@Override
		//			protected Cluster buildCluster(Builder builder) {
		//				return builder.addContactPoint("10.0.0.10").build();
		//			}
		//		})
		//		.build();
		
		//		env.execute("WriteTupleIntoCassandra");
		// Added cassandra sink

		// execute program
		env.execute("Flink Streaming Java API Skeleton");
	}
}
