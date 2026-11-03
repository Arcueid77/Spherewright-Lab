"""Interpret public DTO variants without inventing missing evidence."""

def is_read_tool(name):
    return name.startswith(('spherewright_get_','spherewright_inspect_','spherewright_list_')) or name=='spherewright_preview_voyager_route'

def consumer_network(entity):
    if entity.get('componentKind') == 'power-node':
        return None  # not applicable: membership needs complete power topology
    return entity.get('powerNetworkId')


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
            and plan.get('additionalVoyagerGameTicks')==0 and config['additionalVoyagerGameTicks']==0)
    return plan.get('remotePrimaryRecoveryAuthorizationUsed') is True and plan.get('completedSavedLandingAdmissionUsed') is True


def powered_consumers_share_network(entities, network_id):
    consumers=[e for e in entities if e.get('componentKind') != 'power-node']
    return bool(consumers) and all(consumer_network(e)==network_id for e in consumers)


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
        'operation':{'prepareTool','arguments'},'adopt-paid-build':{'buildId','expectedObjects','itemId'},
        'read':{'tool'},'dump':{'queries'},'build-object':{'itemId','positions'},
        'build-belt':{'source','ends','maximumNewBelts'},'build-free-belt':{'candidates','maximumNewBelts'},
        'build-sorter':{'source','destination','filterItemId'},'configure':{'entity'},
        'wait-buffer':{'entity','itemId','minimumCount','maximumSeconds'},'wait-player-still':{'maximumSeconds'},'prove-network':{'entities','networkId'},'save-close':set(),'handoff-caller':set()}
    for step in steps:
        kind=step.get('kind')
        if kind not in required or not ({'kind','role'}|required[kind])<=set(step):
            raise ValueError('immutable_plan_shape_invalid:'+str(kind))
        if kind=='dump' and any(not {'name','tool'}<=set(q) for q in step['queries']):
            raise ValueError('immutable_dump_query_shape_invalid')


