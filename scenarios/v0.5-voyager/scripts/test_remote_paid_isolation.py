"""A completed paid remote object stays distinct from its unknown drone tail."""
from pathlib import Path
import copy,datetime as dt,sys,unittest
sys.path.insert(0,str(Path(__file__).parent/'live'))
sys.path.insert(0,str(Path(__file__).parent))
from contracts import remote_paid_saved_after_isolated_remote,remote_failed_resume_saved_after_paid,remote_healthy_saved_after_isolation,remote_live_exit_after_isolation,completed_home_window_admitted,owned_saved_recovery_context
from driver import ordinary_remote_prepare_arguments


def fixture():
    old=dict(recoveryProfile='ordinary-owned-remote',recoveryMode='authorize_remote_primary_recovery',sourceRole='primary',
        originalActionsReconciled=False,sourceTick=100,spentGameTicks=1000,planetId=402,
        returnReserveGameTicks=54000,cleanupReserveGameTicks=3000,expectedNativeVersion='native',nativeAssemblySha256='native-hash',
        originalUnknownActionsNeverReplayed=['older'])
    current=dict(old,sourceTick=130,spentGameTicks=1030,originalUnknownActionsNeverReplayed=['older','paid'])
    loaded=dict(sessionId='session',localPlanetId=402,gameTick=101,gameLoaded=True,ownedBySpherewright=True,writesAllowed=True)
    item=dict(index=0,state='pending_construction',prebuildId=4,inventoryBefore=1,inventoryAfter=0,
        beforeInventoryHash='before',afterInventoryHash='after')
    original=dict(actionId='paid',actionKind='build',sessionId='session',planetId=402,completedAtGameTick=129,
        terminal=True,succeeded=False,state='outcome_unknown',reconciledFromOutcomeUnknown=False,
        blueprintBuildId='build',blueprintObjects=[item],itemDeltas=[dict(itemId=2103,delta=-1,beforeCount=1,afterCount=0)],
        constructionControl=dict(executionKind='structured_native',dispatchDisabled=True,physicalIdleVerified=False,
            wholeBatchDebitSharedByObjectReceipts=True))
    done=dict(item,state='completed',entityId=9)
    build=dict(buildId='build',sessionId='session',planetId=402,capturedAtGameTick=130,phase='outcome_unknown',actionId='paid',
        persistenceHealthy=True,freshWorldReconciled=True,doNotReplayWholeBlueprint=True,
        submittedCount=1,completedCount=1,objects=[done],site=dict(objects=[dict(itemId=2103,position=dict(x=1.,y=2.,z=3.))]))
    observed=dict(builds=[build]);session=dict(sessionId='session',localPlanetId=402,gameTick=130,gameLoaded=True,
        ownedBySpherewright=True,writesAllowed=False,writeQuarantineActionId='paid')
    player=dict(sessionId='session',planetId=402,capturedAtGameTick=130,constructionDrones=dict(enabled=False,
        activeObservationsComplete=True,working=1,idle=2,total=3,activeObservations=[dict(stage=4,targetObjectId=0,nextTargetObjectIds=[0,0,0])]))
    station=dict(sessionId='session',planetId=402,capturedAtGameTick=130,objectId=9,itemId=2103,position=dict(x=1.,y=2.,z=3.),
        logisticsStation=dict(isInterstellar=False,isCollector=False,galacticStationId=0))
    receipt=dict(actionId='save',actionKind='save',sessionId='session',planetId=402,completedAtGameTick=130,terminal=True,succeeded=True)
    saved=dict(passed=True,originalActionId='paid',noLoad=True,noReplay=True,noResume=True,savedGameTick=130,originalSave=receipt)
    closed=dict(passed=True,paidOriginalRetained=True,noReplay=True,primaryTick=130,lastExitTick=130)
    backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=130),lastExit=dict(gameTick=130)))
    return [current,old,loaded,original,observed,session,player,station,saved,closed,backup]


