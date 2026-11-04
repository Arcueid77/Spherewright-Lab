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
        'build-belt':{'source','ends','maximumNewBelts'},'build-free-belt':{'candidates','maximumNewBelts'},'build-belt-to-device':{'starts','destination','maximumNewBelts'},
        'build-sorter':{'source','destination','filterItemId'},'configure':{'entity'},
        'wait-buffer':{'entity','itemId','minimumCount','maximumSeconds'},'wait-player-still':{'maximumSeconds'},'prove-network':{'entities','networkId'},'save-close':set(),'handoff-caller':set(),
        'observe-sail-conversion':{'entity','count','orbitId','maximumSeconds','baselinePath','baselineSha256'},
        'observe-rocket-arrival':{'entity','layerId','nodeId','maximumSeconds','baselinePath','baselineSha256'}}
    for step in steps:
        kind=step.get('kind')
        if kind not in required or not ({'kind','role'}|required[kind])<=set(step):
            raise ValueError('immutable_plan_shape_invalid:'+str(kind))
        if kind=='dump' and any(not {'name','tool'}<=set(q) for q in step['queries']):
            raise ValueError('immutable_dump_query_shape_invalid')


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
        if kind=='read':call(step['tool'],step.get('arguments',{}))
        elif kind=='dump':
            for query in step['queries']:call(query['tool'],query.get('arguments',{}))
        elif kind in ('operation','prepare-only'):
            for query in step.get('reads',[]):call(query['tool'],query.get('arguments',{}))
            call(step['prepareTool'],step['arguments'])

