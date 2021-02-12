####################
# Import libraries #
####################
import os
import geopandas as gpd
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from datetime import datetime
import smtplib, ssl
import time
import schedule

##########################
# Define shape file path #
##########################
fp_place='shape_file/budapest/budapest.shp'

####################
# Basic parameters #
####################
# Open Access Hub login data
oah_user='USERNAME' # Your Open Access Hub username
oah_pass='PASSWORD' # Your Open Access Hub password

#E-mail data
port = 465  # Email client port for SSL
smtp_server = "smtp.gmail.com" #SMTP server
sender_email = "XXXX@gmail.com"  # Enter sender e-mail address
receiver_email = "YYYY@gmail.com"  # Enter receiver e-mail address
password = "MAILPASSWORD" # Enter sender e-mail password

#####################################################
# Search parameters - See sentinelsat documentation #
#####################################################
start_date='NOW-1DAY'
end_date='NOW'
platformname='Sentinel-2'
processinglevel = 'Level-2A'
min_cloud=0
max_cloud=100

#################################
# Open shapefile and get bounds #
#################################
shapefile = gpd.read_file(fp_place)
shapefile_EPSG4326=shapefile.to_crs(epsg=4326)
shp_bounds=shapefile_EPSG4326.total_bounds
lonmin=shapefile_EPSG4326.total_bounds[0]
latmin=shapefile_EPSG4326.total_bounds[1]
lonmax=shapefile_EPSG4326.total_bounds[2]
latmax=shapefile_EPSG4326.total_bounds[3]

# Create wkt of shapefile
wkt = "POINT(%f %f %f %f)" %  (float(lonmin) , float(latmin), float(lonmax), float(latmax))

###################################################
# Create function for data check and mail sending #
###################################################
def job():
    #Checking Sentinel data on SciHub, based on search requirements
    api = SentinelAPI(oah_user,oah_pass, 'https://scihub.copernicus.eu/apihub')
    count=api.count(area=wkt, date=(start_date, end_date), platformname=platformname,area_relation='Contains',raw=None,cloudcoverpercentage=(min_cloud,max_cloud),limit=20, processinglevel = processinglevel)
    now = datetime.now()
    now = now.strftime("%d/%m/%Y %H:%M:%S")
    print(now+' - Checking for new data')
    

    if count>0:
        # Write available image data to dataframe
        products = api.query(area=wkt, date=(start_date, end_date), platformname=platformname,area_relation='Contains',raw=None,cloudcoverpercentage=(min_cloud,max_cloud),limit=20, processinglevel = processinglevel)
        products_df = api.to_dataframe(products)
        detail=products_df.iat[0,4]
        
        # Get and format important data of satellite imagery
        img_sat=products_df.iloc[0,36] # Get satellite name
        img_proc_lvl=products_df.iloc[0,37] # Get image processing level
        img_date=products_df.iloc[0,4][6:16] # Get acquisition date
        img_time=products_df.iloc[0,4][17:25] # Get acquisition time
        img_cloud=str(products_df.iloc[0,19])[:5]+' %' # Get cloud coverage
              
        #Prepare e-mail content
        subject="New satellite image available - "+img_date
        body="Properites if the new satellite imagery is the following.\n\n"+'Satellite: '+img_sat+'\n'+'Processing level: '+img_proc_lvl+'\n'+'Timestamp of imagery: '+img_date+', '+img_time+'\n'+'Cloud cover percentage: '+img_cloud
        message=f'Subject:{subject}\n\n{body}'      
        
        #Send e-mail and go to sleep
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.encode("utf8"))
        now = datetime.now()
        now = now.strftime("%d/%m/%Y %H:%M:%S")
        print(now+' - Mail has been sent')
        time.sleep(82800) #23 hours 
        return
    else:
        # If no new image available, print message
        print(now+' - There is no new data available')
        return

########################################################
# Run function every hour - See schedule documentation #
########################################################  
schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)