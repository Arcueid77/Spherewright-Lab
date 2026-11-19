"""Interpret public DTO variants without inventing missing evidence."""

def owned_saved_recovery_context(config):
    if config.get('recoveryMode')=='authorize_remote_primary_recovery' and config.get('sourceRole')=='lastExit':return True
    if (config.get('recoveryProfile')=='ordinary-owned-remote'
            and config.get('recoveryMode')=='authorize_remote_primary_recovery' and config.get('sourceRole')=='primary'):
        # The driver separately validates this evidence, its historical home
        # source and the later complete remote save before allowing any launch.
        return bool(config.get('remoteSavedUnknownIsolation') or config.get('remotePaidSavedUnknownIsolation')
            or config.get('remoteFailedResumeSavedIsolation') or config.get('remoteHealthySavedIsolation')
            or config.get('remotePausedHarvestSavedIsolation') or config.get('remoteFailedSameTickSavedIsolation')
            or config.get('remoteRoundtripPausedIsolation')) and config.get('originalActionsReconciled') is False
    if (config.get('recoveryProfile')=='successful-outbound-surface'
            and config.get('recoveryMode')=='authorize_remote_primary_recovery' and config.get('sourceRole')=='primary'):
        return bool(config.get('surfacePreviousRemoteIsolation')) and config.get('originalActionsReconciled') is False
    home=config.get('closedJourneyHome') or {}
    return (config.get('recoveryProfile')=='ordinary-owned-home'
        and config.get('recoveryMode') in ('default','verified_newer_lastexit','reauthorize_expired_primary')
        and (config.get('recoveryMode')!='reauthorize_expired_primary' or config.get('sourceRole')=='primary')
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


def quarantined_navigation_original_accounted(config, reference, receipt, session, preservation):
    native = receipt.get('nativeSurfaceNavigationReadback') or {}
    action = reference.get('actionId')
    return (owned_saved_recovery_context(config)
        and bool(action) and receipt.get('actionId') == action and receipt.get('actionKind') == 'move'
        and receipt.get('terminal') is True and receipt.get('state') == 'outcome_unknown'
        and receipt.get('succeeded') is False and native.get('evidenceVersion') == 1
        and bool(reference.get('planBindingHash')) and native.get('planBindingHash') == reference['planBindingHash']
        and all(native.get(key) is True for key in
            ('nativeNavigationStarted', 'nativeFlyObserved', 'nativeArrivalObserved', 'nativeNavigationReleased'))
        and all(item.get('delta') == 0 for item in receipt.get('itemDeltas', []))
        and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True
        and session.get('writesAllowed') is False and session.get('writeQuarantineActionId') == action
        and session.get('sessionId') == receipt.get('sessionId')
        and preservation.get('passed') is True and preservation.get('originalUnknownRetained') is True
        and preservation.get('noReplay') is True and preservation.get('noForceKill') is True
        and all(type(value) is int for value in (receipt.get('completedAtGameTick'), session.get('gameTick'),
            preservation.get('currentLastExit'), config.get('sourceTick')))
        and 0 <= receipt['completedAtGameTick'] <= session['gameTick']
            <= preservation['currentLastExit'] <= config['sourceTick'])

def quarantined_local_move_saved_source(config, reference, receipt, session, preservation, saved_source):
    """Retain an unknown ordinary Move while proving the later saved source.

    This accounts for the old action only; it does not declare arrival, idle,
    ground contact, or a successful recovery. Runtime separately verifies the
    complete current backup and Native identity before invoking this check.
    """
    tick = config.get('sourceTick'); action = reference.get('actionId')
    renamed = config.get('restoreRenamedLastExitIdentity') is True
    saved_hash = preservation.get('sourceSha256') if renamed else preservation.get('primarySha256')
    return (config.get('recoveryProfile') == 'successful-outbound-surface'
        and config.get('recoveryMode') == 'authorize_remote_primary_recovery'
        and config.get('sourceRole') == ('lastExit' if renamed else 'primary') and type(tick) is int and tick >= 0
        and isinstance(action, str) and bool(action)
        and receipt.get('actionId') == action and receipt.get('actionKind') == 'move'
        and receipt.get('terminal') is True and receipt.get('state') == 'outcome_unknown'
        and receipt.get('succeeded') is False and receipt.get('reconciledFromOutcomeUnknown') is False
        and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True
        and session.get('writesAllowed') is False and session.get('writeHealth') == 'quarantined'
        and session.get('writeQuarantineActionId') == action
        and session.get('sessionId') == receipt.get('sessionId')
        and session.get('localPlanetId') == receipt.get('planetId') == config.get('planetId')
        and type(receipt.get('completedAtGameTick')) is int and 0 <= receipt['completedAtGameTick'] <= tick
        and type(session.get('gameTick')) is int and session['gameTick'] == tick
        and preservation.get('passed') is True and preservation.get('exactLiveTickMatched') is True
        and preservation.get('fullFileHashVerified') is True
        and type(preservation.get('savedGameTick')) is int and preservation['savedGameTick'] == tick
        and preservation.get('sessionCutSha256') == reference.get('sessionSha256')
        and isinstance(saved_hash, str) and bool(saved_hash)
        and (not renamed or preservation.get('sameNativeWorldCreation') is True
            and config.get('expectedRenamedLastExitContentHash') == 'sha256:' + saved_hash.lower())
        and type(saved_source.get('gameTick')) is int and saved_source['gameTick'] == tick
        and saved_source.get('sha256') == saved_hash)

def surface_unknown_after_isolated_remote(config,previous,action):
    """Keep earlier isolated outcomes when a later saved Move needs shore recovery."""
    old=previous.get('originalUnknownActionsNeverReplayed');current=config.get('originalUnknownActionsNeverReplayed')
    before=previous.get('sourceTick');tick=config.get('sourceTick')
    return (config.get('recoveryProfile')=='successful-outbound-surface'
        and previous.get('recoveryProfile')=='ordinary-owned-remote'
        and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
        and config.get('sourceRole')==previous.get('sourceRole')=='primary'
        and config.get('planetId')==previous.get('planetId')
        and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
        and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
        and all(isinstance(x,str) and x for x in (*old,*current,action))
        and len(set(old))==len(old) and len(set(current))==len(current)
        and action not in old and set(current)==set(old)|{action}
        and type(before)is int and type(tick)is int and 0<=before<=tick
        and type(previous.get('spentGameTicks'))is int and previous['spentGameTicks']>=0
        and config.get('spentGameTicks')==previous['spentGameTicks']+tick-before
        and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
        and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
        and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
        and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256'))


def surface_failed_resume_saved_after_isolation(config,previous,failed,cut,save_plan,saved,closed,preservation,backup):
    """A later failed surface resume is saved without resolving the old Move."""
    old=previous.get('originalUnknownActionsNeverReplayed');current=config.get('originalUnknownActionsNeverReplayed')
    before=previous.get('sourceTick');tick=config.get('sourceTick');session=cut.get('session') or {}
    player=cut.get('player') or {};action=failed.get('actionId');failure=failed.get('nativeFirstFailure') or {}
    latest=backup.get('latest') or {}
    return (config.get('recoveryProfile')==previous.get('recoveryProfile')=='successful-outbound-surface'
        and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
        and config.get('sourceRole')==previous.get('sourceRole')=='primary'
        and config.get('planetId')==previous.get('planetId')
        and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
        and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
        and all(isinstance(x,str) and x for x in (*old,*current)) and len(set(old))==len(old)
        and len(set(current))==len(current) and set(old)==set(current)
        and type(before)is int and type(tick)is int and 0<=before<=tick
        and type(previous.get('spentGameTicks'))is int and previous['spentGameTicks']>=0
        and config.get('spentGameTicks')==previous['spentGameTicks']+tick-before
        and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
        and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
        and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
        and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256')
        and isinstance(action,str) and bool(action) and action not in current
        and failed.get('actionKind')=='resume-owned-game' and failed.get('terminal') is True
        and failed.get('state')=='action_failed' and failed.get('succeeded') is False
        and type(failure.get('capturedAtGameTick'))is int and before<=failure['capturedAtGameTick']<=tick
        and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True
        and session.get('writesAllowed') is False and session.get('writeHealth')=='quarantined'
        and session.get('writeQuarantineActionId')==action and session.get('gameTick')==tick
        and session.get('sessionId')==player.get('sessionId')==failed.get('sessionId')==saved.get('sessionId')
        and session.get('localPlanetId')==player.get('planetId')==saved.get('planetId')==config.get('planetId')
        and cut.get('noResume') is True
        and 'native_paused_not_execution_ready' in (player.get('nativeLocalControlEnergy') or {}).get('blockers',[])
        and save_plan.get('prepared') is True and save_plan.get('commitAllowedNow') is True
        and save_plan.get('preservesQuarantine') is True and save_plan.get('preservationGameTick')==tick
        and save_plan.get('commitBlockers')==[] and saved.get('actionKind')=='save'
        and saved.get('terminal') is True and saved.get('state')=='completed' and saved.get('succeeded') is True
        and saved.get('completedAtGameTick')==tick and isinstance(saved.get('actionId'),str)
        and bool(saved['actionId']) and saved['actionId'] not in (*current,action)
        and closed.get('passed') is True and closed.get('gameStopped') is True
        and preservation.get('passed') is True and preservation.get('minimumCurrentTick')==tick
        and preservation.get('originalQuarantineRetained') is True and preservation.get('noResume') is True
        and backup.get('complete') is True and backup.get('verified') is True
        and (latest.get('primary') or {}).get('gameTick')==(latest.get('lastExit') or {}).get('gameTick')==tick)


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
    if entity.get('componentKind')=='power-generator' and entity.get('itemId') in (2204,2211):
        fuel=entity.get('fuelPowerState') or {};fuel_item=fuel.get('bufferedFuelItemId');count=fuel.get('bufferedFuelCount')
        if not (fuel.get('state')=='observed' and type(fuel_item)is int and fuel_item>=0
                and type(count)is int and count>=0 and (fuel_item>0 or count==0)):
            raise ValueError('generator_fuel_stock_unobserved')
        return count if fuel_item==item_id else 0
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
        if (row.get('countUnit','items')!='items'
                or row.get('unitsPerItem',1)!=1):
            continue
        count=row['count']
        if type(count)is not int or count<0:raise ValueError('physical_item_count_invalid')
        total+=count
    return total


def observed_stack_device_matches(entity, expected):
    stack=entity.get('stack') or {}
    if not (stack.get('complete') is True and stack.get('state')=='observed'
            and stack.get('selectedObjectId')==entity.get('objectId')):return False
    layers=[row for row in stack.get('layers',[]) if row.get('objectId')==entity.get('objectId')]
    if len(layers)!=1:return False
    state=layers[0].get('deviceState') or {}
    return bool(expected) and all(key in state and type(state[key])is type(value)
                                 and state[key]==value for key,value in expected.items())


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
    if config.get('recoveryProfile')=='ordinary-owned-remote':
        return (config.get('recoveryMode')=='authorize_remote_primary_recovery'
            and (config.get('sourceRole')=='primary' or config.get('sourceRole')=='lastExit' and bool(
                config.get('remoteFailedResumeSavedIsolation') or config.get('remoteLiveExitIsolation')))
            and plan.get('recoveryMode')==config['recoveryMode'] and plan.get('exactEmbeddedIdentityVerified') is True
            and isinstance(config.get('expectedNativeVersion'),str) and bool(config['expectedNativeVersion'])
            and plan.get('sourceGameVersion')==plan.get('targetGameVersion')==config['expectedNativeVersion']
            and plan.get('successfulOutboundSurfaceSourceUsed') is False
            and plan.get('completedSavedLandingAdmissionUsed') is False
            and plan.get('failedLandingRecoveryAuthorizationUsed') is False
            and not plan.get('originalFailedFlightActionId') and plan.get('savedLandingAccountingAnchorGameTick') is None
            and plan.get('nativeOriginalOutcomeProved') is False)
    if config.get('recoveryProfile') == 'successful-outbound-surface':
        renamed = config.get('restoreRenamedLastExitIdentity') is True
        return (config.get('recoveryMode') == 'authorize_remote_primary_recovery'
            and config.get('sourceRole') == ('lastExit' if renamed else 'primary') and type(config.get('sourceTick')) is int
            and plan.get('recoveryMode') == config['recoveryMode']
            and plan.get('exactEmbeddedIdentityVerified') is True
            and isinstance(config.get('expectedNativeVersion'), str) and bool(config['expectedNativeVersion'])
            and plan.get('sourceGameVersion') == plan.get('targetGameVersion') == config['expectedNativeVersion']
            and plan.get('renamedLastExitIdentityRestorationPlanned') is renamed
            and (not renamed or plan.get('expectedRenamedLastExitContentHash') == config.get('expectedRenamedLastExitContentHash'))
            and plan.get('successfulOutboundSurfaceSourceUsed') is True
            and plan.get('completedSavedLandingAdmissionUsed') is False
            and plan.get('failedLandingRecoveryAuthorizationUsed') is False
            and not plan.get('originalFailedFlightActionId')
            and plan.get('savedLandingAccountingAnchorGameTick') is None
            and plan.get('nativeOriginalOutcomeProved') is False
            and type(plan.get('surfaceRecoveryExpectedSourceGameTick')) is int
            and plan['surfaceRecoveryExpectedSourceGameTick'] == config['sourceTick']
            and type(plan.get('candidateGameTick')) is int and type(plan.get('minimumGameTick')) is int
            and plan['candidateGameTick'] == plan['minimumGameTick'] == config['sourceTick'])
    if plan.get('successfulOutboundSurfaceSourceUsed') is True:
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
    reauthorizing=mode=='reauthorize_expired_primary'
    if mode not in ('default','verified_newer_lastexit','reauthorize_expired_primary'):return False
    common=(plan.get('recoveryMode')==mode and plan.get('expectedPlanetId')==config['planetId']
        and plan.get('sourceGameVersion')==plan.get('targetGameVersion')==config['expectedNativeVersion']
        and plan.get('userConfirmationRequired') is reauthorizing and plan.get('commitAllowedNow') is (not reauthorizing)
        and [row.get('code')for row in plan.get('commitBlockers',[])]==(['USER_CONFIRMATION_REQUIRED']if reauthorizing else [])
        and plan.get('additionalVoyagerGameTicks')==0
        and plan.get('originalJourneyMaximumGameTicks') is None and plan.get('effectiveJourneyMaximumGameTicks') is None
        and all(plan.get(k) is False for k in ('remotePrimaryRecoveryAuthorizationUsed','failedLandingRecoveryAuthorizationUsed',
            'completedSavedLandingAdmissionUsed','opensSavedWorldOnly','previousAutomationRemainsStopped','newChargingProhibited')))
    if not common:return False
    if reauthorizing:
        return (config.get('sourceRole')=='primary'
            and plan.get('candidateGameTick')==plan.get('minimumGameTick')==config['sourceTick']
            and plan.get('exactEmbeddedIdentityVerified') is True
            and plan.get('recoveryEvidenceVersion')==2 and bool(plan.get('confirmationDigest')))
    if verified:
        return (plan.get('candidateGameTick')==plan.get('minimumGameTick')==config['sourceTick']
            and plan.get('exactEmbeddedIdentityVerified') is True and plan.get('recoveryEvidenceVersion')==1)
    if config.get('quarantinedDefaultLastExit') is True:
        minimum=plan.get('minimumGameTick')
        return (config.get('sourceRole')=='lastExit'
            and bool(config.get('isolatedPaidBeltBuilds') or config.get('quarantinedNavigationOriginals'))
            and type(minimum)is int and config['sourcePrimaryGameTick']<config['originalQuarantineMinimumTick']<=minimum<=config['sourceTick']
            and plan.get('candidateGameTick') is None and plan.get('exactEmbeddedIdentityVerified') is False
            and plan.get('recoveryEvidenceVersion')==0)
    minimum=plan.get('minimumGameTick');ticket_floor=config.get('ticketMinimumGameTick')
    # A normal save may advance the protected Native ticket after this caller's
    # earlier snapshot. The freshly backed-up primary remains the no-loss ceiling.
    return (config.get('sourceRole')=='primary' and plan.get('candidateGameTick') is None
        and plan.get('exactEmbeddedIdentityVerified') is False
        and type(minimum)is int and type(ticket_floor)is int and type(config.get('sourceTick'))is int
        and 0<=ticket_floor<=minimum<=config['sourceTick']
        and plan.get('recoveryEvidenceVersion')==0)


def powered_consumers_share_network(entities, network_id):
    consumers=[e for e in entities if e.get('componentKind') != 'power-node']
    return bool(consumers) and all(consumer_network(e)==network_id for e in consumers)


def native_movement_order_released(player,before):
    """A completed move can be real progress before its player lands."""
    physics=player.get('nativePhysics') or {}
    return (player.get('isAlive') is True and player.get('isOnPlanet') is True
        and bool(before.get('sessionId')) and player.get('sessionId')==before.get('sessionId')
        and type(before.get('planetId')) is int and before['planetId']>0
        and player.get('planetId')==before['planetId']
        and physics.get('currentOrderPresent') is False
        and type(physics.get('queuedOrderCount')) is int and physics['queuedOrderCount']==0)


def strict_native_player_idle(player,allow_passive_drift=False):
    physics=player.get('nativePhysics') or {};ground=physics.get('groundContact') or {}
    drift=allow_passive_drift and player.get('movementState')=='Drift'
    vectors=('walkRtsVelocity','driftRtsVelocity','walkManualVelocity','driftManualVelocity')
    if not drift:vectors=('velocity',*vectors)
    velocity=physics.get('velocity') or {}
    # Unity evaluates each Vector3 squared component in binary32. Half its
    # smallest subnormal rounds to zero, matching the Native zero-magnitude test.
    zero_square_maximum=2.0**-150
    return ((drift or player.get('movementState')=='Walk') and player.get('speed',float('inf'))<=.1
        and (drift or ground.get('checkSphereHit') is True) and physics.get('currentOrderPresent') is False
        and physics.get('queuedOrderCount')==0
        and (not drift or all(type(velocity.get(axis))in(int,float)for axis in 'xyz')
            and sum(velocity[axis]**2 for axis in 'xyz')<=.01)
        and all(isinstance(physics.get(key),Mapping)
            and all(type(physics[key].get(axis)) in (int,float)
                and physics[key][axis]*physics[key][axis]<=zero_square_maximum
                for axis in 'xyz') for key in vectors))


def completed_saved_surface_move(config, result, session, player):
    """Prove the distinct native Move embedded in a successful saved recovery."""
    import math
    move=(player.get('nativePhysics') or {}).get('resumeSurfaceRecoveryMove') or {}
    def vector(value):
        if not isinstance(value,Mapping):return None
        values=[value.get(k) for k in 'xyz']
        return values if all(type(x) in (int,float) and math.isfinite(x) for x in values) else None
    source=vector(move.get('sourcePosition'));target=vector(move.get('targetPosition'))
    current=vector(move.get('currentPosition'));requested=vector(config.get('surfaceRecoveryTarget'))
    player_position=vector(player.get('position'))
    if any(x is None for x in (source,target,current,requested,player_position)):return False
    source_radius=math.dist(source,[0,0,0]);requested_radius=math.dist(requested,[0,0,0])
    if source_radius<1 or requested_radius<1:return False
    normalized=[x*source_radius/requested_radius for x in requested]
    return (config.get('recoveryProfile')=='successful-outbound-surface'
        and (config.get('firstOperation') or {}).get('kind')=='surface-recovery-move'
        and result.get('terminal') is True and result.get('succeeded') is True
        and result.get('state')=='completed' and result.get('actionKind')=='resume-owned-game'
        and isinstance(result.get('actionId'),str) and bool(result['actionId'])
        and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True
        and session.get('writesAllowed') is True and session.get('sessionId')==result.get('sessionId')==player.get('sessionId')
        and session.get('localPlanetId')==result.get('planetId')==player.get('planetId')==config.get('planetId')
        and type(config.get('sourceTick')) is int and move.get('sourceGameTick')==config['sourceTick']
        and type(move.get('capturedAtGameTick')) is int and type(player.get('capturedAtGameTick')) is int
        and config['sourceTick']<=move['capturedAtGameTick']<=player['capturedAtGameTick']
        and move.get('resumeActionId')==result['actionId'] and move.get('state')=='completed_idle'
        and move.get('nativeOperation')=='OrderNode.MoveTo/Player.Order'
        and move.get('nativeOrderAccepted') is True and move.get('strictPhysicalIdleProved') is True
        and move.get('failure') is None and move.get('newGameTicksGranted') is False
        and move.get('originalUnknownOutcomeChanged') is False and strict_native_player_idle(player)
        and math.dist(normalized,target)<=.05 and math.dist(current,player_position)<=.2)


def saved_home_source_covers(config, backup, floor):
    """The selected complete home save must cover the old proven boundary."""
    latest=backup.get('latest') or {};primary=(latest.get('primary') or {}).get('gameTick')
    last_exit=(latest.get('lastExit') or {}).get('gameTick');tick=config.get('sourceTick');role=config.get('sourceRole')
    return (owned_saved_recovery_context(config) and role in ('primary','lastExit')
        and all(type(x)is int for x in (primary,last_exit,tick,floor)) and 0<=floor<=primary<=tick
        and floor<=last_exit<=tick and max(primary,last_exit)==tick
        and (primary if role=='primary' else last_exit)==tick)


def isolated_surface_unknown_after_saved_home(config, old_config, original, receipt, session, preservation,
                                             old_source, progress, loaded, flight, home_save, backup):
    """Carry the old unknown unchanged through a distinct proved return and Save."""
    native=flight.get('voyagerFlightReadback') or {}
    tick=config.get('sourceTick'); saved=home_save.get('completedAtGameTick')
    return (saved_home_source_covers(config,backup,saved)
        and original.get('actionId') in config.get('originalUnknownActionsNeverReplayed',())
        and quarantined_local_move_saved_source(old_config,original,receipt,session,preservation,old_source)
        and progress.get('verified') is True and progress.get('oldUnknownReconciled') is False and progress.get('noReplay') is True
        and completed_saved_surface_move(old_config,progress.get('originalResumeReceipt') or {},loaded,progress.get('player') or {})
        and flight.get('actionKind')=='interplanetary-flight' and flight.get('terminal') is True
        and flight.get('state')=='completed' and flight.get('succeeded') is True
        and flight.get('sessionId')==loaded.get('sessionId') and native.get('isReturnLeg') is True
        and native.get('bindingVerified') is True and native.get('nativeExitObserved') is True
        and native.get('actualPlanetId')==native.get('selectedDestinationPlanetId')==config.get('planetId')
        and home_save.get('actionKind')=='save' and home_save.get('terminal') is True
        and home_save.get('state')=='completed' and home_save.get('succeeded') is True
        and home_save.get('sessionId')==loaded.get('sessionId') and home_save.get('planetId')==config.get('planetId')
        and all(type(x)is int for x in (flight.get('completedAtGameTick'),saved,tick))
        and old_config['sourceTick']<=flight['completedAtGameTick']<=saved<=tick)


def isolated_saved_menu_unknown(config, receipt, observed_action, observation, close_intent, close_result, backup):
    """A complete Save plus observed unloaded menu isolates, not resolves, the old return."""
    native=receipt.get('mainMenuReturnReadback') or {}
    observed=(observed_action.get('response') or {}).get('result') or {}
    saved=native.get('savedGameTick');tick=config.get('sourceTick');pid=observation.get('processId')
    return (saved_home_source_covers(config,backup,saved)
        and receipt.get('actionId') in config.get('originalUnknownActionsNeverReplayed',())
        and receipt.get('actionKind')=='return-to-main-menu' and receipt.get('terminal') is True
        and receipt.get('state')=='outcome_unknown' and receipt.get('succeeded') is False
        and receipt.get('reconciledFromOutcomeUnknown') is False
        and native.get('normalSaveConfirmed') is True and native.get('completeSaveVerified') is True
        and native.get('nativeEndRequested') is True and type(saved)is int and type(tick)is int and 0<=saved<=tick
        and observed_action.get('toolError') is False and (observed_action.get('response') or {}).get('success') is True
        and observed.get('actionId')==receipt.get('actionId') and observed.get('terminal') is True
        and observed.get('state')=='outcome_unknown' and observed.get('reconciledFromOutcomeUnknown') is False
        and observation.get('gameLoaded') is False and observation.get('originalActionReplayed') is False
        and type(pid)is int and pid>0 and close_intent.get('processId')==pid and close_intent.get('forceKill') is False
        and close_intent.get('maximumRequests')==1 and close_result.get('passed') is True and close_result.get('gameStopped') is True)


def remote_saved_after_isolated_home(config, home, loaded, outbound, menu_save, backup):
    """Carry a previously isolated history through a distinct saved outbound.

    The caller independently verifies the historical isolation and both complete
    backups. This only binds that history to the later owned session, original
    successful outbound, and exact remote save; it never resolves old actions.
    """
    current_unknowns=config.get('originalUnknownActionsNeverReplayed')
    home_unknowns=home.get('originalUnknownActionsNeverReplayed')
    if not (isinstance(current_unknowns,(list,tuple)) and isinstance(home_unknowns,(list,tuple))
            and current_unknowns and all(isinstance(x,str) and x for x in (*current_unknowns,*home_unknowns))
            and len(set(current_unknowns))==len(current_unknowns)
            and len(set(home_unknowns))==len(home_unknowns) and set(current_unknowns)==set(home_unknowns)):
        return False
    latest=backup.get('latest') or {};primary=(latest.get('primary') or {}).get('gameTick')
    last_exit=(latest.get('lastExit') or {}).get('gameTick');tick=config.get('sourceTick')
    launch=outbound.get('voyagerFlightReadback') or {};saved=menu_save.get('mainMenuReturnReadback') or {}
    home_tick=home.get('sourceTick');loaded_tick=loaded.get('gameTick')
    start=outbound.get('startedAtGameTick');arrival=outbound.get('completedAtGameTick')
    save_tick=menu_save.get('completedAtGameTick');session=loaded.get('sessionId')
    return (config.get('recoveryProfile')=='ordinary-owned-remote'
        and config.get('recoveryMode')=='authorize_remote_primary_recovery'
        and config.get('sourceRole')=='primary' and config.get('surfaceRecoveryTarget') is None
        and config.get('originalActionsReconciled') is False
        and home.get('recoveryProfile')=='ordinary-owned-home' and home.get('originalActionsReconciled') is False
        and type(config.get('planetId')) is int and config['planetId']>0
        and type(home.get('planetId')) is int and home['planetId']>0
        and config['planetId']!=home['planetId'] and bool(session)
        and isinstance(config.get('expectedNativeVersion'),str) and bool(config['expectedNativeVersion'])
        and config.get('expectedNativeVersion')==home.get('expectedNativeVersion')
        and isinstance(config.get('nativeAssemblySha256'),str) and bool(config['nativeAssemblySha256'])
        and config.get('nativeAssemblySha256')==home.get('nativeAssemblySha256')
        and all(type(x)is int for x in (home_tick,loaded_tick,start,arrival,save_tick,tick,primary,last_exit))
        and 0<=home_tick<=loaded_tick<=start<=arrival<=save_tick==tick==primary
        and 0<=last_exit<=tick
        and backup.get('complete') is True and backup.get('verified') is True
        and loaded.get('gameLoaded') is True and loaded.get('ownedBySpherewright') is True
        and loaded.get('writesAllowed') is True and loaded.get('localPlanetId')==home.get('planetId')
        and isinstance(outbound.get('actionId'),str) and bool(outbound['actionId'])
        and outbound['actionId'] not in current_unknowns
        and outbound.get('actionKind')=='interplanetary-flight' and outbound.get('terminal') is True
        and outbound.get('state')=='completed' and outbound.get('succeeded') is True
        and outbound.get('sessionId')==session and outbound.get('planetId')==home.get('planetId')
        and launch.get('isReturnLeg') is False and launch.get('bindingVerified') is True
        and launch.get('nativeExitObserved') is True
        and launch.get('actualPlanetId')==launch.get('selectedDestinationPlanetId')==config.get('planetId')
        and isinstance(menu_save.get('actionId'),str) and bool(menu_save['actionId'])
        and menu_save['actionId'] not in current_unknowns and menu_save['actionId']!=outbound['actionId']
        and menu_save.get('actionKind')=='return-to-main-menu' and menu_save.get('terminal') is True
        and menu_save.get('state')=='completed' and menu_save.get('succeeded') is True
        and menu_save.get('sessionId')==session and menu_save.get('planetId')==config.get('planetId')
        and saved.get('normalSaveConfirmed') is True and saved.get('completeSaveVerified') is True
        and saved.get('nativeEndRequested') is True and saved.get('mainMenuVerified') is True
        and saved.get('savedGameTick')==save_tick)


def remote_paused_saved_after_isolated_home(config, home, loaded, outbound, cut, save_plan, saved, closed, preservation, backup):
    """Carry the same isolated home history through a paused outbound save."""
    old=home.get('originalUnknownActionsNeverReplayed');current=config.get('originalUnknownActionsNeverReplayed')
    session=cut.get('session') or {};player=cut.get('player') or {};native=outbound.get('voyagerFlightReadback') or {}
    latest=backup.get('latest') or {};tick=config.get('sourceTick');home_tick=home.get('sourceTick')
    start=outbound.get('startedAtGameTick');arrival=outbound.get('completedAtGameTick');loaded_tick=loaded.get('gameTick')
    ident=loaded.get('sessionId');action=outbound.get('actionId');blockers=session.get('writeBlockers') or []
    return (config.get('recoveryProfile')=='ordinary-owned-remote'
        and config.get('recoveryMode')=='authorize_remote_primary_recovery' and config.get('sourceRole')=='primary'
        and config.get('surfaceRecoveryTarget') is None and config.get('originalActionsReconciled') is False
        and home.get('recoveryProfile')=='ordinary-owned-home' and home.get('originalActionsReconciled') is False
        and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
        and len(set(old))==len(old) and len(set(current))==len(current) and set(old)==set(current)
        and config.get('planetId')!=home.get('planetId') and type(config.get('planetId')) is int and config['planetId']>0
        and isinstance(config.get('expectedNativeVersion'),str) and bool(config['expectedNativeVersion'])
        and config.get('expectedNativeVersion')==home.get('expectedNativeVersion')
        and isinstance(config.get('nativeAssemblySha256'),str) and bool(config['nativeAssemblySha256'])
        and config.get('nativeAssemblySha256')==home.get('nativeAssemblySha256')
        and all(type(x)is int for x in (home_tick,loaded_tick,start,arrival,tick))
        and 0<=home_tick<=loaded_tick<=start<=arrival<=tick
        and type(home.get('spentGameTicks')) is int
        and config.get('spentGameTicks')==home['spentGameTicks']+tick-home_tick
        and config.get('returnReserveGameTicks')==home.get('returnReserveGameTicks')
        and config.get('cleanupReserveGameTicks')==home.get('cleanupReserveGameTicks')
        and isinstance(ident,str) and bool(ident) and loaded.get('gameLoaded') is True
        and loaded.get('ownedBySpherewright') is True and loaded.get('writesAllowed') is True
        and loaded.get('localPlanetId')==home.get('planetId')
        and isinstance(action,str) and bool(action) and action not in current
        and outbound.get('actionKind')=='interplanetary-flight' and outbound.get('terminal') is True
        and outbound.get('state')=='completed' and outbound.get('succeeded') is True
        and outbound.get('sessionId')==ident and outbound.get('planetId')==home.get('planetId')
        and native.get('isReturnLeg') is False and native.get('bindingVerified') is True
        and native.get('nativeExitObserved') is True
        and native.get('actualPlanetId')==native.get('selectedDestinationPlanetId')==config.get('planetId')
        and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True
        and session.get('sessionId')==player.get('sessionId')==ident
        and session.get('localPlanetId')==player.get('planetId')==config.get('planetId')
        and session.get('writesAllowed') is False and session.get('writeHealth')=='quarantined'
        and session.get('writeQuarantineActionId')==action and cut.get('noResume') is True
        and session.get('gameTick')==tick and any(x.get('code')=='WRITE_SUBSYSTEM_QUARANTINED' for x in blockers if isinstance(x,dict))
        and 'native_paused_not_execution_ready' in (player.get('nativeLocalControlEnergy') or {}).get('blockers',[])
        and save_plan.get('prepared') is True and save_plan.get('commitAllowedNow') is True
        and save_plan.get('preservesQuarantine') is True and save_plan.get('preservationGameTick')==tick
        and save_plan.get('commitBlockers')==[]
        and saved.get('actionKind')=='save' and saved.get('terminal') is True and saved.get('succeeded') is True
        and saved.get('state')=='completed' and saved.get('sessionId')==ident
        and saved.get('planetId')==config.get('planetId') and saved.get('completedAtGameTick')==tick
        and isinstance(saved.get('actionId'),str) and bool(saved['actionId'])
        and saved['actionId'] not in current and saved['actionId']!=action
        and closed.get('passed') is True and closed.get('gameStopped') is True
        and preservation.get('passed') is True and preservation.get('minimumCurrentTick')==tick
        and preservation.get('originalQuarantineRetained') is True and preservation.get('noResume') is True
        and backup.get('complete') is True and backup.get('verified') is True
        and (latest.get('primary') or {}).get('gameTick')==(latest.get('lastExit') or {}).get('gameTick')==tick)


def remote_roundtrip_paused_after_isolation(config, previous, loaded, home_return, home_save, outbound,
                                             cut, save_plan, saved, closed, preservation, backup):
    """Carry isolated history through an observed home return and new paused outbound."""
    old=previous.get('originalUnknownActionsNeverReplayed');current=config.get('originalUnknownActionsNeverReplayed')
    session=cut.get('session') or {};player=cut.get('player') or {};blockers=session.get('writeBlockers') or []
    back=home_return.get('voyagerFlightReadback') or {};away=outbound.get('voyagerFlightReadback') or {}
    tick=config.get('sourceTick');before=previous.get('sourceTick');ident=loaded.get('sessionId')
    action=outbound.get('actionId');home=back.get('actualPlanetId');latest=backup.get('latest') or {}
    times=(before,loaded.get('gameTick'),home_return.get('startedAtGameTick'),home_return.get('completedAtGameTick'),
           home_save.get('completedAtGameTick'),outbound.get('startedAtGameTick'),outbound.get('completedAtGameTick'),tick)
    ids=(home_return.get('actionId'),home_save.get('actionId'),action,saved.get('actionId'))
    return (config.get('recoveryProfile')=='ordinary-owned-remote'
        and previous.get('recoveryProfile') in ('ordinary-owned-remote','successful-outbound-surface')
        and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
        and config.get('sourceRole')==previous.get('sourceRole')=='primary'
        and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
        and config.get('surfaceRecoveryTarget') is None
        and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
        and all(isinstance(x,str) and x for x in (*old,*current,*ids))
        and len(set(old))==len(old) and len(set(current))==len(current) and set(old)==set(current)
        and len(set(ids))==len(ids) and not set(ids).intersection(current)
        and all(type(x)is int for x in times) and 0<=times[0]<=times[1]<=times[2]<=times[3]<=times[4]<=times[5]<=times[6]<=times[7]
        and type(previous.get('spentGameTicks'))is int and previous['spentGameTicks']>=0
        and config.get('spentGameTicks')==previous['spentGameTicks']+tick-before
        and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
        and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
        and isinstance(config.get('expectedNativeVersion'),str) and bool(config['expectedNativeVersion'])
        and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
        and isinstance(config.get('nativeAssemblySha256'),str) and bool(config['nativeAssemblySha256'])
        and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256')
        and isinstance(ident,str) and bool(ident) and loaded.get('gameLoaded') is True
        and loaded.get('ownedBySpherewright') is True and loaded.get('writesAllowed') is True
        and loaded.get('localPlanetId')==previous.get('planetId')==config.get('planetId')
        and type(home)is int and home>0 and home!=config.get('planetId')
        and home_return.get('sessionId')==home_save.get('sessionId')==outbound.get('sessionId')==ident
        and home_return.get('actionKind')==outbound.get('actionKind')=='interplanetary-flight'
        and all(x.get('terminal') is True and x.get('state')=='completed' and x.get('succeeded') is True
                for x in (home_return,home_save,outbound,saved))
        and home_return.get('planetId')==config.get('planetId') and back.get('isReturnLeg') is True
        and back.get('bindingVerified') is True and back.get('nativeExitObserved') is True
        and back.get('selectedDestinationPlanetId')==home
        and home_save.get('actionKind')=='save' and home_save.get('planetId')==home
        and outbound.get('planetId')==home and away.get('isReturnLeg') is False
        and away.get('bindingVerified') is True and away.get('nativeExitObserved') is True
        and away.get('actualPlanetId')==away.get('selectedDestinationPlanetId')==config.get('planetId')
        and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True
        and session.get('sessionId')==player.get('sessionId')==saved.get('sessionId')==ident
        and session.get('localPlanetId')==player.get('planetId')==saved.get('planetId')==config.get('planetId')
        and session.get('writesAllowed') is False and session.get('writeHealth')=='quarantined'
        and session.get('writeQuarantineActionId')==action and session.get('gameTick')==tick
        and any(x.get('code')=='WRITE_SUBSYSTEM_QUARANTINED' for x in blockers if isinstance(x,dict))
        and cut.get('noResume') is True
        and 'native_paused_not_execution_ready' in (player.get('nativeLocalControlEnergy') or {}).get('blockers',[])
        and save_plan.get('prepared') is True and save_plan.get('commitAllowedNow') is True
        and save_plan.get('preservesQuarantine') is True and save_plan.get('preservationGameTick')==tick
        and save_plan.get('commitBlockers')==[] and saved.get('actionKind')=='save' and saved.get('completedAtGameTick')==tick
        and closed.get('passed') is True and closed.get('gameStopped') is True
        and preservation.get('passed') is True and preservation.get('minimumCurrentTick')==tick
        and preservation.get('originalQuarantineRetained') is True and preservation.get('noResume') is True
        and backup.get('complete') is True and backup.get('verified') is True
        and (latest.get('primary') or {}).get('gameTick')==(latest.get('lastExit') or {}).get('gameTick')==tick)


def remote_paid_saved_after_isolated_remote(config, previous, loaded, original, observed, session, player, station, saved, closed, backup):
    """Carry one observed paid remote building through its normal paused save.

    The historical remote source and both complete backups are independently
    checked by the caller. Entity completion and debit do not resolve the old
    action or certify its physically returning drone.
    """
    import math
    old=previous.get('originalUnknownActionsNeverReplayed');current=config.get('originalUnknownActionsNeverReplayed')
    action=original.get('actionId');tick=config.get('sourceTick');before=previous.get('sourceTick')
    builds=observed.get('builds') or [];drones=player.get('constructionDrones') or {}
    active=drones.get('activeObservations') or [];receipt=saved.get('originalSave') or {}
    latest=backup.get('latest') or {};primary=(latest.get('primary') or {}).get('gameTick');last=(latest.get('lastExit') or {}).get('gameTick')
    if not (config.get('recoveryProfile')==previous.get('recoveryProfile')=='ordinary-owned-remote'
            and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
            and config.get('sourceRole')==previous.get('sourceRole')=='primary'
            and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
            and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
            and all(isinstance(x,str) and x for x in (*old,*current)) and isinstance(action,str) and bool(action)
            and len(set(old))==len(old) and len(set(current))==len(current)
            and action not in old and set(current)==set(old)|{action}
            and type(before)is int and type(tick)is int and 0<=before<tick
            and type(previous.get('spentGameTicks'))is int and previous['spentGameTicks']>=0
            and config.get('spentGameTicks')==previous.get('spentGameTicks')+tick-before
            and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
            and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
            and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
            and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256')
            and loaded.get('gameLoaded') is True and loaded.get('ownedBySpherewright') is True and loaded.get('writesAllowed') is True
            and type(loaded.get('gameTick'))is int and before<=loaded['gameTick']<=tick
            and loaded.get('localPlanetId')==config.get('planetId')==previous.get('planetId')
            and session.get('sessionId')==player.get('sessionId')==station.get('sessionId')==original.get('sessionId')==loaded.get('sessionId')
            and session.get('localPlanetId')==player.get('planetId')==station.get('planetId')==original.get('planetId')==config.get('planetId')
            and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True and session.get('writesAllowed') is False
            and session.get('writeQuarantineActionId')==action and session.get('gameTick')==tick
            and player.get('capturedAtGameTick')==station.get('capturedAtGameTick')==tick
            and original.get('actionKind')=='build' and original.get('terminal') is True and original.get('succeeded') is False
            and original.get('state')=='outcome_unknown' and original.get('reconciledFromOutcomeUnknown') is False
            and type(original.get('completedAtGameTick'))is int and loaded['gameTick']<=original['completedAtGameTick']<=tick
            and len(original.get('itemDeltas') or [])==1 and original['itemDeltas'][0].get('delta')==-1
            and original['itemDeltas'][0].get('itemId')==station.get('itemId')==2103
            and len(builds)==1 and saved.get('passed') is True and saved.get('originalActionId')==action
            and all(saved.get(k)is True for k in ('noLoad','noReplay','noResume')) and saved.get('savedGameTick')==tick
            and receipt.get('actionKind')=='save' and receipt.get('terminal') is True and receipt.get('succeeded') is True
            and receipt.get('sessionId')==loaded.get('sessionId') and receipt.get('planetId')==config.get('planetId')
            and receipt.get('completedAtGameTick')==tick and receipt.get('actionId')!=action
            and closed.get('passed') is True and closed.get('paidOriginalRetained') is True and closed.get('noReplay') is True
            and closed.get('primaryTick')==closed.get('lastExitTick')==primary==last==tick
            and backup.get('complete') is True and backup.get('verified') is True): return False
    b=builds[0];objects=b.get('objects') or [];originals=original.get('blueprintObjects') or []
    specs=(b.get('site') or {}).get('objects') or [];station_detail=station.get('logisticsStation') or {}
    control=original.get('constructionControl') or {}
    if not (b.get('actionId')==action and b.get('buildId')==original.get('blueprintBuildId') and bool(b.get('buildId'))
            and b.get('sessionId')==loaded.get('sessionId') and b.get('planetId')==config.get('planetId')
            and b.get('capturedAtGameTick')==tick and b.get('phase')=='outcome_unknown'
            and b.get('persistenceHealthy') is True and b.get('freshWorldReconciled') is True
            and b.get('doNotReplayWholeBlueprint') is True
            and b.get('submittedCount')==b.get('completedCount')==1 and len(objects)==len(originals)==len(specs)==1
            and control.get('executionKind')=='structured_native' and control.get('dispatchDisabled') is True
            and control.get('physicalIdleVerified') is False and control.get('wholeBatchDebitSharedByObjectReceipts') is True
            and objects[0].get('state')=='completed' and objects[0].get('entityId')==station.get('objectId')
            and type(station.get('objectId'))is int and station['objectId']>0
            and type(objects[0].get('prebuildId'))is int and objects[0]['prebuildId']>0
            and objects[0].get('prebuildId')==originals[0].get('prebuildId')
            and all(objects[0].get(k)==originals[0].get(k) and objects[0].get(k) is not None
                    for k in ('inventoryBefore','inventoryAfter','beforeInventoryHash','afterInventoryHash'))
            and type(objects[0]['inventoryBefore'])is int and objects[0]['inventoryAfter']==objects[0]['inventoryBefore']-1
            and original['itemDeltas'][0].get('beforeCount')==objects[0]['inventoryBefore']
            and original['itemDeltas'][0].get('afterCount')==objects[0]['inventoryAfter']
            and specs[0].get('itemId')==2103 and station_detail.get('isInterstellar') is False
            and station_detail.get('isCollector') is False and station_detail.get('galacticStationId')==0
            and drones.get('enabled') is False and drones.get('activeObservationsComplete') is True
            and all(type(drones.get(k))is int and drones[k]>=0 for k in ('working','idle','total'))
            and drones['working']+drones['idle']==drones['total']
            and type(drones.get('working'))is int and drones['working']>0 and len(active)==drones['working']
            and all(x.get('stage')==4 and x.get('targetObjectId')==0
                    and x.get('nextTargetObjectIds')==[0,0,0] for x in active)): return False
    a=station.get('position') or {};p=specs[0].get('position') or {}
    return (set(a)==set(p)=={'x','y','z'} and all(type(v)in(int,float) and math.isfinite(v) for v in (*a.values(),*p.values()))
        and math.dist([a[k] for k in 'xyz'],[p[k] for k in 'xyz'])<=.01)


def remote_failed_resume_saved_after_paid(config, previous, failed, cut, closed, backup, saved=None):
    """Carry a known failed recovery through an exact current owned save."""
    old=previous.get('originalUnknownActionsNeverReplayed');current=config.get('originalUnknownActionsNeverReplayed')
    before=previous.get('sourceTick');tick=config.get('sourceTick');session=cut.get('session') or {}
    player=cut.get('player') or {};station=cut.get('station') or {};builds=(cut.get('build') or {}).get('builds') or []
    failure=failed.get('nativeFirstFailure') or {};latest=backup.get('latest') or {}
    if not (config.get('recoveryProfile')==previous.get('recoveryProfile')=='ordinary-owned-remote'
            and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
            and config.get('sourceRole') in ('primary','lastExit') and previous.get('sourceRole') in ('primary','lastExit')
            and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
            and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
            and all(isinstance(x,str) and x for x in (*old,*current)) and len(set(old))==len(old)
            and len(set(current))==len(current) and set(current)==set(old)
            and type(before)is int and type(tick)is int and 0<=before<tick
            and type(previous.get('spentGameTicks'))is int and previous['spentGameTicks']>=0
            and config.get('spentGameTicks')==previous['spentGameTicks']+tick-before
            and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
            and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
            and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
            and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256')
            and failed.get('actionKind')=='resume-owned-game' and failed.get('terminal') is True
            and failed.get('succeeded') is False and failed.get('state')=='action_failed'
            and cut.get('noReplay') is True
            and isinstance(failed.get('actionId'),str) and bool(failed['actionId']) and failed['actionId'] not in current
            and failure.get('capturedAtGameTick')==tick and session.get('gameTick')==tick
            and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True and session.get('writesAllowed') is False
            and session.get('writeQuarantineActionId')==failed['actionId'] and session.get('sessionId')==failed.get('sessionId')
            and session.get('localPlanetId')==failed.get('planetId')==player.get('planetId')==station.get('planetId')==config.get('planetId')
            and player.get('sessionId')==station.get('sessionId')==session.get('sessionId')
            and player.get('capturedAtGameTick')==station.get('capturedAtGameTick')==tick
            and station.get('itemId')==2103 and type(station.get('objectId'))is int and station['objectId']>0
            and len(builds)==1 and builds[0].get('actionId') in old and builds[0].get('phase')=='outcome_unknown'
            and builds[0].get('completedCount')==1 and len(builds[0].get('objects') or [])==1
            and builds[0]['objects'][0].get('state')=='completed' and builds[0]['objects'][0].get('entityId')==station['objectId']
            and closed.get('passed') is True and closed.get('noReplay') is True
            and closed.get('latestTick')==tick and backup.get('complete') is True and backup.get('verified') is True
            and closed.get('primaryTick')==(latest.get('primary') or {}).get('gameTick')
            and closed.get('lastExitTick')==(latest.get('lastExit') or {}).get('gameTick')):return False
    if config['sourceRole']=='lastExit':
        if not (saved is None and closed.get('actualDiscardedTicks')==0 and closed.get('pausedCutTick')==tick
                and closed.get('primaryTick')==before and closed.get('lastExitTick')==tick):return False
    else:
        receipt=(saved or {}).get('originalSave') or {}
        if not ((saved or {}).get('passed') is True and saved.get('originalResumeActionId')==failed['actionId']
                and all(saved.get(k)is True for k in ('noLoad','noReplay','noResume')) and saved.get('savedGameTick')==tick
                and receipt.get('actionKind')=='save' and receipt.get('terminal') is True and receipt.get('succeeded') is True
                and receipt.get('sessionId')==session.get('sessionId') and receipt.get('planetId')==config.get('planetId')
                and receipt.get('completedAtGameTick')==tick and closed.get('savedTick')==tick
                and closed.get('primaryTick')==closed.get('lastExitTick')==tick):return False
    drones=player.get('constructionDrones') or {};active=drones.get('activeObservations') or []
    return (drones.get('enabled') is False and drones.get('activeObservationsComplete') is True
        and all(type(drones.get(k))is int and drones[k]>=0 for k in ('working','idle','total'))
        and drones['working']+drones['idle']==drones['total'] and len(active)==drones['working']
        and all(x.get('stage')==4 and x.get('targetObjectId')==0 and x.get('nextTargetObjectIds')==[0,0,0] for x in active))


def remote_healthy_saved_after_isolation(config, previous, loaded, resumed, menu_save, backup):
    """Carry unchanged old unknowns through one distinct healthy remote save."""
    old=previous.get('originalUnknownActionsNeverReplayed');current=config.get('originalUnknownActionsNeverReplayed')
    before=previous.get('sourceTick');tick=config.get('sourceTick');latest=backup.get('latest') or {}
    save=menu_save.get('mainMenuReturnReadback') or {};session=loaded.get('sessionId')
    return (config.get('recoveryProfile')==previous.get('recoveryProfile')=='ordinary-owned-remote'
        and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
        and config.get('sourceRole')=='primary' and previous.get('sourceRole') in ('primary','lastExit')
        and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
        and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
        and all(isinstance(x,str) and x for x in (*old,*current)) and len(set(old))==len(old)
        and len(set(current))==len(current) and set(old)==set(current)
        and type(before)is int and type(tick)is int and 0<=before<=tick
        and type(previous.get('spentGameTicks'))is int and previous['spentGameTicks']>=0
        and config.get('spentGameTicks')==previous['spentGameTicks']+tick-before
        and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
        and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
        and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
        and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256')
        and isinstance(session,str) and bool(session) and loaded.get('gameLoaded') is True
        and loaded.get('ownedBySpherewright') is True and loaded.get('writesAllowed') is True
        and loaded.get('localPlanetId')==config.get('planetId')==previous.get('planetId')
        and type(loaded.get('gameTick'))is int and before<=loaded['gameTick']<=tick
        and resumed.get('actionKind')=='resume-owned-game' and resumed.get('terminal') is True and resumed.get('succeeded') is True
        and resumed.get('state')=='completed' and resumed.get('sessionId')==session and resumed.get('planetId')==config.get('planetId')
        and resumed.get('actionId') not in current and menu_save.get('actionId') not in current
        and menu_save.get('actionId')!=resumed.get('actionId') and menu_save.get('actionKind')=='return-to-main-menu'
        and menu_save.get('terminal') is True and menu_save.get('succeeded') is True and menu_save.get('state')=='completed'
        and menu_save.get('sessionId')==session and menu_save.get('planetId')==config.get('planetId')
        and menu_save.get('completedAtGameTick')==tick and save.get('savedGameTick')==tick
        and all(save.get(k)is True for k in ('normalSaveConfirmed','completeSaveVerified','nativeEndRequested','mainMenuVerified'))
        and backup.get('complete') is True and backup.get('verified') is True
        and (latest.get('primary') or {}).get('gameTick')==(latest.get('lastExit') or {}).get('gameTick')==tick)


def remote_paused_harvest_saved_after_isolation(config, previous, loaded, resumed, reference, harvest, cut,
                                                session, save_plan, saved, closed, preservation, backup):
    """Carry a no-effect harvest and prior unknowns through the actual paused save."""
    old=previous.get('originalUnknownActionsNeverReplayed'); current=config.get('originalUnknownActionsNeverReplayed')
    before=previous.get('sourceTick'); tick=config.get('sourceTick'); action=reference.get('actionId')
    latest=backup.get('latest') or {}; session_id=loaded.get('sessionId')
    return (config.get('recoveryProfile')==previous.get('recoveryProfile')=='ordinary-owned-remote'
        and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
        and config.get('sourceRole')=='primary' and previous.get('sourceRole') in ('primary','lastExit')
        and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
        and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old) and bool(action)
        and len(set(old))==len(old) and len(set(current))==len(current) and action not in old
        and set(current)==set(old)|{action}
        and type(before)is int and type(tick)is int and 0<=before<=tick
        and type(previous.get('spentGameTicks'))is int and previous['spentGameTicks']>=0
        and config.get('spentGameTicks')==previous['spentGameTicks']+tick-before
        and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
        and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
        and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
        and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256')
        and isinstance(session_id,str) and bool(session_id) and loaded.get('gameLoaded') is True
        and loaded.get('ownedBySpherewright') is True and loaded.get('writesAllowed') is True
        and loaded.get('localPlanetId')==config.get('planetId')==previous.get('planetId')
        and type(loaded.get('gameTick'))is int and before<=loaded['gameTick']<=tick
        and resumed.get('actionKind')=='resume-owned-game' and resumed.get('terminal') is True
        and resumed.get('succeeded') is True and resumed.get('state')=='completed'
        and resumed.get('sessionId')==session_id and resumed.get('planetId')==config.get('planetId')
        and quarantined_harvest_no_effect_accounted(config,reference,harvest,cut,session,preservation)
        and session.get('sessionId')==session_id and session.get('gameTick')==tick
        and save_plan.get('prepared') is True and save_plan.get('commitAllowedNow') is True
        and save_plan.get('preservesQuarantine') is True and save_plan.get('preservationGameTick')==tick
        and saved.get('actionKind')=='save' and saved.get('terminal') is True and saved.get('succeeded') is True
        and saved.get('state')=='completed' and saved.get('sessionId')==session_id
        and saved.get('planetId')==config.get('planetId') and saved.get('completedAtGameTick')==tick
        and saved.get('actionId') not in current and resumed.get('actionId') not in current
        and closed.get('passed') is True and closed.get('gameStopped') is True
        and backup.get('complete') is True and backup.get('verified') is True
        and (latest.get('primary') or {}).get('gameTick')==(latest.get('lastExit') or {}).get('gameTick')==tick)


def remote_failed_same_tick_saved_after_isolation(config, previous, failed, session, save_plan, saved, closed, backup):
    """A known failed load at the saved tick does not erase earlier progress."""
    old=previous.get('originalUnknownActionsNeverReplayed');current=config.get('originalUnknownActionsNeverReplayed')
    tick=config.get('sourceTick');latest=backup.get('latest') or {};failure=failed.get('nativeFirstFailure') or {}
    return (config.get('recoveryProfile')==previous.get('recoveryProfile')=='ordinary-owned-remote'
        and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
        and config.get('sourceRole')=='primary' and previous.get('sourceRole')=='primary'
        and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
        and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
        and len(set(old))==len(old) and len(set(current))==len(current) and set(old)==set(current)
        and type(tick)is int and tick==previous.get('sourceTick')
        and config.get('spentGameTicks')==previous.get('spentGameTicks')
        and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
        and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
        and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
        and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256')
        and failed.get('actionKind')=='resume-owned-game' and failed.get('terminal') is True
        and failed.get('succeeded') is False and failed.get('state')=='action_failed'
        and failure.get('capturedAtGameTick')==tick and failed.get('actionId') not in current
        and session.get('sessionId')==failed.get('sessionId') and session.get('localPlanetId')==config.get('planetId')
        and session.get('gameTick')==tick and session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True
        and session.get('writesAllowed') is False and session.get('writeQuarantineActionId')==failed.get('actionId')
        and save_plan.get('prepared') is True and save_plan.get('commitAllowedNow') is True
        and save_plan.get('preservesQuarantine') is True and save_plan.get('preservationGameTick')==tick
        and saved.get('actionKind')=='save' and saved.get('terminal') is True and saved.get('succeeded') is True
        and saved.get('state')=='completed' and saved.get('sessionId')==session.get('sessionId')
        and saved.get('planetId')==config.get('planetId') and saved.get('completedAtGameTick')==tick
        and saved.get('actionId') not in current and closed.get('passed') is True and closed.get('gameStopped') is True
        and backup.get('complete') is True and backup.get('verified') is True
        and (latest.get('primary') or {}).get('gameTick')==(latest.get('lastExit') or {}).get('gameTick')==tick)


def remote_live_exit_after_isolation(config, previous, loaded, resumed, last, closed, actions, backup):
    """Carry an independently resumed remote world through its exact newer LastExit."""
    old=previous.get('originalUnknownActionsNeverReplayed'); current=config.get('originalUnknownActionsNeverReplayed')
    before=previous.get('sourceTick'); tick=config.get('sourceTick'); latest=backup.get('latest') or {}
    session=loaded.get('sessionId'); blockers=last.get('writeBlockers') or []
    if not (config.get('recoveryProfile')==previous.get('recoveryProfile')=='ordinary-owned-remote'
        and config.get('recoveryMode')==previous.get('recoveryMode')=='authorize_remote_primary_recovery'
        and config.get('sourceRole')=='lastExit' and previous.get('sourceRole') in ('primary','lastExit')
        and config.get('originalActionsReconciled') is previous.get('originalActionsReconciled') is False
        and isinstance(old,(list,tuple)) and isinstance(current,(list,tuple)) and bool(old)
        and len(set(old))==len(old) and len(set(current))==len(current) and set(old)==set(current)
        and type(before)is int and type(tick)is int and before<tick
        and type(previous.get('spentGameTicks'))is int
        and config.get('spentGameTicks')==previous['spentGameTicks']+tick-before
        and config.get('returnReserveGameTicks')==previous.get('returnReserveGameTicks')
        and config.get('cleanupReserveGameTicks')==previous.get('cleanupReserveGameTicks')
        and config.get('expectedNativeVersion')==previous.get('expectedNativeVersion')
        and config.get('nativeAssemblySha256')==previous.get('nativeAssemblySha256')
        and isinstance(session,str) and bool(session)
        and loaded.get('gameLoaded') is True and loaded.get('ownedBySpherewright') is True and loaded.get('writesAllowed') is True
        and loaded.get('localPlanetId')==last.get('localPlanetId')==config.get('planetId')==previous.get('planetId')
        and type(loaded.get('gameTick'))is int and before<=loaded['gameTick']<=tick
        and resumed.get('actionKind')=='resume-owned-game' and resumed.get('terminal') is True
        and resumed.get('succeeded') is True and resumed.get('state')=='completed'
        and resumed.get('sessionId')==last.get('sessionId')==session and resumed.get('planetId')==config.get('planetId')
        and resumed.get('actionId') not in current
        and last.get('gameLoaded') is True and last.get('ownedBySpherewright') is True
        and last.get('writesAllowed') is False and last.get('writeHealth')=='quarantined'
        and last.get('writeQuarantineActionId')==resumed.get('actionId') and last.get('gameTick')==tick
        and any(x.get('code')=='WRITE_SUBSYSTEM_QUARANTINED' for x in blockers if isinstance(x,dict))
        and closed.get('normalEof') is True and closed.get('processExitCode')==0
        and closed.get('readerThreadsStopped') is True and closed.get('phaseClosed') is True
        and type(closed.get('priorRpcCount'))is int and type(closed.get('requestCount'))is int
        and config.get('priorRpcCount',-1)>=closed['priorRpcCount']+closed['requestCount']
        and backup.get('complete') is True and backup.get('verified') is True
        and (latest.get('lastExit') or {}).get('gameTick')==tick
        and type((latest.get('primary') or {}).get('gameTick'))is int
        and before<=(latest['primary']['gameTick'])<tick
        and isinstance(actions,(list,tuple)) and actions):return False
    ids=[a.get('actionId') for a in actions]
    return (len(set(ids))==len(ids) and resumed.get('actionId') in ids
        and all(isinstance(a.get('actionId'),str) and a['actionId'] and a['actionId'] not in current
            and a.get('sessionId')==session and a.get('planetId')==config.get('planetId')
            and a.get('terminal') is True and a.get('succeeded') is True and a.get('state')=='completed'
            and (a.get('actionKind')=='resume-owned-game' or
                 type(a.get('completedAtGameTick'))is int and loaded['gameTick']<=a['completedAtGameTick']<=tick)
            for a in actions))


def completed_home_window_admitted(config, loaded, arrival, saved, journey, handoff):
    """A saved, completed return can start a new finite home work window."""
    seconds=config.get('completedHomeWindowSeconds'); home=config.get('attachmentPlanetId')
    native=arrival.get('voyagerFlightReadback') or {};session=loaded.get('sessionId')
    arrived=arrival.get('completedAtGameTick');saved_tick=saved.get('completedAtGameTick')
    return (type(seconds) in (int,float) and 0<seconds<=86400
        and type(home)is int and home>0 and home in config.get('authorizedPlanetIds',())
        and isinstance(session,str) and bool(session)
        and arrival.get('terminal') is True and arrival.get('succeeded') is True
        and arrival.get('sessionId')==session and native.get('actualPlanetId')==home
        and native.get('nativeExitObserved') is True and type(arrived)is int
        and saved.get('terminal') is True and saved.get('succeeded') is True and saved.get('actionKind')=='save'
        and saved.get('sessionId')==session and saved.get('planetId')==home
        and type(saved_tick)is int and saved_tick>=arrived
        and journey.get('phase')=='completed' and journey.get('homePlanetId')==home
        and journey.get('completedSaveGameTick')==saved_tick
        and journey.get('completedSaveActionId')==saved.get('actionId')
        and journey.get('completedSaveSessionId')==session
        and handoff.get('callerStopped') is True and handoff.get('noActiveGameAction') is True
        and handoff.get('gameProcessRetained') is True)


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
    if arc/(len(samples)-1)>1+1e-6:return False
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
        'read':{'tool'},'dump':{'queries'},'build-object':{'itemId','positions'},'build-resource':{'itemId','nodeId'},
        'build-stack':{'itemId','anchor'},
        'build-belt':{'source','ends','maximumNewBelts'},'build-belt-between':{'source','destination','maximumNewBelts'},'build-free-belt':{'candidates','maximumNewBelts'},'build-belt-to-device':{'starts','destination','maximumNewBelts'},
        'build-sorter':{'source','destination','filterItemId'},'configure':{'entity'},
        'wait-buffer':{'entity','itemId','minimumCount','maximumSeconds'},'wait-stack-device':{'entity','expected','maximumSeconds'},'wait-player-still':{'maximumSeconds'},'prove-network':{'entities','networkId'},'save-close':set(),'handoff-caller':set(),
        'observe-sail-conversion':{'entity','count','orbitId','maximumSeconds','baselinePath','baselineSha256'},
        'observe-piler-aggregation':{'piler','input','output','itemId','maximumItems','maximumSeconds'},
        'observe-receiver-power':{'entity','starId','networkId','gameTicks','maximumSampleGapGameTicks','pollSeconds','maximumSeconds'},
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
        if kind=='build-resource' and any(type(step[key])is not int or step[key]<=0 for key in ('itemId','nodeId')):
            raise ValueError('immutable_resource_build_identity_invalid')
        if kind=='build-belt-between' and (any(not (type(step[key]) is int and step[key]>0 or isinstance(step[key],str) and bool(step[key]))
                for key in ('source','destination')) or step['source']==step['destination']
                or type(step['maximumNewBelts']) is not int or step['maximumNewBelts']<=0):
            raise ValueError('immutable_belt_endpoints_invalid')
        if kind=='build-belt-to-device' and 'source' in step:
            raise ValueError('native_bound_belt_to_device_unsupported')
        if kind=='observe-receiver-power':
            entity=step['entity']
            if (not (type(entity) is int and entity > 0 or isinstance(entity,str) and bool(entity))
                    or any(type(step[key]) is not int or step[key] <= 0
                    for key in ('starId','networkId','gameTicks','maximumSampleGapGameTicks'))
                    or step['maximumSampleGapGameTicks'] > step['gameTicks']
                    or type(step['pollSeconds']) not in (int,float) or not .25 <= step['pollSeconds'] <= 30
                    or type(step['maximumSeconds']) not in (int,float)
                    or not 0 < step['maximumSeconds'] < float('inf')):
                raise ValueError('finite_receiver_observation_declaration_required')
        if kind=='wait-stack-device':
            expected=step['expected'];seconds=step['maximumSeconds']
            if (not isinstance(expected,Mapping) or not 1<=len(expected)<=16
                    or any(not isinstance(key,str) or not 1<=len(key)<=64 or type(value)not in(int,bool,str)
                           for key,value in expected.items())
                    or type(seconds)not in(int,float) or not 0<seconds<=900):
                raise ValueError('bounded_stack_device_observation_required')
        if kind=='wait-player-still':
            seconds=step['maximumSeconds'];interval=step.get('pollSeconds',.5);energy=step.get('minimumCoreEnergy',0)
            if (type(seconds) not in (int,float) or not 0<seconds<=7200
                    or type(interval) not in (int,float) or not .25<=interval<=30
                    or type(energy) not in (int,float) or not 0<=energy<float('inf')):
                raise ValueError('bounded_player_observation_required')
        if kind=='observe-piler-aggregation' and (type(step['maximumItems'])is not int or not 2<=step['maximumItems']<=64
                or type(step['itemId'])is not int or step['itemId']<=0
                or type(step['maximumSeconds'])not in(int,float) or not 0<step['maximumSeconds']<=1800):
            raise ValueError('bounded_piler_observation_required')
        if 'modelIndex' in step and (type(step['modelIndex']) is not int or step['modelIndex'] <= 0):
            raise ValueError('immutable_native_model_invalid')
        if 'freshStaleMaximumSeconds' in step:
            seconds=step['freshStaleMaximumSeconds']
            if kind not in ('operation','prepare-only') or type(seconds) not in(int,float) or not 0<=seconds<=60:
                raise ValueError('finite_fresh_stale_allowance_required')
        if 'expectedWindPowerTopologyHash' in step:
            value=step['expectedWindPowerTopologyHash']
            if (kind!='operation' or step.get('prepareTool')!='spherewright_prepare_dismantle'
                    or not isinstance(value,str) or len(value)!=71 or not value.startswith('sha256:')
                    or any(ch not in '0123456789abcdefABCDEF' for ch in value[7:])):
                raise ValueError('wind_impact_binding_invalid')
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
        if kind == 'build-belt-between':
            call('spherewright_prepare_build',dict(buildingItemId=2001,expectedPlayerStateHash='schema-placeholder',
                sourceObjectId=1,expectedSourceStateHash='schema-placeholder',destinationObjectId=2,
                expectedDestinationStateHash='schema-placeholder',beltPathMode=step.get('beltPathMode','native_grid')))
        elif kind == 'build-stack':
            arguments = dict(buildingItemId=step['itemId'], expectedPlayerStateHash='schema-placeholder',
                stackOnObjectId=1, expectedStackStateHash='schema-placeholder')
            if 'modelIndex' in step:
                arguments['preferredModelIndex'] = step['modelIndex']
            call('spherewright_prepare_build', arguments)
        elif kind == 'build-object' and 'modelIndex' in step:
            call('spherewright_prepare_build', dict(buildingItemId=step['itemId'],
                expectedPlayerStateHash='schema-placeholder', preferredModelIndex=step['modelIndex']))
        elif kind=='read':call(step['tool'],step.get('arguments',{}))
        elif kind=='observe-receiver-power':
            call('spherewright_get_session_state',{})
            call('spherewright_inspect_factory_entity',dict(objectId=1))
        elif kind=='dump':
            for query in step['queries']:call(query['tool'],query.get('arguments',{}))
        elif kind in ('operation','prepare-only'):
            for query in step.get('reads',[]):call(query['tool'],query.get('arguments',{}))
            call(step['prepareTool'],step['arguments'])

