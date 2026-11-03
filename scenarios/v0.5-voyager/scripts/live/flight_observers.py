"""Copied Native counters only; no simulation, manufacture, firing or replay."""
import time
from evidence import need,read,sha


class SailConversionTrace:
 def __init__(self,initial,count,orbit):
  self.count=count;self.orbit=orbit;self.flight_seen=False;self.converted=False;self.star=initial['starId'];self.base=initial['activeSailCount']
  self.base_orbit=self.target(initial)['sailCount']
  self.check(initial)
  need(initial['sailCount']==count and initial['inFlightSailCount']==0,'exact_isolated_sail_ammo_baseline_required')
 def target(self,s):
  matches=[o for o in s['orbits'] if o['orbitId']==self.orbit and o['enabled']]
  need(len(matches)==1,'exact_native_sail_orbit_missing');return matches[0]
 def check(self,s):
  need(s['nativeBindingVerified'] and s['swarmAvailable'] and s['orbitCoverageComplete']
   and s['starEjectorCoverageComplete'] and s['starEjectorCount']==1 and s['starId']==self.star,'sail_native_source_coverage_changed')
  need(type(s['sailCount'])is int and type(s['activeSailCount'])is int and type(s['inFlightSailCount'])is int,'sail_native_counts_unavailable')
 def observe(self,s):
  self.check(s);ammo=s['sailCount'];flying=s['inFlightSailCount'];arrived=s['activeSailCount']-self.base
  need(s['orbitId']==self.orbit and s['runtimeOrbitId']==self.orbit and not s['automaticOrbitSelection'],'native_sail_target_orbit_changed')
  need(min(ammo,flying,arrived)>=0 and ammo+flying+arrived==self.count,'isolated_native_sail_mass_balance_changed')
  self.flight_seen |= flying>0 and ammo<self.count
  self.converted |= arrived>0 and ammo<self.count
  return (self.flight_seen and self.converted and ammo==0 and flying==0 and arrived==self.count
   and self.target(s)['sailCount']-self.base_orbit==self.count)


class RocketArrivalTrace:
 def __init__(self,initial,planet,layer,node):
  self.planet=planet;self.layer=layer;self.node=node;self.star=initial['starId'];self.rocket=None;self.last_progress=None
  self.check(initial);self.base=self.target(initial)['structurePoints'];self.initial_ammo=initial['rocketCount']
  need(self.base==0 and initial['inFlightRocketCount']==0,'pristine_native_rocket_target_baseline_required')
 def target(self,s):
  matches=[n for n in s['nodes'] if n['layerId']==self.layer and n['nodeId']==self.node]
  need(len(matches)==1,'exact_native_rocket_receiving_node_missing');return matches[0]
 def check(self,s):
  need(s['nativeBindingVerified'] and s['sphereAvailable'] and s['rocketCoverageComplete'] and s['nodeCoverageComplete']
   and s['starSiloCoverageComplete'] and s['starSiloCount']==1 and s['starId']==self.star,'rocket_native_source_coverage_changed')
 def observe(self,s):
  self.check(s);n=self.target(s);need(0<=n['structurePoints']-self.base<=1 and 0<=s['rocketCount']<=1,'more_than_one_native_rocket_or_point_observed')
  need(type(s['inFlightRocketCount'])is int and 0<=s['inFlightRocketCount']<=1 and len(s['rockets'])==s['inFlightRocketCount'],'native_rocket_pool_count_unproved')
  for r in s['rockets']:
   need(r['sourcePlanetId']==self.planet and r['targetLayerId']==self.layer and r['targetNodeId']==self.node,'rocket_source_or_target_changed')
   need(self.rocket in (None,r['rocketId']),'second_native_rocket_observed');self.rocket=r['rocketId']
   progress=r['nativeFlightProgress'];need(self.last_progress is None or progress>=self.last_progress,'native_rocket_flight_regressed');self.last_progress=progress
  return self.rocket is not None and s['rocketCount']==0 and s['inFlightRocketCount']==0 and n['structurePoints']==self.base+1 and n['orderedStructurePoints']==0


def baseline(executor,step,entity):
 need(sha(step['baselinePath'])==step['baselineSha256'],'immutable_native_baseline_changed');initial=read(step['baselinePath'])
 need(initial['sessionId']==executor.ctx['sessionId'] and initial['planetId']==executor.ctx['planetId'] and initial['objectId']==entity,'native_baseline_identity_changed')
 executor.runtime.put(step['role']+'-baseline-reference.private.json',dict(path=step['baselinePath'],sha256=step['baselineSha256']))
 return initial


def observe_sails(executor,step):
 entity=executor.object_id(step['entity']);initial=baseline(executor,step,entity);s=initial.get('ejector') or {}
 trace=SailConversionTrace(s,step['count'],step['orbitId'])
 end=time.monotonic()+step['maximumSeconds'];sample=0
 while time.monotonic()<end:
  executor.state();e=executor.entity(entity);sample+=1;executor.runtime.put(step['role']+f'-native-{sample:05d}.private.json',e)
  if trace.observe(e.get('ejector') or {}):
   executor.runtime.put(step['role']+'-proof.private.json',dict(passed=True,exactAmmoConsumed=step['count'],nativeFlightObserved=True,nativeSwarmConversionObserved=True,final=e));return
  time.sleep(1)
 raise RuntimeError('finite_native_sail_observation_window_ended_no_replay')


def observe_rocket(executor,step):
 entity=executor.object_id(step['entity']);initial=baseline(executor,step,entity);trace=RocketArrivalTrace(initial.get('silo') or {},executor.ctx['planetId'],step['layerId'],step['nodeId'])
 end=time.monotonic()+step['maximumSeconds'];sample=0
 while time.monotonic()<end:
  executor.state();e=executor.entity(entity);sample+=1;executor.runtime.put(step['role']+f'-native-{sample:05d}.private.json',e)
  if trace.observe(e.get('silo') or {}):
   executor.runtime.put(step['role']+'-proof.private.json',dict(passed=True,rocketId=trace.rocket,nativeFlightObserved=True,exactNativeStructurePointAdded=1,final=e));return
  time.sleep(1)
 raise RuntimeError('finite_native_rocket_observation_window_ended_no_replay')
