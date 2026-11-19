"""Saved surface-source caller tests; no Unity world or real save is used."""
from pathlib import Path
import copy
import json
import math
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / 'live'))
from contracts import quarantined_local_move_saved_source, resume_admission_echo, completed_saved_surface_move
from driver import Live
from evidence import sha
from runtime import Runtime
import sdk_probe


class SavedSurfaceDriverTests(unittest.TestCase):
    def setUp(self):
        self.config = dict(recoveryProfile='successful-outbound-surface',
            recoveryMode='authorize_remote_primary_recovery', sourceRole='primary',
            sourceTick=1200, planetId=201, expectedNativeVersion='synthetic-native', recoveryWindowSeconds=7200,
            additionalVoyagerGameTicks=300, originalJourneyMaximumGameTicks=10000,
            surfaceRecoveryTarget=dict(x=200., y=1., z=2.))
        self.plan = dict(prepared=True, planToken='new-plan', confirmationDigest='new-digest',
            recoveryMode='authorize_remote_primary_recovery', exactEmbeddedIdentityVerified=True,
            sourceGameVersion='synthetic-native', targetGameVersion='synthetic-native',
            userConfirmationRequired=True, commitAllowedNow=False,
            commitBlockers=[dict(code='USER_CONFIRMATION_REQUIRED')],
            remotePrimaryRecoveryAuthorizationUsed=True, successfulOutboundSurfaceSourceUsed=True,
            renamedLastExitIdentityRestorationPlanned=False, expectedRenamedLastExitContentHash='',
            completedSavedLandingAdmissionUsed=False, failedLandingRecoveryAuthorizationUsed=False,
            originalFailedFlightActionId='', savedLandingAccountingAnchorGameTick=None,
            nativeOriginalOutcomeProved=False, discardedUnstoredProgressGameTicks=0,
            surfaceRecoveryExpectedSourceGameTick=1200, candidateGameTick=1200, minimumGameTick=1200,
            expectedPlanetId=201, additionalVoyagerGameTicks=300,
            originalJourneyMaximumGameTicks=10000, effectiveJourneyMaximumGameTicks=10300,
            surfaceRecoveryMaximumWorkGameTicks=600, surfaceRecoveryMaximumWallSeconds=20,
            surfaceRecoveryTarget=dict(x=200., y=1., z=2.))
        self.reference = dict(actionId='old-move', sessionSha256='SESSION-HASH')
        self.receipt = dict(actionId='old-move', actionKind='move', terminal=True, state='outcome_unknown',
            succeeded=False, reconciledFromOutcomeUnknown=False, sessionId='session', planetId=201,
            completedAtGameTick=1198, itemDeltas=[dict(itemId=1, delta=-1)])
        self.session = dict(gameLoaded=True, ownedBySpherewright=True, writesAllowed=False, writeHealth='quarantined',
            writeQuarantineActionId='old-move', sessionId='session', localPlanetId=201, gameTick=1200)
        self.preservation = dict(passed=True, exactLiveTickMatched=True, fullFileHashVerified=True,
            savedGameTick=1200, sessionCutSha256='SESSION-HASH', primarySha256='PRIMARY-HASH')
        self.primary = dict(gameTick=1200, sha256='PRIMARY-HASH')

    def adapter(self, plan=None):
        a = Live(None)
        a.runtime = SimpleNamespace(config=self.config, put=lambda *_: None)
        a.calls = []
        def call(name, args):
            a.calls.append((name, args))
            return copy.deepcopy(self.plan if plan is None else plan)
        a.call = call
        return a

    def test_new_surface_prepare_forwards_live_saved_tick_without_borrowing_ticket_tick(self):
        a = self.adapter()
        p = a.prepare_resume(dict(session=dict(restartResumeAvailable=True, restartResumeToken='token')),
                             time.monotonic() + 5)
        self.assertEqual(self.plan, p)
        tool, request = a.calls[0]
        self.assertEqual('spherewright_prepare_resume_owned_game', tool)
        self.assertEqual(1200, request['surfaceRecoveryExpectedSourceGameTick'])
        self.assertNotIn('minimumRecoveryGameTick', request)
        self.assertNotIn('expectedRecoveryGameTick', request)
        self.assertEqual((200., 1., 2.), tuple(request['surfaceRecoveryTarget' + k.upper()] for k in 'xyz'))
        self.assertFalse(any('_commit_' in name for name, _ in a.calls))

    def test_wrong_source_disclosure_never_returns_a_committable_plan(self):
        changes = [('successfulOutboundSurfaceSourceUsed', False), ('completedSavedLandingAdmissionUsed', True),
            ('failedLandingRecoveryAuthorizationUsed', True), ('nativeOriginalOutcomeProved', True),
            ('recoveryMode', 'other'), ('exactEmbeddedIdentityVerified', False), ('confirmationDigest', ''),
            ('sourceGameVersion', 'other'),
            ('discardedUnstoredProgressGameTicks', 1), ('candidateGameTick', 1199),
            ('minimumGameTick', 1199), ('surfaceRecoveryExpectedSourceGameTick', 1199),
            ('surfaceRecoveryTarget', dict(x=201., y=1., z=2.))]
        for key, value in changes:
            with self.subTest(key=key):
                bad = copy.deepcopy(self.plan); bad[key] = value
                a = self.adapter(bad)
                with self.assertRaises(RuntimeError):
                    a.prepare_resume(dict(session=dict(restartResumeAvailable=True, restartResumeToken='token')),
                                     time.monotonic() + 5)
                self.assertFalse(any('_commit_' in name for name, _ in a.calls))

    def test_old_move_remains_unknown_and_its_actual_saved_primary_is_bound(self):
        self.assertTrue(quarantined_local_move_saved_source(self.config, self.reference, self.receipt,
            self.session, self.preservation, self.primary))
        # Movement can consume real items or energy; that is not evidence of
        # a successful arrival and is not grounds to invent a no-effect result.
        self.assertEqual(-1, self.receipt['itemDeltas'][0]['delta'])
        for obj, key, value in [(self.receipt, 'state', 'completed'), (self.receipt, 'sessionId', 'other'),
            (self.session, 'writeQuarantineActionId', 'other'), (self.session, 'writeHealth', 'healthy'), (self.session, 'gameTick', 1199),
            (self.preservation, 'sessionCutSha256', 'other'), (self.preservation, 'primarySha256', 'other'),
            (self.preservation, 'savedGameTick', 1199), (self.primary, 'sha256', 'other')]:
            with self.subTest(key=key):
                original = obj[key]; obj[key] = value
                self.assertFalse(quarantined_local_move_saved_source(self.config, self.reference, self.receipt,
                    self.session, self.preservation, self.primary))
                obj[key] = original

    def test_surface_role_cannot_be_accidentally_used_by_an_ordinary_recovery(self):
        self.assertTrue(resume_admission_echo(self.config, self.plan))
        self.assertFalse(resume_admission_echo(dict(self.config, recoveryProfile='other'), self.plan))
        self.assertFalse(resume_admission_echo(dict(self.config, sourceRole='lastExit'), self.plan))

    def test_missing_or_invalid_target_refuses_before_calling_mcp(self):
        for value in (None, dict(x=1., y=2.), dict(x=1., y=2., z=float('nan'))):
            with self.subTest(value=value):
                c = dict(self.config, surfaceRecoveryTarget=value)
                a = self.adapter(); a.runtime.config = c
                with self.assertRaisesRegex(RuntimeError, 'successful_surface_source_shape_invalid'):
                    a.prepare_resume(dict(session=dict(restartResumeAvailable=True, restartResumeToken='token')),
                                     time.monotonic() + 5)
                self.assertEqual([], a.calls)

    def test_offline_preflight_isolates_unknown_action_without_claiming_reconciliation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def evidence(name, value):
                path = root / name
                path.write_text(json.dumps(value), encoding='utf-8')
                return path
            receipt = evidence('receipt.json', self.receipt)
            session = evidence('session.json', self.session)
            preservation_data = dict(self.preservation, sessionCutSha256=sha(session))
            preservation = evidence('preservation.json', preservation_data)
            qualified = evidence('qualified.json', dict(passed=True, sourceSha='source'))
            sdk = evidence('sdk.json', dict(passed=True))
            steam = evidence('steam.exe', {})
            original = dict(actionId='old-move', receiptPath=str(receipt), receiptSha256=sha(receipt),
                sessionPath=str(session), sessionSha256=sha(session), preservationPath=str(preservation),
                preservationSha256=sha(preservation))
            config = dict(self.config, sourceSha='source', qualifiedInputs=[], terminalOriginalActions=[],
                quarantinedLocalMoveOriginals=[original], firstOperationReady=True, originalActionsReconciled=False,
                priorRpcCount=0, maximumRpc=50, maximumWallSeconds=900, initialSteps=[],
                qualificationPath=str(qualified), sdkQualificationPath=str(sdk))
            evidence_out = {}
            runtime = SimpleNamespace(config=config, output=root, stopped=lambda:None, cohort=lambda:None,
                verify_revision_stamps=lambda:None, verify_backup=lambda:dict(rows=[{}], latest=dict(primary=self.primary)),
                mcp_executable=lambda:'synthetic', put=lambda name,value:evidence_out.update({name:value}))
            fields = ('resumeToken','recoveryMode','recoveryDeadlineUtc','recoveryScope','maximumChargeGameTicks',
                'maximumChargeWallSeconds','additionalVoyagerGameTicks','surfaceRecoveryExpectedSourceGameTick',
                'surfaceRecoveryTargetX','surfaceRecoveryTargetY','surfaceRecoveryTargetZ',
                'restoreRenamedLastExitIdentity','expectedRenamedLastExitContentHash')
            schema = dict(name='spherewright_prepare_resume_owned_game',
                inputSchema=dict(properties={key:{} for key in fields}, required=['resumeToken']))
            fake_client = SimpleNamespace(initialize=lambda:(None, [schema], None, None))
            with patch('driver.Client', return_value=fake_client), patch('driver.subprocess.check_output', return_value=str(steam)):
                proof = Live(runtime).offline_preflight()
            self.assertFalse(proof['original_actions_reconciled'])
            self.assertTrue(proof['original_unknowns_isolated'])
            self.assertEqual('outcome_unknown', json.loads(receipt.read_text())['state'])
            self.assertEqual(proof, evidence_out['offline-ready.private.json'])

            # An older installed SDK without this argument is rejected while
            # the game is still stopped, before any recovery can be submitted.
            old_schema = copy.deepcopy(schema)
            del old_schema['inputSchema']['properties']['surfaceRecoveryExpectedSourceGameTick']
            old_client = SimpleNamespace(initialize=lambda:(None, [old_schema], None, None))
            with patch('driver.Client', return_value=old_client):
                with self.assertRaisesRegex(ValueError, 'actual_sdk_argument_shape'):
                    Live(runtime).offline_preflight()

            # A changed saved primary stops before any client or launch.
            runtime.verify_backup = lambda:dict(rows=[{}], latest=dict(primary=dict(self.primary, sha256='changed')))
            with patch('driver.Client') as client:
                with self.assertRaisesRegex(RuntimeError, 'original_local_move_or_covering_saved_source_unproved'):
                    Live(runtime).offline_preflight()
                client.assert_not_called()

    def test_renamed_last_exit_is_selected_only_with_its_exact_hash_and_disclosure(self):
        content = 'A'*64
        config = dict(self.config, sourceRole='lastExit', restoreRenamedLastExitIdentity=True,
            expectedRenamedLastExitContentHash='sha256:'+content.lower())
        plan = dict(self.plan, renamedLastExitIdentityRestorationPlanned=True,
            expectedRenamedLastExitContentHash=config['expectedRenamedLastExitContentHash'])
        a = self.adapter(plan); a.runtime.config = config
        a.prepare_resume(dict(session=dict(restartResumeAvailable=True,restartResumeToken='token')),time.monotonic()+5)
        request = a.calls[0][1]
        self.assertTrue(request['restoreRenamedLastExitIdentity'])
        self.assertEqual(config['expectedRenamedLastExitContentHash'],request['expectedRenamedLastExitContentHash'])
        self.assertEqual(1200,request['surfaceRecoveryExpectedSourceGameTick'])
        self.assertNotIn('minimumRecoveryGameTick',request)
        self.assertTrue(resume_admission_echo(config,plan))
        self.assertFalse(resume_admission_echo(config,dict(plan,renamedLastExitIdentityRestorationPlanned=False)))
        self.assertFalse(resume_admission_echo(config,dict(plan,expectedRenamedLastExitContentHash='sha256:'+'b'*64)))
        preservation = dict(self.preservation, sourceSha256=content, sameNativeWorldCreation=True)
        source = dict(gameTick=1200,sha256=content)
        self.assertTrue(quarantined_local_move_saved_source(config,self.reference,self.receipt,self.session,preservation,source))
        self.assertFalse(quarantined_local_move_saved_source(config,self.reference,self.receipt,self.session,
            dict(preservation,sameNativeWorldCreation=False),source))
        self.assertFalse(quarantined_local_move_saved_source(config,self.reference,self.receipt,self.session,
            preservation,dict(source,sha256='B'*64)))

    def test_backup_reader_uses_the_renamed_identity_only_for_fixed_last_exit(self):
        content = 'A'*64
        runtime = Runtime.__new__(Runtime)
        runtime.config = dict(self.config,sourceRole='lastExit',restoreRenamedLastExitIdentity=True,
            expectedRenamedLastExitContentHash='sha256:'+content.lower(),renamedSavedIdentity='user-save',
            savePaths=dict(primary='managed-save.dsv'))
        runtime.native_paths = lambda:dict(primary=Path('managed-save.dsv'),lastExit=Path('LastExit.dsv'),
                                         currentCheckpoint=Path('checkpoint.dsv'))
        observed=[]
        def file_proof(path,identity):
            observed.append((path.name,identity));return dict(sha256=content,gameTick=1200)
        with patch('runtime.native_file_proof',side_effect=file_proof):
            result=runtime.native_proofs()
        self.assertEqual(content,result['lastExit']['sha256'])
        self.assertEqual([('managed-save.dsv','managed-save'),('LastExit.dsv','user-save'),
                          ('checkpoint.dsv','managed-save')],observed)
        runtime.config['expectedRenamedLastExitContentHash']='sha256:'+'b'*64
        with patch('runtime.native_file_proof',side_effect=file_proof):
            with self.assertRaisesRegex(RuntimeError,'renamed_saved_last_exit_hash_changed'):
                runtime.native_proofs()

    def test_offline_sdk_probe_includes_surface_boundary_within_its_request_budget(self):
        shapes = json.loads((Path(__file__).parent / 'fixtures/captured-sdk-surface-shapes.json').read_text())
        instances = []
        class FakeClient:
            def __init__(self, executable, directory, maximum, seconds):
                self.maximum = maximum; self.count = 0; self.calls = []; instances.append(self)
            def initialize(self):
                self.count = 4
                return None, [dict(name=name, inputSchema=schema) for name, schema in shapes.items()], None, None
            def call(self, name, args):
                self.count += 1
                if self.count > self.maximum: raise RuntimeError('sdk_probe_budget_exhausted')
                self.calls.append((name, args))
                if args.get('direction') == 'Production-Reset-To-Player':
                    return dict(error=dict(code='INVALID_REQUEST')), True
                return dict(error=dict(code='BRIDGE_NOT_READY')), True
            def close(self): return dict(requestCount=self.count, normalEof=True)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'probe'
            with patch.object(sdk_probe, 'Client', FakeClient), patch.object(sys, 'argv', ['sdk_probe', 'synthetic', str(output)]):
                sdk_probe.main()
            self.assertTrue(json.loads((output / 'result.private.json').read_text())['passed'])
        client = instances[0]
        self.assertLessEqual(client.count, client.maximum)
        surface = [args for name,args in client.calls if name == 'spherewright_prepare_resume_owned_game'
                   and 'surfaceRecoveryExpectedSourceGameTick' in args and not args.get('restoreRenamedLastExitIdentity')]
        self.assertEqual(1, len(surface)); self.assertEqual(100, surface[0]['surfaceRecoveryExpectedSourceGameTick'])
        self.assertNotIn('minimumRecoveryGameTick', surface[0]); self.assertNotIn('expectedRecoveryGameTick', surface[0])
        renamed = [args for name,args in client.calls if name == 'spherewright_prepare_resume_owned_game'
                   and args.get('restoreRenamedLastExitIdentity') is True]
        self.assertEqual(1, len(renamed)); self.assertEqual('sha256:'+'a'*64, renamed[0]['expectedRenamedLastExitContentHash'])

    def test_completed_embedded_move_counts_only_with_real_order_and_grounded_arrival(self):
        config = dict(self.config, firstOperation=dict(kind='surface-recovery-move'))
        # Native projects the requested target to the source radius.
        factor = 200. / math.sqrt(200.**2 + 1.**2 + 2.**2)
        target = {k:self.config['surfaceRecoveryTarget'][k]*factor for k in 'xyz'}
        zero = dict(x=0., y=0., z=0.)
        move = dict(resumeActionId='new-resume', state='completed_idle', nativeOperation='OrderNode.MoveTo/Player.Order',
            sourceGameTick=1200, capturedAtGameTick=1205, nativeOrderAccepted=True, strictPhysicalIdleProved=True,
            failure=None, newGameTicksGranted=False, originalUnknownOutcomeChanged=False,
            sourcePosition=dict(x=200., y=0., z=0.), targetPosition=target, currentPosition=target)
        player = dict(sessionId='new-session', planetId=201, capturedAtGameTick=1207, position=target,
            movementState='Walk', speed=0., nativePhysics=dict(groundContact=dict(checkSphereHit=True),
                currentOrderPresent=False, queuedOrderCount=0, velocity=zero, walkRtsVelocity=zero,
                driftRtsVelocity=zero, walkManualVelocity=zero, driftManualVelocity=zero, resumeSurfaceRecoveryMove=move))
        result = dict(actionId='new-resume', actionKind='resume-owned-game', state='completed',
            terminal=True, succeeded=True, sessionId='new-session', planetId=201)
        session = dict(gameLoaded=True, ownedBySpherewright=True, writesAllowed=True, sessionId='new-session', localPlanetId=201)
        # This fixture uses a target just over two metres from the source.
        self.assertTrue(completed_saved_surface_move(config,result,session,player))
        # The owned action may stop on actual grounded land before its target.
        early=copy.deepcopy(player);early['position']=dict(x=199.99,y=10.,z=0.)
        early['nativePhysics']['resumeSurfaceRecoveryMove']['currentPosition']=dict(early['position'])
        self.assertTrue(completed_saved_surface_move(config,result,session,early))
        for key,value in [('resumeActionId','old-move'),('state','armed'),('nativeOrderAccepted',False),
            ('strictPhysicalIdleProved',False),('failure','failed'),('originalUnknownOutcomeChanged',True),
            ('sourceGameTick',1199),('currentPosition',dict(x=150.,y=0.,z=0.)),
            ('currentPosition',dict(x=200.,y=0.,z=0.))]:
            with self.subTest(key=key):
                bad = copy.deepcopy(player); bad['nativePhysics']['resumeSurfaceRecoveryMove'][key] = value
                self.assertFalse(completed_saved_surface_move(config,result,session,bad))
        bad = copy.deepcopy(player); bad['nativePhysics']['groundContact']['checkSphereHit'] = False
        self.assertFalse(completed_saved_surface_move(config,result,session,bad))
        self.assertFalse(completed_saved_surface_move(config,dict(result,succeeded=False),session,player))
        self.assertFalse(completed_saved_surface_move(config,result,dict(session,writesAllowed=False),player))

        a = self.adapter(); a.runtime.config = config; stored = {}
        a.runtime.put = lambda name,value:stored.update({name:value}); a.player = lambda:player
        self.assertTrue(a.verify_recovery_as_first_work(self.plan,result,session,time.monotonic()+5))
        self.assertTrue(stored['actual-progress.private.json']['verified'])
        self.assertFalse(stored['actual-progress.private.json']['oldUnknownReconciled'])
        self.assertEqual([],a.calls)

        bad = copy.deepcopy(player); bad['nativePhysics']['resumeSurfaceRecoveryMove']['resumeActionId']='other'
        a.player = lambda:bad
        with self.assertRaisesRegex(RuntimeError,'completed_saved_surface_move_unproved_no_replay'):
            a.verify_recovery_as_first_work(self.plan,result,session,time.monotonic()+5)
        self.assertEqual([],a.calls)
        bad['movementState']='Drift'; bad['nativePhysics']['resumeSurfaceRecoveryMove']['state']='failed'
        with patch('driver.time.sleep') as sleep:
            with self.assertRaisesRegex(RuntimeError,'completed_saved_surface_move_unproved_no_replay'):
                a.verify_recovery_as_first_work(self.plan,result,session,time.monotonic()+5)
            sleep.assert_not_called()


if __name__ == '__main__':
    unittest.main()
