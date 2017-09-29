package org.insight.flink;

import com.google.gson.Gson;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple8;
import org.apache.flink.util.Collector;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class UnpackEventStream implements 
	FlatMapFunction<String, Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> {

    @Override
    public void flatMap(String s, 
	Collector<Tuple8<Integer,Date,String,String,Float,Float,Float,Float>> collector) 
		throws Exception {
        
	Gson gson = new Gson();
        Map<String, String> map = new HashMap<String, String>();
        Map<String, String> myMap = gson.fromJson(s, map.getClass());

        String[] event_class = {"Medium", "Low", "High"};
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
