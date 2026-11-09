"""Exact saved-space roles; opening a save never grants healthy automation."""
import math


def saved_identity_token(config, session):
    if session.get('restartResumeAvailable') is True and session.get('restartResumeToken'):
        return session['restartResumeToken']
    if config.get('recoveryProfile') == 'exact-paused-space' and config.get('recoveryMode') == 'open_saved_last_exit':
        return config.get('consumedSavedIdentityToken') or None
    if (config.get('recoveryProfile') == 'fresh-remote-file-access'
        and config.get('recoveryMode') == 'authorize_remote_primary_recovery'
        and config.get('sourceRole') == 'lastExit'
        and type(config.get('sourceTick')) is int and config['sourceTick'] >= 0
        and config.get('isolatedInterruptedOwnedResumes')):
        token = config.get('consumedSavedIdentityToken')
        return token if isinstance(token, str) and 0 < len(token) <= 256 else None
    return None


def exact_last_exit_echo(config, plan):
    return (config.get('recoveryMode') == 'open_saved_last_exit'
        and plan.get('recoveryMode') == 'open_saved_last_exit'
        and plan.get('candidateGameTick') == plan.get('minimumGameTick') == config['sourceTick']
        and plan.get('sourceGameVersion') == plan.get('targetGameVersion') == config['expectedNativeVersion']
        and plan.get('exactEmbeddedIdentityVerified') is True
        and all(plan.get(k) is True for k in ('opensExactLastExitOnly', 'opensSavedWorldOnly',
            'previousAutomationRemainsStopped', 'newChargingProhibited', 'userConfirmationRequired'))
        and plan.get('commitAllowedNow') is False
        and [b.get('code') for b in plan.get('commitBlockers', [])] == ['USER_CONFIRMATION_REQUIRED']
        and plan.get('additionalVoyagerGameTicks') == 0)


def paused_space_source(config, session, player, open_action):
    transit = player.get('spaceTransit') or {}
    speed = transit.get('speed')
    blockers = session.get('writeBlockers') or []
    return (session.get('gameLoaded') is True and session.get('ownedBySpherewright') is True
        and session.get('writesAllowed') is False and session.get('writeHealth') == 'quarantined'
        and session.get('writeQuarantineActionId') == open_action
        and len(blockers) == 1 and blockers[0].get('code') == 'WRITE_SUBSYSTEM_QUARANTINED'
        and session.get('localPlanetId') == (config['planetId'] or None) and session.get('gameTick') == config['sourceTick']
        and player.get('planetId') == config['planetId'] and player.get('isOnPlanet') is (config['planetId']>0)
        and player.get('movementState') == 'Sail' and transit.get('nativePaused') is True
        and transit.get('frozenSavedPoseVerified') is True
        and transit.get('warping') is False and transit.get('warpCommand') is False
        and transit.get('warpState') == 0 and type(speed) in (int, float)
        and math.isfinite(speed) and speed >= 0)


def exact_ui_supply(result, count):
    r = result.get('mechaWarperSupplyReadback') or {}
    keys = ('packageCountBefore', 'packageCountAfter', 'chamberCountBefore', 'chamberCountAfter',
            'packageIncBefore', 'packageIncAfter', 'chamberIncBefore', 'chamberIncAfter')
    return (type(count) is int and 1 <= count <= 19
        and result.get('terminal') is True and result.get('succeeded') is True
        and result.get('actionKind') == 'supply_mecha_warpers'
        and r.get('evidenceScope') == 'synchronous_native_ui_partial_warper_chamber_topup'
        and r.get('spaceMomentumPreserved') is True
        and isinstance(r.get('frozenSpacePoseBefore'), str) and bool(r['frozenSpacePoseBefore'])
        and r.get('frozenSpacePoseAfter') == r['frozenSpacePoseBefore']
        and all(type(r.get(k)) is int and r[k] >= 0 for k in keys)
        and r.get('requestedCount') == r.get('actualStored') == count
        and r['packageCountBefore'] - r['packageCountAfter'] == count
        and r['chamberCountAfter'] - r['chamberCountBefore'] == count
        and r['chamberCountAfter'] <= 20
        and type(r.get('autoReplenishWarperBefore')) is bool
        and r.get('autoReplenishWarperAfter') is r['autoReplenishWarperBefore']
        and sum(r[k] for k in ('packageIncBefore', 'chamberIncBefore'))
            == sum(r[k] for k in ('packageIncAfter', 'chamberIncAfter'))
        and r.get('readbackComplete') is True and r.get('conservationVerified') is True)
