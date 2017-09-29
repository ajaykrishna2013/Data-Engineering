/*
Schema for storing raw ISD-lite hourly weather data.
More can be read about these weather sets here: http://www.ncdc.noaa.gov/oa/climate/isd/
*/

DROP KEYSPACE IF EXISTS cep_analytics;
CREATE KEYSPACE cep_analytics WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

use cep_analytics;

/*
Weather stations that correspond with collected raw weather data.
*/

CREATE TABLE smarthome_usage_gen_table (
    home_id int,
    generation float,           
    usage float,            	 
    event_start_time timestamp,    
    event_end_time timestamp,    
    PRIMARY KEY (home_id, event_start_time)
)WITH CLUSTERING ORDER BY (event_start_time DESC);

CREATE TABLE smarthome_cep_table (
    home_id int,
    event_start_time timestamp,    
    event_end_time timestamp,    
    event_description text,
    event_severity text,
    latitude float, 
    longitude float,
    PRIMARY KEY (event_description, event_start_time)
)WITH CLUSTERING ORDER BY (event_start_time DESC);

