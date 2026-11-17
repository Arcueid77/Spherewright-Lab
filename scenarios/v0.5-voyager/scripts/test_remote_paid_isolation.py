"""A completed paid remote object stays distinct from its unknown drone tail."""
from pathlib import Path
import copy,sys,unittest
sys.path.insert(0,str(Path(__file__).parent/'live'))
from contracts import remote_paid_saved_after_isolated_remote


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


class RemotePaidIsolationTests(unittest.TestCase):
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
