##########################
# Könyvtárak importálása #
##########################
import os
import geopandas as gpd
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from datetime import datetime
import smtplib, ssl
import time
import schedule

#############################
# Shape file elérési útvonal#
#############################
fp_place='shape_file/budapest/budapest.shp'

########################
# Alapvető paraméterek #
########################
# Open Access Hub bejelentkezési adatok
oah_user='FELHASZNÁLÓNÉV' # Your Open Access Hub felhasználónév
oah_pass='JELSZÓ' # Your Open Access Hub jelszó

#E-mail adat
port = 465  # Email port SSL-hez
smtp_server = "smtp.gmail.com" #SMTP szerver
sender_email = "XXXX@gmail.com"  # Küldő e-mail címe
receiver_email = "YYYY@gmail.com"  # Címzett e-mail címe
password = "MAILPASSWORD" # Küldő e-mail cím jelszava

########################################################
# Keresési paraméterek - Lásd sentinelsat dokumentáció #
########################################################
start_date='NOW-1DAY'
end_date='NOW'
platformname='Sentinel-2'
processinglevel = 'Level-2A'
min_cloud=0
max_cloud=100

##############################################
# Shapefile megnyitása befoglaló koordináták #
##############################################
shapefile = gpd.read_file(fp_place)
shapefile_EPSG4326=shapefile.to_crs(epsg=4326)
shp_bounds=shapefile_EPSG4326.total_bounds
lonmin=shapefile_EPSG4326.total_bounds[0]
latmin=shapefile_EPSG4326.total_bounds[1]
lonmax=shapefile_EPSG4326.total_bounds[2]
latmax=shapefile_EPSG4326.total_bounds[3]

# WKT előűllítása shapefile alapján
wkt = "POINT(%f %f %f %f)" %  (float(lonmin) , float(latmin), float(lonmax), float(latmax))

####################################################
# Függvény új adat kereséséhez és e-mail küldéshez #
####################################################
def job():
    #Sentinel műholdképek keresése SciHub-on, keresési kritériumok alapján
    api = SentinelAPI(oah_user,oah_pass, 'https://scihub.copernicus.eu/apihub')
    count=api.count(area=wkt, date=(start_date, end_date), platformname=platformname,area_relation='Contains',raw=None,cloudcoverpercentage=(min_cloud,max_cloud),limit=20, processinglevel = processinglevel)
    now = datetime.now()
    now = now.strftime("%d/%m/%Y %H:%M:%S")
    print(now+' - Új adat keresése')
    

    if count>0:
        # Elérhető műholdképek adatainak dataframe-be írása
        products = api.query(area=wkt, date=(start_date, end_date), platformname=platformname,area_relation='Contains',raw=None,cloudcoverpercentage=(min_cloud,max_cloud),limit=20, processinglevel = processinglevel)
        products_df = api.to_dataframe(products)
        detail=products_df.iat[0,4]
        
        # E-mailbe írandó adatok formázása
        img_sat=products_df.iloc[0,36] # Get satellite name
        img_proc_lvl=products_df.iloc[0,37] # Get image processing level
        img_date=products_df.iloc[0,4][6:16] # Get acquisition date
        img_time=products_df.iloc[0,4][17:25] # Get acquisition time
        img_cloud=str(products_df.iloc[0,19])[:5]+' %' # Get cloud coverage
              
        #E-mail tartalom előkészítése
        subject="Új műholdkép - "+img_date
        body="A vizsgált területről készült új műholdkép adatai.\n\n"+'Műhold: '+img_sat+'\n'+'Feldolgozási szint: '+img_proc_lvl+'\n'+'Felvétel rögzítve: '+img_date+', '+img_time+'\n'+'Felvétel felhőzöttsége: '+img_cloud
        message=f'Subject:{subject}\n\n{body}'      
        
        #E-mail küldése és keresés szüneteltetése
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.encode("utf8"))
        now = datetime.now()
        now = now.strftime("%d/%m/%Y %H:%M:%S")
        print(now+' - E-mail elküldve')
        time.sleep(82800) #23 hours 
        return
    else:
        # Jelezzen ha nincs új műholdkép
        print(now+' - Nem érhető el új műholdkép')
        return

#################################################################
# Függvény futtatása minden órában - Lásd schedule dokumentáció #
#################################################################  
schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)