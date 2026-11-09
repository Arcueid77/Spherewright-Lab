"""Exercise the real packaged MCP SDK while the game is stopped."""
from pathlib import Path
import sys,datetime as dt
from evidence import need,put
from mcp_client import Client

def main():
    executable,output=sys.argv[1:];out=Path(output);out.mkdir(exist_ok=False)
    c=Client(executable,out/'client',maximum=48,seconds=60)
    try:
        _,tools,_,_=c.initialize();schemas={t['name']:t['inputSchema'] for t in tools}
        ctx=dict(sessionId='synthetic-offline-session',planetId=402);h='sha256:'+'a'*64
        cases=[
            ('spherewright_prepare_transfer',dict(ctx,direction='belt-cargo-to-player',storageEntityId=1,itemId=0,count=0,expectedPlayerStateHash=h,expectedStorageStateHash=h)),
            ('spherewright_prepare_refuel',dict(ctx,itemId=1802,count=20,expectedPlayerStateHash=h)),
            ('spherewright_prepare_blueprint_build',dict(ctx,expectedStateHash=h,expectedPlayerStateHash=h,
                resumeBuildId='11111111-1111-4111-8111-111111111111',maximumObjectsToSubmit=11,allowNewPaidConstructionWindow=True)),
            ('spherewright_prepare_transfer',dict(ctx,direction='player-to-generator-fuel',storageEntityId=20,itemId=1802,count=8,expectedPlayerStateHash=h,expectedStorageStateHash=h)),
            ('spherewright_prepare_transfer',dict(ctx,direction='player-to-storage',storageEntityId=1,itemId=1301,count=2,expectedPlayerStateHash=h,expectedStorageStateHash=h)),
            ('spherewright_prepare_transfer',dict(ctx,direction='production-reset-to-player',storageEntityId=1,itemId=0,count=0,expectedPlayerStateHash=h,expectedStorageStateHash=h)),
            ('spherewright_prepare_build',dict(ctx,buildingItemId=2101,expectedPlayerStateHash=h,preferredPositionX=1.,preferredPositionY=199.,preferredPositionZ=1.)),
            ('spherewright_prepare_build',dict(ctx,buildingItemId=2001,expectedPlayerStateHash=h,sourceObjectId=18,expectedSourceStateHash=h,pathEndX=1.,pathEndY=199.,pathEndZ=1.)),
            ('spherewright_prepare_build',dict(ctx,buildingItemId=2011,expectedPlayerStateHash=h,sourceObjectId=18,destinationObjectId=21,expectedSourceStateHash=h,expectedDestinationStateHash=h,initialSorterFilterItemId=1011)),
            ('spherewright_prepare_configure_building',dict(ctx,entityId=21,recipeId=32,mode='production',expectedFactoryStateHash=h)),
            ('spherewright_prepare_configure_building',dict(ctx,entityId=25,recipeId=0,mode='sorter-filter',filterItemId=1301,expectedFactoryStateHash=h)),
            ('spherewright_prepare_configure_building',dict(ctx,entityId=23,recipeId=0,mode='storage-capacity',storageOperation='filter-empty-or-matching',filterItemId=1123,expectedFactoryStateHash=h)),
            ('spherewright_prepare_configure_building',dict(ctx,entityId=30,recipeId=0,mode='dyson-minimal-receiving-node',expectedFactoryStateHash=h)),
            ('spherewright_prepare_configure_building',dict(ctx,entityId=0,recipeId=0,mode='enable-mecha-construction-drones',expectedFactoryStateHash=h)),
            ('spherewright_prepare_configure_building',dict(ctx,entityId=30,recipeId=0,mode='logistics-station-delivery',stationVesselDeliveryMinimumPercent=1,expectedFactoryStateHash=h,expectedStationConfigurationStateHash=h)),
            ('spherewright_prepare_save',dict(ctx,expectedRevision=1)),
            ('spherewright_prepare_handcraft',dict(ctx,recipeId=8,count=1,expectedPlayerStateHash=h)),
            ('spherewright_prepare_harvest',dict(ctx,resourceKind='vein',nodeId=1,requestedYieldCount=1,expectedResourceStateHash=h,expectedPlayerStateHash=h)),
            ('spherewright_preview_voyager_route',dict(ctx,destinationPlanetId=104,expectedPlayerStateHash=h,expectedCatalogStateHash=h,maximumFlightGameTicks=108000,returnReserveGameTicks=54000)),
            ('spherewright_prepare_voyager_flight',dict(ctx,expectedRouteStateHash=h,expectedPlayerStateHash=h)),
            ('spherewright_prepare_resume_owned_game',dict(resumeToken='synthetic-offline-token',recoveryMode='authorize_remote_primary_recovery',minimumRecoveryGameTick=100,expectedRecoveryGameTick=100,
                recoveryDeadlineUtc=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=3)).isoformat(),recoveryScope='continue_original_finite_task',maximumChargeGameTicks=18000,maximumChargeWallSeconds=300,
                additionalVoyagerGameTicks=432000,surfaceRecoveryTargetX=1.,surfaceRecoveryTargetY=199.,surfaceRecoveryTargetZ=1.))]
        cases.append(('spherewright_prepare_resume_owned_game',dict(resumeToken='synthetic-offline-token',recoveryMode='authorize_failed_landing_last_exit',minimumRecoveryGameTick=100,expectedRecoveryGameTick=100,
            recoveryDeadlineUtc=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=12)).isoformat(),recoveryScope='continue_original_finite_task',maximumChargeGameTicks=18000,maximumChargeWallSeconds=300,priorActionKnownTerminalFailed=True)))
        for mode in ('disable-mecha-research-auto-supply','enable-mecha-research-auto-supply'):
            cases.append(('spherewright_prepare_configure_building',dict(ctx,entityId=0,recipeId=0,mode=mode,expectedFactoryStateHash=h)))
        cases.append(('spherewright_prepare_configure_building',dict(ctx,entityId=0,recipeId=0,
            mode='enable-mecha-warper-auto-supply',expectedFactoryStateHash=h)))
        cases.append(('spherewright_prepare_resume_owned_game',dict(resumeToken='synthetic-offline-token',recoveryMode='default')))
        cases.append(('spherewright_prepare_resume_owned_game',dict(resumeToken='synthetic-offline-token',
            recoveryMode='open_saved_last_exit',minimumRecoveryGameTick=100,expectedRecoveryGameTick=100)))
        cases.append(('spherewright_prepare_supply_mecha_warpers',dict(sessionId=ctx['sessionId'],planetId=0,
            count=18,uiTopUp=True,expectedPlayerStateHash=h)))
        cases.append(('spherewright_prepare_interplanetary_flight',dict(sessionId=ctx['sessionId'],planetId=0,
            destinationPlanetId=101,expectedPlayerStateHash=h,expectedStarSystemStateHash=h,minimumCoreEnergyRatio=.8,
            stoppedSpaceReturnMaximumGameTicks=54000,stoppedSpaceReturnMaximumWallSeconds=14400)))
        cases.append(('spherewright_prepare_interplanetary_flight',dict(sessionId=ctx['sessionId'],planetId=101,
            destinationPlanetId=101,expectedPlayerStateHash=h,expectedStarSystemStateHash=h,minimumCoreEnergyRatio=.8,
            stoppedSpaceReturnMaximumGameTicks=51899,stoppedSpaceReturnMaximumWallSeconds=14400,
            savedHomeReturnPredecessorActionId='11111111-1111-4111-8111-111111111111',priorHomeReturnKnownTerminalFailed=True)))
        cases.extend([
            ('spherewright_prepare_build', dict(ctx, buildingItemId=2101, stackOnObjectId=1,
                expectedStackStateHash=h, preferredModelIndex=51, expectedPlayerStateHash=h)),
            ('spherewright_prepare_move', dict(ctx, targetX=1., targetY=199., targetZ=1.,
                previewWalkingRoute=True, expectedPlayerStateHash=h)),
        ])
        proof=[]
        for tool,args in cases:
            schema=schemas[tool];need(set(schema.get('required',[]))<=set(args),'sdk_required_field_missing')
            need(set(args)<=set(schema['properties']),'sdk_unknown_field')
            r,bad=c.call(tool,args);code=(r.get('error') or {}).get('code')
            need(code in ('BRIDGE_UNAVAILABLE','BRIDGE_NOT_READY'),'sdk_arguments_not_admitted:'+tool+':'+str(code))
            proof.append(dict(tool=tool,argumentsAdmitted=True,bridgeUnavailableAsExpected=True))
        r,bad=c.call('spherewright_prepare_transfer',dict(ctx,direction='Production-Reset-To-Player',storageEntityId=1,itemId=0,count=0,expectedPlayerStateHash=h,expectedStorageStateHash=h))
        need(bad and (r.get('error') or {}).get('code')=='INVALID_REQUEST','actual_sdk_transfer_case_contract_changed')
        put(out/'result.private.json',dict(passed=True,cases=proof,exactEnumCaseRejected=True,gameLaunches=0,gameCommits=0))
    finally:put(out/'client-close.private.json',c.close())

if __name__=='__main__':main()
