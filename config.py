from datetime import datetime, timedelta


INTERPLAY_ASSET_WSDL = 'http://100.116.91.47/services/Assets?wsdl'
INTERPLAY_JOB_WSDL = 'http://100.116.91.47/services/Jobs?wsdl'
INTERPLAY_ARCHIVE_WSDL = 'http://100.116.91.47/services/Archive?wsdl'
INTERPLAY_MOB_URI = [
    'interplay://ECNOCAWG?mobid=',
    'interplay://ECNOCBWG?mobid='
    ]
INTERPLAY_ARCHIVE_PROFILE = [
    'NOCA Automation Only Longform',
    'NOCB Automation Only Longform'
    ]
INTERPLAY_PATHS = [
    'interplay://ECNOCAWG/Projects/00_AIRSPEED5000/A5K01/ING111',
    'interplay://ECNOCAWG/Projects/00_AIRSPEED5000/A5K01/ING112',
    'interplay://ECNOCAWG/Projects/00_AIRSPEED5000/A5K01/ING113',
    'interplay://ECNOCAWG/Projects/00_AIRSPEED5000/A5K01/ING114',
    'interplay://ECNOCAWG/Projects/00_AIRSPEED5000/A5K02/ING121',
    'interplay://ECNOCAWG/Projects/00_AIRSPEED5000/A5K02/ING122',
    'interplay://ECNOCAWG/Projects/00_AIRSPEED5000/A5K02/ING123',
    'interplay://ECNOCAWG/Projects/00_AIRSPEED5000/A5K02/ING124',
    'interplay://ECNOCBWG/Projects/00_AIRSPEED5000/A5K01/ING211',
    'interplay://ECNOCBWG/Projects/00_AIRSPEED5000/A5K01/ING212',
    'interplay://ECNOCBWG/Projects/00_AIRSPEED5000/A5K01/ING213',
    'interplay://ECNOCBWG/Projects/00_AIRSPEED5000/A5K01/ING214',
    'interplay://ECNOCBWG/Projects/00_AIRSPEED5000/A5K02/ING221',
    'interplay://ECNOCBWG/Projects/00_AIRSPEED5000/A5K02/ING222',
    'interplay://ECNOCBWG/Projects/00_AIRSPEED5000/A5K02/ING223',
    'interplay://ECNOCBWG/Projects/00_AIRSPEED5000/A5K02/ING224',
    'interplay://ECNOCBWG//Catalogs/Ready For Air/ADIC restores/Protected Restore Folder 2017 Purge/',
]

DATABASE = "media"
DB_USER = "pyuser"
DB_PASS = "unicornbacon"  # because it's delicious -Jonathan
DB_HOST = "localhost"  # Home Sweet Home

AUTO_ARCHIVE_MIN_DURATION = timedelta(minutes=15)
AUTO_ARCHIVE_MAX_DURATION = timedelta(minutes=120)
AUTO_ARCHIVE_START_TIME_HOUR = 16  # int hour of the day 0-23
AUTO_ARCHIVE_START_TIME_MINUTE = 19  # int minute in the hour 0-59
AUTO_ARCHIVE_END_TIME_HOUR = 8  # int hour of the day 0-23 must be larger than start hour
AUTO_ARCHIVE_END_TIME_MINUTE = 0
AUTO_ARCHIVE_MAX_NUM_ASSETS = 25  # int
