"""Interpret public DTO variants without inventing missing evidence."""

def owned_saved_recovery_context(config):
    if config.get('recoveryMode')=='authorize_remote_primary_recovery' and config.get('sourceRole')=='lastExit':return True
    home=config.get('closedJourneyHome') or {}
    return (config.get('recoveryProfile')=='ordinary-owned-home'
        and config.get('recoveryMode') in ('default','verified_newer_lastexit')
        and config.get('sourceRole') in ('primary','lastExit') and home.get('phase')=='completed'
        and home.get('homePlanetId')==config.get('planetId') and type(home.get('completedSaveGameTick'))is int
        and type(config.get('sourceTick'))is int and 0<home['completedSaveGameTick']<=config['sourceTick'])

def quarantined_paid_original_accounted(config,reference,receipt,preservation):
    count=reference.get('paidObjectCount');item=reference.get('itemId');objects=receipt.get('blueprintObjects') or []
    control=receipt.get('constructionControl') or {};failure=receipt.get('nativeFirstFailure') or {}
    return (owned_saved_recovery_context(config)
        and receipt.get('actionId')==reference.get('actionId') and receipt.get('terminal') is True
        and receipt.get('state')=='outcome_unknown' and control.get('executionKind')=='structured_native'
        and control.get('dispatchDisabled') is True and control.get('wholeBatchDebitSharedByObjectReceipts') is True
        and type(count)is int and 1<=count<=12 and len(objects)==count
        and sum(x.get('delta',0) for x in receipt.get('itemDeltas',[]) if x.get('itemId')==item)==-count
        and all(type(o.get('inventoryBefore'))is int and o['inventoryBefore']>=count
            and o.get('inventoryAfter')==o['inventoryBefore']-count and o.get('prebuildId',0)>0
            and o.get('beforeInventoryHash') and o.get('afterInventoryHash') for o in objects)
        and preservation.get('passed') is True and preservation.get('originalUnknownRetained') is True
        and preservation.get('noReplay') is True and preservation.get('noResume') is True
        # This is the frozen ORIGINAL stop receipt. Later normally saved
        # progress may advance its floor; Runtime separately verifies the full
        # exact current-source backup before any new Native owned recovery.
        and type(preservation.get('currentLastExit'))is int and type(config.get('sourceTick'))is int
        and type(failure.get('capturedAtGameTick'))is int
        and failure['capturedAtGameTick']<=preservation['currentLastExit']<=config['sourceTick'])

def quarantined_harvest_no_effect_accounted(config,reference,receipt,cut,session,preservation):
    action=reference.get('actionId');tick=cut.get('observedGameTick')
    return (owned_saved_recovery_context(config)
        and receipt.get('actionId')==action and receipt.get('actionKind')=='harvest'
        and receipt.get('terminal') is True and receipt.get('state')=='outcome_unknown'
        and receipt.get('targetObjectId')==reference.get('nodeId')==cut.get('nodeId')
        and reference.get('itemId')==cut.get('itemId') and type(receipt.get('requestedCount'))is int and receipt['requestedCount']>0
        and cut.get('originalActionId')==action and cut.get('noReplay') is True and cut.get('noResume') is True
        and type(cut.get('beforeNodeAmount'))is int and cut['beforeNodeAmount']>0
        and receipt.get('beforeTargetAmount')==cut['beforeNodeAmount']==cut.get('afterNodeAmount')
        and type(cut.get('beforePackageCount'))is int and cut['beforePackageCount']>=0
        and cut['beforePackageCount']==cut.get('afterPackageCount') and cut.get('nodeDecrease')==cut.get('packageIncrease')==0
        and type(tick)is int and type(receipt.get('completedAtGameTick'))is int and tick>=receipt['completedAtGameTick']
        and session.get('sessionId')==receipt.get('sessionId') and session.get('gameLoaded') is True
        and session.get('ownedBySpherewright') is True and session.get('writesAllowed') is False
        and session.get('writeQuarantineActionId')==action and session.get('gameTick')==tick
        and preservation.get('passed') is True and preservation.get('originalUnknownRetained') is True
        and preservation.get('noReplay') is True and preservation.get('noResume') is True
        and type(preservation.get('currentLastExit'))is int and type(config.get('sourceTick'))is int
        and tick<=preservation['currentLastExit']<=config['sourceTick'])

