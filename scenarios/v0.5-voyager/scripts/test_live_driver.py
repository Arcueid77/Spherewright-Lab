"""Caller regressions: actual DTO shape, unaccepted refusals and original-action ownership."""
from pathlib import Path
import copy
import sys,unittest,tempfile,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from contracts import ordinary_owned_resume_echo,powered_consumers_share_network,paused_failed_cut,validate_steps,resume_admission_echo,validate_native_calls,strict_native_player_idle,fully_observed_dry_surface,observed_short_crossing_dry_landing,native_warper_auto_supply_enabled
from driver import Live,ToolRefused,AcceptedActionFailure,NativePreacceptanceRefusal
from factory import Factory,resolve_refs
from runtime import freeze,Runtime

class LiveDriverTests(unittest.TestCase):
 def test_unknown_physical_stop_only_allows_independent_saved_source_after_exact_paid_create_accounting(self):
  from contracts import quarantined_paid_original_accounted
  c=dict(recoveryMode='authorize_remote_primary_recovery',sourceRole='lastExit',sourceTick=900)
  reference=dict(actionId='original-unknown',paidObjectCount=2,itemId=2001)
  receipt=dict(actionId='original-unknown',terminal=True,state='outcome_unknown',
   constructionControl=dict(executionKind='structured_native',dispatchDisabled=True,wholeBatchDebitSharedByObjectReceipts=True),
   blueprintObjects=[dict(prebuildId=i,inventoryBefore=12,inventoryAfter=10,beforeInventoryHash='before',afterInventoryHash='after') for i in (1,2)],
   itemDeltas=[dict(itemId=2001,delta=-2)],nativeFirstFailure=dict(capturedAtGameTick=900))
  saved=dict(passed=True,originalUnknownRetained=True,noReplay=True,noResume=True,currentLastExit=900)
  self.assertTrue(quarantined_paid_original_accounted(c,reference,receipt,saved))
  for target,key,value in [('config','sourceRole','primary'),('saved','currentLastExit',899),('receipt','itemDeltas',[]),
    ('control','dispatchDisabled',False)]:
   config=copy.deepcopy(c);r=copy.deepcopy(receipt);p=copy.deepcopy(saved)
   {'config':config,'saved':p,'receipt':r,'control':r['constructionControl']}[target][key]=value
   self.assertFalse(quarantined_paid_original_accounted(config,reference,r,p))
 def test_generic_blueprint_operation_only_accepts_exact_paid_readmission_echo(self):
  a=Factory.__new__(Factory);a.ctx=dict(sessionId='synthetic',planetId=402);a.refs={};records={};calls=[]
  a.runtime=type('Runtime',(),dict(put=lambda _,name,value:records.__setitem__(name,value)))()
  fields={'sessionId':{},'planetId':{},'resumeBuildId':{},'expectedStateHash':{},'expectedPlayerStateHash':{},'allowNewPaidConstructionWindow':{}}
  a.schemas={'spherewright_prepare_blueprint_build':dict(properties=fields,required=list(fields)),
   'spherewright_commit_blueprint_build':dict(properties=dict(sessionId={},planetId={},planToken={},idempotencyKey={}))}
  build='11111111-1111-4111-8111-111111111111'
  step=dict(role='resume-paid',prepareTool='spherewright_prepare_blueprint_build',arguments=dict(resumeBuildId=build,
   expectedStateHash='fresh-progress',expectedPlayerStateHash='fresh-player',allowNewPaidConstructionWindow=True))
  def call(tool,args):
   calls.append(tool);return dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='fresh-paid',
    plannedPaidConstructionReadmission=True,blueprintBuild=dict(buildId=build))
  a.call=call;a.commit=lambda *_:'same-paid-only'
  a.successful_original=lambda _:dict(blueprintBuildId=build,itemDeltas=[],constructionControl=dict(physicalIdleVerified=True))
  self.assertEqual(build,a.native_operation_once(step)['blueprintBuildId']);self.assertEqual(['spherewright_prepare_blueprint_build'],calls)
  wrong=copy.deepcopy(step);wrong['arguments']['resumeBuildId']=''
  with self.assertRaisesRegex(RuntimeError,'paid_resume_only'):a.native_operation_once(wrong)
  a.call=lambda *_:dict(prepared=True,commitAllowedNow=True,commitBlockers=[],plannedPaidConstructionReadmission=False)
  with self.assertRaisesRegex(RuntimeError,'native_echo_missing'):a.native_operation_once(step)
 def test_generator_first_work_preserves_native_source_family_echo_and_same_tick_debit(self):
  records={};calls=[];a=Factory.__new__(Factory);a.ctx=dict(sessionId='synthetic-owned',planetId=402);a.active=None
  config=dict(firstOperation=dict(kind='generator-fuel',entityId=20,itemId=1802,count=8),initialSteps=[])
  a.runtime=type('Runtime',(),dict(config=config,put=lambda _,name,value:records.__setitem__(name,value)))()
  a.player=lambda:dict(stateHash='player',inventory=[dict(itemId=1802,count=85)])
  a.entity=lambda _:dict(stateHash='generator',fuelPowerState=dict(loadedFuelItemId=1802,loadedFuelEnergyJoules=0))
  def call(tool,args):
   calls.append((tool,args));return dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='bound-fuel',
    generatorColdStartFuel=dict(evidenceVersion=1,entityId=20,itemId=1802,count=8,emptyUnlitGenerator=True,nativeOperation='PlanetFactory.InsertInto'))
  a.call=call;work=a.prepare_first_work({},0)
  self.assertEqual('transfer',work['action_kind']);self.assertEqual('spherewright_commit_transfer',work['tool'])
  self.assertEqual('player-to-generator-fuel',calls[0][1]['direction']);self.assertEqual('generator',calls[0][1]['expectedStorageStateHash'])
  result=dict(actionId='original-generator-fuel',actionKind='transfer',terminal=True,succeeded=True,beforeTargetAmount=0,afterTargetAmount=8,
   itemDeltas=[dict(itemId=1802,delta=-8)])
  self.assertTrue(a.verify_progress(work,result));a.execute_plan=lambda *_:None;a.await_next_plan=lambda:None
  a.continue_prepared_work(result);self.assertTrue(records['first-generator-fuel-native-conservation.private.json']['passed'])
  result['afterTargetAmount']=9;self.assertFalse(a.verify_progress(work,result))
 def test_normal_refuel_crosses_real_startup_dispatch_readback_and_factory_continuation(self):
  import startup_to_action as gate
  records={};a=Factory.__new__(Factory);a.ctx=dict(sessionId='synthetic-owned',planetId=402);a.active=None
  config=dict(firstOperation=dict(kind='refuel',itemId=1802,count=20,useNativeExactCount=True),initialSteps=[])
  a.runtime=type('Runtime',(),dict(config=config,put=lambda _,name,value:records.__setitem__(name,value)))()
  a.offline_preflight=lambda:{k:True for k in gate.READINESS_FLAGS};a.launch_once=lambda _:1
  a.wait_ready=lambda *_:{};a.prepare_resume=lambda *_:'fresh-resume';a.commit_resume_once=lambda _:'original-resume'
  a.verify_loaded=lambda *_:{};a.player=lambda:dict(stateHash='fresh',inventory=[dict(itemId=1802,count=100)])
  terminal=dict(actionId='original-fuel',actionKind='refuel',terminal=True,state='completed',succeeded=True,
   beforeTargetAmount=75,afterTargetAmount=90,itemDeltas=[dict(itemId=1802,delta=-15)])
  a.wait_original=lambda handle:dict(actionId=handle,terminal=True,state='completed',succeeded=True) if handle=='original-resume' else terminal
  def call(tool,args):
   if tool=='spherewright_prepare_refuel':
    if args['count']==20:raise ToolRefused(tool,dict(code='INVALID_REQUEST',retryable=True,
     message="DSP's native one-stack fuel transfer will move exactly 15 item(s) into grid 2; the requested count was 20."))
    self.assertEqual(15,args['count']);return dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='bound-fuel-plan')
   self.assertEqual('spherewright_commit_refuel',tool);return dict(actionId='original-fuel',accepted=True)
  a.call=call;a.execute_plan=lambda *_:records.__setitem__('prepared-work-executed',True)
  a.await_next_plan=lambda:None;a.cleanup_known_state=lambda:self.fail('successful native work cannot trigger cleanup')
  result=gate.run(a,lambda _:None)
  self.assertTrue(result.passed,result.failure);self.assertEqual('original-fuel',result.first_action_id)
  self.assertTrue(records['prepared-work-executed']);self.assertTrue(records['actual-progress.private.json']['verified'])
  self.assertEqual(15,records['first-refuel-native-conservation.private.json']['exactPackageDebit'])
 def test_captured_native_partial_fuel_capacity_fresh_prepares_and_proves_the_exact_original_transfer(self):
  import time
  records={};a=Factory.__new__(Factory);a.ctx=dict(sessionId='synthetic-owned',planetId=402);a.active=None
  config=dict(firstOperation=dict(kind='refuel',itemId=1802,count=20,useNativeExactCount=True),initialSteps=[])
  a.runtime=type('Runtime',(),dict(config=config,put=lambda _,name,value:records.__setitem__(name,value)))()
  observations=iter([dict(stateHash='first',inventory=[dict(itemId=1802,count=100)]),
   dict(stateHash='fresh',inventory=[dict(itemId=1802,count=100)]),
   dict(stateHash='after',inventory=[dict(itemId=1802,count=88)],fuelStorage=[dict(itemId=1802,count=89)])])
  a.player=lambda:next(observations);calls=[]
  def call(tool,args):
   calls.append((tool,args))
   if len(calls)==1:raise ToolRefused(tool,dict(code='INVALID_REQUEST',retryable=True,
    message="DSP's native one-stack fuel transfer will move exactly 12 item(s) into grid 2; the requested count was 20."))
   return dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='fresh-count-bound-plan')
  a.call=call;work=a.prepare_first_work({},time.monotonic()+30)
  self.assertEqual([(20,'first'),(12,'fresh')],[(x[1]['count'],x[1]['expectedPlayerStateHash']) for x in calls])
  result=dict(actionId='original-only',actionKind='refuel',terminal=True,succeeded=True,beforeTargetAmount=78,afterTargetAmount=90,
   itemDeltas=[dict(itemId=1802,delta=-12)])
  self.assertTrue(a.verify_progress(work,result))
  self.assertEqual(12,records['actual-progress.private.json']['exactNativeTransferCount'])
  a.execute_plan=lambda *_:None;a.await_next_plan=lambda:None;a.continue_prepared_work(result)
  self.assertEqual(12,records['first-refuel-native-conservation.private.json']['exactPackageDebit'])
 def test_native_refuel_disclosure_cannot_increase_the_immutable_fuel_ceiling(self):
  import time
  a=Live(None);a.runtime=type('Config',(),dict(config=dict(firstOperation=dict(kind='refuel',itemId=1802,count=20,useNativeExactCount=True))))()
  a.ctx={};a.active=None;a.player=lambda:dict(stateHash='fresh')
  def refused(tool,args):raise ToolRefused(tool,dict(code='INVALID_REQUEST',retryable=True,
   message="DSP's native one-stack fuel transfer will move exactly 30 item(s) into grid 3; the requested count was 20."))
  a.call=refused
  with self.assertRaises(ToolRefused):a.prepare_first_work({},time.monotonic()+30)
 def test_legacy_closed_caller_inherits_its_hash_bound_actual_rpc_baseline(self):
  from evidence import actual_prior_rpc_count,sha
  with tempfile.TemporaryDirectory() as folder:
   prior=Path(folder);config=prior/'inputs.private.json'
   config.write_text(json.dumps(dict(priorRpcCount=49092,maximumRpc=200000)),encoding='utf-8')
   (prior/'run-config-reference.private.json').write_text(json.dumps(dict(path=str(config),sha256=sha(config))),encoding='utf-8')
   closed=dict(requestCount=98,maximumRequests=150908)
   self.assertEqual(49190,actual_prior_rpc_count(prior,closed))
   config.write_text(json.dumps(dict(priorRpcCount=0,maximumRpc=200000)),encoding='utf-8')
   with self.assertRaisesRegex(RuntimeError,'original_caller_config_changed'):actual_prior_rpc_count(prior,closed)
 def test_legacy_closed_caller_rejects_a_different_original_finite_allowance(self):
  from evidence import actual_prior_rpc_count,sha
  with tempfile.TemporaryDirectory() as folder:
   prior=Path(folder);config=prior/'inputs.private.json'
   config.write_text(json.dumps(dict(priorRpcCount=49092,maximumRpc=200000)),encoding='utf-8')
   (prior/'run-config-reference.private.json').write_text(json.dumps(dict(path=str(config),sha256=sha(config))),encoding='utf-8')
   with self.assertRaisesRegex(RuntimeError,'original_caller_allowance_mismatch'):
    actual_prior_rpc_count(prior,dict(requestCount=98,maximumRequests=200000))
 def test_first_refuel_is_a_fresh_prepare_not_an_automatic_resubmit(self):
  a=Live(None);a.runtime=type('Config',(),dict(config=dict(firstOperation=dict(kind='refuel',itemId=1802,count=20))))()
  a.ctx=dict(sessionId='synthetic-owned',planetId=1);a.player=lambda:dict(stateHash='fresh-player')
  calls=[]
  def call(tool,args):
   calls.append((tool,args));return dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='not-committed')
  a.call=call;work=a.prepare_first_work({},0)
  self.assertEqual('spherewright_commit_refuel',work['tool'])
  self.assertEqual([('spherewright_prepare_refuel',dict(a.ctx,itemId=1802,count=20,expectedPlayerStateHash='fresh-player'))],calls)
 def test_packet_preflight_and_execution_share_duplicate_receipt_admission_before_effects(self):
  steps=[dict(kind='wait-buffer',role='product',entity=7,itemId=1127,minimumCount=20,maximumSeconds=60),
   dict(kind='dump',role='product',queries=[])]
  # Structural validation alone admitted this real caller error; packet
  # preflight must use precisely the production admission before publishing.
  validate_steps(steps)
  a=Factory.__new__(Factory);a.schemas={};a.runtime=None
  a.step=lambda *_:self.fail('rejected packet cannot reach a world step')
  with self.assertRaisesRegex(RuntimeError,'immutable_plan_duplicate_roles'):a.validate_plan(steps)
  with self.assertRaisesRegex(RuntimeError,'immutable_plan_duplicate_roles'):a.execute_plan(steps,'packet')
 def test_partial_plan_handoff_requires_its_last_settled_world_step_and_an_explicit_wait(self):
  from handoff_blocked_buffer import blocked_suffix
  steps=[dict(kind='operation',role='chips'),dict(kind='dump',role='chip-proof'),
   dict(kind='wait-buffer',role='product',entity=7,itemId=1127,minimumCount=20),
   dict(kind='operation',role='take-back'),dict(kind='operation',role='silo')]
  wait,suffix=blocked_suffix(steps,'product','chips')
  self.assertEqual(20,wait['minimumCount']);self.assertEqual(['take-back','silo'],suffix)
  with self.assertRaisesRegex(RuntimeError,'exact_last_settled_prefix'):blocked_suffix(steps,'product','older-action')
  invalid=copy.deepcopy(steps);invalid[2]['kind']='operation'
  with self.assertRaisesRegex(RuntimeError,'explicit_positive_native_buffer'):blocked_suffix(invalid,'product','chips')
  invalid=copy.deepcopy(steps);invalid[2]['entity']='unresolved-reference'
  with self.assertRaisesRegex(RuntimeError,'explicit_positive_native_buffer'):blocked_suffix(invalid,'product','chips')
 def test_old_module_stamp_refuses_offline_before_game_or_file_loading(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'stamps.json';p.write_text(json.dumps(dict(passed=True,sourceSha='old')))
   r=Runtime.__new__(Runtime);r.config=dict(sourceSha='new',revisionStamps=str(p))
   with self.assertRaisesRegex(RuntimeError,'revision_stamp_source_changed_before_launch'):r.verify_revision_stamps()

 def test_failed_pre_recovery_audit_stops_wait_and_preserves_without_another_launch(self):
  import time,startup_to_action as gate
  with tempfile.TemporaryDirectory() as folder:
   (Path(folder)/'startup-readiness-abort.private.json').write_text('{}')
   a=Live(None);a.runtime=type('Evidence',(),dict(output=Path(folder)))()
   a.process=lambda:self.fail('aborted readiness cannot continue launching or recovering')
   with self.assertRaises(gate.StartupReadinessFailure):a.wait_ready(None,time.monotonic()+10)
   self.assertTrue(a.failure_requires_preservation(gate.StartupReadinessFailure()))
   a.loaded=True;self.assertFalse(a.failure_requires_preservation(gate.StartupReadinessFailure()))

 def test_pre_recovery_failure_never_automatically_saves_an_unexpected_loaded_world(self):
  a=Live(None);a.runtime=type('Evidence',(),dict(config={}))();a.preserve_unloaded_startup_only=True
  a.call=lambda *_:dict(gameLoaded=True,ownedBySpherewright=True,writesAllowed=True)
  with self.assertRaisesRegex(RuntimeError,'cannot_save_or_exit_an_already_loaded_world'):a.cleanup_known_state()

 def test_captured_route_hash_is_route_specific_and_not_generic_state_hash(self):
  route=json.loads((Path(__file__).parent/'fixtures/captured-voyager-route-disabled-auto-supply.json').read_text())
  self.assertFalse(route['budgetSufficient']);self.assertEqual(2,route['availableWarpers']);self.assertEqual(3,route['requiredWarpers'])
  self.assertEqual(route['routeStateHash'],resolve_refs(dict(ref='route.routeStateHash'),dict(route=route)))
  with self.assertRaises(KeyError):resolve_refs(dict(ref='route.stateHash'),dict(route=route))

 def test_warper_setting_requires_complete_exact_zero_transfer_readback(self):
  detail=dict(enabledBefore=False,enabledAfter=True,readbackComplete=True,packageContentsPreserved=True,conservationVerified=True,
   packageCountBefore=40,packageCountAfter=40,packageIncBefore=0,packageIncAfter=0,
   chamberCountBefore=2,chamberCountAfter=2,chamberIncBefore=0,chamberIncAfter=0)
  result=dict(terminal=True,succeeded=True,actionKind='configure-building',mechaWarperAutoSupplyReadback=detail)
  self.assertTrue(native_warper_auto_supply_enabled(result))
  for field,value in [('enabledAfter',None),('enabledBefore',True),('chamberCountAfter',20),('packageCountAfter',20),('packageContentsPreserved',False),('conservationVerified',False)]:
   changed=copy.deepcopy(result);changed['mechaWarperAutoSupplyReadback'][field]=value
   self.assertFalse(native_warper_auto_supply_enabled(changed),field)
  result['terminal']=False;self.assertFalse(native_warper_auto_supply_enabled(result))

 def test_warper_first_operation_uses_player_and_requires_nullable_cohort_echo(self):
  a=Live.__new__(Live);a.ctx=dict(sessionId='synthetic',planetId=104)
  a.runtime=type('Evidence',(),dict(config=dict(firstOperation=dict(entityId=0,recipeId=0,mode='enable-mecha-warper-auto-supply'))))()
  a.player=lambda:dict(stateHash='fresh-player-hash');a.entity=lambda _:self.fail('player setting cannot inspect entity0')
  args=[];plan=dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='synthetic')
  a.call=lambda name,value:args.append(value) or plan
  with self.assertRaisesRegex(RuntimeError,'cohort_echo_missing_no_commit'):a.prepare_first_work({},0)
  plan['plannedMechaWarperAutoSupplyEnabled']=True;a.prepare_first_work({},0)
  self.assertEqual('fresh-player-hash',args[-1]['expectedFactoryStateHash'])

 def test_normal_close_keeps_prior_caller_rpc_spending(self):
  a=Live.__new__(Live);a.active=None;a.cleanup_entered=False;a.prior_rpc_count=30;records={}
  a.runtime=type('Evidence',(),dict(config={},put=lambda _,name,value:records.update({name:value})))()
  a.call=lambda *_:dict(gameLoaded=False)
  a.c=type('Client',(),dict(close=lambda _:dict(requestCount=7,normalEof=True,processExitCode=0)))()
  a.normal_close_current_process=lambda:None;a.cleanup_known_state()
  self.assertEqual(30,records['client-close.private.json']['priorRpcCount']);self.assertEqual(7,records['client-close.private.json']['requestCount'])
  self.assertIsNone(a.c)

 def test_only_explicit_unaccepted_stale_reprepares_with_new_evidence_role(self):
  from unittest.mock import patch
  a=Factory.__new__(Factory);a.active=None;seen=[];health=[];receipts=[]
  a.runtime=type('Evidence',(),dict(put=lambda _,name,value:receipts.append((name,value))))()
  a.state=lambda:health.append(True)
  def once(step,commit_requested):
   seen.append(step['role'])
   if len(seen)==1:
    captured=json.loads((Path(__file__).parent/'fixtures/captured-unaccepted-transfer-stale.json').read_text())
    raise NativePreacceptanceRefusal(captured['tool'],captured['error'])
   return dict(terminal=True,state='succeeded',actionId='new-original')
  a.native_operation_once=once
  with patch('factory.time.sleep'):r=a.native_operation(dict(role='dose',freshStaleMaximumSeconds=5))
  self.assertEqual(['dose','dose-fresh-01'],seen);self.assertEqual([True],health)
  self.assertFalse(receipts[0][1]['actionAccepted']);self.assertEqual('new-original',r['actionId'])

 def test_captured_transfer_refusal_has_no_accepted_handle(self):
  captured=json.loads((Path(__file__).parent/'fixtures/captured-unaccepted-transfer-stale.json').read_text())
  a=Live.__new__(Live);a.active=None;a.runtime=type('Evidence',(),dict(put=lambda *_:None))()
  def call(*_):raise ToolRefused(captured['tool'],captured['error'])
  a.call=call
  with self.assertRaises(NativePreacceptanceRefusal) as result:a.commit('original',captured['tool'],dict(planToken='synthetic',idempotencyKey='synthetic'))
  self.assertIsNone(a.active);self.assertEqual('STALE_STATE',result.exception.error['code'])

 def test_unknown_or_accepted_failure_never_reprepares(self):
  for error,active in [(ToolRefused('commit',dict(code='REQUEST_TIMEOUT')),'unresolved_submission:dose'),
    (NativePreacceptanceRefusal('commit',dict(code='STALE_STATE')),'original-accepted'),
    (AcceptedActionFailure('terminal failed',dict(actionId='original',terminal=True)),None)]:
   a=Factory.__new__(Factory);a.active=active;calls=[]
   def once(*_):calls.append(True);raise error
   a.native_operation_once=once
   with self.assertRaises(type(error)):a.native_operation(dict(role='dose',freshStaleMaximumSeconds=5))
   self.assertEqual([True],calls)

 def test_dependent_plan_requires_actual_complete_receipt(self):
  with tempfile.TemporaryDirectory() as folder:
   a=Factory.__new__(Factory);a.runtime=type('Evidence',(),dict(output=Path(folder)))()
   (Path(folder)/'continuation-003-failure.private.json').write_text('{}')
   with self.assertRaisesRegex(RuntimeError,'plan_predecessor_did_not_complete'):
    a.require_completed_predecessor(4,dict(requiresCompletedPlanSequence=3))
   (Path(folder)/'continuation-003-complete.private.json').write_text('{}')
   a.require_completed_predecessor(4,dict(requiresCompletedPlanSequence=3))
   with self.assertRaisesRegex(RuntimeError,'invalid_plan_predecessor'):
    a.require_completed_predecessor(4,dict(requiresCompletedPlanSequence=4))

 def test_long_evidence_path_rejects_complete_packet_before_any_game_step(self):
  with tempfile.TemporaryDirectory() as folder:
   a=Factory.__new__(Factory);a.schemas={'spherewright_get_session_state':dict(properties={},required=[])}
   a.runtime=type('Evidence',(),dict(output=Path(folder)))();seen=[];a.step=lambda s:seen.append(s)
   steps=[dict(kind='read',role='short',tool='spherewright_get_session_state'),dict(kind='read',role='x'*260,tool='spherewright_get_session_state')]
   with self.assertRaisesRegex(RuntimeError,'immutable_plan_evidence_path_too_long'):a.execute_plan(steps,'new')
   self.assertEqual([],seen)

 def test_actual_returning_to_sending_race_waits_then_fresh_prepares_without_clearing_cargo(self):
  from unittest.mock import patch
  a=Live.__new__(Live);a.ctx=dict(sessionId='same',planetId=104);a.active=None;a.state=lambda:None
  a.runtime=type('Evidence',(),dict(config={},put=lambda *_:None))()
  base=dict(itemId=2011,pickTargetObjectId=1,insertTargetObjectId=2,filterItemId=None)
  samples=iter([dict(base,inserterStage='Returning',buffers=[],configurationStateHash='returning'),
   dict(base,inserterStage='Sending',buffers=[dict(itemId=1106,count=1)],configurationStateHash='sending'),
   dict(base,inserterStage='Inserting',buffers=[dict(itemId=1106,count=1)],configurationStateHash='inserting')])
  a.entity=lambda _:next(samples);calls=[]
  def prepare(name,args):
   calls.append(args)
   if len(calls)==1:raise ToolRefused(name,dict(code='ACTION_REJECTED'))
   return dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='native-fresh')
  a.call=prepare
  with patch('driver.time.sleep'):q=a.prepare_sorter_filter_when_ready('volatile',7,1201)
  self.assertEqual('native-fresh',q['planToken']);self.assertEqual(['returning','inserting'],[c['expectedFactoryStateHash']for c in calls])

 def test_research_configuration_binds_fresh_current_tech_separately_from_recipe(self):
  a=Live.__new__(Live);a.ctx=dict(sessionId='same',planetId=104)
  a.runtime=type('Evidence',(),dict(put=lambda *_:None))();a.entity=lambda _:dict(stateHash='native-full-hash')
  args_seen=[]
  def call(name,args):
   if name=='spherewright_get_progression_state':return dict(currentTechId=1303)
   args_seen.append(args)
   if args.get('mode')=='research' and args.get('techId')!=1303:raise ToolRefused(name,dict(code='INVALID_TECHNOLOGY'))
   return dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='synthetic')
  a.call=call;a.commit=lambda *_:'original';a.successful_original=lambda _:dict(succeeded=True)
  a.configure('fresh-research',7,0,'research')
  self.assertEqual(1303,args_seen[0]['techId']);self.assertEqual(0,args_seen[0]['recipeId'])

 def test_production_short_crossing_checks_fresh_terminal_evidence_before_commit(self):
  sample=json.loads((Path(__file__).parent/'fixtures/captured-observed-short-crossing.json').read_text())
  player=json.loads((Path(__file__).parent/'fixtures/captured-known-move-stop.json').read_text())['player'];player['coreEnergy']=1600000000
  end=sample['surfacePreview']['samples'][-1]['position'];args=dict(arrivalTolerance=1.5,expectedPlayerStateHash='synthetic',**{'target'+k.upper():end[k]*1.001 for k in'xyz'})
  q=dict(sample,prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='synthetic')
  a=Factory.__new__(Factory);a.ctx=dict(sessionId='same',planetId=104);a.refs={}
  a.schemas=json.loads((Path(__file__).parent/'fixtures/captured-sdk-plan-schemas.json').read_text())
  a.runtime=type('Evidence',(),dict(config=dict(ordinaryConstructionPlanetIds=[104]),put=lambda *_:None))()
  a.call=lambda name,_:player if name=='spherewright_get_player_state' else q
  a.commit=lambda *_:self.fail('invalid fresh landing evidence cannot accept a Move')
  step=dict(kind='prepare-only',role='reviewed',prepareTool='spherewright_prepare_move',arguments=args,
    reads=[dict(name='p',tool='spherewright_get_player_state')],requireObservedShortCrossingDryLanding=True)
  self.assertIs(q,a.native_operation(step,commit_requested=False))
  q['surfacePreview']['samples'][-1]['shoreRisk']='detected'
  with self.assertRaisesRegex(RuntimeError,'fresh_short_crossing_dry_landing_unproved_no_commit'):a.native_operation(step)

 def test_real_short_crossing_requires_complete_observation_and_sufficient_dry_terminal_suffix(self):
  sample=json.loads((Path(__file__).parent/'fixtures/captured-observed-short-crossing.json').read_text())
  player=json.loads((Path(__file__).parent/'fixtures/captured-known-move-stop.json').read_text())['player'];player['coreEnergy']=1600000000
  end=sample['surfacePreview']['samples'][-1]['position'];args=dict(arrivalTolerance=1.5,**{'target'+k.upper():end[k]*1.001 for k in 'xyz'})
  self.assertFalse(fully_observed_dry_surface(sample))
  self.assertTrue(observed_short_crossing_dry_landing(sample,args,player))
  for bad in [dict(args,arrivalTolerance=.5),dict(args,targetX=400)]:self.assertFalse(observed_short_crossing_dry_landing(sample,bad,player))
  self.assertFalse(observed_short_crossing_dry_landing(sample,args,dict(player,coreEnergy=1279999999)))
  for field,value in [('state','partial'),('unknownSampleCount',1),('arcLengthMetres',64)]:
   bad=copy.deepcopy(sample);bad['surfacePreview'][field]=value;self.assertFalse(observed_short_crossing_dry_landing(bad,args,player))
  for field,value in [('groundHit',False),('waterHit',False),('groundBelowWaterMetres',None),('groundBelowWaterMetres',.1)]:
   bad=copy.deepcopy(sample);bad['surfacePreview']['samples'][-1][field]=value;self.assertFalse(observed_short_crossing_dry_landing(bad,args,player))
  move=dict(kind='operation',role='crossing',prepareTool='spherewright_prepare_move',arguments=args,requireObservedShortCrossingDryLanding=True)
  with self.assertRaisesRegex(ValueError,'short_crossing_requires_immediate_strict_stop'):validate_steps([move])
  validate_steps([move,dict(kind='wait-player-still',role='native-stop',maximumSeconds=45,minimumCoreEnergy=1280000000)])

 def test_existing_evidence_role_rejects_whole_plan_before_any_game_step(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'used-p-before.private.json').write_text('{}')
   a=Factory.__new__(Factory);a.schemas={'spherewright_get_session_state':dict(properties={},required=[])}
   a.runtime=type('Evidence',(),dict(output=root))();called=[];a.step=lambda s:called.append(s)
   steps=[dict(kind='read',role='fresh',tool='spherewright_get_session_state'),dict(kind='read',role='used',tool='spherewright_get_session_state')]
   with self.assertRaisesRegex(RuntimeError,'immutable_plan_role_previously_used:used'):a.execute_plan(steps,'next')
   self.assertEqual([],called)
   self.assertEqual('{}',(root/'used-p-before.private.json').read_text())

 def test_captured_dry_preview_can_still_end_in_a_real_stalled_move(self):
  sample=json.loads((Path(__file__).parent/'fixtures/captured-dry-preview-stalled-walk.json').read_text())
  self.assertTrue(fully_observed_dry_surface(sample))
  self.assertFalse(sample['originalOutcome']['succeeded'])
  self.assertTrue(sample['originalOutcome']['doNotRetrySameTarget'])
  for field,value in [('state','partial'),('unknownSampleCount',1),('shoreRisk','detected'),('arcLengthMetres',65)]:
   bad=copy.deepcopy(sample);bad['surfacePreview'][field]=value
   self.assertFalse(fully_observed_dry_surface(bad))
  for field,value in [('groundHit',False),('waterHit',None),('groundBelowWaterMetres',None),('groundBelowWaterMetres',0)]:
   bad=copy.deepcopy(sample);bad['surfacePreview']['samples'][0][field]=value
   self.assertFalse(fully_observed_dry_surface(bad))
  dry=copy.deepcopy(sample)
  for row in dry['surfacePreview']['samples']:row.update(waterHit=False,groundBelowWaterMetres=None)
  self.assertTrue(fully_observed_dry_surface(dry))

 def test_opted_in_production_move_rejects_unknown_terrain_before_commit(self):
  sample=json.loads((Path(__file__).parent/'fixtures/captured-dry-preview-stalled-walk.json').read_text())
  q=dict(sample,prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='synthetic')
  a=Factory.__new__(Factory);a.ctx=dict(sessionId='same',planetId=7);a.refs={}
  a.schemas=json.loads((Path(__file__).parent/'fixtures/captured-sdk-plan-schemas.json').read_text())
  events=[];a.runtime=type('Evidence',(),dict(put=lambda _,name,value:events.append(name)))()
  a.call=lambda *_:q;a.commit=lambda *_:self.fail('terrain rejection must never accept an action')
  step=dict(kind='prepare-only',role='actual-advisory',prepareTool='spherewright_prepare_move',requireFullyObservedDrySurface=True,
    arguments=dict(targetX=1.,targetY=200.,targetZ=1.,expectedPlayerStateHash='synthetic'))
  self.assertIs(q,a.native_operation(step,commit_requested=False))
  q['surfacePreview']['samples'][0]['waterHit']=None
  with self.assertRaisesRegex(RuntimeError,'fresh_move_dry_surface_advisory_unproved_no_commit'):
   a.native_operation(step,commit_requested=True)

 def test_native_elevated_free_span_forwards_observed_layers_without_changing_material_writer(self):
  a=Factory.__new__(Factory);a.state=lambda:None;a.layout=lambda p:p
  a.ctx=dict(sessionId='synthetic',planetId=101)
  calls=[];a.build=lambda role,args,maximum:calls.append((role,args,maximum))
  a.step(dict(kind='build-free-belt',role='native-observed',maximumNewBelts=13,candidates=[dict(
    start=dict(x=1.,y=200.,z=1.),end=dict(x=2.,y=200.,z=2.),beltPathMode='native_elevated_grid',
    beltStartAltitudeLevel=1,beltEndAltitudeLevel=1)]))
  self.assertEqual(1,len(calls));self.assertEqual(13,calls[0][2]);self.assertEqual('native_elevated_grid',calls[0][1]['beltPathMode'])
  self.assertEqual((1,1),(calls[0][1]['beltStartAltitudeLevel'],calls[0][1]['beltEndAltitudeLevel']))

 def test_ordinary_home_resume_uses_native_null_candidate_and_no_confirmation_profile(self):
  c=dict(recoveryMode='default',sourceRole='primary',planetId=101,sourceTick=200,ticketMinimumGameTick=198,expectedNativeVersion='synthetic-version')
  p=dict(recoveryMode='default',expectedPlanetId=101,sourceGameVersion='synthetic-version',targetGameVersion='synthetic-version',
    userConfirmationRequired=False,commitAllowedNow=True,commitBlockers=[],additionalVoyagerGameTicks=0,
    originalJourneyMaximumGameTicks=None,effectiveJourneyMaximumGameTicks=None,
    candidateGameTick=None,minimumGameTick=198,exactEmbeddedIdentityVerified=False,recoveryEvidenceVersion=0,
    **{k:False for k in ('remotePrimaryRecoveryAuthorizationUsed','failedLandingRecoveryAuthorizationUsed',
      'completedSavedLandingAdmissionUsed','opensSavedWorldOnly','previousAutomationRemainsStopped','newChargingProhibited')})
  self.assertTrue(ordinary_owned_resume_echo(c,p))
  for key,value in [('candidateGameTick',0),('minimumGameTick',197),('userConfirmationRequired',True),
      ('sourceGameVersion','other-version'),('opensSavedWorldOnly',True),('originalJourneyMaximumGameTicks',0)]:
   with self.subTest(key=key):self.assertFalse(ordinary_owned_resume_echo(c,dict(p,**{key:value})))
  verified=dict(c,recoveryMode='verified_newer_lastexit',sourceRole='lastExit')
  p.update(recoveryMode='verified_newer_lastexit',candidateGameTick=200,minimumGameTick=200,
    exactEmbeddedIdentityVerified=True,recoveryEvidenceVersion=1)
  self.assertTrue(ordinary_owned_resume_echo(verified,p))
  p['candidateGameTick']=199;self.assertFalse(ordinary_owned_resume_echo(verified,p))

 def test_ordinary_home_build_uses_its_real_result_branch_and_never_refunds_a_postcheck_failure(self):
  for delta,valid in [(-2,True),(-1,False)]:
   a=Factory.__new__(Factory);a.ctx=dict(planetId=104);a.used={};a.refs={}
   a.runtime=type('Evidence',(),dict(config=dict(planetId=104,ordinaryConstructionPlanetIds=[104],materialCeilings={'2001':4},maximumFundingWaitSeconds=1),put=lambda *_:None))()
   a.prepare_build=lambda _: (dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='synthetic',itemBudget=[dict(itemId=2001,count=2)]),dict(inventory=[dict(itemId=2001,count=3)]))
   a.commit=lambda *_:'original';a.successful_original=lambda _:dict(actionId='original',targetObjectIds=[100,101],itemDeltas=[dict(itemId=2001,delta=delta)])
   a.state=lambda:None;a.player=lambda:dict(inventory=[dict(itemId=2001,count=1)],constructionDrones=dict(working=0,idle=3,total=3,pendingBuildTargets=0,pendingRepairTargets=0))
   a.entity=lambda i:dict(objectId=i,itemId=2001)
   if valid:
    a.build('home-feed',dict(buildingItemId=2001),2);self.assertEqual([100,101],a.refs['home-feed'])
   else:
    with self.assertRaisesRegex(RuntimeError,'ordinary_build_original_debit_or_entities_unproved'):a.build('home-feed',dict(buildingItemId=2001),2)
   self.assertEqual(2,a.used[2001])
 def test_current_native_checkpoint_follows_owned_ticket_without_dropping_historical_roles(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);durable=root/'durable';durable.mkdir();primary=root/'Spherewright_owned.dsv';primary.write_bytes(b'synthetic')
   current=root/'Spherewright_PreFlight_synthetic-new.dsv';current.write_bytes(b'synthetic');old=root/'Spherewright_PreFlight_synthetic-old.dsv';old.write_bytes(b'synthetic')
   lock=root/'lock.json';lock.write_text(json.dumps(dict(native=dict(version='synthetic-native'))))
   ticket=durable/'flight-checkpoint.json';ticket.write_text(json.dumps(dict(ownedSaveName=primary.stem,gameVersion='synthetic-native',checkpointSaveName=current.stem)))
   r=Runtime.__new__(Runtime);r.config=dict(savePaths=dict(primary=str(primary),currentCheckpoint=str(old)),durableRoots=[str(durable)],labSourceLock=str(lock))
   self.assertEqual(current.resolve(),r.native_paths()['currentCheckpoint']);self.assertEqual(str(old),r.config['savePaths']['currentCheckpoint'])
   ticket.write_text(json.dumps(dict(ownedSaveName='foreign-owned',gameVersion='synthetic-native',checkpointSaveName=current.stem)))
   with self.assertRaisesRegex(RuntimeError,'current_checkpoint_identity_changed'):r.native_paths()
 def test_first_real_move_requires_actual_delta_grounded_walk_and_zero_native_velocity(self):
  a=Live(None);a.runtime=type('Evidence',(),dict(config=dict(firstOperation=dict(kind='move')),put=lambda *_:None))()
  a.first_before=dict(position=dict(x=0,y=200,z=0));p=dict(position=dict(x=2,y=200,z=0),movementState='Walk',speed=0,nativePhysics=dict(groundContact=dict(checkSphereHit=True),currentOrderPresent=False,queuedOrderCount=0,**{k:dict(x=0,y=0,z=0) for k in ('velocity','walkRtsVelocity','driftRtsVelocity','walkManualVelocity','driftManualVelocity')}))
  a.player=lambda:p;result=dict(succeeded=True,actionId='original')
  self.assertTrue(a.verify_progress({},result));p['nativePhysics']['groundContact']['checkSphereHit']=False
  self.assertFalse(a.verify_progress({},result))
 def test_actual_global_read_does_not_receive_planet_context_and_explicit_unknowns_reject(self):
  a=Factory.__new__(Factory);a.ctx=dict(sessionId='same',planetId=7)
  a.schemas={'spherewright_get_session_state':dict(properties={},required=[]),'spherewright_get_gameplay_journal':dict(properties=dict(sessionId={}),required=['sessionId'])}
  self.assertEqual({},a.read_args('spherewright_get_session_state',{}))
  self.assertEqual(dict(sessionId='same'),a.read_args('spherewright_get_gameplay_journal',{}))
  with self.assertRaises(RuntimeError):a.read_args('spherewright_get_session_state',dict(planetId=7))
 def test_captured_invalid_dump_shape_rejects_the_entire_plan_before_any_game_step(self):
  a=Factory.__new__(Factory);called=[];a.step=lambda s:called.append(s)
  with self.assertRaisesRegex(ValueError,'immutable_plan_shape_invalid:dump'):
   a.execute_plan([dict(kind='build-object',role='already-planned',itemId=2101,positions=[]),dict(kind='dump',role='captured-caller-error',entities=[])],'test')
  self.assertEqual([],called)
  validate_steps([dict(kind='dump',role='fixed',queries=[dict(name='player',tool='spherewright_get_player_state')])])
  with self.assertRaisesRegex(ValueError,'immutable_plan_shape_invalid:prove-network'):
   validate_steps([dict(kind='prove-network',role='captured-second-error',entities=['consumer'])])
 def test_actual_failed_session_and_player_shapes_prove_pause_without_invented_fields(self):
  s=dict(sessionId='same',gameTick=3,gameLoaded=True,ownedBySpherewright=True,writesAllowed=False,writeQuarantineActionId='original')
  p=dict(position=dict(x=1,y=2,z=3),coreEnergy=1600000000,nativeLocalControlEnergy=dict(blockers=['native_paused_not_execution_ready']))
  self.assertTrue(paused_failed_cut(s,s,p,p,'original'))
  self.assertFalse(paused_failed_cut(s,dict(s,gameTick=4),p,p,'original'))
  self.assertFalse(paused_failed_cut(s,s,p,dict(p,coreEnergy=1599999999),'original'))
  self.assertFalse(paused_failed_cut(s,s,p,dict(p,nativeLocalControlEnergy=dict(blockers=[])),'original'))
  self.assertFalse(paused_failed_cut(s,s,p,p,'other'))
 def test_actual_failed_landing_admission_is_distinct_from_completed_saved_landing_and_pins_original(self):
  c=dict(recoveryMode='authorize_failed_landing_last_exit',failedLandingActionId='original',sourceTick=3,additionalVoyagerGameTicks=0)
  p=dict(failedLandingRecoveryAuthorizationUsed=True,remotePrimaryRecoveryAuthorizationUsed=False,completedSavedLandingAdmissionUsed=False,
    priorActionTerminalFailureAttested=True,priorActionTerminalCompletionAttested=False,originalFailedFlightActionId='original',savedLandingAccountingAnchorGameTick=3,additionalVoyagerGameTicks=0,discardedUnstoredProgressGameTicks=None,exactEmbeddedIdentityVerified=True)
  self.assertTrue(resume_admission_echo(c,p))
  self.assertFalse(resume_admission_echo(c,dict(p,originalFailedFlightActionId='another')))
  self.assertFalse(resume_admission_echo(c,dict(p,completedSavedLandingAdmissionUsed=True)))
  self.assertFalse(resume_admission_echo(c,dict(p,additionalVoyagerGameTicks=1)))
  self.assertFalse(resume_admission_echo(c,dict(p,exactEmbeddedIdentityVerified=False)))
  self.assertFalse(resume_admission_echo(c,dict(p,discardedUnstoredProgressGameTicks=1)))
  self.assertFalse(resume_admission_echo(dict(c,recoveryMode='authorize_remote_primary_recovery'),dict(p,remotePrimaryRecoveryAuthorizationUsed=True,completedSavedLandingAdmissionUsed=True)))
 def test_captured_native_failed_landing_nullable_field_uses_its_actual_mode_contract(self):
  p=json.loads((Path(__file__).parent/'fixtures/captured-failed-landing-prepared.json').read_text())
  c=dict(recoveryMode=p['recoveryMode'],failedLandingActionId=p['originalFailedFlightActionId'],sourceTick=3,additionalVoyagerGameTicks=0)
  self.assertIsNone(p['discardedUnstoredProgressGameTicks']);self.assertTrue(resume_admission_echo(c,p))
  p['failedLandingRecoveryAuthorizationUsed']=False;self.assertFalse(resume_admission_echo(c,p))
 def test_successful_native_saved_landing_has_no_failed_action_or_failed_accounting_anchor(self):
  c=dict(recoveryMode='authorize_remote_primary_recovery')
  p=dict(remotePrimaryRecoveryAuthorizationUsed=True,discardedUnstoredProgressGameTicks=0,completedSavedLandingAdmissionUsed=False,
    originalFailedFlightActionId='',savedLandingAccountingAnchorGameTick=None,failedLandingRecoveryAuthorizationUsed=False,successfulFlightWitnessRetiredAtGameTick=10)
  self.assertTrue(resume_admission_echo(c,p));self.assertFalse(resume_admission_echo(c,dict(p,originalFailedFlightActionId='unmatched-failure')))
  self.assertFalse(resume_admission_echo(c,dict(p,savedLandingAccountingAnchorGameTick=3)))
  self.assertFalse(resume_admission_echo(c,dict(p,discardedUnstoredProgressGameTicks=1)))
  self.assertTrue(resume_admission_echo(c,dict(p,completedSavedLandingAdmissionUsed=True,originalFailedFlightActionId='original-failure',successfulFlightWitnessRetiredAtGameTick=None)))
 def test_actual_sdk_metadata_rejects_captured_wrong_tool_before_any_plan_execution(self):
  schemas=json.loads((Path(__file__).parent/'fixtures/captured-sdk-plan-schemas.json').read_text())
  with self.assertRaisesRegex(ValueError,'actual_sdk_unknown_tool'):
   validate_native_calls([dict(kind='read',role='captured-invalid',tool='spherewright_get_power_networks')],schemas)
  validate_native_calls([dict(kind='read',role='real-api',tool='spherewright_get_power_summary')],schemas)
  args=dict(targetX=1.,targetY=200.,targetZ=1.,expectedPlayerStateHash=dict(ref='p.stateHash'))
  validate_native_calls([dict(kind='operation',role='real-move',prepareTool='spherewright_prepare_move',arguments=args)],schemas)
  with self.assertRaisesRegex(ValueError,'actual_sdk_argument_shape'):
   validate_native_calls([dict(kind='operation',role='missing-required',prepareTool='spherewright_prepare_move',arguments={})],schemas)
  with self.assertRaisesRegex(ValueError,'actual_sdk_nonnullable'):
   validate_native_calls([dict(kind='operation',role='null-coordinate',prepareTool='spherewright_prepare_move',arguments=dict(args,targetX=None))],schemas)
 def test_captured_native_idle_observation_never_substitutes_body_zero_for_zero_rts_and_no_order(self):
  sample=json.loads((Path(__file__).parent/'fixtures/captured-known-move-stop.json').read_text());p=sample['player']
  self.assertEqual('action_failed',sample['original']['state']);self.assertFalse(sample['original']['succeeded'])
  self.assertTrue(strict_native_player_idle(p));p['nativePhysics']['walkRtsVelocity']['x']=.01;self.assertFalse(strict_native_player_idle(p))
  p['nativePhysics']['walkRtsVelocity']['x']=0;p['nativePhysics']['currentOrderPresent']=True;self.assertFalse(strict_native_player_idle(p))
  p['nativePhysics']['currentOrderPresent']=False;del p['nativePhysics']['driftManualVelocity'];self.assertFalse(strict_native_player_idle(p))
 def test_free_belt_input_binds_actual_native_device_endpoint_and_finite_exact_material_limit(self):
  a=Factory.__new__(Factory);a.refs={'station':9};a.state=lambda:None;a.entity=lambda _:dict(endpointStateHash='native-endpoint')
  a.ctx=dict(sessionId='synthetic',planetId=101)
  a.layout=lambda x:x;calls=[];a.build=lambda role,args,limit:calls.append((args,limit))
  a.step(dict(kind='build-belt-to-device',role='input',starts=[dict(x=1,y=200,z=1)],destination='station',maximumNewBelts=4))
  self.assertEqual('native-endpoint',calls[0][0]['expectedDestinationStateHash']);self.assertEqual(9,calls[0][0]['destinationObjectId'])
  self.assertNotIn('sourceObjectId',calls[0][0]);self.assertEqual(4,calls[0][1])
  self.assertNotIn('maxNewBelts',calls[0][0])
 def test_accepted_unknown_build_holds_material_budget_without_reclassifying_it_as_actual_consumption(self):
  a=Factory.__new__(Factory);a.runtime=type('Evidence',(),dict(config=dict(materialCeilings={'2001':1}),put=lambda *_:None))()
  a.ctx=dict(sessionId='same',planetId=7);a.used={};a.prepare_build=lambda args:(dict(prepared=True,commitAllowedNow=True,commitBlockers=[],itemBudget=[dict(itemId=2001,count=1)],planToken='one'),{})
  a.commit=lambda *_:'accepted-original'
  def unknown(_):raise AcceptedActionFailure('original unknown',dict(state='outcome_unknown'))
  a.successful_original=unknown
  with self.assertRaises(AcceptedActionFailure):a.build('original',dict(buildingItemId=2001),1)
  self.assertEqual({},a.used);self.assertEqual(dict(itemId=2001,count=1),a.material_holds['accepted-original'])
  with self.assertRaisesRegex(RuntimeError,'material_ceiling_exhausted'):a.build('not-a-replay',dict(buildingItemId=2001),1)
 def test_readonly_preflight_cannot_fall_through_to_a_game_commit_or_bypass_build_material_accounting(self):
  a=Factory.__new__(Factory);a.ctx=dict(sessionId='same',planetId=7);a.runtime=type('Evidence',(),dict(put=lambda *_:None))()
  a.schemas={'spherewright_prepare_build':dict(properties=dict(sessionId={},planetId={},buildingItemId={}),required=[])}
  a.call=lambda *_:dict(prepared=True,commitAllowedNow=True,commitBlockers=[])
  def forbidden(*_):raise AssertionError('a preflight must not commit')
  a.commit=forbidden;s=dict(role='native-only',prepareTool='spherewright_prepare_build',arguments=dict(buildingItemId=2001))
  self.assertTrue(a.native_operation(s,commit_requested=False)['prepared'])
  with self.assertRaisesRegex(RuntimeError,'operation_family_not_allowed'):a.native_operation(s)
 def test_native_object_candidate_keeps_its_explicit_sdk_yaw_in_the_exact_build_call(self):
  a=Factory.__new__(Factory);a.state=lambda:None;a.layout=lambda x:x;calls=[];a.build=lambda role,args,limit:calls.append(args)
  a.ctx=dict(sessionId='synthetic',planetId=101)
  a.step(dict(kind='build-object',role='oriented-device',itemId=2311,positions=[dict(x=1,y=200,z=1,preferredYaw=90.)]))
  self.assertEqual(90.,calls[0]['preferredYaw']);self.assertEqual(2311,calls[0]['buildingItemId'])
 def test_native_recovery_required_paused_landing_keeps_healthy_session_without_inventing_quarantine(self):
  s=dict(sessionId='same',gameTick=3,localPlanetId=7,gameLoaded=True,ownedBySpherewright=True,writesAllowed=True,writeQuarantineActionId=None,flightCheckpointId='native-current')
  p=dict(position=dict(x=1,y=2,z=3),coreEnergy=33120896,nativeLocalControlEnergy=dict(blockers=['native_paused_not_execution_ready']))
  t=dict(actionId='original',actionKind='interplanetary-flight',state='recovery_required',recoveryRequired=True,flightCheckpointId='native-current',voyagerFlightReadback=dict(bindingVerified=True,nativeExitObserved=True,actualPlanetId=7))
  self.assertTrue(paused_failed_cut(s,s,p,p,'original',t))
  self.assertFalse(paused_failed_cut(s,s,p,p,'original'))
  self.assertFalse(paused_failed_cut(s,dict(s,flightCheckpointId='another'),p,p,'original',t))
  self.assertFalse(paused_failed_cut(s,s,p,p,'original',dict(t,voyagerFlightReadback=dict(bindingVerified=True,nativeExitObserved=False,actualPlanetId=7))))
 def test_frozen_operation_resolves_nested_hash_references_to_json_scalars(self):
  a=Factory.__new__(Factory);a.ctx=dict(sessionId='same',planetId=7)
  a.runtime=type('Evidence',(),dict(put=lambda *_:None))()
  a.schemas={
   'spherewright_get_player_state':dict(properties=dict(sessionId={},planetId={}),required=['sessionId','planetId']),
   'spherewright_prepare_move':dict(properties={k:{} for k in ('sessionId','planetId','targetX','targetY','targetZ','expectedPlayerStateHash')},required=[]),
   'spherewright_commit_move':dict(properties={k:{} for k in ('sessionId','planetId','planToken','idempotencyKey')},required=[])}
  observed=[]
  def call(tool,args):
   observed.append((tool,args));json.dumps(args)
   return dict(stateHash='fresh') if tool=='spherewright_get_player_state' else dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='one')
  a.call=call;a.commit=lambda *_:'original';a.successful_original=lambda _:dict(succeeded=True)
  s=freeze(dict(role='move',prepareTool='spherewright_prepare_move',reads=[dict(name='p',tool='spherewright_get_player_state',arguments={})],arguments=dict(targetX=1,targetY=2,targetZ=3,expectedPlayerStateHash=dict(ref='p.stateHash'))))
  a.native_operation(s);self.assertEqual('fresh',observed[-1][1]['expectedPlayerStateHash'])
 def test_known_failed_move_keeps_healthy_idle_writer_but_unknown_cannot_do_so(self):
  a=Factory.__new__(Factory);a.active=None;a.ctx=dict(sessionId='same')
  a.call=lambda *_:dict(gameLoaded=True,ownedBySpherewright=True,writesAllowed=True,sessionId='same')
  a.player=lambda:dict(movementState='Walk',speed=0,nativePhysics=dict(groundContact=dict(checkSphereHit=True),currentOrderPresent=False,queuedOrderCount=0,**{k:dict(x=0,y=0,z=0) for k in ('velocity','walkRtsVelocity','driftRtsVelocity','walkManualVelocity','driftManualVelocity')}),handcraftQueue=[],constructionDrones=dict(working=0))
  result=dict(actionId='original',actionKind='move',state='action_failed',terminal=True)
  self.assertTrue(a.can_await_after_known_move(AcceptedActionFailure('known',result)))
  result['state']='outcome_unknown';self.assertFalse(a.can_await_after_known_move(AcceptedActionFailure('unknown',result)))
  result['state']='action_failed';a.player=lambda:dict(movementState='Drift',speed=1)
  self.assertFalse(a.can_await_after_known_move(AcceptedActionFailure('moving',result)))
 def test_actual_detached_runpy_entry_resolves_shared_modules_outside_its_directory(self):
  script=Path(__file__).resolve().parent/'live/run.py'
  with tempfile.TemporaryDirectory() as folder:
   probe=subprocess.run([sys.executable,'-c','import runpy,sys;runpy.run_path(sys.argv[1],run_name="import_only_probe")',str(script)],
     cwd=folder,capture_output=True,text=True,timeout=10)
   self.assertEqual(0,probe.returncode,probe.stderr)
 def test_real_pole_shape_null_is_not_a_disconnected_consumer(self):
  # Exact public DTO branch captured from a real paid pole; identifiers and
  # position omitted. Membership itself still needs the public power graph.
  pole=dict(componentKind='power-node',powerNetworkId=None,recipeId=0)
  miner=dict(componentKind='miner',powerNetworkId=2)
  self.assertTrue(powered_consumers_share_network([pole,miner],2))
  self.assertFalse(powered_consumers_share_network([pole],2))
  self.assertFalse(powered_consumers_share_network([pole,dict(componentKind='miner',powerNetworkId=None)],2))
 def test_private_config_cannot_mutate_a_running_stage(self):
  x=freeze(dict(stages=[dict(item=1)]))
  with self.assertRaises(TypeError):x['stages'][0]['item']=2
 def test_unaccepted_prepare_and_local_postcheck_do_not_trigger_preservation(self):
  a=Live(None)
  self.assertFalse(a.failure_requires_preservation(ToolRefused('spherewright_prepare_build',dict(code='BUILD_LOCATION_INVALID'))))
  self.assertFalse(a.failure_requires_preservation(ValueError('local DTO mismatch')))
 def test_unknown_result_retains_original_action_and_never_submits_cleanup(self):
  a=Live(None);a.active='original';a.c=type('Client',(),dict(deadline=float('inf')))()
  a.runtime=type('Evidence',(),dict(put=lambda *_:None))()
  a.call=lambda *args:dict(terminal=True,state='outcome_unknown',succeeded=False)
  a.wait_original('original');self.assertEqual('original',a.active)
 def test_bounded_slow_poll_keeps_same_real_native_waiting_to_terminal_handle(self):
  from unittest.mock import patch
  a=Live(None);a.active='original';a.c=type('Client',(),dict(deadline=float('inf')))()
  a.runtime=type('Evidence',(),dict(config=dict(actionPollSeconds=2),put=lambda *_:None))()
  # Actual Native handcraft DTO transitions; no all-true admission substitute.
  results=iter([dict(actionId='original',actionKind='handcraft',state='waiting_for_game',terminal=False,succeeded=False),
                dict(actionId='original',actionKind='handcraft',state='completed',terminal=True,succeeded=True)])
  calls=[]
  def call(tool,args):calls.append((tool,args));return next(results)
  a.call=call
  with patch('driver.time.sleep') as sleep:
   result=a.wait_original('original');sleep.assert_called_once_with(2)
  self.assertTrue(result['succeeded']);self.assertIsNone(a.active)
  self.assertEqual([('spherewright_get_action_result',dict(actionId='original'))]*2,calls)
 def test_nonfinite_or_unbounded_poll_interval_refuses_before_rpc(self):
  for interval in (True,0,-1,float('nan'),float('inf'),31,'2'):
   a=Live(None);a.runtime=type('Evidence',(),dict(config=dict(actionPollSeconds=interval)))()
   a.call=lambda *_:self.fail('invalid poll policy must not dispatch')
   with self.assertRaisesRegex(RuntimeError,'bounded_original_action_poll_interval_required'):a.wait_original('original')

if __name__=='__main__':unittest.main()
