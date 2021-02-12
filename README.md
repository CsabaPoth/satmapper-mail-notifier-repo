# Sentinel-2 New Satellite Imagery Mail Notifier

This Python code checks Open Access Hub hourly if new Sentinel-2 satellite imagery is available or not based on search parameters. 
If new imagery is available, script will send a notification e-mail with the imagery details through the given sender e-mail account to the given receiver e-mail account and goes to sleep for 23 hours.
The are that the code is looking for is based on the Shapefile located in the shape_file folder. Example is Budapest.
Open Access Hub registration is necessary to access Sentinel-2 data!

## Required libraries
The following libraries have to be installed in order to run this code 
- OS
- Geopandas
- Sentinelsat
- Datetime
- Smtplib
- Time
- Schedule

## Required imputs
The code needs to be modified with your data (see below) in order to work properly.

- shapefile of yourinterest
- shapefile file path
- Open Access Hub account (username and password)
- sender e-mail account (username and password)
- receiver e-mail address
