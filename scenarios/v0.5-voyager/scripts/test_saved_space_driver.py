"""Saved-space caller transitions, using production driver entry points."""
from pathlib import Path
import copy,sys,unittest
sys.path.insert(0,str(Path(__file__).parent/'live'))
from driver import Live
from factory import Factory
from saved_space import exact_last_exit_echo,paused_space_source,exact_ui_supply
from startup_to_action import ACTUAL_WORK_KINDS


class SavedSpaceDriverTests(unittest.TestCase):
 def setUp(self):
  self.config=dict(recoveryProfile='exact-paused-space',recoveryMode='open_saved_last_exit',
   sourceTick=1000,expectedNativeVersion='synthetic-version',firstOperation=dict(kind='supply-mecha-warpers',count=18))
  self.session=dict(sessionId='synthetic',gameLoaded=True,ownedBySpherewright=True,writesAllowed=False,
   writeHealth='quarantined',writeQuarantineActionId='synthetic-open',localPlanetId=None,gameTick=1000,
   writeBlockers=[dict(code='WRITE_SUBSYSTEM_QUARANTINED')])
  self.player=dict(planetId=0,isOnPlanet=False,stateHash='fresh',movementState='Sail',
   spaceTransit=dict(speed=0,nativePaused=True,warping=False,warpCommand=False,warpState=0))
  self.plan=dict(recoveryMode='open_saved_last_exit',candidateGameTick=1000,minimumGameTick=1000,
   sourceGameVersion='synthetic-version',targetGameVersion='synthetic-version',exactEmbeddedIdentityVerified=True,
   opensExactLastExitOnly=True,opensSavedWorldOnly=True,previousAutomationRemainsStopped=True,
   newChargingProhibited=True,userConfirmationRequired=True,commitAllowedNow=False,
   commitBlockers=[dict(code='USER_CONFIRMATION_REQUIRED')],additionalVoyagerGameTicks=0)

 def adapter(self):
  a=Live(None);a.runtime=type('Evidence',(),dict(config=self.config,put=lambda *args:None))()
  a.player=lambda:copy.deepcopy(self.player)
  return a

 def test_exact_open_is_a_paused_source_and_not_healthy_automation(self):
  self.assertTrue(exact_last_exit_echo(self.config,self.plan))
  self.assertTrue(paused_space_source(self.config,self.session,self.player,'synthetic-open'))
  a=self.adapter();a.call=lambda *args:copy.deepcopy(self.session)
  a.verify_loaded(dict(succeeded=True,actionId='synthetic-open'),None)
  self.assertEqual(0,a.ctx['planetId']);self.assertTrue(a.loaded)
  for key,value in [('gameTick',999),('writesAllowed',True),('writeQuarantineActionId','foreign')]:
   changed=dict(self.session,**{key:value})
   self.assertFalse(paused_space_source(self.config,changed,self.player,'synthetic-open'))
  changed=dict(self.session,writeBlockers=self.session['writeBlockers']+[dict(code='OTHER')])
  self.assertFalse(paused_space_source(self.config,changed,self.player,'synthetic-open'))
  for key,value in [('nativePaused',False),('speed',float('nan')),('warpState',None)]:
   changed=copy.deepcopy(self.player);changed['spaceTransit'][key]=value
   self.assertFalse(paused_space_source(self.config,self.session,changed,'synthetic-open'))

 def test_prepare_open_uses_exact_tick_without_charging_or_old_task_grant(self):
  a=self.adapter();calls=[]
  a.call=lambda name,args:calls.append((name,args)) or self.plan
  import time
  a.prepare_resume(dict(session=dict(restartResumeToken='synthetic-token')),time.monotonic()+5)
  args=calls[0][1]
  self.assertEqual({'resumeToken','recoveryMode','minimumRecoveryGameTick','expectedRecoveryGameTick'},set(args))
  self.assertEqual(1000,args['expectedRecoveryGameTick'])
  changed=dict(self.plan,opensExactLastExitOnly=None)
  self.assertFalse(exact_last_exit_echo(self.config,changed))

 def test_first_work_requires_explicit_ui_echo_before_any_commit(self):
  a=self.adapter();a.ctx=dict(sessionId='synthetic',planetId=0);calls=[]
  plan=dict(prepared=True,commitAllowedNow=True,commitBlockers=[],planToken='synthetic')
  a.call=lambda name,args:calls.append((name,args)) or plan
  with self.assertRaisesRegex(RuntimeError,'first_native_ui_supply_unproved'):a.prepare_first_work(None,None)
  plan['plannedMechaWarperUiTopUp']=True
  w=a.prepare_first_work(None,None)
  self.assertEqual('spherewright_commit_supply_mecha_warpers',w['tool'])
  self.assertIn(w['action_kind'],ACTUAL_WORK_KINDS)
  self.assertTrue(calls[-1][1]['uiTopUp']);self.assertEqual(18,calls[-1][1]['count'])
  self.assertFalse(any('_commit_' in name for name,_ in calls))

 def test_supply_counts_and_inc_must_conserve_at_native_call_boundary(self):
  r=dict(terminal=True,succeeded=True,actionKind='supply_mecha_warpers',mechaWarperSupplyReadback=dict(requestedCount=18,actualStored=18,
   evidenceScope='synchronous_native_ui_partial_warper_chamber_topup',autoReplenishWarperBefore=True,autoReplenishWarperAfter=True,
   packageCountBefore=20,packageCountAfter=2,chamberCountBefore=2,chamberCountAfter=20,
   packageIncBefore=0,packageIncAfter=0,chamberIncBefore=0,chamberIncAfter=0,
   readbackComplete=True,conservationVerified=True))
  self.assertTrue(exact_ui_supply(r,18))
  for key,value in [('actualStored',17),('chamberCountAfter',None),('packageCountAfter',1),('chamberIncAfter',1)]:
   changed=copy.deepcopy(r);changed['mechaWarperSupplyReadback'][key]=value
   self.assertFalse(exact_ui_supply(changed,18))

 def test_paused_space_plan_rejects_generic_build_before_world_calls(self):
  a=Factory.__new__(Factory);a.ctx=dict(planetId=0)
  a.state=lambda:self.fail('forbidden plan cannot inspect or submit world state')
  with self.assertRaisesRegex(RuntimeError,'paused_space_plan_only_reads_or_exact_home_return'):
   a.step(dict(kind='build-object',role='forbidden',itemId=1,positions=[]))


if __name__=='__main__':unittest.main()
