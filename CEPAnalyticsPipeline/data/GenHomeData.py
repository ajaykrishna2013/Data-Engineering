import pandas as pd

Norcal_df = pd.read_csv('Norcal.csv')
HomeAMeterAnomaly_df = pd.read_csv('HomeAMeterAnomaly.csv')
HomeAWeather_df = pd.read_csv('HomeAWeather.csv')

for index, row in Norcal_df.iterrows():
        filename = 'Home'+str(index)+'MeterAnomaly.csv'
        HomeAMeterAnomaly_df['LAT'] = row['latitude']
        HomeAMeterAnomaly_df['LONG'] = row['longitude']
        HomeAMeterAnomaly_df['home_id'] = index
        Home1MeterAnomaly_df = HomeAMeterAnomaly_df.copy()
        Home1MeterAnomaly_df.to_csv(filename, index=False)
	if index == 4:
		break