def failed_resume_fixture():
    previous,_,_,_,observed,session,player,station,_,_,_=fixture()
    current=dict(previous,sourceRole='lastExit',sourceTick=140,spentGameTicks=1040)
    failed=dict(actionId='resume-failed',actionKind='resume-owned-game',sessionId='session',planetId=402,
        terminal=True,succeeded=False,state='action_failed',nativeFirstFailure=dict(capturedAtGameTick=140))
    session=dict(session,gameTick=140,writeQuarantineActionId='resume-failed')
    player=dict(player,capturedAtGameTick=140);station=dict(station,capturedAtGameTick=140)
    cut=dict(session=session,player=player,station=station,build=observed,noReplay=True)
    closed=dict(passed=True,noReplay=True,actualDiscardedTicks=0,pausedCutTick=140,lastExitTick=140,latestTick=140,primaryTick=130)
    backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=130),lastExit=dict(gameTick=140)))
    return [current,previous,failed,cut,closed,backup]


def failed_resume_with_paused_save_fixture():
    previous,_,_,oldcut,_,_=failed_resume_fixture()
    current=dict(previous,sourceRole='primary',sourceTick=150,spentGameTicks=1050)
    failed=dict(actionId='resume-failed-again',actionKind='resume-owned-game',sessionId='session',planetId=402,
        terminal=True,succeeded=False,state='action_failed',nativeFirstFailure=dict(capturedAtGameTick=150))
    cut=copy.deepcopy(oldcut);cut['session'].update(gameTick=150,writeQuarantineActionId='resume-failed-again')
    cut['player']['capturedAtGameTick']=150;cut['station']['capturedAtGameTick']=150
    receipt=dict(actionId='save2',actionKind='save',sessionId='session',planetId=402,completedAtGameTick=150,terminal=True,succeeded=True)
    saved=dict(passed=True,originalResumeActionId='resume-failed-again',noLoad=True,noReplay=True,noResume=True,savedGameTick=150,originalSave=receipt)
    closed=dict(passed=True,noReplay=True,savedTick=150,primaryTick=150,lastExitTick=150,latestTick=150)
    backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=150),lastExit=dict(gameTick=150)))
    return [current,previous,failed,cut,closed,backup,saved]


def healthy_saved_fixture():
    previous=failed_resume_with_paused_save_fixture()[0]
    current=dict(previous,sourceRole='primary',sourceTick=200,spentGameTicks=1100,
        originalUnknownActionsNeverReplayed=list(previous['originalUnknownActionsNeverReplayed']))
    loaded=dict(sessionId='healthy-session',localPlanetId=402,gameTick=151,gameLoaded=True,ownedBySpherewright=True,writesAllowed=True)
    resumed=dict(actionId='successful-resume',actionKind='resume-owned-game',sessionId='healthy-session',planetId=402,
        terminal=True,succeeded=True,state='completed')
    menu=dict(actionId='new-menu-save',actionKind='return-to-main-menu',sessionId='healthy-session',planetId=402,
        terminal=True,succeeded=True,state='completed',completedAtGameTick=200,
        mainMenuReturnReadback=dict(savedGameTick=200,normalSaveConfirmed=True,completeSaveVerified=True,nativeEndRequested=True,mainMenuVerified=True))
    backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=200),lastExit=dict(gameTick=200)))
    return [current,previous,loaded,resumed,menu,backup]


def live_exit_fixture():
    previous=healthy_saved_fixture()[0]
    previous.update(priorRpcCount=100,sourceTick=200,spentGameTicks=1100)
    current=dict(previous,sourceRole='lastExit',sourceTick=250,spentGameTicks=1150,priorRpcCount=110,
        originalUnknownActionsNeverReplayed=list(previous['originalUnknownActionsNeverReplayed']))
    loaded=dict(sessionId='live-session',localPlanetId=402,gameTick=201,gameLoaded=True,ownedBySpherewright=True,writesAllowed=True)
    resumed=dict(actionId='resume',actionKind='resume-owned-game',sessionId='live-session',planetId=402,
        terminal=True,succeeded=True,state='completed')
    move=dict(actionId='move',actionKind='move',sessionId='live-session',planetId=402,completedAtGameTick=220,
        terminal=True,succeeded=True,state='completed')
    last=dict(sessionId='live-session',localPlanetId=402,gameTick=250,gameLoaded=True,ownedBySpherewright=True,
        writesAllowed=False,writeHealth='quarantined',writeQuarantineActionId='resume',
        writeBlockers=[dict(code='WRITE_SUBSYSTEM_QUARANTINED')])
    closed=dict(normalEof=True,processExitCode=0,readerThreadsStopped=True,phaseClosed=True,priorRpcCount=100,requestCount=10)
    backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=202),lastExit=dict(gameTick=250)))
    return [current,previous,loaded,resumed,last,closed,[resumed,move],backup]


