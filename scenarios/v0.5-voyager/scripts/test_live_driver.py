"""Caller regressions: actual DTO shape, unaccepted refusals and original-action ownership."""
from pathlib import Path
import copy
import sys,unittest,tempfile,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from contracts import ordinary_owned_resume_echo,powered_consumers_share_network,paused_failed_cut,validate_steps,resume_admission_echo,validate_native_calls,strict_native_player_idle,fully_observed_dry_surface
from driver import Live,ToolRefused,AcceptedActionFailure
from factory import Factory
from runtime import freeze,Runtime

class LiveDriverTests(unittest.TestCase):
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
  a.layout=lambda x:x;calls=[];a.build=lambda role,args,limit:calls.append((args,limit))
  a.step(dict(kind='build-belt-to-device',role='input',starts=[dict(x=1,y=200,z=1)],destination='station',maximumNewBelts=4))
  self.assertEqual('native-endpoint',calls[0][0]['expectedDestinationStateHash']);self.assertEqual(9,calls[0][0]['destinationObjectId'])
  self.assertNotIn('sourceObjectId',calls[0][0]);self.assertEqual(4,calls[0][1])
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

if __name__=='__main__':unittest.main()