def isolated_paid_belt_build_accounted(config,receipt,plan,observation,preservation):
    """Accounts a frozen paid original without changing its unknown outcome."""
    import math
    deltas=receipt.get('itemDeltas') or [];points=plan.get('plannedPath') or [];entities=observation.get('entities') or []
    count=len(points)
    if not (owned_saved_recovery_context(config) and receipt.get('actionKind')=='build'
            and receipt.get('terminal') is True and receipt.get('state')=='outcome_unknown'
            and observation.get('originalActionId')==receipt.get('actionId')
            and observation.get('writeQuarantineActionId')==receipt.get('actionId')
            and len(deltas)==1 and deltas[0].get('itemId')==2001 and 1<=count<=64
            and deltas[0].get('delta')==-count and deltas[0].get('beforeCount',-1)-count==deltas[0].get('afterCount')
            and observation.get('packageCount')==deltas[0].get('afterCount')
            and len(entities)==count and len({e.get('objectId')for e in entities})==count
            and preservation.get('passed') is True and preservation.get('originalUnknownRetained') is True
            and preservation.get('noReplay') is True and preservation.get('normalExitOnly') is True
            and type(observation.get('capturedAtGameTick'))is int
            and receipt.get('completedAtGameTick',-1)<=observation['capturedAtGameTick']
            and observation['capturedAtGameTick']<=config.get('sourceTick',-1)):return False
    for point,entity in zip(points,entities):
        position=entity.get('position') or {}
        if not (type(entity.get('objectId'))is int and entity['objectId']>0 and entity.get('itemId')==2001
                and set(position)==set(point)=={'x','y','z'}
                and all(type(v)in(int,float)and math.isfinite(v)for v in [*position.values(),*point.values()])
                and math.dist([position[k]for k in 'xyz'],[point[k]for k in 'xyz'])<=.01):return False
    return True


def is_read_tool(name):
    return name.startswith(('spherewright_get_','spherewright_inspect_','spherewright_list_')) or name=='spherewright_preview_voyager_route'

def native_warper_auto_supply_enabled(result):
    detail=result.get('mechaWarperAutoSupplyReadback') or {}
    return (result.get('terminal') is True and result.get('succeeded') is True
        and result.get('actionKind')=='configure-building'
        and detail.get('enabledBefore') is False and detail.get('enabledAfter') is True
        and detail.get('readbackComplete') is True and detail.get('packageContentsPreserved') is True
        and detail.get('conservationVerified') is True
        and all(type(detail.get(k+'Before'))is int and detail[k+'Before']>=0
            and type(detail.get(k+'After'))is int and detail[k+'After']==detail[k+'Before']
            for k in ('packageCount','packageInc','chamberCount','chamberInc')))

def consumer_network(entity):
    if entity.get('componentKind') == 'power-node':
        return None  # not applicable: membership needs complete power topology
    return entity.get('powerNetworkId')


def observed_item_count(entity,item_id):
    """Physical stock only; station orders and demand metadata are not cargo."""
    if entity.get('componentKind')=='station':
        station=entity.get('logisticsStation') or {}
        if station.get('entityId')!=entity.get('objectId'):
            raise ValueError('station_stock_binding_unproved')
        rows=station.get('storageSlots')
        if not isinstance(rows,list):raise ValueError('station_stock_slots_unobserved')
    else:rows=entity['buffers']
    total=0
    for row in rows:
        if row['itemId']!=item_id:continue
        count=row['count']
        if type(count)is not int or count<0:raise ValueError('physical_item_count_invalid')
        total+=count
    return total


