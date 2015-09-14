#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


# Country Codes for ISO alpha-2 and alpha-3 mapping https://raw.githubusercontent.com/datasets/country-codes/master/data/country-codes.csv
country_codes=pd.read_csv("https://raw.githubusercontent.com/datasets/country-codes/master/data/country-codes.csv")
ISO23=country_codes.loc[:,['ISO3166-1-Alpha-2', 'ISO3166-1-Alpha-3']].set_index('ISO3166-1-Alpha-2')['ISO3166-1-Alpha-3']
ISO32=country_codes.loc[:,['ISO3166-1-Alpha-3', 'ISO3166-1-Alpha-2']].set_index('ISO3166-1-Alpha-3')['ISO3166-1-Alpha-2']

# Country Names (CLDR 27.0.1) https://raw.githubusercontent.com/hanteng/pyCountryNames/master/country_names.csv
country_names=pd.read_csv("https://raw.githubusercontent.com/hanteng/pyCountryNames/master/country_names.csv").set_index('tags')
country_names_locale=country_names.loc['en_Latn_US']#zh_Hant_TW  zh_Hans_CN en_Latn_US


weo = pd.DataFrame.from_csv('data/values.csv', sep=',', header=0 ) # index_col=['Indicator','Country']
weo['Year']=weo['Year'].astype(np.int)
#weo=weo_reset.reindex(['Year','Indicator','Country'])
weo_reset=weo.reset_index()
weo  = weo_reset.set_index(['Year','Country','Indicator'])#duplicate entries if ['Indicator','Country','Year']

#data cleaning
def cleanup(stuff):
    if stuff in ['--',]:
        stuff=None
    return stuff

weo['Value']=[cleanup(x) for x in weo['Value']]
weo['Value']=weo['Value'].astype(np.float64)

weo_ = weo['Value'].unstack()   # the addition of ['Value'] essential here to keep the columns simple...  now that the unstack method turns index values into column names
weo_p= weo_.to_panel()
#print(weo_p.loc[:,2014,"TWN"])

#<class 'pandas.core.panel.Panel'>
#Dimensions: 44 (items) x 41 (major_axis) x 189 (minor_axis)
#Items axis: BCA to TX_RPCH
#Major_axis axis: 1980 to 2020
#Minor_axis axis: AFG to ZWE



ye_ = 2014
in_ = ['LP','PPPGDP']
import pyCountryGroup
income=pyCountryGroup.wp.loc['worldbank',:,['incomelevel']]
OECD=income[income.incomelevel=="OEC"].index.values.tolist()

#http://www.kaweb.co.uk/blog/list-eu-countries-and-iso-3166-1-alpha-3-code/
EU28=["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE", "GBR"]

countries_=list(set(OECD).union(set(EU28)))

#ISO3country_names=country_names.loc['zh_Hant_TW'][ISO32['X']]

'''
>>> list(set(OECD).difference(set(EU28)))
['AUS', 'CHL', 'CHE', 'NOR', 'USA', 'ISL', 'ISR', 'KOR', 'NZL', 'JPN', 'CAN']
>>> list(set(EU28).difference(set(OECD)))
['LVA', 'CYP', 'HRV', 'ROU', 'BGR', 'MLT', 'LTU', 'HUN']
>>> list(set(EU28).intersection(set(OECD)))
['IRL', 'ITA', 'GRC', 'POL', 'CZE', 'SWE', 'ESP', 'SVN', 'NLD', 'EST', 'FRA', 'LUX', 'SVK', 'DEU', 'PRT', 'FIN', 'DNK', 'GBR', 'AUT', 'BEL']
'''
countries_.sort()
countries_names=[country_names.loc['zh_Hant_TW'][ISO32[c_]] for c_ in countries_]

working_=weo_p.loc[in_,2014,countries_]

working_proportion=working_/working_.sum()
working_proportion['halfhalf'] = (working_proportion['LP']+working_proportion['PPPGDP'])/2
# http://www.aljazeera.com/news/2015/09/nations-split-eu-release-refugee-quotas-mediterranean-150909041714912.html
# The president of the European Union Commission Jean-Claude Juncker wants 22 of the member states to accept another 120,000 people, on top of the 40,000 already agreed upon, bringing the total number to 160,000
working_proportion['fairshare'] = ["{0:.2f}%".format(i*100) for i in working_proportion['halfhalf'] ]

working_proportion['0.16M'] = working_proportion['halfhalf'] *.16e6 #
#An estimated 400,000 refugees are expected to cross the Mediterranean this year
working_proportion['0.4M'] = working_proportion['halfhalf'] *.4e6 #
working_proportion['4.1M'] = working_proportion['halfhalf'] *4.1e6
working_proportion['10.6M'] = working_proportion['halfhalf'] *10.6e6

