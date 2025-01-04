#!/usr/bin/env python3

from operator import itemgetter
import csv
import re
import sys

from evemap import EVEMAP

# https://www.fuzzwork.co.uk/dump/latest/staStations.csv
def load_stations(mapfile='staStations.csv'):
  with open(mapfile) as f:
    reader = csv.reader(f)
    # stationID,security,dockingCostPerVolume,maxShipVolumeDockable,officeRentalCost,operationID,stationTypeID,corporationID,solarSystemID,constellationID,regionID,stationName,x,y,z,reprocessingEfficiency,reprocessingStationsTake,reprocessingHangarFlag
    # => stationID,solarSystemID,stationName
    return [[int(line[0]),int(line[8]),line[11]] for line in list(reader)[1:]]

stations = load_stations()

def partition_station_name(s):
  pieces = s.split(' - ')
  planet = pieces[0].strip()
  station = pieces[-1].strip()
  if len(pieces)>2:
    moon = pieces[1].strip()
  else:
    moon = None 

  # Fix roman numerals in planets
  substs = [
    (' XIII', ' 13'),
    (' VIII', ' 08'),
    (' VII', ' 07'),
    (' XII', ' 12'),
    (' XIV', ' 13'),
    (' III', ' 03'),
    (' XI', ' 11'),
    (' IX', ' 09'),
    (' IV', ' 04'),
    (' VI', ' 06'),
    (' II', ' 02'),
    (' I', ' 01'),
    (' V', ' 05'),
    (' X', ' 10'),
  ]
  for pat,sub in substs:
    if pat in planet:
      planet = planet.replace(pat,sub)
      break

  # Fix digits in moons
  if moon is not None:
    m = re.search('Moon (\d+)', moon)
    if m is not None:
      moon_num = m.group(1)
      moon = re.sub('Moon \d+', f'M{moon_num.zfill(2)}', moon)
  else:
    moon = ''

  return (planet,moon,station)


def sorted_station_string(station_list):
  l2 = sorted(station_list, key=itemgetter(2))
  l1 = sorted(l2, key=itemgetter(1))
  l0 = sorted(l1, key=itemgetter(0))
  return [','.join(_) for _ in l0]

stationmap = {_:[] for _ in EVEMAP.systems}
for station,system,name in stations:
  if system not in stationmap:
    stationmap[system] = []
  stationmap[system].append(partition_station_name(name))

smap = {k:sorted_station_string(v,) for k,v in stationmap.items()}

################################################################################
# Adjust the policy here:
avoids = ['Juunigaishi'] # These are not just invalid CDPs, but also systems invalid to route through for jumps

jita_cdp = EVEMAP.bfs(['Jita'], avoids, 4)
#stac_cdp = EVEMAP.bfs(['Stacmon'], avoids, 4)
#amarr_cdp = EVEMAP.bfs(['Amarr'], avoids, 2)
#dodixie_cdp = EVEMAP.bfs(['Dodixie'], avoids, 0)
#rens_cdp = EVEMAP.bfs(['Rens'], avoids, 1)
#hek_cdp = EVEMAP.bfs(['Hek'], avoids, 1)
#averon_cdp = EVEMAP.bfs(['Averon'], avoids, 0)