class RemotePaidIsolationTests(unittest.TestCase):
    def test_completed_saved_home_return_can_start_a_fresh_finite_work_window(self):
        config=dict(completedHomeWindowSeconds=7200,attachmentPlanetId=104,authorizedPlanetIds=[104,402])
        loaded=dict(sessionId='session')
        arrival=dict(terminal=True,succeeded=True,sessionId='session',completedAtGameTick=200,
            voyagerFlightReadback=dict(actualPlanetId=104,nativeExitObserved=True))
        saved=dict(actionId='save',actionKind='save',terminal=True,succeeded=True,sessionId='session',
            planetId=104,completedAtGameTick=201)
        journey=dict(phase='completed',homePlanetId=104,completedSaveGameTick=201,
            completedSaveActionId='save',completedSaveSessionId='session')
        handoff=dict(callerStopped=True,noActiveGameAction=True,gameProcessRetained=True)
        args=[config,loaded,arrival,saved,journey,handoff]
        self.assertTrue(completed_home_window_admitted(*args))
        changes=[lambda a:a[0].update(completedHomeWindowSeconds=0),
                 lambda a:a[2]['voyagerFlightReadback'].update(actualPlanetId=402),
                 lambda a:a[3].update(succeeded=False),
                 lambda a:a[4].update(completedSaveGameTick=200),
                 lambda a:a[5].update(noActiveGameAction=False)]
        for change in changes:
            altered=copy.deepcopy(args);change(altered)
            self.assertFalse(completed_home_window_admitted(*altered))

    def test_successful_live_resume_and_exact_newer_exit_preserve_prior_progress(self):
        self.assertTrue(remote_live_exit_after_isolation(*live_exit_fixture()))
        changes=[
            lambda a:a[0].update(sourceRole='primary'),
            lambda a:a[0].update(spentGameTicks=1149),
            lambda a:a[0].update(priorRpcCount=109),
            lambda a:a[0]['originalUnknownActionsNeverReplayed'].remove('paid'),
            lambda a:a[2].update(sessionId='other'),
            lambda a:a[3].update(succeeded=False),
            lambda a:a[4].update(writeQuarantineActionId='other'),
            lambda a:a[4].update(gameTick=249),
            lambda a:a[5].update(normalEof=False),
            lambda a:a[6][1].update(succeeded=False),
            lambda a:a[7]['latest']['lastExit'].update(gameTick=249),
        ]
        for change in changes:
            args=copy.deepcopy(live_exit_fixture());change(args)
            self.assertFalse(remote_live_exit_after_isolation(*args))

    def test_exact_live_exit_can_prepare_a_new_remote_window(self):
        c=live_exit_fixture()[0]
        c.update(surfaceRecoveryTarget=None,recoveryWindowSeconds=7200,additionalVoyagerGameTicks=800000,
            remoteLiveExitIsolation={'frozen':'evidence'})
        args=ordinary_remote_prepare_arguments(c,'synthetic',dt.datetime.now(dt.timezone.utc))
        self.assertEqual(250,args['minimumRecoveryGameTick'])
        self.assertEqual(250,args['expectedRecoveryGameTick'])

    def test_healthy_remote_save_keeps_prior_unknowns_and_actual_spending(self):
        self.assertTrue(remote_healthy_saved_after_isolation(*healthy_saved_fixture()))
        changes=[lambda a:a[0].update(spentGameTicks=1099),lambda a:a[0]['originalUnknownActionsNeverReplayed'].remove('paid'),
                 lambda a:a[2].update(writesAllowed=False),lambda a:a[3].update(succeeded=False),
                 lambda a:a[4]['mainMenuReturnReadback'].update(completeSaveVerified=False),
                 lambda a:a[5]['latest']['lastExit'].update(gameTick=199)]
        for change in changes:
            args=copy.deepcopy(healthy_saved_fixture());change(args)
            self.assertFalse(remote_healthy_saved_after_isolation(*args))

    def test_later_failed_resume_can_carry_an_exact_paused_primary_save(self):
        self.assertTrue(remote_failed_resume_saved_after_paid(*failed_resume_with_paused_save_fixture()))
        c=failed_resume_with_paused_save_fixture()[0];c['remoteFailedResumeSavedIsolation']={'frozen':'evidence'}
        self.assertTrue(owned_saved_recovery_context(c))
        c['originalActionsReconciled']=True;self.assertFalse(owned_saved_recovery_context(c))
        for mutate in (lambda a:a[6].update(originalResumeActionId='different'),
                       lambda a:a[6]['originalSave'].update(succeeded=False),
                       lambda a:a[4].update(savedTick=149),
                       lambda a:a[5]['latest']['primary'].update(gameTick=149)):
            args=copy.deepcopy(failed_resume_with_paused_save_fixture());mutate(args)
            self.assertFalse(remote_failed_resume_saved_after_paid(*args))

    def test_newer_exit_preparation_requires_its_distinct_isolation_chain(self):
        c=failed_resume_fixture()[0]
        c.update(surfaceRecoveryTarget=None,recoveryWindowSeconds=7200,additionalVoyagerGameTicks=800000,
            remoteFailedResumeSavedIsolation={'frozen':'evidence'})
        args=ordinary_remote_prepare_arguments(c,'synthetic',dt.datetime.now(dt.timezone.utc))
        self.assertEqual(140,args['minimumRecoveryGameTick']);self.assertEqual(140,args['expectedRecoveryGameTick'])
        c.pop('remoteFailedResumeSavedIsolation')
        with self.assertRaisesRegex(RuntimeError,'ordinary_remote_source_shape_invalid'):
            ordinary_remote_prepare_arguments(c,'synthetic',dt.datetime.now(dt.timezone.utc))

    def test_later_failed_recovery_can_carry_the_newer_exact_normal_exit(self):
        self.assertTrue(remote_failed_resume_saved_after_paid(*failed_resume_fixture()))

    def test_newer_exit_never_implies_an_unknown_or_rolled_back_resume_succeeded(self):
        changes=[
            lambda a:a[0].update(sourceRole='primary'),
            lambda a:a[0].update(spentGameTicks=1039),
            lambda a:a[2].update(state='outcome_unknown'),
            lambda a:a[2].update(succeeded=True),
            lambda a:a[3]['session'].update(writeQuarantineActionId='different'),
            lambda a:a[3]['station'].update(itemId=2104),
            lambda a:a[3]['build']['builds'][0]['objects'][0].update(entityId=10),
            lambda a:a[4].update(actualDiscardedTicks=1),
            lambda a:a[5]['latest']['lastExit'].update(gameTick=139),
        ]
        for change in changes:
            with self.subTest(change=change):
                args=copy.deepcopy(failed_resume_fixture());change(args)
                self.assertFalse(remote_failed_resume_saved_after_paid(*args))

    def test_completed_paid_entity_and_distinct_returning_drone_remain_unknown(self):
        self.assertTrue(remote_paid_saved_after_isolated_remote(*fixture()))

    def test_changed_action_debit_site_tail_save_or_budget_is_not_isolated(self):
        changes=[
            lambda a:a[0]['originalUnknownActionsNeverReplayed'].remove('paid'),
            lambda a:a[0].update(spentGameTicks=1029),
            lambda a:a[0].update(returnReserveGameTicks=1),
            lambda a:a[2].update(sessionId='different'),
            lambda a:a[3]['itemDeltas'][0].update(delta=0),
            lambda a:a[3]['constructionControl'].update(physicalIdleVerified=True),
            lambda a:a[4]['builds'][0]['objects'][0].update(state='pending_construction'),
            lambda a:a[4]['builds'][0]['objects'][0].update(afterInventoryHash='changed'),
            lambda a:a[5].update(writeQuarantineActionId='different'),
            lambda a:a[6]['constructionDrones']['activeObservations'][0].update(stage=3),
            lambda a:a[7].update(position=dict(x=2.,y=2.,z=3.)),
            lambda a:a[7]['logisticsStation'].update(isInterstellar=True),
            lambda a:a[8].update(noReplay=False),
            lambda a:a[8]['originalSave'].update(succeeded=False),
            lambda a:a[9].update(primaryTick=129),
            lambda a:a[10].update(verified=False),
        ]
        for change in changes:
            with self.subTest(change=change):
                args=copy.deepcopy(fixture());change(args)
                self.assertFalse(remote_paid_saved_after_isolated_remote(*args))


if __name__=='__main__':unittest.main()
