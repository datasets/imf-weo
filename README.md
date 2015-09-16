IMF World Economic Outlook (WEO) database. The [IMF World Economic
Outlook][weo] is a twice-yearly survey by IMF staff that presents IMF staff
economists' analyses of global economic developments during the near and medium
term. Associated with the report is the [World Economic Outlook
Database][weo-db], a country-level dataset of major macro-economic variables
(GDP, Unemployment, Debt etc). It is the data from that database which is
provided here.

[weo]: http://www.imf.org/external/ns/cs.aspx?id=29
[weo-db]: http://www.imf.org/external/ns/cs.aspx?id=28

## Data

The source database is made of annual values for each country on 45 indicators
since 1980. In addition the database includes the IMF projects approximately 6
years into the future.

We extract this data and normalize into 2 files:

* Indicators - `data/indicators.csv` - the list of indicators
* Values - `data/values.csv` - set of values for each indicator, country, year tuple.
* Country - 'data/country.csv' - set of value for mapping each ISO country code, WEO country code, and CLDR English Name

### Sources

Note the XLS files actual turn out to be tsv files!

* [Listing page for WEO Database][weo-db]
* 2015 - http://www.imf.org/external/pubs/ft/weo/2015/01/weodata/index.aspx
  * http://www.imf.org/external/pubs/ft/weo/2015/01/weodata/WEOApr2015all.xls
* 2014 - http://www.imf.org/external/pubs/ft/weo/2014/01/weodata/index.aspx
  * http://www.imf.org/external/pubs/ft/weo/2014/01/weodata/WEOApr2014all.xls
* 2011 - http://www.imf.org/external/pubs/ft/weo/2011/02/weodata/index.aspx
  * http://www.imf.org/external/pubs/ft/weo/2011/02/weodata/WEOSep2011all.xls

## Preparation

Code to extract the data from the source WEO Database is in the `scripts`
directory.