def resume_admission_echo(config,plan):
    failed=config.get('recoveryMode')=='authorize_failed_landing_last_exit'
    if failed:
        return (plan.get('failedLandingRecoveryAuthorizationUsed') is True
            and plan.get('remotePrimaryRecoveryAuthorizationUsed') is False
            and plan.get('completedSavedLandingAdmissionUsed') is False
            and plan.get('priorActionTerminalFailureAttested') is True
            and plan.get('priorActionTerminalCompletionAttested') is False
            and plan.get('originalFailedFlightActionId')==config.get('failedLandingActionId')
            and bool(config.get('failedLandingActionId'))
            and plan.get('savedLandingAccountingAnchorGameTick')==config['sourceTick']
            # Failed-landing mode selects the exact fixed LastExit directly;
            # discarded-primary-progress is not applicable, not a missing zero.
            and plan.get('discardedUnstoredProgressGameTicks') is None
            and plan.get('exactEmbeddedIdentityVerified') is True
            and plan.get('additionalVoyagerGameTicks')==0 and config['additionalVoyagerGameTicks']==0)
    if plan.get('remotePrimaryRecoveryAuthorizationUsed') is not True or plan.get('discardedUnstoredProgressGameTicks')!=0:
        return False
    if plan.get('completedSavedLandingAdmissionUsed') is True:
        # A separately completed admission of an old failed outbound.
        return bool(plan.get('originalFailedFlightActionId')) and plan.get('successfulFlightWitnessRetiredAtGameTick') is None
    # An ordinary successful Native landing has no failed-flight identity or
    # saved-failed-landing accounting anchor. Native MCP validates its own
    # successful checkpoint witness and the exact no-loss source before echoing.
    return (plan.get('completedSavedLandingAdmissionUsed') is False and not plan.get('originalFailedFlightActionId')
        and plan.get('savedLandingAccountingAnchorGameTick') is None and plan.get('failedLandingRecoveryAuthorizationUsed') is False)


def ordinary_owned_resume_echo(config,plan):
    """Ordinary home resume has different nullable/confirmation fields from remote recovery."""
    mode=config.get('recoveryMode');verified=mode=='verified_newer_lastexit'
    if mode not in ('default','verified_newer_lastexit'):return False
    common=(plan.get('recoveryMode')==mode and plan.get('expectedPlanetId')==config['planetId']
        and plan.get('sourceGameVersion')==plan.get('targetGameVersion')==config['expectedNativeVersion']
        and plan.get('userConfirmationRequired') is False and plan.get('commitAllowedNow') is True
        and plan.get('commitBlockers')==[] and plan.get('additionalVoyagerGameTicks')==0
        and plan.get('originalJourneyMaximumGameTicks') is None and plan.get('effectiveJourneyMaximumGameTicks') is None
        and all(plan.get(k) is False for k in ('remotePrimaryRecoveryAuthorizationUsed','failedLandingRecoveryAuthorizationUsed',
            'completedSavedLandingAdmissionUsed','opensSavedWorldOnly','previousAutomationRemainsStopped','newChargingProhibited')))
    if not common:return False
    if verified:
        return (plan.get('candidateGameTick')==plan.get('minimumGameTick')==config['sourceTick']
            and plan.get('exactEmbeddedIdentityVerified') is True and plan.get('recoveryEvidenceVersion')==1)
    return (config.get('sourceRole')=='primary' and plan.get('candidateGameTick') is None
        and plan.get('exactEmbeddedIdentityVerified') is False
        and plan.get('minimumGameTick')==config['ticketMinimumGameTick']<=config['sourceTick']
        and plan.get('recoveryEvidenceVersion')==0)


def powered_consumers_share_network(entities, network_id):
    consumers=[e for e in entities if e.get('componentKind') != 'power-node']
    return bool(consumers) and all(consumer_network(e)==network_id for e in consumers)


def strict_native_player_idle(player):
    physics=player.get('nativePhysics') or {};ground=physics.get('groundContact') or {}
    vectors=('velocity','walkRtsVelocity','driftRtsVelocity','walkManualVelocity','driftManualVelocity')
    return (player.get('movementState')=='Walk' and player.get('speed',float('inf'))<=.1
        and ground.get('checkSphereHit') is True and physics.get('currentOrderPresent') is False
        and physics.get('queuedOrderCount')==0
        and all(isinstance(physics.get(key),Mapping) and all(physics[key].get(axis)==0 for axis in 'xyz') for key in vectors))


def fully_observed_dry_surface(prepared):
    """Advisory terrain admission only; a dry preview never proves route clearance."""
    import math
    surface=prepared.get('surfacePreview') or {}
    samples=surface.get('samples') or []
    arc=surface.get('arcLengthMetres')
    if not (surface.get('state')=='observed' and surface.get('reasonCode') is None
            and surface.get('shoreRisk')=='not_detected'
            and surface.get('unknownSampleCount')==0 and surface.get('shoreRiskSampleCount')==0
            and type(arc) in (int,float) and math.isfinite(arc) and 0<=arc<=64
            and 2<=len(samples)<=65):return False
    for sample in samples:
        if sample.get('groundHit') is not True or sample.get('shoreRisk')!='not_detected':return False
        if sample.get('waterHit') is False:continue  # no water: depth is N/A
        depth=sample.get('groundBelowWaterMetres')
        if (sample.get('waterHit') is not True or type(depth) not in (int,float)
                or not math.isfinite(depth) or depth>=0):return False
    return True


