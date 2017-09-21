package org.insight.flink;

import org.apache.flink.api.java.tuple.Tuple6;
import org.apache.flink.api.java.tuple.Tuple8;
import org.apache.flink.cep.PatternSelectFunction;

import java.util.Date;
import java.util.List;
import java.util.Map;

public class PackageCapturedEvents implements
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