# Certain systems/structures are bad for undock. This allows exceptions from the "top station" rule.
# This is less important for 3rd-party hauling, but the functionality exists nonetheless.
# If you want to remove a system entirely, use None.
# Exceptions in this list do *NOT* mean they are included as a CDP, only that
# if they are, the replacement is used (or it is removed, if None)
SPECIAL_CASES = {
  'Uedama': None, # Unsafe
  'Sivala': None, # Unsafe
  'Isanamo': None, # Unsafe
  'Haatomo': None, # Unsafe
  'Saatuban': None, # Unsafe

  'Jita': 'Jita 04,M04,Caldari Navy Assembly Plant', # Trade Hub
  'Stacmon': ',,The Quad', # Uni Structure
  'Hek': 'Hek 08,M12,Boundless Creation Factory', # Trade Hub
  'Rens': 'Rens 06,M08,Brutor Tribe Treasury', # Trade Hub
  'Dodixie': 'Dodixie 09,M20,Federation Navy Assembly Plant', # Trade Hub

  'Alenia': 'Alenia 05,M05,Republic Security Services Assembly Plant',
  'Averon': 'Averon 07,M03,The Rock', # Uni Structure
  'Direrie': 'Direrie 05,M17,Federal Freight Storage',
  'Korama': 'Korama 02,M07,Perkone Warhouse', # Collision problems with top station
  'Manarq': ',,IChooseYou Market and Industry', # Upwell Structure
  'Paara': 'Paara 02,,Sukuuvestaa Corporation Warehouse', # Collision problems with top station
  'Perimeter': ',,Scrapyard', # Uni Structure
  'Sotrentaira': 'Sotrentaira 07,M03,Genolution Biotech Production',
  'Vellaine': 'Vellaine 05,M04,Echelon Entertainment Development Studio', # Collision problems with top station
  #'Liekuri': ? Possible collision problems
}
SPECIAL_CASES.update({_:None for _ in avoids})
################################################################################

korsiki_route = ['Jita','New Caldari','Josameto','Liekuri','Obanen','Olo','Osmon','Korsiki']
#route = ['Jita','Perimeter','Urlen','Kusomonmon','Suroken','Haatomo','Uedama','Sivala','Hatakani','Kassigainen','Synchelle','Pakhshi','Tar','Merolles','Alentene','Cistuvaert','Stacmon','Aidart','Stacmon']
#route1 = ['Jita','Perimeter','Urlen','Sirppala','Inaro','Waskisen','Ikao','Uedama','Sivala','Hatakani','Kassigainen','Synchelle','Pakhshi','Tar','Merolles','Alentene','Cistuvaert','Stacmon','Aidart','Stacmon']
#route2 = ['Jita','Sobaseki','Veisto','Sarekuwa','Halaima','Kamio','Ikao','Uedama','Sivala','Hatakani','Kassigainen','Synchelle','Pakhshi','Tar','Merolles','Alentene','Cistuvaert','Stacmon','Aidart','Stacmon']

#dodi_route = ['Stacmon','Aidart','Cistuvaert','Alentene','Alenia','Tourier','Yulai','Ourapheh','Botane','Dodixie']
#aver_route = ['Stacmon','Aidart','Cistuvaert','Alentene','Merolles','Tar','Manarq','Tolle','Carirgnottin','Averon']

cdp = (
  set(jita_cdp)
| set(EVEMAP.bfs(korsiki_route,avoids,0))
)
#  set(EVEMAP.bfs(route1,avoids,0))
#| set(EVEMAP.bfs(route2,avoids,0))
#| set(EVEMAP.bfs(dodi_route,avoids,0))
#| set(EVEMAP.bfs(aver_route,avoids,0))
#| set(stac_cdp)
#| set(jita_cdp)
#| set(amarr_cdp)
#| set(dodixie_cdp)
#| set(rens_cdp)
#| set(hek_cdp)
#| set(averon_cdp)
#)


# Filter systems with stations. If you don't want them, remove the else: block.
cdp_stations = []
for c in cdp:
  top_station = smap[EVEMAP.name_to_id(c)]
  if c in SPECIAL_CASES:
    if SPECIAL_CASES[c] is None:
      pass # Omit the system
    else:
      cdp_stations.append( (c, [SPECIAL_CASES[c]]) )
  elif len(top_station)>0:
    cdp_stations.append( (c, top_station) )
  else:
    pass # Omit the system -- PushX and iChooseYou are now handled via special cases
  #else:
  #  cdp_stations.append( (c, [',,PushX Mailbox']) )


[print(f'{x},{y[0]}') for x,y in sorted(cdp_stations,key=itemgetter(0))]
print(len(cdp_stations), file=sys.stderr)