def observed_short_crossing_dry_landing(prepared,arguments,player):
    """Published short-crossing contract, not blanket dry-ground admission."""
    import math
    if arguments.get('arrivalTolerance')!=1.5 or not strict_native_player_idle(player):return False
    if player.get('coreEnergy',0)<1280000000:return False
    surface=prepared.get('surfacePreview') or {};samples=surface.get('samples') or [];arc=surface.get('arcLengthMetres')
    if not (surface.get('state')=='observed' and surface.get('unknownSampleCount')==0
            and type(arc) in (int,float) and math.isfinite(arc) and 0<arc<=64 and 2<=len(samples)<=65):return False
    spacing=arc/(len(samples)-1)
    if spacing>1+1e-6:return False
    for row in samples:
        depth=row.get('groundBelowWaterMetres')
        if (row.get('groundHit') is not True or row.get('waterHit') is not True
                or type(depth) not in(int,float) or not math.isfinite(depth)):return False
    tail=0
    for row in reversed(samples):
        if row['groundBelowWaterMetres']<=-.1 and row.get('shoreRisk')=='not_detected':tail+=1
        else:break
    if (tail-1)*spacing<max(4,2*arguments['arrivalTolerance']+1):return False
    target=[arguments.get('target'+k.upper()) for k in 'xyz'];end=(samples[-1].get('position') or {})
    if any(type(x)not in(int,float) or not math.isfinite(x)for x in target):return False
    if any(type(end.get(k))not in(int,float) or not math.isfinite(end[k])for k in'xyz'):return False
    mismatch=abs(math.sqrt(sum(x*x for x in target))-math.sqrt(sum(end[k]**2 for k in'xyz')))
    return arguments['arrivalTolerance']>mismatch+.25


def paused_failed_cut(first_session, second_session, first_player, second_player, action_id,terminal=None):
    # SessionState has no isPaused and PlayerState exposes coreEnergy, not
    # energy. Use the actual public paused-cost blocker and stable cut.
    quarantine=(second_session.get('writesAllowed') is False and second_session.get('writeQuarantineActionId')==action_id)
    native=(terminal or {}).get('voyagerFlightReadback') or {}
    flight=(terminal or {}).get('actionId')==action_id and (terminal or {}).get('state')=='recovery_required' \
        and (terminal or {}).get('recoveryRequired') is True and (terminal or {}).get('actionKind')=='interplanetary-flight' \
        and bool((terminal or {}).get('flightCheckpointId')) and (terminal or {}).get('flightCheckpointId')==second_session.get('flightCheckpointId') \
        and native.get('bindingVerified') is True and native.get('nativeExitObserved') is True and native.get('actualPlanetId')==second_session.get('localPlanetId')
    return (first_session.get('gameTick')==second_session.get('gameTick')
        and first_session.get('sessionId')==second_session.get('sessionId')
        and second_session.get('gameLoaded') is True and second_session.get('ownedBySpherewright') is True
        and (quarantine or flight)
        and first_player.get('position') is not None and first_player.get('position')==second_player.get('position')
        and isinstance(first_player.get('coreEnergy'),(int,float)) and first_player['coreEnergy']==second_player.get('coreEnergy')
        and 'native_paused_not_execution_ready' in (second_player.get('nativeLocalControlEnergy') or {}).get('blockers',[]))


