#!/usr/bin/python3

import csv
import os
import sys
from matplotlib import pyplot as plt


cwd = os.getcwd()


#refactor: pyGnuplot ile çizmelisin
#refactor: requested data in config file
#refactor: insert explanation into dicts (key:short, value:explain)




def process_rawdata(c, queried_indicator):
	#f's are files
	fvalues = open("{}/data/values.csv".format(cwd))
	fcountry = open("{}/data/country.csv".format(cwd))
	findicator = open("{}/data/indicators.csv".format(cwd))
	#r's are readers
	rvalues = csv.reader(fvalues)
	rcountry = csv.reader(fcountry)
	rindicators = csv.reader(findicator)

	#get EXPLANATION of queried macroecon indicator
	explanation = []
	for indic in rindicators:
		if(queried_indicator == indic[0]):
			explanation.append(indic[1])
			explanation.append(indic[2])

	#get the COUNTRY CODE as user input
	for count in rcountry:
		if(c == count[2]):
			country_code = count[0]

	#get all INDICATOR VALUES for retrieved country
	country_values = []
	rvalues = csv.reader(fvalues)
	for val in rvalues:
		if(country_code == val[0]):
			country_values.append((val[1],val[2],val[3]))

	#get the SPECIFIC INDICATOR for queried country
	plotdata = []
	for c_v in country_values:
		if(c_v[0] == queried_indicator):
			c_v = list(c_v)
			c_v.pop(0)
			plotdata.append(c_v)

	#organising plotdata for plotting
	x = []
	y = []
	for i in plotdata:
		x.append(i[0])
		y.append(i[1])

	fcountry.close()
	findicator.close()
	fvalues.close()

	return (x, y, explanation)




#request data from user  
#country = input("which country do you want?\n")

countries = ["Switzerland", "United States", "Turkey", "Australia"]
queried_indicator = "PCPIE"


country_data = []

for country in countries:
	xs = []
	ys = []
	x, y, explanation = process_rawdata(country, queried_indicator)
	for i in x:
		xs.append(i)
	for j in y:
		ys.append(j)
	country_data.append((xs,ys))


#plt.title(queried_indicator)
for i in  range(len(countries)):
	plt.plot(country_data[i][0],
		country_data[i][1])


plt.legend(countries)
plt.show()
