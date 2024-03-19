#!/usr/bin/env python3

import math
import csv
from evemap import EVEMAP

def _load_cdp(cdpfile='cdp.csv'):
  with open(cdpfile) as f:
    reader = csv.reader(f)
    # sys_name,planet,moon,station
    return [sys_name for sys_name,_,_,_ in list(reader)]
cdplist = [EVEMAP.name_to_id(_) for _ in _load_cdp()]
cdpset = set(cdplist)

# Brute-force nearest CDP
nearest_cdp = {sys_id:(None,999) for sys_id in EVEMAP.hs_systems}

bei_id = EVEMAP.name_to_id('Bei')
max_jumps = 5
for sys_id in EVEMAP.hs_systems:
  if sys_id == bei_id:
    x = 1
  jumps=0
  if sys_id in cdpset:
    nearest_cdp[sys_id] = ([sys_id],0)
    continue
  origins = [sys_id]
  for j in range(1,max_jumps+1):
    horizon = EVEMAP._bfs(origins,1)
    near = cdpset & horizon
    if len(near)>0:
      nearest_cdp[sys_id] = ([_ for _ in near],j)
      break
    origins = horizon

print('Jita:',nearest_cdp[EVEMAP.name_to_id('Jita')]) # Expect Jita 0
print('Bei:',nearest_cdp[EVEMAP.name_to_id('Bei')]) # Expect Hek 1
print('Eust:',nearest_cdp[EVEMAP.name_to_id('Eust')]) # Expect Hek 3
print('Amarr:',nearest_cdp[EVEMAP.name_to_id('Amarr')]) # Expect None 999

sys_names = sorted([EVEMAP.id_to_name(_) for _ in EVEMAP.hs_systems])
for sys_name in sys_names:
  sys_id = EVEMAP.name_to_id(sys_name)
  cdp,jumps = nearest_cdp[sys_id]
  if cdp is None:
    cdp_names = 'n/a'
  else:
    cdp_names = '; '.join([EVEMAP.id_to_name(c) for c in cdp])
  jump_name = jumps if jumps<999 else 'n/a'
  print(f'{sys_name},{cdp_names},{jump_name}')
