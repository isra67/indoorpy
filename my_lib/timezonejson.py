#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.logger import Logger

from itools import *

#import json
from operator import itemgetter


# ###############################################################
#
# Declarations
#
# ###############################################################

# timezones
timezones_json = {"Africa/Abidjan":0,"Africa/Accra":0,"Africa/Addis_Ababa":180,"Africa/Algiers":60,"Africa/Asmara":180,"Africa/Asmera":180,"Africa/Bamako":0,"Africa/Bangui":60,"Africa/Banjul":0,"Africa/Bissau":0,"Africa/Blantyre":120,"Africa/Brazzaville":60,"Africa/Bujumbura":120,"Africa/Cairo":120,"Africa/Casablanca":60,"Africa/Ceuta":120,"Africa/Conakry":0,"Africa/Dakar":0,"Africa/Dar_es_Salaam":180,"Africa/Djibouti":180,"Africa/Douala":60,"Africa/El_Aaiun":60,"Africa/Freetown":0,"Africa/Gaborone":120,"Africa/Harare":120,"Africa/Johannesburg":120,"Africa/Juba":180,"Africa/Kampala":180,"Africa/Khartoum":180,"Africa/Kigali":120,"Africa/Kinshasa":60,"Africa/Lagos":60,"Africa/Libreville":60,"Africa/Lome":0,"Africa/Luanda":60,"Africa/Lubumbashi":120,"Africa/Lusaka":120,"Africa/Malabo":60,"Africa/Maputo":120,"Africa/Maseru":120,"Africa/Mbabane":120,"Africa/Mogadishu":180,"Africa/Monrovia":0,"Africa/Nairobi":180,"Africa/Ndjamena":60,"Africa/Niamey":60,"Africa/Nouakchott":0,"Africa/Ouagadougou":0,"Africa/Porto-Novo":60,"Africa/Sao_Tome":0,"Africa/Timbuktu":0,"Africa/Tripoli":120,"Africa/Tunis":60,"Africa/Windhoek":60,"America/Adak":-540,"America/Anchorage":-480,"America/Anguilla":-240,"America/Antigua":-240,"America/Araguaina":-180,"America/Argentina/Buenos_Aires":-180,"America/Argentina/Catamarca":-180,"America/Argentina/ComodRivadavia":-180,"America/Argentina/Cordoba":-180,"America/Argentina/Jujuy":-180,"America/Argentina/La_Rioja":-180,"America/Argentina/Mendoza":-180,"America/Argentina/Rio_Gallegos":-180,"America/Argentina/Salta":-180,"America/Argentina/San_Juan":-180,"America/Argentina/San_Luis":-180,"America/Argentina/Tucuman":-180,"America/Argentina/Ushuaia":-180,"America/Aruba":-240,"America/Asuncion":-240,"America/Atikokan":-300,"America/Atka":-540,"America/Bahia":-180,"America/Bahia_Banderas":-300,"America/Barbados":-240,"America/Belem":-180,"America/Belize":-360,"America/Blanc-Sablon":-240,"America/Boa_Vista":-240,"America/Bogota":-300,"America/Boise":-360,"America/Buenos_Aires":-180,"America/Cambridge_Bay":-360,"America/Campo_Grande":-240,"America/Cancun":-300,"America/Caracas":-270,"America/Catamarca":-180,"America/Cayenne":-180,"America/Cayman":-300,"America/Chicago":-300,"America/Chihuahua":-360,"America/Coral_Harbour":-300,"America/Cordoba":-180,"America/Costa_Rica":-360,"America/Creston":-420,"America/Cuiaba":-240,"America/Curacao":-240,"America/Danmarkshavn":0,"America/Dawson":-420,"America/Dawson_Creek":-420,"America/Denver":-360,"America/Detroit":-240,"America/Dominica":-240,"America/Edmonton":-360,"America/Eirunepe":-300,"America/El_Salvador":-360,"America/Ensenada":-420,"America/Fort_Wayne":-240,"America/Fortaleza":-180,"America/Glace_Bay":-180,"America/Godthab":-120,"America/Goose_Bay":-180,"America/Grand_Turk":-240,"America/Grenada":-240,"America/Guadeloupe":-240,"America/Guatemala":-360,"America/Guayaquil":-300,"America/Guyana":-240,"America/Halifax":-180,"America/Havana":-240,"America/Hermosillo":-420,"America/Indiana/Indianapolis":-240,"America/Indiana/Knox":-300,"America/Indiana/Marengo":-240,"America/Indiana/Petersburg":-240,"America/Indiana/Tell_City":-300,"America/Indiana/Vevay":-240,"America/Indiana/Vincennes":-240,"America/Indiana/Winamac":-240,"America/Indianapolis":-240,"America/Inuvik":-360,"America/Iqaluit":-240,"America/Jamaica":-300,"America/Jujuy":-180,"America/Juneau":-480,"America/Kentucky/Louisville":-240,"America/Kentucky/Monticello":-240,"America/Knox_IN":-300,"America/Kralendijk":-240,"America/La_Paz":-240,"America/Lima":-300,"America/Los_Angeles":-420,"America/Louisville":-240,"America/Lower_Princes":-240,"America/Maceio":-180,"America/Managua":-360,"America/Manaus":-240,"America/Marigot":-240,"America/Martinique":-240,"America/Matamoros":-300,"America/Mazatlan":-360,"America/Mendoza":-180,"America/Menominee":-300,"America/Merida":-300,"America/Metlakatla":-480,"America/Mexico_City":-300,"America/Miquelon":-120,"America/Moncton":-180,"America/Monterrey":-300,"America/Montevideo":-180,"America/Montreal":-240,"America/Montserrat":-240,"America/Nassau":-240,"America/New_York":-240,"America/Nipigon":-240,"America/Nome":-480,"America/Noronha":-120,"America/North_Dakota/Beulah":-300,"America/North_Dakota/Center":-300,"America/North_Dakota/New_Salem":-300,"America/Ojinaga":-360,"America/Panama":-300,"America/Pangnirtung":-240,"America/Paramaribo":-180,"America/Phoenix":-420,"America/Port-au-Prince":-240,"America/Port_of_Spain":-240,"America/Porto_Acre":-300,"America/Porto_Velho":-240,"America/Puerto_Rico":-240,"America/Rainy_River":-300,"America/Rankin_Inlet":-300,"America/Recife":-180,"America/Regina":-360,"America/Resolute":-300,"America/Rio_Branco":-300,"America/Rosario":-180,"America/Santa_Isabel":-420,"America/Santarem":-180,"America/Santiago":-180,"America/Santo_Domingo":-240,"America/Sao_Paulo":-180,"America/Scoresbysund":0,"America/Shiprock":-360,"America/Sitka":-480,"America/St_Barthelemy":-240,"America/St_Johns":-150,"America/St_Kitts":-240,"America/St_Lucia":-240,"America/St_Thomas":-240,"America/St_Vincent":-240,"America/Swift_Current":-360,"America/Tegucigalpa":-360,"America/Thule":-180,"America/Thunder_Bay":-240,"America/Tijuana":-420,"America/Toronto":-240,"America/Tortola":-240,"America/Vancouver":-420,"America/Virgin":-240,"America/Whitehorse":-420,"America/Winnipeg":-300,"America/Yakutat":-480,"America/Yellowknife":-360,"Antarctica/Casey":480,"Antarctica/Davis":420,"Antarctica/DumontDUrville":600,"Antarctica/Macquarie":660,"Antarctica/Mawson":300,"Antarctica/McMurdo":720,"Antarctica/Palmer":-180,"Antarctica/Rothera":-180,"Antarctica/South_Pole":720,"Antarctica/Syowa":180,"Antarctica/Troll":120,"Antarctica/Vostok":360,"Arctic/Longyearbyen":120,"Asia/Aden":180,"Asia/Almaty":360,"Asia/Amman":180,"Asia/Anadyr":720,"Asia/Aqtau":300,"Asia/Aqtobe":300,"Asia/Ashgabat":300,"Asia/Ashkhabad":300,"Asia/Baghdad":180,"Asia/Bahrain":180,"Asia/Baku":300,"Asia/Bangkok":420,"Asia/Beirut":180,"Asia/Bishkek":360,"Asia/Brunei":480,"Asia/Calcutta":330,"Asia/Chita":480,"Asia/Choibalsan":480,"Asia/Chongqing":480,"Asia/Chungking":480,"Asia/Colombo":330,"Asia/Dacca":360,"Asia/Damascus":180,"Asia/Dhaka":360,"Asia/Dili":540,"Asia/Dubai":240,"Asia/Dushanbe":300,"Asia/Gaza":180,"Asia/Harbin":480,"Asia/Hebron":180,"Asia/Ho_Chi_Minh":420,"Asia/Hong_Kong":480,"Asia/Hovd":420,"Asia/Irkutsk":480,"Asia/Istanbul":180,"Asia/Jakarta":420,"Asia/Jayapura":540,"Asia/Jerusalem":180,"Asia/Kabul":270,"Asia/Kamchatka":720,"Asia/Karachi":300,"Asia/Kashgar":360,"Asia/Kathmandu":345,"Asia/Katmandu":345,"Asia/Khandyga":540,"Asia/Kolkata":330,"Asia/Krasnoyarsk":420,"Asia/Kuala_Lumpur":480,"Asia/Kuching":480,"Asia/Kuwait":180,"Asia/Macao":480,"Asia/Macau":480,"Asia/Magadan":600,"Asia/Makassar":480,"Asia/Manila":480,"Asia/Muscat":240,"Asia/Nicosia":180,"Asia/Novokuznetsk":420,"Asia/Novosibirsk":360,"Asia/Omsk":360,"Asia/Oral":300,"Asia/Phnom_Penh":420,"Asia/Pontianak":420,"Asia/Pyongyang":540,"Asia/Qatar":180,"Asia/Qyzylorda":360,"Asia/Rangoon":390,"Asia/Riyadh":180,"Asia/Saigon":420,"Asia/Sakhalin":600,"Asia/Samarkand":300,"Asia/Seoul":540,"Asia/Shanghai":480,"Asia/Singapore":480,"Asia/Srednekolymsk":660,"Asia/Taipei":480,"Asia/Tashkent":300,"Asia/Tbilisi":240,"Asia/Tehran":270,"Asia/Tel_Aviv":180,"Asia/Thimbu":360,"Asia/Thimphu":360,"Asia/Tokyo":540,"Asia/Ujung_Pandang":480,"Asia/Ulaanbaatar":480,"Asia/Ulan_Bator":480,"Asia/Urumqi":360,"Asia/Ust-Nera":600,"Asia/Vientiane":420,"Asia/Vladivostok":600,"Asia/Yakutsk":540,"Asia/Yekaterinburg":300,"Asia/Yerevan":240,"Atlantic/Azores":0,"Atlantic/Bermuda":-180,"Atlantic/Canary":60,"Atlantic/Cape_Verde":-60,"Atlantic/Faeroe":60,"Atlantic/Faroe":60,"Atlantic/Jan_Mayen":120,"Atlantic/Madeira":60,"Atlantic/Reykjavik":0,"Atlantic/South_Georgia":-120,"Atlantic/St_Helena":0,"Atlantic/Stanley":-180,"Australia/ACT":600,"Australia/Adelaide":570,"Australia/Brisbane":600,"Australia/Broken_Hill":570,"Australia/Canberra":600,"Australia/Currie":600,"Australia/Darwin":570,"Australia/Eucla":525,"Australia/Hobart":600,"Australia/LHI":630,"Australia/Lindeman":600,"Australia/Lord_Howe":630,"Australia/Melbourne":600,"Australia/NSW":600,"Australia/North":570,"Australia/Perth":480,"Australia/Queensland":600,"Australia/South":570,"Australia/Sydney":600,"Australia/Tasmania":600,"Australia/Victoria":600,"Australia/West":480,"Australia/Yancowinna":570,"Brazil/Acre":-300,"Brazil/DeNoronha":-120,"Brazil/East":-180,"Brazil/West":-240,"Canada/Atlantic":-180,"Canada/Central":-300,"Canada/East-Saskatchewan":-360,"Canada/Eastern":-240,"Canada/Mountain":-360,"Canada/Newfoundland":-150,"Canada/Pacific":-420,"Canada/Saskatchewan":-360,"Canada/Yukon":-420,"Chile/Continental":-180,"Chile/EasterIsland":-300,"Etc/GMT":0,"Etc/GMT+0":0,"Etc/GMT+1":-60,"Etc/GMT+10":-600,"Etc/GMT+11":-660,"Etc/GMT+12":-720,"Etc/GMT+2":-120,"Etc/GMT+3":-180,"Etc/GMT+4":-240,"Etc/GMT+5":-300,"Etc/GMT+6":-360,"Etc/GMT+7":-420,"Etc/GMT+8":-480,"Etc/GMT+9":-540,"Etc/GMT-0":0,"Etc/GMT-1":60,"Etc/GMT-10":600,"Etc/GMT-11":660,"Etc/GMT-12":720,"Etc/GMT-13":780,"Etc/GMT-14":840,"Etc/GMT-2":120,"Etc/GMT-3":180,"Etc/GMT-4":240,"Etc/GMT-5":300,"Etc/GMT-6":360,"Etc/GMT-7":420,"Etc/GMT-8":480,"Etc/GMT-9":540,"Etc/GMT0":0,"Etc/Greenwich":0,"Etc/UCT":0,"Etc/UTC":0,"Etc/Universal":0,"Etc/Zulu":0,"Europe/Amsterdam":120,"Europe/Andorra":120,"Europe/Athens":180,"Europe/Belfast":60,"Europe/Belgrade":120,"Europe/Berlin":120,"Europe/Bratislava":120,"Europe/Brussels":120,"Europe/Bucharest":180,"Europe/Budapest":120,"Europe/Busingen":120,"Europe/Chisinau":180,"Europe/Copenhagen":120,"Europe/Dublin":60,"Europe/Gibraltar":120,"Europe/Guernsey":60,"Europe/Helsinki":180,"Europe/Isle_of_Man":60,"Europe/Istanbul":180,"Europe/Jersey":60,"Europe/Kaliningrad":120,"Europe/Kiev":180,"Europe/Lisbon":60,"Europe/Ljubljana":120,"Europe/London":60,"Europe/Luxembourg":120,"Europe/Madrid":120,"Europe/Malta":120,"Europe/Mariehamn":180,"Europe/Minsk":180,"Europe/Monaco":120,"Europe/Moscow":180,"Europe/Nicosia":180,"Europe/Oslo":120,"Europe/Paris":120,"Europe/Podgorica":120,"Europe/Prague":120,"Europe/Riga":180,"Europe/Rome":120,"Europe/Samara":240,"Europe/San_Marino":120,"Europe/Sarajevo":120,"Europe/Simferopol":180,"Europe/Skopje":120,"Europe/Sofia":180,"Europe/Stockholm":120,"Europe/Tallinn":180,"Europe/Tirane":120,"Europe/Tiraspol":180,"Europe/Uzhgorod":180,"Europe/Vaduz":120,"Europe/Vatican":120,"Europe/Vienna":120,"Europe/Vilnius":180,"Europe/Volgograd":180,"Europe/Warsaw":120,"Europe/Zagreb":120,"Europe/Zaporozhye":180,"Europe/Zurich":120,"Indian/Antananarivo":180,"Indian/Chagos":360,"Indian/Christmas":420,"Indian/Cocos":390,"Indian/Comoro":180,"Indian/Kerguelen":300,"Indian/Mahe":240,"Indian/Maldives":300,"Indian/Mauritius":240,"Indian/Mayotte":180,"Indian/Reunion":240,"Mexico/BajaNorte":-420,"Mexico/BajaSur":-360,"Mexico/General":-300,"Pacific/Apia":780,"Pacific/Auckland":720,"Pacific/Chatham":765,"Pacific/Chuuk":600,"Pacific/Easter":-300,"Pacific/Efate":660,"Pacific/Enderbury":780,"Pacific/Fakaofo":780,"Pacific/Fiji":720,"Pacific/Funafuti":720,"Pacific/Galapagos":-360,"Pacific/Gambier":-540,"Pacific/Guadalcanal":660,"Pacific/Guam":600,"Pacific/Honolulu":-600,"Pacific/Johnston":-600,"Pacific/Kiritimati":840,"Pacific/Kosrae":660,"Pacific/Kwajalein":720,"Pacific/Majuro":720,"Pacific/Marquesas":-570,"Pacific/Midway":-660,"Pacific/Nauru":720,"Pacific/Niue":-660,"Pacific/Norfolk":690,"Pacific/Noumea":660,"Pacific/Pago_Pago":-660,"Pacific/Palau":540,"Pacific/Pitcairn":-480,"Pacific/Pohnpei":660,"Pacific/Ponape":660,"Pacific/Port_Moresby":600,"Pacific/Rarotonga":-600,"Pacific/Saipan":600,"Pacific/Samoa":-660,"Pacific/Tahiti":-600,"Pacific/Tarawa":720,"Pacific/Tongatapu":780,"Pacific/Truk":600,"Pacific/Wake":720,"Pacific/Wallis":720,"Pacific/Yap":600}
##json.dumps()


# ###############################################################
#
# Functions
#
# ###############################################################

def getTimeZoneList():
    "fill timezone list"

    Logger.debug('%s:' % whoami())

    ##l = ["Africa/Abidjan","Africa/Accra","Africa/Addis_Ababa","Europe/Brussels","Africa/Algiers","Africa/Asmara"]
    #l = [k for k, v in sorted(timezones_json.iteritems(), key=lambda(k, v): (-v, k))]
    l = timezones_json.keys()
    #Logger.debug('%s: %r' % (whoami(), l))

    return l

# ###############################################################
