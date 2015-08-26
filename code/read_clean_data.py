import shapefile
import pandas as pd
import os
import numpy as np
import pickle
from collections import defaultdict

def read_file(year, basefile_name): 
	'''
	Input: String
	Output: Pandas DataFrame

	Read in the shapefiles from the given filepath and translate the result into a 
	pandas dataframe. 
	'''
	filepath = '../../data/raw_data/MODIS/' + str(year) + '/' + basefile_name
	
	sf = shapefile.Reader(filepath)
	# The first field is simply a spec that we don't actually want. 
	col_names = [field[0] for field in sf.fields[1:]]
	df = pd.DataFrame(sf.records(), columns=col_names)

	if year<=2008: 
		df = format_df(df)
	else: 
		df = df.drop('SRC', axis=1)

	df['year'] = [date[0] for date in df['DATE']]
	df['month'] = [date[1] for date in df['DATE']]
	df['day'] = [date[2] for date in df['DATE']]

	df = df.drop('DATE', axis=1)

	return df, sf

def get_basefile_name(year): 
	'''
	Input: Integer
	Output: String

	Take in the given year, navigate to the satellite data for that year, and 
	pull the basefile name that the shapefile library will need to put all 
	of the files together. 
	'''
	current_dir = '../../data/raw_data/MODIS/' + str(year) + '/'
	files = os.listdir(current_dir)

	ext_index = files[0].find('.')
	basefile_name = files[0][:ext_index]
	return basefile_name

def format_df(df): 
	'''
	Input: Pandas DataFrame
	Output: Pandas DataFrame

	In the years 2008 and prior, the data is formatted slightly differently than later years. The 
	Fire_ and Fire_ID variables from later years are named differently, as are the LAT and LONG 
	variables. For these, we simply need to change names. For the TEMP variable from years 2009+, we need to 
	use the T21 from the years prior to 2008, and for the JULIAN varible in years 2009+, we need to parse
	part of the JDATE variable. 
	'''

	df = df.rename(columns={'MCD14ML_': 'FIRE_', 'MCD14ML_ID': 'FIRE_ID', 'WGS84LAT': 'LAT', 'WGS84LONG': 'LONG', 
							'T21': 'TEMP', 'UTC': 'GMT', 'SATELLITE': 'SAT_SRC', 'CONFIDENCE': 'CONF'})
	df['JULIAN'] = df['JDATE'].apply(lambda x: int(str(x)[-3:]))
	df = df.drop(['T31', 'JDATE'], axis=1)

	return df

def pickle_df_sf(year, df): 
	'''
	Input: Integer, Pandas DataFrame
	Ouput: Pickled file of DataFrame
	'''

	with open('../../data/pickled_data/MODIS/' + 'df_' + str(year) + '.pkl', 'w+') as f: 
		pickle.dump(df, f)

if __name__ == '__main__': 
	for year in range(2001, 2016): 
		basefile_name = get_basefile_name(year)
		shapefile_df, shapefile_sf = read_file(year, basefile_name)
		pickle_df_sf(year, shapefile_df)

		