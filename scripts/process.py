import csv
import urllib
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

url_2014 = 'http://www.imf.org/external/pubs/ft/weo/2014/01/weodata/WEOApr2014all.xls'
# weirdly it turns out the xls (url_2014) is in fact a tsv file ...
fp_2014 = 'archive/imf-weo-2014-feb.tsv'

def download():
    logger.info('Retrieving source database: %s ...' % url_2014)
    urllib.urlretrieve(url_2014, fp_2014)
    logger.info('Source database downloaded to: %s' % fp_2014)

def extract():
    logger.info('Starting extraction of data from: %s' % fp_2014)
    reader = csv.DictReader(open(fp_2014), delimiter='\t')
    indicators = {}
    countrys = {}
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
        countrys[row['ISO']] = row['Country']

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
                tmprow['Value'] = row[year]
                tmprow['Year'] = year
                values.append(tmprow)

        # TODO: indicate whether a value is an estimate using
        # 'Estimates Start After'

        # delete 'Estimates Start After'
    
    outfp = 'data/indicators.csv'
    writer = csv.writer(open(outfp, 'w'))
    indheader = ['id', 'title', 'description', 'units', 'scale']
    writer.writerow(indheader)
    for k in sorted(indicators.keys()):
        writer.writerow( [k] + indicators[k] )

    outfp = 'data/values.csv'
    header = ['Country', 'Indicator', 'Year', 'Value']
    writer = csv.DictWriter(open(outfp, 'w'), header)
    writer.writeheader()
    writer.writerows(values)

    logger.info('Completed data extraction to data/ directory')

def process():
    download()
    extract()

def check_indicators():
    reader = csv.DictReader(open(fp_2014), delimiter='\t')
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
                print count
                print notes
            if indicators[id][2] != row['Units']:
                print count
                print row['Units']
            if indicators[id][3] != row['Scale']:
                print count
                print row['Scale']
        indicators[id] = ind
    print len(indicators)  
    for k,v in indicators.items():
        print k, '\t\t',  v[0]

# check_indicators()

if __name__ == '__main__':
    # extract()
    process()

