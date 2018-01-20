#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Fixing unicode issues e.g. STP:  São Tomé and Príncipe
import os
if not os.getenv('PYTHONIOENCODING', None): # PyInstaller workaround
    os.environ['PYTHONIOENCODING'] = 'utf_8'

import csv
import urllib.request #Python 3
import logging
import codecs
import sys

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

url_2014 = 'http://www.imf.org/external/pubs/ft/weo/2014/01/weodata/WEOApr2014all.xls'
url_2015 = 'http://www.imf.org/external/pubs/ft/weo/2015/01/weodata/WEOApr2015all.xls'
url = url_2015

# weirdly it turns out the xls (url_2014) is in fact a tsv file ...
fp_2014 = 'archive/imf-weo-2015-feb.tsv'
fp_2015 = 'archive/imf-weo-2015-apr.tsv'
fp = fp_2015

# Specifying the locale of the source
#import locale
#locale.setlocale(locale.LC_NUMERIC, 'English') #'English_United States.1252'


def download():
    logger.info('Retrieving source database: %s ...' % url)
    #urllib.request.urlretrieve fp)
    f=urllib.request.urlopen(url)
    output=f.read().decode('cp1252')

    path=os.path.dirname(fp)
    if not os.path.exists(path):
        os.makedirs(path)
        
    with codecs.open(fp, "w", "utf-8") as temp:
        temp.write(output)
    
    logger.info('Source database downloaded to: %s' % fp)


def f_open(fn):
    if sys.version_info >= (3,0,0):
        f = open(fn, 'w', newline='', encoding='utf-8')
    else:
        f = open(filename, 'wb')
    return f
    


def extract():
    logger.info('Starting extraction of data from: %s' % fp)
    reader = csv.DictReader(open(fp, encoding='utf-8'), delimiter='\t')
    indicators = {}
    WEOcountry_names=dict() #countrys = {}
    WEOcountry_codes=dict()
    values = []

    years = reader.fieldnames[9:-1]

    

    for count, row in enumerate(reader):
        # last 2 rows are blank/metadata
        # so get out when we hit a blank row
        if not row['Country']:
            break

        indicators[row['WEO Subject Code']] = [
            row['Subject Descriptor'] + ' (%s)' % row['Units'],  
            row['Subject Notes'],
            row['Units'],
            row['Scale']
            ]
        
        # not sure we really need given iso is standard
        # just for double check on data integrity and names encoding
        if row['ISO'] not in WEOcountry_names:
            WEOcountry_names[row['ISO']] = row['Country']
            try:
                WEOcountry_codes[row['ISO']] = row['WEO Country Code']
            except:
                print(row)
                break;

        # need to store notes somewhere with an id ...
        # also need to uniquify the notes ...
        notes = row['Country/Series-specific Notes']
        newrow = {
            'Country': row['ISO'],
            'Indicator': row['WEO Subject Code'],
            'Year': None,
            'Value': None
            }
        for year in years:
            if row[year] != 'n/a':
                tmprow = dict(newrow)
                try:
                    tmprow['Value'] = locale.atof (row[year] )          # Converting "1,033.591" to 1033.591
                except:
                    tmprow['Value'] = row[year] 
                tmprow['Year'] = year
                values.append(tmprow)

        # TODO: indicate whether a value is an estimate using
        # 'Estimates Start After'

        # delete 'Estimates Start After'
    
    outfp = 'data/indicators.csv'
   
    path=os.path.dirname(outfp)
    if not os.path.exists(path):
        os.makedirs(path)

    writer = csv.writer(f_open(outfp))
    indheader = ['id', 'title', 'description', 'units', 'scale']
    writer.writerow(indheader)
    for k in sorted(indicators.keys()):
        writer.writerow( [k] + indicators[k] )
    logger.info('Number of Indicators included: {}'.format(len(indicators.keys())))

    outfp = 'data/country.csv'
    writer = csv.writer(f_open(outfp))
    header = ['ISO', 'WEO', 'Name']
    writer.writerow(header)
    for k in sorted(WEOcountry_names.keys()):
        writer.writerow( [k] + [WEOcountry_codes[k],WEOcountry_names[k],])
    logger.info('Number of Countries included: {}'.format(len(WEOcountry_names.keys())))


    outfp = 'data/values.csv'
    f = f_open(outfp)
    writer = csv.writer(f)
    header = ['Country', 'Indicator', 'Year', 'Value']
    writer = csv.DictWriter(f, header)
    writer.writeheader()
    writer.writerows(values)


    logger.info('Completed data extraction to data/ directory')

def process():
    download()
    extract()

def check_indicators():
    reader = csv.DictReader(open(fp, encoding='utf-8'), delimiter='\t')
    header = ['id', 'title', 'description']
    indicators = {}
    for count, row in enumerate(reader):
        id = row['WEO Subject Code']
        notes = row['Subject Notes']
        ind = [
            row['Subject Descriptor'],
            notes,
            row['Units'],
            row['Scale']
            ]
        # check whether indicators differ
        # in their descriptions etc
        if id in indicators:
            if indicators[id][1] != notes:
                print(count)
                print(notes)
            if indicators[id][2] != row['Units']:
                print(count)
                print(row['Units'])
            if indicators[id][3] != row['Scale']:
                print(count)
                print(row['Scale'])
        indicators[id] = ind
    print(len(indicators)) 
    for k,v in indicators.items():
        print (k, '\t\t',  v[0])

# check_indicators()

#'''
if __name__ == '__main__':
    # extract()
    process()
#'''

