"""Unknown originals stay isolated across a separately saved home return."""
from pathlib import Path
import copy,math,sys,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent/'live'))
from contracts import isolated_surface_unknown_after_saved_home,isolated_saved_menu_unknown,remote_saved_after_isolated_home,remote_paused_saved_after_isolated_home,remote_roundtrip_paused_after_isolation,owned_saved_recovery_context
from driver import Live


class SavedHomeIsolationTests(unittest.TestCase):
    def setUp(self):
        self.old=dict(recoveryProfile='successful-outbound-surface',recoveryMode='authorize_remote_primary_recovery',
            sourceRole='primary',sourceTick=1200,planetId=201,firstOperation=dict(kind='surface-recovery-move'),
            surfaceRecoveryTarget=dict(x=200.,y=1.,z=2.))
        self.config=dict(recoveryProfile='ordinary-owned-home',recoveryMode='default',sourceRole='primary',
            sourceTick=1300,planetId=104,closedJourneyHome=dict(phase='completed',homePlanetId=104,completedSaveGameTick=1260),
            originalUnknownActionsNeverReplayed=['old-move','old-menu'])
        self.original=dict(actionId='old-move',sessionSha256='SESSION-HASH')
        self.receipt=dict(actionId='old-move',actionKind='move',terminal=True,state='outcome_unknown',succeeded=False,
            reconciledFromOutcomeUnknown=False,sessionId='old-session',planetId=201,completedAtGameTick=1198)
        self.session=dict(gameLoaded=True,ownedBySpherewright=True,writesAllowed=False,writeHealth='quarantined',
            writeQuarantineActionId='old-move',sessionId='old-session',localPlanetId=201,gameTick=1200)
        self.preservation=dict(passed=True,exactLiveTickMatched=True,fullFileHashVerified=True,savedGameTick=1200,
            sessionCutSha256='SESSION-HASH',primarySha256='OLD-SOURCE')
        self.old_source=dict(gameTick=1200,sha256='OLD-SOURCE')
        factor=200./math.sqrt(200.**2+1.**2+2.**2);target={k:self.old['surfaceRecoveryTarget'][k]*factor for k in 'xyz'}
        zero=dict(x=0.,y=0.,z=0.)
        move=dict(resumeActionId='new-resume',state='completed_idle',nativeOperation='OrderNode.MoveTo/Player.Order',
            sourceGameTick=1200,capturedAtGameTick=1205,nativeOrderAccepted=True,strictPhysicalIdleProved=True,
            failure=None,newGameTicksGranted=False,originalUnknownOutcomeChanged=False,
            sourcePosition=dict(x=200.,y=0.,z=0.),targetPosition=target,currentPosition=target)
        player=dict(sessionId='new-session',planetId=201,capturedAtGameTick=1207,position=target,movementState='Walk',speed=0.,
            nativePhysics=dict(groundContact=dict(checkSphereHit=True),currentOrderPresent=False,queuedOrderCount=0,
                velocity=zero,walkRtsVelocity=zero,driftRtsVelocity=zero,walkManualVelocity=zero,driftManualVelocity=zero,
                resumeSurfaceRecoveryMove=move))
        resumed=dict(actionId='new-resume',actionKind='resume-owned-game',state='completed',terminal=True,succeeded=True,
            sessionId='new-session',planetId=201)
        self.progress=dict(verified=True,oldUnknownReconciled=False,noReplay=True,originalResumeReceipt=resumed,player=player)
        self.loaded=dict(gameLoaded=True,ownedBySpherewright=True,writesAllowed=True,sessionId='new-session',localPlanetId=201)
        self.flight=dict(actionKind='interplanetary-flight',terminal=True,state='completed',succeeded=True,sessionId='new-session',
            completedAtGameTick=1250,voyagerFlightReadback=dict(isReturnLeg=True,bindingVerified=True,nativeExitObserved=True,
                actualPlanetId=104,selectedDestinationPlanetId=104))
        self.home_save=dict(actionKind='save',terminal=True,state='completed',succeeded=True,sessionId='new-session',
            planetId=104,completedAtGameTick=1260)
        self.backup=dict(latest=dict(primary=dict(gameTick=1300),lastExit=dict(gameTick=1300)))
        self.menu=dict(actionId='old-menu',actionKind='return-to-main-menu',terminal=True,state='outcome_unknown',succeeded=False,
            reconciledFromOutcomeUnknown=False,mainMenuReturnReadback=dict(normalSaveConfirmed=True,completeSaveVerified=True,
                nativeEndRequested=True,savedGameTick=1295))
        self.observed=dict(toolError=False,response=dict(success=True,result=dict(actionId='old-menu',terminal=True,
            state='outcome_unknown',reconciledFromOutcomeUnknown=False)))
        self.observation=dict(gameLoaded=False,originalActionReplayed=False,processId=123)
        self.intent=dict(processId=123,forceKill=False,maximumRequests=1);self.closed=dict(passed=True,gameStopped=True)

    def surface(self):
        return isolated_surface_unknown_after_saved_home(self.config,self.old,self.original,self.receipt,self.session,
            self.preservation,self.old_source,self.progress,self.loaded,self.flight,self.home_save,self.backup)

    def menu_check(self):
        return isolated_saved_menu_unknown(self.config,self.menu,self.observed,self.observation,self.intent,self.closed,self.backup)

    def test_separate_recovery_and_saved_return_isolate_but_do_not_resolve_the_old_move(self):
        self.assertTrue(self.surface());self.assertEqual('outcome_unknown',self.receipt['state'])
        for obj,key,value in [(self.receipt,'state','completed'),(self.progress,'oldUnknownReconciled',True),
            (self.flight['voyagerFlightReadback'],'actualPlanetId',105),(self.home_save,'completedAtGameTick',1301),
            (self.backup['latest']['primary'],'gameTick',1299)]:
            with self.subTest(key=key):
                old=obj[key];obj[key]=value;self.assertFalse(self.surface());obj[key]=old

    def test_saved_unloaded_menu_keeps_the_original_unknown(self):
        self.assertTrue(self.menu_check());self.assertEqual('outcome_unknown',self.menu['state'])
        for obj,key,value in [(self.menu['mainMenuReturnReadback'],'completeSaveVerified',False),
            (self.observed['response']['result'],'actionId','different'),(self.observation,'gameLoaded',True),
            (self.observation,'originalActionReplayed',True),(self.intent,'processId',124),
            (self.backup['latest']['primary'],'gameTick',1294)]:
            with self.subTest(key=key):
                old=obj[key];obj[key]=value;self.assertFalse(self.menu_check());obj[key]=old

    def test_newer_last_exit_covers_the_same_saved_home_without_claiming_old_success(self):
        self.config.update(sourceRole='lastExit',recoveryMode='verified_newer_lastexit',sourceTick=1400)
        self.backup['latest']['lastExit']['gameTick']=1400
        self.assertTrue(self.surface());self.assertTrue(self.menu_check())
        self.backup['latest']['lastExit']['gameTick']=1399
        self.assertFalse(self.surface());self.assertFalse(self.menu_check())

    def test_isolated_history_survives_a_distinct_successful_outbound_and_complete_remote_save(self):
        self.config.update(originalActionsReconciled=False,expectedNativeVersion='native',nativeAssemblySha256='assembly')
        remote=dict(recoveryProfile='ordinary-owned-remote',recoveryMode='authorize_remote_primary_recovery',
            sourceRole='primary',sourceTick=1600,planetId=201,originalActionsReconciled=False,
            originalUnknownActionsNeverReplayed=['old-move','old-menu'],expectedNativeVersion='native',nativeAssemblySha256='assembly')
        loaded=dict(gameLoaded=True,ownedBySpherewright=True,writesAllowed=True,sessionId='later-session',localPlanetId=104,gameTick=1310)
        outbound=dict(actionId='new-flight',actionKind='interplanetary-flight',terminal=True,state='completed',succeeded=True,
            sessionId='later-session',planetId=104,startedAtGameTick=1320,completedAtGameTick=1400,
            voyagerFlightReadback=dict(isReturnLeg=False,bindingVerified=True,nativeExitObserved=True,
                actualPlanetId=201,selectedDestinationPlanetId=201))
        menu=dict(actionId='new-menu',actionKind='return-to-main-menu',terminal=True,state='completed',succeeded=True,
            sessionId='later-session',planetId=201,completedAtGameTick=1600,
            mainMenuReturnReadback=dict(normalSaveConfirmed=True,completeSaveVerified=True,nativeEndRequested=True,
                mainMenuVerified=True,savedGameTick=1600))
        backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=1600),lastExit=dict(gameTick=1600)))
        check=lambda:remote_saved_after_isolated_home(remote,self.config,loaded,outbound,menu,backup)
        self.assertTrue(check())
        for obj,key,value in [(remote,'originalActionsReconciled',True),
            (remote,'originalUnknownActionsNeverReplayed',['old-move']),
            (remote,'expectedNativeVersion','different-native'),(loaded,'localPlanetId',201),
            (outbound,'actionId','old-move'),(outbound,'sessionId','different-session'),
            (outbound['voyagerFlightReadback'],'isReturnLeg',True),
            (outbound['voyagerFlightReadback'],'actualPlanetId',202),
            (menu,'actionId','old-menu'),(menu,'sessionId','different-session'),
            (menu['mainMenuReturnReadback'],'completeSaveVerified',False),
            (menu['mainMenuReturnReadback'],'savedGameTick',1599),
            (backup['latest']['primary'],'gameTick',1599),(backup,'verified',False)]:
            with self.subTest(key=key,value=value):
                old=obj[key];obj[key]=value;self.assertFalse(check());obj[key]=old
        remote['originalUnknownActionsNeverReplayed']=tuple(remote['originalUnknownActionsNeverReplayed'])
        self.assertTrue(check())  # Runtime freezes config lists before preflight.
        backup['latest']['lastExit']['gameTick']=1590
        self.assertTrue(check())  # A verified current primary covers the remote save.
        backup['latest']['lastExit']['gameTick']=1601
        self.assertFalse(check())  # Never prefer an older primary over a newer exit save.
        backup['latest']['lastExit']['gameTick']=1600
        self.assertFalse(owned_saved_recovery_context(remote))
        remote['remoteSavedUnknownIsolation']=dict(homeConfigPath='bound-evidence')
        self.assertTrue(owned_saved_recovery_context(remote))
        remote['originalActionsReconciled']=True
        self.assertFalse(owned_saved_recovery_context(remote))

    def test_completed_outbound_can_preserve_its_exact_paused_save_without_resolving_old_unknowns(self):
        self.config.update(originalActionsReconciled=False,expectedNativeVersion='native',nativeAssemblySha256='assembly',
            spentGameTicks=1000,returnReserveGameTicks=54000,cleanupReserveGameTicks=3000)
        remote=dict(recoveryProfile='ordinary-owned-remote',recoveryMode='authorize_remote_primary_recovery',
            sourceRole='primary',sourceTick=1600,planetId=201,originalActionsReconciled=False,
            originalUnknownActionsNeverReplayed=['old-move','old-menu'],expectedNativeVersion='native',
            nativeAssemblySha256='assembly',spentGameTicks=1300,returnReserveGameTicks=54000,cleanupReserveGameTicks=3000)
        loaded=dict(gameLoaded=True,ownedBySpherewright=True,writesAllowed=True,sessionId='later-session',localPlanetId=104,gameTick=1310)
        outbound=dict(actionId='new-flight',actionKind='interplanetary-flight',terminal=True,state='completed',succeeded=True,
            sessionId='later-session',planetId=104,startedAtGameTick=1320,completedAtGameTick=1400,
            voyagerFlightReadback=dict(isReturnLeg=False,bindingVerified=True,nativeExitObserved=True,
                actualPlanetId=201,selectedDestinationPlanetId=201))
        session=dict(gameLoaded=True,ownedBySpherewright=True,writesAllowed=False,writeHealth='quarantined',
            writeQuarantineActionId='new-flight',sessionId='later-session',localPlanetId=201,gameTick=1600,
            writeBlockers=[dict(code='WRITE_SUBSYSTEM_QUARANTINED')])
        player=dict(sessionId='later-session',planetId=201,nativeLocalControlEnergy=dict(blockers=['native_paused_not_execution_ready']))
        cut=dict(session=session,player=player,noResume=True)
        plan=dict(prepared=True,commitAllowedNow=True,preservesQuarantine=True,preservationGameTick=1600,commitBlockers=[])
        saved=dict(actionId='paused-save',actionKind='save',terminal=True,state='completed',succeeded=True,
            sessionId='later-session',planetId=201,completedAtGameTick=1600)
        closed=dict(passed=True,gameStopped=True)
        preserved=dict(passed=True,minimumCurrentTick=1600,originalQuarantineRetained=True,noResume=True)
        backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=1600),lastExit=dict(gameTick=1600)))
        check=lambda:remote_paused_saved_after_isolated_home(remote,self.config,loaded,outbound,cut,plan,saved,closed,preserved,backup)
        self.assertTrue(check())
        for obj,key,value in [(remote,'spentGameTicks',1299),(remote,'originalUnknownActionsNeverReplayed',['old-move']),
            (outbound,'succeeded',False),(outbound['voyagerFlightReadback'],'actualPlanetId',202),
            (session,'writeQuarantineActionId','different'),(cut,'noResume',False),
            (plan,'preservesQuarantine',False),(saved,'completedAtGameTick',1599),
            (closed,'gameStopped',False),(backup['latest']['lastExit'],'gameTick',1599)]:
            with self.subTest(key=key,value=value):
                old=obj[key];obj[key]=value;self.assertFalse(check());obj[key]=old

    def test_remote_roundtrip_keeps_original_unknowns_and_preserves_the_new_outbound(self):
        previous=dict(recoveryProfile='ordinary-owned-remote',recoveryMode='authorize_remote_primary_recovery',
            sourceRole='primary',sourceTick=1000,planetId=201,originalActionsReconciled=False,
            originalUnknownActionsNeverReplayed=['old-move','old-menu'],expectedNativeVersion='native',
            nativeAssemblySha256='assembly',spentGameTicks=200,returnReserveGameTicks=54000,cleanupReserveGameTicks=3000)
        current=dict(previous,sourceTick=1300,spentGameTicks=500,surfaceRecoveryTarget=None,
            remoteRoundtripPausedIsolation={'previousConfigPath':'bound'})
        loaded=dict(sessionId='same',gameLoaded=True,ownedBySpherewright=True,writesAllowed=True,localPlanetId=201,gameTick=1010)
        home=dict(actionId='home',actionKind='interplanetary-flight',terminal=True,state='completed',succeeded=True,
            sessionId='same',planetId=201,startedAtGameTick=1020,completedAtGameTick=1100,
            voyagerFlightReadback=dict(isReturnLeg=True,bindingVerified=True,nativeExitObserved=True,
                actualPlanetId=104,selectedDestinationPlanetId=104))
        home_save=dict(actionId='home-save',actionKind='save',terminal=True,state='completed',succeeded=True,
            sessionId='same',planetId=104,completedAtGameTick=1110)
        outbound=dict(actionId='outbound',actionKind='interplanetary-flight',terminal=True,state='completed',succeeded=True,
            sessionId='same',planetId=104,startedAtGameTick=1120,completedAtGameTick=1200,
            voyagerFlightReadback=dict(isReturnLeg=False,bindingVerified=True,nativeExitObserved=True,
                actualPlanetId=201,selectedDestinationPlanetId=201))
        session=dict(sessionId='same',gameLoaded=True,ownedBySpherewright=True,writesAllowed=False,
            writeHealth='quarantined',writeQuarantineActionId='outbound',localPlanetId=201,gameTick=1300,
            writeBlockers=[dict(code='WRITE_SUBSYSTEM_QUARANTINED')])
        player=dict(sessionId='same',planetId=201,nativeLocalControlEnergy=dict(blockers=['native_paused_not_execution_ready']))
        cut=dict(session=session,player=player,noResume=True)
        plan=dict(prepared=True,commitAllowedNow=True,preservesQuarantine=True,preservationGameTick=1300,commitBlockers=[])
        saved=dict(actionId='paused-save',actionKind='save',terminal=True,state='completed',succeeded=True,
            sessionId='same',planetId=201,completedAtGameTick=1300)
        closed=dict(passed=True,gameStopped=True)
        preserved=dict(passed=True,minimumCurrentTick=1300,originalQuarantineRetained=True,noResume=True)
        backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=1300),lastExit=dict(gameTick=1300)))
        check=lambda:remote_roundtrip_paused_after_isolation(current,previous,loaded,home,home_save,outbound,
            cut,plan,saved,closed,preserved,backup)
        self.assertTrue(check());self.assertTrue(owned_saved_recovery_context(current))
        for obj,key,value in [(current,'spentGameTicks',499),(current,'originalUnknownActionsNeverReplayed',['old-move']),
            (home,'succeeded',False),(home['voyagerFlightReadback'],'isReturnLeg',False),
            (home_save,'completedAtGameTick',1121),(outbound,'sessionId','other'),
            (session,'writeQuarantineActionId','home'),(saved,'completedAtGameTick',1299),
            (closed,'gameStopped',False),(backup['latest']['lastExit'],'gameTick',1299)]:
            with self.subTest(key=key,value=value):
                old=obj[key];obj[key]=value;self.assertFalse(check());obj[key]=old

    def test_home_preflight_reports_isolation_without_using_surface_resume_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);steam=root/'steam.exe';steam.write_text('synthetic',encoding='utf-8')
            keys=('surfaceConfig','surfaceProgress','loadedSession','homeFlight','homeSave','menuReceipt',
                'menuObservedAction','menuObservation','closeIntent','closeResult')
            refs={}
            for k in keys:refs[k+'Path']=str(root/(k+'.json'));refs[k+'Sha256']='HASH'
            original=dict(actionId='old-move')
            for k in ('receipt','session','preservation'):
                original[k+'Path']=str(root/(k+'.json'));original[k+'Sha256']='HASH'
            old=dict(quarantinedLocalMoveOriginals=[original],backupManifest=str(root/'old-backup.json'),
                backupManifestSha256='HASH',sourceRole='primary',savePaths=dict(primary=str(root/'primary.dsv')))
            old_backup=dict(complete=True,verified=True,latest=dict(primary=dict(gameTick=1200,sha256='HASH')),
                rows=[dict(originalPath=str(root/'primary.dsv'),backupPath=str(root/'copy.dsv'),sha256='HASH')])
            docs={refs[k+'Path']:{} for k in keys};docs[refs['surfaceConfigPath']]=old;docs[old['backupManifest']]=old_backup
            docs.update({original[k+'Path']:{} for k in ('receipt','session','preservation')})
            docs[str(root/'qualified.json')]=dict(passed=True,sourceSha='source');docs[str(root/'sdk.json')]=dict(passed=True)
            config=dict(self.config,sourceSha='source',qualifiedInputs=[],terminalOriginalActions=[],homeSavedUnknownIsolation=refs,
                firstOperationReady=True,originalActionsReconciled=False,priorRpcCount=0,maximumRpc=50,maximumWallSeconds=900,
                initialSteps=[],qualificationPath=str(root/'qualified.json'),sdkQualificationPath=str(root/'sdk.json'))
            stored={};runtime=SimpleNamespace(config=config,output=root,stopped=lambda:None,cohort=lambda:None,
                verify_revision_stamps=lambda:None,verify_backup=lambda:dict(rows=[{}],latest=self.backup['latest']),
                mcp_executable=lambda:'synthetic',put=lambda name,value:stored.update({name:value}))
            client=SimpleNamespace(initialize=lambda:(None,[],None,None))
            with patch('driver.sha',return_value='HASH'),patch('driver.read',side_effect=lambda p:docs[str(p)]),\
                 patch('driver.isolated_surface_unknown_after_saved_home',return_value=True),\
                 patch('driver.isolated_saved_menu_unknown',return_value=True),patch('driver.Client',return_value=client),\
                 patch('driver.subprocess.check_output',return_value=str(steam)),\
                 patch('driver.successful_surface_prepare_arguments',side_effect=AssertionError('wrong profile')):
                proof=Live(runtime).offline_preflight()
            self.assertFalse(proof['original_actions_reconciled']);self.assertTrue(proof['original_unknowns_isolated'])


if __name__=='__main__':unittest.main()