working_proportion[['0.16M', '0.4M','4.1M', '10.6M']] = working_proportion[['0.16M', '0.4M','4.1M', '10.6M']].astype(int)

ccodes=working_proportion.sort("halfhalf").index.tolist() #,ascending=False
c_codes=ccodes
c_names=[country_names.loc['en_Latn_US'][ISO32[c_]] for c_ in c_codes]
working_proportion['Country Name']=c_names
c_names_zh=[country_names.loc['zh_Hant_TW'][ISO32[c_]] for c_ in c_codes]


working_proportion=working_proportion.sort("halfhalf",ascending=False)
working_proportion[['Country Name','fairshare','0.16M', '0.4M','4.1M', '10.6M']].to_csv('proportion.csv', float_format='%.3f')
working_proportion=working_proportion.sort("halfhalf",ascending=True)

halfhalf= [working_proportion['halfhalf'][x] for x in ccodes]



scatter_x = working_['LP'][ccodes]      #LP,Population (Persons),"For census purposes, the total population of the country consists of all persons falling within the scope of the census. In the broadest sense, the total may comprise either all usual residents of the country or all persons present in the country at the time of the census. [Principles and Recommendations for Population and Housing Censuses, Revision 1, paragraph 2.42]",Persons,Millions
scatter_y = working_['PPPGDP'][ccodes] #PPPGDP,Gross domestic product based on purchasing-power-parity (PPP) valuation of country GDP (Current international dollar),"These data form the basis for the country weights used to generate the World Economic Outlook country group composites for the domestic economy.   The IMF is not a primary source for purchasing power parity (PPP) data. WEO weights have been created from primary sources and are used solely for purposes of generating country group composites. For primary source information, please refer to one of the following sources: the Organization for Economic Cooperation and Development, the World Bank, or the Penn World Tables.   For further information see Box A2 in the April 2004 World Economic Outlook, Box 1.2 in the September 2003 World Economic Outlook for a discussion on the measurement of global growth and Box A.1 in the May 2000 World Economic Outlook for a summary of the revised PPP-based weights, and Annex IV of the May 1993 World Economic Outlook. See also Anne Marie Gulde and Marianne Schulze-Ghattas, Purchasing Power Parity Based Weights for the World Economic Outlook, in Staff Studies for the World Economic Outlook (Washington: IMF, December 1993), pp. 106-23.",Current international dollar,Billions
regression = np.polyfit(scatter_x, scatter_y, 1)

from bokeh.plotting import ColumnDataSource, gridplot, figure, output_file, show
from bokeh.models import HoverTool, BoxSelectTool, NumeralTickFormatter
from collections import OrderedDict

# We need to generate actual values for the regression line.
r_x, r_y = zip(*((i, i*regression[0] + regression[1]) for i in range(360)))


# We need to put these data into a ColumnDataSource
source = ColumnDataSource(
    data=dict(
        scatter_x=scatter_x,
        scatter_y=scatter_y,
        x0= [i * .5 for i in halfhalf],
        barx=halfhalf,
        bary=ccodes,
        fairshare=["{0:.2f}%".format(i*100) for i in halfhalf],
        c_name=c_names,
        c_name_zh=c_names_zh,
        c_code=c_codes,
    )
)

output_file("regression.html")
TOOLS = 'pan,wheel_zoom,box_zoom,box_select,crosshair,hover,resize,reset' #[BoxSelectTool(), HoverTool()]#'box_zoom,box_select,crosshair,resize,reset'

# NEW: create a column data source for the plots to share
from bokeh.models import ColumnDataSource


# create a new plot and add a renderer
fig_cor = figure(width=600, height=720, title="Correlation between PPPGDP and LP among OECD plus EU-28",title_text_font_size='12pt', x_axis_label = "x: Population 人口大小 [LP] (millions)", y_axis_label = "y: Economy Size GDP based on PPP 經濟大小 [PPPGDP] (billions)", tools=TOOLS)
fig_cor.line(r_x, r_y, color="red")
fig_cor.circle('scatter_x', 'scatter_y', size=20, color="navy", source=source, alpha=0.5)  #source parameter added
text_props = {
    "angle": 0,
    "color": "black",
    "text_align": "left",
    "text_baseline": "middle"
}
fig_cor.text(x=scatter_x, y=scatter_y, text=c_codes,
    text_font_style="bold", text_font_size="13pt", **text_props)  #text=working_['LP'].keys().tolist(),


