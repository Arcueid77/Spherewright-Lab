"""Finite native factory steps; configurations contain IDs/layouts and material ceilings."""
import math,time,uuid
from collections.abc import Mapping
from driver import Live,ToolRefused,AcceptedActionFailure,NativePreacceptanceRefusal
from evidence import need,read,sha
from contracts import powered_consumers_share_network,validate_steps,is_read_tool,validate_native_calls,strict_native_player_idle,fully_observed_dry_surface,observed_short_crossing_dry_landing,observed_item_count
from flight_observers import observe_sails,observe_rocket

def distance(a,b): return math.dist([a[k] for k in 'xyz'],[b[k] for k in 'xyz'])
def count(player,item): return sum(r['count'] for r in player['inventory'] if r['itemId']==item)

def resolve_refs(x,values):
 if isinstance(x,Mapping) and set(x)=={'ref'}:
  value=values
  for key in x['ref'].split('.'):value=value[int(key)] if isinstance(value,(list,tuple)) else value[key]
  return value
 if isinstance(x,Mapping):return {k:resolve_refs(v,values) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [resolve_refs(v,values) for v in x]
 return x

class Factory(Live):
 def __init__(self,runtime):
  super().__init__(runtime);self.refs=dict(runtime.config['existingEntities']);self.used={int(k):v for k,v in runtime.config.get('materialUsedAtHandoff',{}).items()}
  self.material_holds=dict(runtime.config.get('materialReservationsAtHandoff',{}))

 def read_args(self,tool,args):
  schema=self.schemas[tool];automatic={k:v for k,v in self.ctx.items() if k in schema['properties']}
  values=dict(automatic,**args)
  need(set(values)<=set(schema['properties']) and set(schema.get('required',[]))<=set(values),'actual_sdk_read_argument_contract_mismatch')
  return values

 def prepare_build(self,args):
  start=time.monotonic();c=self.runtime.config;refusals=0
  while True:
   self.state();p=self.player();args=dict(args,**self.ctx,expectedPlayerStateHash=p['stateHash'])
   try:q=self.call('spherewright_prepare_build',args);return q,p
   except ToolRefused as e:
    first=e.error.get('nativeFirstFailure') or {}
    if self.active is not None or first.get('code') not in ('native_drone_core_or_return_funding_unproved','native_construction_anchor_not_settled'):raise
    need(time.monotonic()-start<c['maximumFundingWaitSeconds'],'finite_funding_wait_exhausted')
    # Read-only observation decides when to fresh prepare. No estimated energy
    # threshold is ever substituted for the Native prepare above.
    refusals+=1;time.sleep(min(30,2**min(refusals,5)))

 def build(self,role,args,maximum):
  self.material_holds=getattr(self,'material_holds',{})
  item=args['buildingItemId'];held=sum(x['count'] for x in self.material_holds.values() if x['itemId']==item)
  remaining=self.runtime.config['materialCeilings'].get(str(item),0)-self.used.get(item,0)-held
  need(remaining>0,'material_ceiling_exhausted')
  q,before=self.prepare_build(args);budget=q['itemBudget']
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'] and len(budget)==1
    and budget[0]['itemId']==item and 1<=budget[0]['count']<=min(maximum,remaining),'exact_build_material_plan_unproved')
  self.runtime.put(role+'-plan.private.json',q)
  original=self.commit(role,'spherewright_commit_build',dict(self.ctx,planToken=q['planToken'],idempotencyKey=str(uuid.uuid4())))
  self.material_holds[original]=dict(itemId=item,count=budget[0]['count'])
  self.runtime.put(role+'-original-material-hold.private.json',dict(originalActionId=original,heldBudget=self.material_holds[original],actualConsumptionNotYetProved=True))
  r=self.successful_original(original)
  # Once accepted, charge this original amount even if a later caller check
  # fails. A post-check must not silently restore a material allowance.
  self.used[item]=self.used.get(item,0)+budget[0]['count']
  self.material_holds.pop(original)
  self.runtime.put(role+'-native-success-material-account.private.json',dict(originalActionId=original,actualConsumedBudget=budget[0],materialUsed=self.used,materialReservations=self.material_holds))
  control=r.get('constructionControl') or {};ids=[o['entityId'] for o in r.get('blueprintObjects') or [] if o.get('entityId')]
  ordinary=self.runtime.config.get('ordinaryConstructionPlanetIds')
  ordinary_here=self.ctx['planetId'] in ordinary if ordinary is not None else self.ctx['planetId']!=self.runtime.config['planetId']
  if not control and ordinary_here:
   # Ordinary home construction uses positive targetObjectIds and Native
   # topology completion, not the remote structured-control DTO branch.
   ids=r.get('targetObjectIds') or []
   need(len(ids)==budget[0]['count'] and len(set(ids))==len(ids) and all(type(i)is int and i>0 for i in ids)
    and sum(d['delta'] for d in r.get('itemDeltas',[]) if d['itemId']==item)==-len(ids),'ordinary_build_original_debit_or_entities_unproved')
   end=time.monotonic()+self.runtime.config['maximumFundingWaitSeconds']
   while True:
    self.state();p=self.player();d=p.get('constructionDrones') or {}
    if d.get('working')==0 and d.get('idle')==d.get('total') and d.get('pendingBuildTargets')==0 and d.get('pendingRepairTargets')==0:break
    need(time.monotonic()<end,'ordinary_build_native_drone_idle_still_unproved');time.sleep(.5)
   need(count(p,item)==count(before,item)-len(ids),'ordinary_build_package_delta_needs_original_reconciliation')
   self.runtime.put(role+'-ordinary-native-idle.private.json',dict(originalActionId=r['actionId'],player=p,controlNotApplicable=True))
  else:
   need(control.get('physicalIdleVerified') and control.get('exactBindingVerified') and control.get('wholeBatchDebitSharedByObjectReceipts')
     and len(ids)==budget[0]['count'] and len(set(ids))==len(ids) and count(self.player(),item)==count(before,item)-len(ids),
     'completed_build_postcheck_needs_original_reconciliation')
  result=[self.entity(i) for i in ids];need(all(e['itemId']==item for e in result),'completed_entity_type_changed')
  self.refs[role]=ids;self.runtime.put(role+'-entities.private.json',dict(entities=result,originalActionId=r['actionId'],buildId=r.get('blueprintBuildId'),debit=budget[0]['count']))
  return result

 def object_id(self,ref):
  value=self.refs[ref] if isinstance(ref,str) else ref
  if isinstance(value,(list,tuple)):need(len(value)==1,'single_entity_reference_required');return value[0]
  return value

 def layout(self,point):
  if 'x' in point:return dict(point)
  c=self.runtime.config['layout'];base=self.entity(self.object_id(c['origin']))['position'];generator=self.entity(self.object_id(c['axisToward']))['position']
  a=[base[k] for k in 'xyz'];length=math.sqrt(sum(x*x for x in a));up=[x/length for x in a]
  raw=[generator[k]-base[k] for k in 'xyz'];proj=sum(x*y for x,y in zip(raw,up));east=[x-proj*y for x,y in zip(raw,up)]
  mag=math.sqrt(sum(x*x for x in east));need(mag>0,'layout_axis_degenerate');east=[x/mag for x in east]
  north=[up[1]*east[2]-up[2]*east[1],up[2]*east[0]-up[0]*east[2],up[0]*east[1]-up[1]*east[0]]
  q=[v+point['east']*e+point['north']*n for v,e,n in zip(a,east,north)];m=math.sqrt(sum(x*x for x in q))
  return dict(zip('xyz',[x*length/m for x in q]))

 def step(self,s):
  if self.ctx['planetId']==0:
   need(s['kind'] in ('read','dump') or s['kind'] in ('operation','prepare-only')
    and s.get('prepareTool')=='spherewright_prepare_interplanetary_flight',
    'paused_space_plan_only_reads_or_exact_home_return')
  role=s['role'];kind=s['kind'];self.state()
  if kind=='operation':return self.native_operation(s)
  if kind=='prepare-only':return self.native_operation(s,commit_requested=False)
  if kind=='observe-sail-conversion':return observe_sails(self,s)
  if kind=='observe-rocket-arrival':return observe_rocket(self,s)
  if kind=='adopt-paid-build':
   value=self.call('spherewright_get_blueprint_builds',dict(self.ctx,buildId=s['buildId']))
   rows=value.get('builds') or [];need(len(rows)==1 and rows[0]['buildId']==s['buildId'],'exact_paid_build_missing')
   objects=rows[0].get('objects') or []
   ids=[o['entityId'] for o in objects if o.get('state')=='completed' and o.get('entityId')]
   need(len(ids)==s['expectedObjects'] and len(set(ids))==len(ids),'paid_build_not_yet_native_completed')
   entities=[self.entity(i) for i in ids];need(all(e['itemId']==s['itemId'] for e in entities),'paid_entity_type_changed')
   action=rows[0].get('actionId');held=self.material_holds.get(action)
   if held is not None:
    need(held['itemId']==s['itemId'] and held['count']==len(ids)
      and all(o.get('inventoryBefore') is not None and o.get('inventoryAfter')==o['inventoryBefore']-len(ids)
       and o.get('beforeInventoryHash') and o.get('afterInventoryHash') for o in objects),'original_reserved_material_debit_unproved')
    self.used[s['itemId']]=self.used.get(s['itemId'],0)+held['count'];self.material_holds.pop(action)
   self.refs[role]=ids;self.runtime.put(role+'-adopted-paid.private.json',dict(build=value,entities=entities,noNewCreate=True,noNewDebit=True));return
  if kind=='read':
   need(is_read_tool(s['tool']),'read_step_cannot_submit')
   args=resolve_refs(s.get('arguments',{}),dict(context=self.ctx,refs=self.refs))
   value=self.call(s['tool'],self.read_args(s['tool'],args));self.runtime.put(role+'-read.private.json',value);return value
  if kind=='build-object':
   last=None
   for position in s['positions']:
    point=self.layout(position)
    args=dict(buildingItemId=s['itemId'],**dict(zip(('preferredPositionX','preferredPositionY','preferredPositionZ'),[point[k] for k in 'xyz'])))
    if 'preferredYaw' in point:args['preferredYaw']=point['preferredYaw']
    try:return self.build(role,args,1)
    except ToolRefused as e:
     if e.error.get('code') not in ('BUILD_LOCATION_INVALID','BUILD_CONNECTION_INVALID'):raise
     last=e
   raise last or RuntimeError('no_layout_candidate')
  if kind=='build-belt':
   source=self.object_id(s['source']);last=None
   for end in s['ends']:
    point=self.layout(end);e=self.entity(source)
    args=dict(buildingItemId=2001,sourceObjectId=source,expectedSourceStateHash=e['endpointStateHash'],
      **dict(zip(('pathEndX','pathEndY','pathEndZ'),[point[k] for k in 'xyz'])))
    for key in ('beltPathMode','beltStartAltitudeLevel','beltEndAltitudeLevel'):
     if key in s:args[key]=s[key]
    try:return self.build(role,args,s['maximumNewBelts'])
    except ToolRefused as err:
     if err.error.get('code') not in ('BUILD_LOCATION_INVALID','BUILD_CONNECTION_INVALID'):raise
     last=err
   raise last or RuntimeError('no_belt_candidate')
  if kind=='build-free-belt':
   last=None
   for candidate in s['candidates']:
    start=self.layout(candidate['start']);end=self.layout(candidate['end'])
    args=dict(buildingItemId=2001,preferredPositionX=start['x'],preferredPositionY=start['y'],preferredPositionZ=start['z'],
      pathEndX=end['x'],pathEndY=end['y'],pathEndZ=end['z'])
    for key in ('beltPathMode','beltStartAltitudeLevel','beltEndAltitudeLevel'):
     if key in candidate:args[key]=candidate[key]
    try:return self.build(role,args,s['maximumNewBelts'])
    except ToolRefused as err:
     if err.error.get('code') not in ('BUILD_LOCATION_INVALID','BUILD_CONNECTION_INVALID'):raise
     last=err
   raise last or RuntimeError('no_free_belt_candidate')
  if kind=='build-belt-to-device':
   destination=self.object_id(s['destination']);last=None
   for start in s['starts']:
    target=self.entity(destination);point=self.layout(start)
    try:return self.build(role,dict(buildingItemId=2001,destinationObjectId=destination,expectedDestinationStateHash=target['endpointStateHash'],
      **dict(zip(('preferredPositionX','preferredPositionY','preferredPositionZ'),[point[k] for k in 'xyz']))),s['maximumNewBelts'])
    except ToolRefused as error:
     if error.error.get('code') not in ('BUILD_LOCATION_INVALID','BUILD_CONNECTION_INVALID'):raise
     last=error
   raise last or RuntimeError('no_native_device_input_path_candidate')
  if kind=='build-sorter':
   dest=self.object_id(s['destination']);sources=self.refs[s['source']] if isinstance(s['source'],str) else [s['source']]
   if not isinstance(sources,(list,tuple)):sources=[sources]
   entities=[self.entity(i) for i in sources];target=self.entity(dest)
   entities.sort(key=lambda e:distance(e['position'],target['position']));last=None
   for e in entities[:s.get('maximumCandidates',3)]:
    target=self.entity(dest)
    try:return self.build(role,dict(buildingItemId=2011,sourceObjectId=e['objectId'],destinationObjectId=dest,
      expectedSourceStateHash=e['endpointStateHash'],expectedDestinationStateHash=target['endpointStateHash'],initialSorterFilterItemId=s['filterItemId']),1)
    except ToolRefused as err:
     if err.error.get('code') not in ('BUILD_LOCATION_INVALID','BUILD_CONNECTION_INVALID'):raise
     last=err
   raise last or RuntimeError('no_sorter_candidate')
  if kind=='configure':
   return self.configure(role,self.object_id(s['entity']),s.get('recipeId',0),s.get('mode','production'),s.get('filterItemId',0))
  if kind=='wait-buffer':
   interval=s.get('pollSeconds',2)
   need(type(interval) in (int,float) and .25<=interval<=30,'bounded_product_poll_interval_required')
   end=time.monotonic()+s['maximumSeconds']
   while time.monotonic()<end:
    self.state();e=self.entity(self.object_id(s['entity']))
    if observed_item_count(e,s['itemId'])>=s['minimumCount']:
     self.runtime.put(role+'-proof.private.json',e);return e
    time.sleep(interval)
   raise RuntimeError('finite_product_wait_exhausted')
  if kind=='wait-player-still':
   end=time.monotonic()+s['maximumSeconds']
   while time.monotonic()<end:
    self.state();p=self.player();physics=p.get('nativePhysics') or {};velocity=physics.get('velocity') or {};ground=physics.get('groundContact') or {}
    if strict_native_player_idle(p) and p.get('coreEnergy',0)>=s.get('minimumCoreEnergy',0):
     self.runtime.put(role+'-physical-still.private.json',p);return p
    time.sleep(.5)
   raise RuntimeError('finite_grounded_physical_still_wait_exhausted')
  if kind=='prove-network':
   entities=[self.entity(self.object_id(ref)) for ref in s['entities']]
   need(powered_consumers_share_network(entities,s['networkId']),'consumer_network_unproved')
   power=self.call('spherewright_get_power_summary',self.ctx);self.runtime.put(role+'-proof.private.json',dict(entities=entities,power=power));return
  if kind=='dump':
   for query in s['queries']:
    self.runtime.put(role+'-'+query['name']+'.private.json',self.call(query['tool'],self.read_args(query['tool'],query.get('arguments',{}))))
   return
  if kind=='handoff-caller':
   need(self.active is None,'unsettled_action_prevents_caller_handoff');state=self.state()
   closed=self.c.close();closed['priorRpcCount']=getattr(self,'prior_rpc_count',0);self.runtime.put('client-close.private.json',closed);self.c=None
   self.runtime.put('caller-handoff.private.json',dict(callerStopped=True,noActiveGameAction=True,gameProcessRetained=True,
     priorRpcCount=closed['priorRpcCount'],requestCount=closed['requestCount'],gameTick=state['gameTick'],noSave=True,noLoad=True,noLaunch=True,
     materialUsed=self.used,materialReservations=self.material_holds));return
  if kind=='save-close':self.cleanup_known_state();return
  raise ValueError('unsupported_immutable_step:'+kind)

 def native_operation(self,s,commit_requested=True):
  seconds=s.get('freshStaleMaximumSeconds',0)
  need(type(seconds) in(int,float) and 0<=seconds<=60,'finite_fresh_stale_allowance_required')
  end=time.monotonic()+seconds;attempt=0
  while True:
   step=dict(s)
   if attempt:step['role']=s['role']+f'-fresh-{attempt:02d}'
   try:return self.native_operation_once(step,commit_requested)
   except (ToolRefused,NativePreacceptanceRefusal) as error:
    # Only an explicit Native STALE_STATE before acceptance permits a NEW
    # prepare. Transport errors, missing handles and accepted failures never do.
    if self.active is not None or error.error.get('code')!='STALE_STATE' or seconds==0:raise
    self.runtime.put(step['role']+'-unaccepted-stale.private.json',dict(tool=error.tool,error=error.error,
     actionAccepted=False,originalIntentRetained=True,newPrepareRequired=True))
    if attempt>=15 or time.monotonic()>=end:raise
    self.state();time.sleep(.1);attempt+=1

 def native_operation_once(self,s,commit_requested=True):
  allowed={'spherewright_prepare_move','spherewright_prepare_harvest','spherewright_prepare_transfer',
   'spherewright_prepare_configure_building','spherewright_prepare_select_research','spherewright_prepare_handcraft',
   'spherewright_prepare_logistics_station_fleet_transfer',
   'spherewright_prepare_refuel','spherewright_prepare_supply_mecha_warpers','spherewright_prepare_voyager_flight',
   'spherewright_prepare_save','spherewright_prepare_interplanetary_flight'}
  prepare=s['prepareTool']
  if not commit_requested:allowed.add('spherewright_prepare_build')
  need(prepare in allowed,'operation_family_not_allowed')
  values=dict(context=dict(self.ctx),refs=getattr(self,'refs',{}))
  def resolve(x):return resolve_refs(x,values)
  def check(tool,args):
   schema=self.schemas[tool];need(set(args)<=set(schema['properties']) and set(schema.get('required',[]))<=set(args),'actual_sdk_argument_contract_mismatch')
  for query in s.get('reads',[]):
   need(is_read_tool(query['tool']),'read_dependency_cannot_submit')
   name=query['name'];args=self.read_args(query['tool'],resolve(query.get('arguments',{})));check(query['tool'],args)
   values[name]=self.call(query['tool'],args);self.runtime.put(s['role']+'-'+name+'-before.private.json',values[name])
  args=dict(self.ctx,**resolve(s['arguments']));check(prepare,args);q=self.call(prepare,args)
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'native_operation_not_prepared')
  if prepare=='spherewright_prepare_interplanetary_flight' and self.ctx['planetId']==0:
   need(q.get('plannedStoppedSpaceHomeReturn') is True,'exact_space_home_return_echo_missing_no_commit')
  self.runtime.put(s['role']+'-plan.private.json',q)
  if s.get('requireFullyObservedDrySurface'):
   need(prepare=='spherewright_prepare_move' and fully_observed_dry_surface(q),'fresh_move_dry_surface_advisory_unproved_no_commit')
  if s.get('requireObservedShortCrossingDryLanding'):
   need(prepare=='spherewright_prepare_move' and self.ctx['planetId'] in self.runtime.config.get('ordinaryConstructionPlanetIds',[])
    and observed_short_crossing_dry_landing(q,args,values.get('p',{})),'fresh_short_crossing_dry_landing_unproved_no_commit')
  if not commit_requested:
   self.runtime.put(s['role']+'-prepare-only.private.json',dict(noCommit=True,noGameActionAccepted=True,notAcceptanceEvidence=True));return q
  commit=prepare.replace('_prepare_','_commit_',1)
  commit_args=dict(planToken=q['planToken'],idempotencyKey=str(uuid.uuid4()))
  for key,value in self.ctx.items():
   if key in self.schemas[commit]['properties']:commit_args[key]=value
  commit_args.update(resolve(s.get('commitArguments',{})));check(commit,commit_args)
  r=self.successful_original(self.commit(s['role'],commit,commit_args))
  if prepare in ('spherewright_prepare_voyager_flight','spherewright_prepare_interplanetary_flight'):
   current=self.call('spherewright_get_session_state',{})
   need(current['sessionId']==self.ctx['sessionId'] and current['ownedBySpherewright'] and current['writesAllowed']
    and current['localPlanetId'] in self.runtime.config.get('authorizedPlanetIds',[self.runtime.config['planetId']]),'flight_context_changed')
   self.ctx=dict(sessionId=current['sessionId'],planetId=current['localPlanetId'])
  return r

 def continue_prepared_work(self,result):
  try:
   if self.runtime.config['firstOperation'].get('kind')=='saved-home-return':
    terminal=result if result.get('terminal') else self.successful_original(self.active)
    need(terminal.get('succeeded') is True,'original_saved_home_return_failed_no_replay')
    s=self.call('spherewright_get_session_state',{})
    need(s['ownedBySpherewright'] and s['writesAllowed'] and s['sessionId']==self.ctx['sessionId']
     and s['localPlanetId'] in self.runtime.config['authorizedPlanetIds'],'saved_home_return_healthy_save_unproved')
    self.ctx=dict(sessionId=s['sessionId'],planetId=s['localPlanetId'])
    self.runtime.put('first-home-return-complete.private.json',dict(original=terminal,session=s))
   self.execute_plan(self.runtime.config['initialSteps'],'initial')
  except (ToolRefused,ValueError,RuntimeError,LookupError,TypeError,OSError) as error:
   self.record_plan_failure('initial-plan-failure.private.json',error)
   if self.active is not None or isinstance(error,AcceptedActionFailure):raise
  self.await_next_plan()

 def record_plan_failure(self,name,error):
  native=(getattr(error,'error',None) or getattr(error,'receipt',None) or {}).get('nativeFirstFailure')
  self.runtime.put(name,dict(error=str(error),activeOriginalAction=self.active,materialUsed=self.used,materialReservations=self.material_holds,nativeFirstFailure=native))

 def validate_plan(self,steps):
  validate_steps(steps)
  validate_native_calls(steps,self.schemas)
  roles=[s['role'] for s in steps]
  need(len(roles)==len(set(roles)),'immutable_plan_duplicate_roles')
  for step in steps:
   if step.get('freshStaleMaximumSeconds',0):
    need(not any(role.startswith(step['role']+'-fresh-') for role in roles),
     'immutable_plan_fresh_attempt_role_collision')
  output=getattr(getattr(self,'runtime',None),'output',None)
  if output is not None:
   names=[p.name for p in output.iterdir()] if output.exists() else []
   for step in steps:
    role=step['role']
    # Keep per-step receipts usable on Windows hosts without long-path
    # opt-in. Reject the complete packet before its first world operation.
    suffix='-fresh-15-native-success-material-account.private.json' if step.get('freshStaleMaximumSeconds',0) else '-native-success-material-account.private.json'
    need(len(str(output/(role+suffix)))<=259,
     'immutable_plan_evidence_path_too_long_use_short_unique_roles:'+role)
    need(not any(name.startswith(role+'-') for name in names),'immutable_plan_role_previously_used:'+role)
 def execute_plan(self,steps,label):
  self.validate_plan(steps)
  for s in steps:
   self.step(s)
   if self.c is None:
    self.runtime.put(label+'-complete.private.json',dict(refs=self.refs,materialUsed=self.used,materialReservations=self.material_holds,normalSavedAndClosed=self.cleanup_entered,callerHandoffOnly=not self.cleanup_entered));return
  self.runtime.put(label+'-complete.private.json',dict(refs=self.refs,materialUsed=self.used,materialReservations=self.material_holds,session=self.call('spherewright_get_session_state',{})))

 def await_next_plan(self):
  sequence=1
  while self.c is not None and time.monotonic()<self.c.deadline-60:
   # Each plan and its hash-bearing envelope are immutable create-once files.
   # No shell/code evaluation or second writer. Refusals keep this owner alive.
   inbox=self.runtime.output/f'next-plan-{sequence:03d}.private.json'
   if not inbox.exists():time.sleep(.5);continue
   envelope=read(inbox);need(sha(envelope['path'])==envelope['sha256'],'next_plan_changed')
   plan=read(envelope['path'])
   try:
    self.require_completed_predecessor(sequence,envelope)
    self.execute_plan(plan['steps'],f'continuation-{sequence:03d}')
   except (ToolRefused,ValueError,RuntimeError,LookupError,TypeError,OSError) as error:
    self.record_plan_failure(f'continuation-{sequence:03d}-failure.private.json',error)
    if self.active is not None:raise
    if isinstance(error,AcceptedActionFailure):
     if not self.can_await_after_known_move(error):raise
     self.runtime.put(f'continuation-{sequence:03d}-known-failed-idle.private.json',dict(originalActionId=error.receipt['actionId'],
      originalFailureRetained=True,healthyIdleReadbackProved=True,nextPlanMustFreshPrepare=True,noAutomaticReplay=True))
   sequence+=1
  if self.c is not None:self.cleanup_known_state()

 def require_completed_predecessor(self,sequence,envelope):
  predecessor=envelope.get('requiresCompletedPlanSequence')
  if predecessor is None:return
  need(type(predecessor)is int and 1<=predecessor<sequence,'invalid_plan_predecessor')
  path=self.runtime.output/f'continuation-{predecessor:03d}-complete.private.json'
  need(path.is_file(),'plan_predecessor_did_not_complete_no_world_steps')

 def can_await_after_known_move(self,error):
  r=error.receipt or {}
  if r.get('state')!='action_failed' or r.get('actionKind') not in ('move','harvest') or not r.get('terminal') or self.active is not None:return False
  s=self.call('spherewright_get_session_state',{})
  if not (s.get('gameLoaded') and s.get('ownedBySpherewright') and s.get('writesAllowed') and s.get('sessionId')==self.ctx['sessionId']):return False
  p=self.player();physics=p.get('nativePhysics') or {};ground=physics.get('groundContact') or {};velocity=physics.get('velocity') or {}
  return (strict_native_player_idle(p) and p.get('handcraftQueue')==[] and (p.get('constructionDrones') or {}).get('working')==0)
