"""Caller regressions: actual DTO shape, unaccepted refusals and original-action ownership."""
from pathlib import Path
import sys,unittest,tempfile,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from contracts import powered_consumers_share_network,paused_failed_cut,validate_steps,resume_admission_echo
from driver import Live,ToolRefused,AcceptedActionFailure
from factory import Factory
from runtime import freeze,Runtime

class LiveDriverTests(unittest.TestCase):
 def test_ordinary_home_build_uses_its_real_result_branch_and_never_refunds_a_postcheck_failure(self):
  for delta,valid in [(-2,True),(-1,False)]:
   a=Factory.__new__(Factory);a.ctx=dict(planetId=104);a.used={};a.refs={}
   a.runtime=type('Evidence',(),dict(config=dict(planetId=402,materialCeilings={'2001':4},maximumFundingWaitSeconds=1),put=lambda *_:None))()
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
   self.assertEqual(current,r.native_paths()['currentCheckpoint']);self.assertEqual(str(old),r.config['savePaths']['currentCheckpoint'])
   ticket.write_text(json.dumps(dict(ownedSaveName='foreign-owned',gameVersion='synthetic-native',checkpointSaveName=current.stem)))
   with self.assertRaisesRegex(RuntimeError,'current_checkpoint_identity_changed'):r.native_paths()
 def test_first_real_move_requires_actual_delta_grounded_walk_and_zero_native_velocity(self):
  a=Live(None);a.runtime=type('Evidence',(),dict(config=dict(firstOperation=dict(kind='move')),put=lambda *_:None))()
  a.first_before=dict(position=dict(x=0,y=200,z=0));p=dict(position=dict(x=2,y=200,z=0),movementState='Walk',speed=0,nativePhysics=dict(groundContact=dict(checkSphereHit=True),velocity=dict(x=0,y=0,z=0)))
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
    priorActionTerminalFailureAttested=True,priorActionTerminalCompletionAttested=False,originalFailedFlightActionId='original',savedLandingAccountingAnchorGameTick=3,additionalVoyagerGameTicks=0)
  self.assertTrue(resume_admission_echo(c,p))
  self.assertFalse(resume_admission_echo(c,dict(p,originalFailedFlightActionId='another')))
  self.assertFalse(resume_admission_echo(c,dict(p,completedSavedLandingAdmissionUsed=True)))
  self.assertFalse(resume_admission_echo(c,dict(p,additionalVoyagerGameTicks=1)))
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
  a.player=lambda:dict(movementState='Walk',speed=0,nativePhysics=dict(groundContact=dict(checkSphereHit=True),velocity=dict(x=0,y=0,z=0)),handcraftQueue=[],constructionDrones=dict(working=0))
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

if __name__=='__main__':unittest.main()