hover = fig_cor.select(dict(type=HoverTool))
hover.tooltips =  OrderedDict([
            ("Country", "@c_name [@c_code]"),
            ("國家", "@c_name_zh [@c_code]"),
            ("(x,y)", "(@scatter_x, @scatter_y)"),
        ]
    )


# create another new plot and add a renderer

fig_bar = figure(width=320, height=720, title= "Fair Proportion among OECD plus EU-28", title_text_font_size='12pt', y_range=ccodes, x_range=[0,int(max(halfhalf)/0.05+1)*0.05],  tools=TOOLS)
fig_bar.xaxis[0].formatter = NumeralTickFormatter(format="0%")
'''
>>> working_proportion.sort("halfhalf",ascending=False).index.tolist()
['USA', 'JPN', 'DEU', 'FRA', 'GBR', 'ITA', 'KOR', 'ESP', 'CAN', 'POL', 'AUS', 'NLD', 'ROU', 'CHL', 'BEL', 'SWE', 'CHE', 'CZE', 'AUT', 'GRC', 'PRT', 'HUN', 'ISR', 'NOR', 'DNK', 'FIN', 'BGR', 'IRL', 'SVK', 'NZL', 'HRV', 'LTU', 'SVN', 'LVA', 'EST', 'LUX', 'CYP', 'MLT', 'ISL']
'''
#x0=[0,]*len(countries_)
#fig_bar.segment(x0, ccodes, halfhalf, ccodes, source=source, line_width=15, line_color="green", alpha=0.4)

fig_bar.rect('x0', 'bary', 'barx', source=source, height=.75, line_color="green", alpha=0.6)#source=source, 
hoverbar = fig_bar.select(dict(type=HoverTool))
hoverbar.tooltips =  OrderedDict([
#            ("index", "$index"),
            ("Fair Share", "@fairshare"),
            ("Country", "@c_name"),
            ("國家", "@c_name_zh"),
            ("Population", "@scatter_x"),
            ("Economy", "@scatter_y"),
#            ("bar(x,y)", "(@barx, @bary)"),
        ]
    )






# put the subplots in a gridplot
p = gridplot([[fig_bar, fig_cor]])


#ccodes.reverse()
#halfhalf.reverse()



show(p)


#CNN: overall numbers http://edition.cnn.com/2015/09/11/world/syria-refugee-crisis-when-war-displaces-half-a-country/
#    The fighting and later rise of ISIS forced 10.6 million people from home -- about half of Syria's pre-war population.
#    4.1M  Refugees abroad       6.5M Displaced withi Syria

#Carnegie Europe:  http://carnegieeurope.eu/2015/07/15/bolder-eu-strategy-for-syrian-refugees/ided
'''Marc Pierini
VISITING SCHOLAR

Since March 2011, more than half of Syria’s 22 million citizens have fled their homes. The number of those who have left the country and registered as refugees in Jordan, Lebanon, or Turkey (or, to a lesser extent, Egypt or Iraq) has now surpassed 4 million. Syrians also account for the highest number of internally displaced persons worldwide: 7.6 million have moved within Syria itself.
These estimates of the numbers of recorded displaced Syrians don’t tell the entire story, however. More citizens have fled Syria by their own means and are now living undocumented in neighboring countries or farther afield—in the Gulf, the Maghreb, or the EU. Unregistered refugees are hard to track, but they and their host communities also suffer from hardship.
As usual in war zones, the immediately neighboring countries have taken in the largest numbers of refugees. There has been a sizable humanitarian effort from host countries in the region, especially Turkey and Jordan, as well as substantial international assistance.

Jordan
Lebanon
Turkey

Turkey has now taken in more refugees than any other country in absolute terms: 1.8 million Syrians against a total precrisis population of 72.1 million.
'''
#UNHCR: http://data.unhcr.org/syrianrefugees/regional.php
#UNHCR Jordan: http://data.unhcr.org/syrianrefugees/country.php?id=107
#UNHCR Lebanon: http://data.unhcr.org/syrianrefugees/country.php?id=122
#UNHCR Turkey: http://data.unhcr.org/syrianrefugees/country.php?id=224

#OECD report: http://www.oecd.org/migration/sicremi.htm
#OECD report: http://www.oecd.org/migration/

#  http://bokeh.pydata.org/en/latest/docs/gallery/periodic.html
#EUI http://syrianrefugees.eu/

#Will a Rohingya refugee go full circle after fleeing Myanmar?  http://www.irinnews.org/report/101981/will-a-rohingya-refugee-go-full-circle-after-fleeing-myanmar


#The United Nations and the Regions (eds)  https://www.academia.edu/5631440/The_United_Nations_and_the_Regions_eds_