def validate_steps(steps):
    required={
        'operation':{'prepareTool','arguments'},'prepare-only':{'prepareTool','arguments'},'adopt-paid-build':{'buildId','expectedObjects','itemId'},
        'read':{'tool'},'dump':{'queries'},'build-object':{'itemId','positions'},
        'build-stack':{'itemId','anchor'},
        'build-belt':{'source','ends','maximumNewBelts'},'build-free-belt':{'candidates','maximumNewBelts'},'build-belt-to-device':{'starts','destination','maximumNewBelts'},
        'build-sorter':{'source','destination','filterItemId'},'configure':{'entity'},
        'wait-buffer':{'entity','itemId','minimumCount','maximumSeconds'},'wait-player-still':{'maximumSeconds'},'prove-network':{'entities','networkId'},'save-close':set(),'handoff-caller':set(),
        'observe-sail-conversion':{'entity','count','orbitId','maximumSeconds','baselinePath','baselineSha256'},
        'observe-rocket-arrival':{'entity','layerId','nodeId','maximumSeconds','baselinePath','baselineSha256'}}
    for index,step in enumerate(steps):
        kind=step.get('kind')
        if kind not in required or not ({'kind','role'}|required[kind])<=set(step):
            raise ValueError('immutable_plan_shape_invalid:'+str(kind))
        if kind == 'build-stack':
            anchor = step['anchor']
            if type(step['itemId']) is not int or step['itemId'] <= 0 or not (
                    type(anchor) is int and anchor > 0 or isinstance(anchor, str) and bool(anchor)):
                raise ValueError('immutable_stack_identity_invalid')
        if 'modelIndex' in step and (type(step['modelIndex']) is not int or step['modelIndex'] <= 0):
            raise ValueError('immutable_native_model_invalid')
        if 'freshStaleMaximumSeconds' in step:
            seconds=step['freshStaleMaximumSeconds']
            if kind not in ('operation','prepare-only') or type(seconds) not in(int,float) or not 0<=seconds<=60:
                raise ValueError('finite_fresh_stale_allowance_required')
        if kind=='dump' and any(not {'name','tool'}<=set(q) for q in step['queries']):
            raise ValueError('immutable_dump_query_shape_invalid')
        if kind=='operation' and step.get('requireObservedShortCrossingDryLanding'):
            stop=steps[index+1] if index+1<len(steps) else {}
            if (step.get('prepareTool')!='spherewright_prepare_move' or stop.get('kind')!='wait-player-still'
                    or stop.get('minimumCoreEnergy',0)<1280000000):
                raise ValueError('short_crossing_requires_immediate_strict_stop_and_energy_readback')


from collections.abc import Mapping


def validate_native_calls(steps,schemas):
    """Compile literal call shapes against the actual MCP tools/list response."""
    def call(tool,args):
        schema=schemas.get(tool)
        if schema is None:raise ValueError('actual_sdk_unknown_tool:'+str(tool))
        properties=schema['properties'];keys=set(args)|({'sessionId','planetId'}&set(properties))
        if set(args)-set(properties) or not set(schema.get('required',[]))<=keys:
            raise ValueError('actual_sdk_argument_shape:'+tool)
        for key,value in args.items():
            if isinstance(value,Mapping) and set(value)=={'ref'}:continue
            spec=properties[key];types=spec.get('type',[]);types=[types] if isinstance(types,str) else types
            if value is None:
                if types and 'null' not in types:raise ValueError('actual_sdk_nonnullable:'+key)
                continue
            matches={'string':isinstance(value,str),'integer':type(value)is int,'number':type(value)in(int,float),
                'boolean':type(value)is bool,'array':isinstance(value,(list,tuple)),'object':isinstance(value,Mapping)}
            if types and not any(matches.get(kind,False) for kind in types):raise ValueError('actual_sdk_type:'+key)
            if 'enum' in spec and value not in spec['enum']:raise ValueError('actual_sdk_enum:'+key)
    for step in steps:
        kind=step['kind']
        if kind == 'build-stack':
            arguments = dict(buildingItemId=step['itemId'], expectedPlayerStateHash='schema-placeholder',
                stackOnObjectId=1, expectedStackStateHash='schema-placeholder')
            if 'modelIndex' in step:
                arguments['preferredModelIndex'] = step['modelIndex']
            call('spherewright_prepare_build', arguments)
        elif kind == 'build-object' and 'modelIndex' in step:
            call('spherewright_prepare_build', dict(buildingItemId=step['itemId'],
                expectedPlayerStateHash='schema-placeholder', preferredModelIndex=step['modelIndex']))
        elif kind=='read':call(step['tool'],step.get('arguments',{}))
        elif kind=='dump':
            for query in step['queries']:call(query['tool'],query.get('arguments',{}))
        elif kind in ('operation','prepare-only'):
            for query in step.get('reads',[]):call(query['tool'],query.get('arguments',{}))
            call(step['prepareTool'],step['arguments'])

