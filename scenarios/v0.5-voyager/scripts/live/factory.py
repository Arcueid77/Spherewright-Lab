"""Finite native factory steps; configurations contain IDs/layouts and material ceilings."""
import math,time,uuid
from collections.abc import Mapping
from driver import Live,ToolRefused,AcceptedActionFailure
from evidence import need,read,sha
from contracts import powered_consumers_share_network,validate_steps,is_read_tool

def distance(a,b): return math.dist([a[k] for k in 'xyz'],[b[k] for k in 'xyz'])
def count(player,item): return sum(r['count'] for r in player['inventory'] if r['itemId']==item)

class Factory(Live):
 def __init__(self,runtime):
  super().__init__(runtime);self.refs=dict(runtime.config['existingEntities']);self.used={int(k):v for k,v in runtime.config.get('materialUsedAtHandoff',{}).items()}

 def read_args(self,tool,args):
  schema=self.schemas[tool];automatic={k:v for k,v in self.ctx.items() if k in schema['properties']}
  values=dict(automatic,**args)
  need(set(values)<=set(schema['properties']) and set(schema.get('required',[]))<=set(values),'actual_sdk_read_argument_contract_mismatch')
  return values

 def prepare_build(self,args):
  start=time.monotonic();c=self.runtime.config
  while True:
   self.state();p=self.player();args=dict(args,**self.ctx,expectedPlayerStateHash=p['stateHash'])
   try:q=self.call('spherewright_prepare_build',args);return q,p
   except ToolRefused as e:
    first=e.error.get('nativeFirstFailure') or {}
    if self.active is not None or first.get('code') not in ('native_drone_core_or_return_funding_unproved','native_construction_anchor_not_settled'):raise
    need(time.monotonic()-start<c['maximumFundingWaitSeconds'],'finite_funding_wait_exhausted')
    # Read-only observation decides when to fresh prepare. No estimated energy
    # threshold is ever substituted for the Native prepare above.
    time.sleep(2)

 def build(self,role,args,maximum):
  item=args['buildingItemId'];remaining=self.runtime.config['materialCeilings'].get(str(item),0)-self.used.get(item,0)
  need(remaining>0,'material_ceiling_exhausted')
  q,before=self.prepare_build(args);budget=q['itemBudget']
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'] and len(budget)==1
    and budget[0]['itemId']==item and 1<=budget[0]['count']<=min(maximum,remaining),'exact_build_material_plan_unproved')
  self.runtime.put(role+'-plan.private.json',q)
  r=self.successful_original(self.commit(role,'spherewright_commit_build',dict(self.ctx,planToken=q['planToken'],idempotencyKey=str(uuid.uuid4()))))
  # Once accepted, charge this original amount even if a later caller check
  # fails. A post-check must not silently restore a material allowance.
  self.used[item]=self.used.get(item,0)+budget[0]['count']
  control=r.get('constructionControl') or {};ids=[o['entityId'] for o in r.get('blueprintObjects') or [] if o.get('entityId')]
  if not control and self.ctx['planetId']!=self.runtime.config['planetId']:
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
  role=s['role'];kind=s['kind'];self.state()
  if kind=='operation':return self.native_operation(s)
  if kind=='adopt-paid-build':
   value=self.call('spherewright_get_blueprint_builds',dict(self.ctx,buildId=s['buildId']))
   rows=value.get('builds') or [];need(len(rows)==1 and rows[0]['buildId']==s['buildId'],'exact_paid_build_missing')
   objects=rows[0].get('objects') or []
   ids=[o['entityId'] for o in objects if o.get('state')=='completed' and o.get('entityId')]
   need(len(ids)==s['expectedObjects'] and len(set(ids))==len(ids),'paid_build_not_yet_native_completed')
   entities=[self.entity(i) for i in ids];need(all(e['itemId']==s['itemId'] for e in entities),'paid_entity_type_changed')
   self.refs[role]=ids;self.runtime.put(role+'-adopted-paid.private.json',dict(build=value,entities=entities,noNewCreate=True,noNewDebit=True));return
  if kind=='read':
   need(is_read_tool(s['tool']),'read_step_cannot_submit')
   value=self.call(s['tool'],self.read_args(s['tool'],s.get('arguments',{})));self.runtime.put(role+'-read.private.json',value);return value
  if kind=='build-object':
   last=None
   for position in s['positions']:
    point=self.layout(position)
    try:return self.build(role,dict(buildingItemId=s['itemId'],**dict(zip(('preferredPositionX','preferredPositionY','preferredPositionZ'),[point[k] for k in 'xyz']))),1)
    except ToolRefused as e:
     if e.error.get('code') not in ('BUILD_LOCATION_INVALID','BUILD_CONNECTION_INVALID'):raise
     last=e
   raise last or RuntimeError('no_layout_candidate')
  if kind=='build-belt':
   source=self.object_id(s['source']);last=None
   for end in s['ends']:
    point=self.layout(end);e=self.entity(source)
    try:return self.build(role,dict(buildingItemId=2001,sourceObjectId=source,expectedSourceStateHash=e['endpointStateHash'],
      **dict(zip(('pathEndX','pathEndY','pathEndZ'),[point[k] for k in 'xyz']))),s['maximumNewBelts'])
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
    try:return self.build(role,args,s['maximumNewBelts'])
    except ToolRefused as err:
     if err.error.get('code') not in ('BUILD_LOCATION_INVALID','BUILD_CONNECTION_INVALID'):raise
     last=err
   raise last or RuntimeError('no_free_belt_candidate')
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
   end=time.monotonic()+s['maximumSeconds']
   while time.monotonic()<end:
    self.state();e=self.entity(self.object_id(s['entity']))
    if sum(b['count'] for b in e['buffers'] if b['itemId']==s['itemId'])>=s['minimumCount']:
     self.runtime.put(role+'-proof.private.json',e);return e
    time.sleep(.5)
   raise RuntimeError('finite_product_wait_exhausted')
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
    priorRpcCount=closed['priorRpcCount'],requestCount=closed['requestCount'],gameTick=state['gameTick'],noSave=True,noLoad=True,noLaunch=True));return
  if kind=='save-close':self.cleanup_known_state();return
  raise ValueError('unsupported_immutable_step:'+kind)

 def native_operation(self,s):
  allowed={'spherewright_prepare_move','spherewright_prepare_harvest','spherewright_prepare_transfer',
   'spherewright_prepare_configure_building','spherewright_prepare_select_research','spherewright_prepare_handcraft',
   'spherewright_prepare_refuel','spherewright_prepare_supply_mecha_warpers','spherewright_prepare_voyager_flight',
   'spherewright_prepare_save'}
  prepare=s['prepareTool'];need(prepare in allowed,'operation_family_not_allowed')
  values=dict(context=dict(self.ctx))
  def select(path):
   x=values
   for key in path.split('.'):x=x[int(key)] if isinstance(x,(list,tuple)) else x[key]
   return x
  def resolve(x):
   if isinstance(x,Mapping) and set(x)=={'ref'}:return select(x['ref'])
   if isinstance(x,Mapping):return {k:resolve(v) for k,v in x.items()}
   if isinstance(x,(list,tuple)):return [resolve(v) for v in x]
   return x
  def check(tool,args):
   schema=self.schemas[tool];need(set(args)<=set(schema['properties']) and set(schema.get('required',[]))<=set(args),'actual_sdk_argument_contract_mismatch')
  for query in s.get('reads',[]):
   need(is_read_tool(query['tool']),'read_dependency_cannot_submit')
   name=query['name'];args=self.read_args(query['tool'],resolve(query.get('arguments',{})));check(query['tool'],args)
   values[name]=self.call(query['tool'],args);self.runtime.put(s['role']+'-'+name+'-before.private.json',values[name])
  args=dict(self.ctx,**resolve(s['arguments']));check(prepare,args);q=self.call(prepare,args)
  need(q['prepared'] and q['commitAllowedNow'] and not q['commitBlockers'],'native_operation_not_prepared')
  self.runtime.put(s['role']+'-plan.private.json',q)
  commit=prepare.replace('_prepare_','_commit_',1)
  commit_args=dict(planToken=q['planToken'],idempotencyKey=str(uuid.uuid4()))
  for key,value in self.ctx.items():
   if key in self.schemas[commit]['properties']:commit_args[key]=value
  commit_args.update(resolve(s.get('commitArguments',{})));check(commit,commit_args)
  r=self.successful_original(self.commit(s['role'],commit,commit_args))
  if prepare=='spherewright_prepare_voyager_flight':
   current=self.call('spherewright_get_session_state',{})
   need(current['sessionId']==self.ctx['sessionId'] and current['ownedBySpherewright']
    and current['localPlanetId'] in self.runtime.config.get('authorizedPlanetIds',[self.runtime.config['planetId']]),'flight_context_changed')
   self.ctx=dict(sessionId=current['sessionId'],planetId=current['localPlanetId'])
  return r

 def continue_prepared_work(self,result):
  try:self.execute_plan(self.runtime.config['initialSteps'],'initial')
  except (ToolRefused,ValueError,RuntimeError,LookupError,TypeError) as error:
   self.runtime.put('initial-plan-failure.private.json',dict(error=str(error),activeOriginalAction=self.active))
   if self.active is not None or isinstance(error,AcceptedActionFailure):raise
  self.await_next_plan()

 def execute_plan(self,steps,label):
  validate_steps(steps)
  for s in steps:
   self.step(s)
   if self.c is None:
    self.runtime.put(label+'-complete.private.json',dict(refs=self.refs,materialUsed=self.used,normalSavedAndClosed=self.cleanup_entered,callerHandoffOnly=not self.cleanup_entered));return
  self.runtime.put(label+'-complete.private.json',dict(refs=self.refs,materialUsed=self.used,session=self.call('spherewright_get_session_state',{})))

 def await_next_plan(self):
  sequence=1
  while self.c is not None and time.monotonic()<self.c.deadline-60:
   # Each plan and its hash-bearing envelope are immutable create-once files.
   # No shell/code evaluation or second writer. Refusals keep this owner alive.
   inbox=self.runtime.output/f'next-plan-{sequence:03d}.private.json'
   if not inbox.exists():time.sleep(.5);continue
   envelope=read(inbox);need(sha(envelope['path'])==envelope['sha256'],'next_plan_changed')
   plan=read(envelope['path'])
   try:self.execute_plan(plan['steps'],f'continuation-{sequence:03d}')
   except (ToolRefused,ValueError,RuntimeError,LookupError,TypeError) as error:
    self.runtime.put(f'continuation-{sequence:03d}-failure.private.json',dict(error=str(error),activeOriginalAction=self.active))
    if self.active is not None:raise
    if isinstance(error,AcceptedActionFailure):
     if not self.can_await_after_known_move(error):raise
     self.runtime.put(f'continuation-{sequence:03d}-known-failed-idle.private.json',dict(originalActionId=error.receipt['actionId'],
      originalFailureRetained=True,healthyIdleReadbackProved=True,nextPlanMustFreshPrepare=True,noAutomaticReplay=True))
   sequence+=1
  if self.c is not None:self.cleanup_known_state()

 def can_await_after_known_move(self,error):
  r=error.receipt or {}
  if r.get('state')!='action_failed' or r.get('actionKind') not in ('move','harvest') or not r.get('terminal') or self.active is not None:return False
  s=self.call('spherewright_get_session_state',{})
  if not (s.get('gameLoaded') and s.get('ownedBySpherewright') and s.get('writesAllowed') and s.get('sessionId')==self.ctx['sessionId']):return False
  p=self.player();physics=p.get('nativePhysics') or {};ground=physics.get('groundContact') or {};velocity=physics.get('velocity') or {}
  return (p.get('movementState')=='Walk' and p.get('speed',float('inf'))<=.1 and ground.get('checkSphereHit') is True
   and all(velocity.get(k)==0 for k in 'xyz') and p.get('handcraftQueue')==[] and (p.get('constructionDrones') or {}).get('working')==0)
