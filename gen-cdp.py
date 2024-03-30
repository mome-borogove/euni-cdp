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
jita_cdp = EVEMAP.bfs(['Jita'], 4)
stac_cdp = EVEMAP.bfs(['Stacmon'], 4)
amarr_cdp = []#EVEMAP.bfs(['Amarr'], 2)
dodixie_cdp = EVEMAP.bfs(['Dodixie'], 1)
rens_cdp = []#EVEMAP.bfs(['Rens'], 1)
hek_cdp = []#EVEMAP.bfs(['Hek'], 1)

SPECIAL_CASES = {
  'Uedama': None, # REMOVE
  'Jita': 'Jita 04,M04,Caldari Navy Assembly Plant',
  'Stacmon': ',,The Quad',
  'Hek': 'Hek 08,M12,Boundless Creation Factory',
  'Rens': 'Rens 06,M08,Brutor Tribe Treasury',
  'Dodixie': 'Dodixie 09,M20,Federation Navy Assembly Plant',
}
################################################################################

route = ['Jita','Perimeter','Urlen','Kusomonmon','Suroken','Haatomo','Uedama','Sivala','Hatakani','Kassigainen','Synchelle','Pakhshi','Tar','Merolles','Alentene','Cistuvaert','Stacmon','Aidart','Stacmon']

cdp = set(EVEMAP.bfs(route,0)) | set(stac_cdp) | set(jita_cdp) | set(amarr_cdp) | set(dodixie_cdp) | set(rens_cdp) | set(hek_cdp)


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
    cdp_stations.append( (c, [',,PushX Mailbox']) )


[print(f'{x},{y[0]}') for x,y in sorted(cdp_stations,key=itemgetter(0))]
print(len(cdp_stations), file=sys.stderr)
