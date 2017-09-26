import pandas as pd

Norcal_df = pd.read_csv('NorCal2.csv')
HomeAMeterAnomaly_df = pd.read_csv('HomeAMeterAnomaly2.csv')
HomeAWeather_df = pd.read_csv('HomeAWeather.csv')

for index, row in Norcal_df.iterrows():
	#name for meter data
        filenameMeter = 'HomesMeterData/Home'+str(index)+'MeterAnomaly.csv'
	#name for weather data
        filenameWeather = 'HomesWeatherData/Home'+str(index)+'Weather.csv'
	#change lat long home id for meter data
        HomeAMeterAnomaly_df['LAT'] = row['LAT']
        HomeAMeterAnomaly_df['LONG'] = row['LONG']
        HomeAMeterAnomaly_df['home_id'] = index
	#change lat long home id for weather data
        HomeAWeather_df['LAT'] = row['LAT']
        HomeAWeather_df['LONG'] = row['LONG']
        HomeAWeather_df['home_id'] = index
	#copy to new data frame
        Home1MeterAnomaly_df = HomeAMeterAnomaly_df.copy()
        Home1Weather_df = HomeAWeather_df.copy()
	#Write to file
        Home1MeterAnomaly_df.to_csv(filenameMeter, index=False)
        Home1Weather_df.to_csv(filenameWeather, index=False)
	if index == 500: break
