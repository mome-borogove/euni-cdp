#!/usr/bin/env python3

import csv

class Evemap(object):
  def __init__(self):
    self._jumps = self._load_jumps()
    self._systems = self._load_systems()

    self._id_to_name = dict([[i,name] for i,name,_ in self._systems])
    self._name_to_id = dict([[name,i] for i,name,_ in self._systems])
    self._id_to_sec = dict([[i,sec]  for i,_,sec in self._systems])

    self._jumpmap = {s:[] for s,_ in self._jumps}
    for src,dst in self._jumps:
      self._jumpmap[src].append(dst)

  # https://www.fuzzwork.co.uk/dump/latest/mapSolarSystemJumps.csv
  def _load_jumps(self, mapfile='mapSolarSystemJumps.csv'):
    with open(mapfile) as f:
      reader = csv.reader(f)
      # fromRegionID,fromConstellationID,fromSolarSystemID,toSolarSystemID,toConstellationID,toRegionID
      return [(int(src),int(dst)) for _,_,src,dst,_,_ in list(reader)[1:]]

  # https://www.fuzzwork.co.uk/dump/latest/mapSolarSystems.csv
  def _load_systems(self, mapfile='mapSolarSystems.csv'):
    with open(mapfile) as f:
      reader = csv.reader(f)
      # regionID,constellationID,solarSystemID,solarSystemName,x,y,z,xMin,xMax,yMin,yMax,zMin,zMax,luminosity,border,fringe,corridor,hub,international,regional,constellation,security,factionID,radius,sunTypeID,securityClass
      # => ID, Name, Security
      return [[int(line[2]),line[3],float(line[21])] for line in list(reader)[1:]]
  
  def id_to_name(self, sys_id):
    return self._id_to_name[sys_id]
  def name_to_id(self, name):
    return self._name_to_id[name]
  def id_to_sec(self, sys_id):
    return self._id_to_sec[sys_id]

  def adj(self, sys_id):
    return self._jumpmap[sys_id]

  def bfs(self, origins, jumps=1):
    return [self.id_to_name(n) for n in self._bfs([self.name_to_id(i) for i in origins], jumps)]

  def _bfs(self, origin_ids, jumps=1):
    # High-sec-only breadth-first search
    visited = set(origin_ids)
    horizon0 = [_ for _ in visited]
    for gates in range(0,jumps):
      horizon1 = set([])
      for v0 in horizon0:
        v1 = set([_ for _ in self.adj(v0) if self.is_hs(_)])
        horizon1 |= v1 - visited
      visited |= horizon1
      horizon0 = horizon1
    return visited # n.b.- this is a set


  def is_hs(self, sys_id):
    sec = self.id_to_sec(sys_id)
    return (sec>=0.45)
  def is_ls(self, sys_id):
    sec = self.id_to_sec(sys_id)
    return (sec<0.45) and (sec>=0) # TODO verify >=0
  def is_ls(self, sys_id):
    sec = self.id_to_sec(sys_id)
    return (sec<0) # TODO verify <0
  @property
  def systems(self):
    return [sys_id for sys_id,_,_ in self._systems]
  @property
  def hs_systems(self):
    return [sys_id for sys_id,_,_ in self._systems if self.is_hs(sys_id)]
  @property
  def ls_systems(self):
    return [sys_id for sys_id,_,_ in self._systems if self.is_ls(sys_id)]
  @property
  def ns_systems(self):
    return [sys_id for sys_id,_,_ in self._systems if self.is_ns(sys_id)]

EVEMAP = Evemap()



