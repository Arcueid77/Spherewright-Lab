"""An ordinary remote save is bound to its exact new finite recovery plan."""
from pathlib import Path
from types import SimpleNamespace
import copy
import sys
import time
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from driver import Live


class SavedRemoteDriverTests(unittest.TestCase):
    def setUp(self):
        self.config=dict(recoveryProfile='ordinary-owned-remote',recoveryMode='authorize_remote_primary_recovery',
            sourceRole='primary',sourceTick=1200,planetId=201,expectedNativeVersion='native',
            recoveryWindowSeconds=7200,additionalVoyagerGameTicks=8000,originalJourneyMaximumGameTicks=108000,
            surfaceRecoveryTarget=None)
        self.plan=dict(prepared=True,planToken='new-plan',confirmationDigest='new-digest',
            recoveryMode='authorize_remote_primary_recovery',userConfirmationRequired=True,commitAllowedNow=False,
            commitBlockers=[dict(code='USER_CONFIRMATION_REQUIRED')],exactEmbeddedIdentityVerified=True,
            sourceGameVersion='native',targetGameVersion='native',remotePrimaryRecoveryAuthorizationUsed=True,
            successfulOutboundSurfaceSourceUsed=False,completedSavedLandingAdmissionUsed=False,
            failedLandingRecoveryAuthorizationUsed=False,originalFailedFlightActionId='',
            savedLandingAccountingAnchorGameTick=None,nativeOriginalOutcomeProved=False,
            discardedUnstoredProgressGameTicks=0,candidateGameTick=1200,minimumGameTick=1200,
            expectedPlanetId=201,additionalVoyagerGameTicks=8000,originalJourneyMaximumGameTicks=108000,
            effectiveJourneyMaximumGameTicks=116000)

    def adapter(self,plan=None):
        a=Live(None);a.runtime=SimpleNamespace(config=self.config,put=lambda *_:None);a.calls=[]
        def call(name,args):
            a.calls.append((name,args));return copy.deepcopy(self.plan if plan is None else plan)
        a.call=call;return a

    def prepare(self,a):
        return a.prepare_resume(dict(session=dict(restartResumeAvailable=True,restartResumeToken='token')),
                                time.monotonic()+5)

    def test_fresh_remote_plan_binds_the_saved_tick_and_addition_without_submitting(self):
        a=self.adapter();self.assertEqual(self.plan,self.prepare(a))
        name,args=a.calls[0]
        self.assertEqual('spherewright_prepare_resume_owned_game',name)
        self.assertEqual((1200,1200,8000),(args['minimumRecoveryGameTick'],args['expectedRecoveryGameTick'],
                                          args['additionalVoyagerGameTicks']))
        self.assertEqual('continue_original_finite_task',args['recoveryScope'])
        self.assertNotIn('surfaceRecoveryTargetX',args)
        self.assertFalse(any('_commit_' in name for name,_ in a.calls))

    def test_changed_identity_tick_or_authority_cannot_produce_a_committable_plan(self):
        for key,value in [('sourceGameVersion','other'),('targetGameVersion','other'),
            ('exactEmbeddedIdentityVerified',False),('recoveryMode','other'),('candidateGameTick',1199),
            ('minimumGameTick',1199),('expectedPlanetId',202),('additionalVoyagerGameTicks',8001),
            ('effectiveJourneyMaximumGameTicks',116001),('successfulOutboundSurfaceSourceUsed',True),
            ('completedSavedLandingAdmissionUsed',True),('failedLandingRecoveryAuthorizationUsed',True),
            ('nativeOriginalOutcomeProved',True),('discardedUnstoredProgressGameTicks',1)]:
            with self.subTest(key=key):
                bad=copy.deepcopy(self.plan);bad[key]=value;a=self.adapter(bad)
                with self.assertRaises(RuntimeError):self.prepare(a)
                self.assertFalse(any('_commit_' in name for name,_ in a.calls))

    def test_wrong_remote_shape_refuses_before_any_call(self):
        for key,value in [('sourceRole','lastExit'),('recoveryMode','default'),
            ('surfaceRecoveryTarget',dict(x=1,y=2,z=3)),('sourceTick',-1),
            ('additionalVoyagerGameTicks',-1),('additionalVoyagerGameTicks',5184001),
            ('recoveryWindowSeconds',86401)]:
            with self.subTest(key=key):
                self.config[key]=value;a=self.adapter()
                with self.assertRaisesRegex(RuntimeError,'ordinary_remote_source_shape_invalid'):self.prepare(a)
                self.assertEqual([],a.calls)
                self.setUp()


if __name__=='__main__':unittest.main()
