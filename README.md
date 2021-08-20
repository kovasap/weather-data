# Weather Data

Some analysis of weather data for fun!

## Getting Data

I first tried getting data via this service:
https://www.ncdc.noaa.gov/cdo-web/datasets.  Unfortunately, the data I got was
pretty inconsistent. I talked to a meteorologist from NOAA via their help email
and was redirected to this beta data:
https://www1.ncdc.noaa.gov/pub/data/hpd/auto/v2/beta/15min/. For this data, I
needed to pick a station, so I looked in the `hpd-stations-inventory` file and
found a list of Washington stations with coordinates. I loaded these up using
this advice: https://webapps.stackexchange.com/a/102780 and found that the
Everett station was the closest to Seattle (sad to see no Seattle station :(
). Then I found and downloaded the file cooresponding to this station ID
(USC00452675).
