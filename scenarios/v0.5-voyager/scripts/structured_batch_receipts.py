"""Pure bounded remote-batch request/receipt checks. No Client, IO or claims.

The future single writer supplies fresh public DTOs and a reserved parent.
Native geometry, energy, deadlines and permission remain Plugin decisions.
"""
import datetime as dt
import math

SUPPORTED = {2301, 2104, 2201, 2203, 2205, 2001, 2011}
OPTIONS = {'preferredPositionX', 'preferredPositionY', 'preferredPositionZ', 'preferredYaw',
           'resourceNodeId', 'expectedResourceStateHash', 'sourceObjectId', 'expectedSourceStateHash',
           'destinationObjectId', 'expectedDestinationStateHash', 'pathEndX', 'pathEndY', 'pathEndZ',
           'pathLength', 'initialSorterFilterItemId', 'beltPathMode'}


def need(ok, code):
    if not ok:
        raise ValueError(code)


def exact_actor(context, player):
    need(isinstance(context.get('journeyId'), str) and bool(context['journeyId'])
         and player.get('sessionId') == context.get('sessionId')
         and player.get('planetId') == context.get('planetId')
         and isinstance(player.get('stateHash'), str) and bool(player['stateHash']),
         'fresh_original_journey_actor_required')


def prepare_build_args(context, player, item, **options):
    exact_actor(context, player)
    need(item in SUPPORTED and not(set(options) - OPTIONS), 'unsupported_item_or_request_field')
    need(all(isinstance(options.get(k), (int, float)) and not isinstance(options[k], bool)
             and math.isfinite(options[k]) for k in ('preferredPositionX', 'preferredPositionY', 'preferredPositionZ')),
         'one_fresh_explicit_pose_required')
    need(options.get('beltPathMode', 'native_grid') == 'native_grid', 'remote_baseline_has_no_elevated_or_cover_mode')
    if item == 2301:
        need(type(options.get('resourceNodeId')) is int and options['resourceNodeId'] > 0
             and bool(options.get('expectedResourceStateHash')), 'fresh_observed_miner_node_required')
    if item == 2001:
        need(all(type(options.get(k)) is int and options[k] > 0 for k in ('sourceObjectId', 'destinationObjectId'))
             and bool(options.get('expectedSourceStateHash')) and bool(options.get('expectedDestinationStateHash')),
             'exact_real_miner_station_endpoints_required')
    return dict(sessionId=context['sessionId'], planetId=context['planetId'], buildingItemId=item,
                expectedPlayerStateHash=player['stateHash'], stateHashVersion=1, **options)


def maximum_new_objects(item):
    return 12 if item == 2001 else 8


def progress_limit(progress):
    site = progress.get('site') or {}; objects = site.get('objects') or []
    need(objects and len(objects) == len(progress.get('objects') or [])
         and len({row.get('itemId') for row in objects}) == 1,
         'exact_site_item_and_progress_count_required')
    item = objects[0].get('itemId')
    need(item in SUPPORTED and site.get('nativeBlueprintObjectLimit') == maximum_new_objects(item),
         'exact_native_item_capacity_required')
    return maximum_new_objects(item)


def prepared_batch(plan, item, now_utc, approved_maximum_new_objects=8):
    need(plan.get('prepared') is True and plan.get('commitAllowedNow') is True
         and plan.get('actionKind') == 'build' and not plan.get('commitBlockers')
         and bool(plan.get('planToken')) and bool(plan.get('expectedStateHash'))
         and plan.get('stateHashVersion') == 1, 'fresh_native_build_capability_required')
    expiry = dt.datetime.fromisoformat(plan['expiresAtUtc'].replace('Z', '+00:00'))
    need(expiry.tzinfo is not None and now_utc.tzinfo is not None and expiry > now_utc,
         'expired_plan_cannot_be_submitted')
    build = plan.get('blueprintBuild') or {}; site = build.get('site') or {}
    objects = site.get('objects') or []; count = len(objects)
    need(type(approved_maximum_new_objects) is int and 1 <= approved_maximum_new_objects <= maximum_new_objects(item),
         'finite_operator_material_limit_required')
    need(bool(build.get('buildId')) and 1 <= count <= approved_maximum_new_objects
         and site.get('nativeBlueprintObjectLimit') == maximum_new_objects(item) and site.get('nativeCheckPerformed') is True
         and site.get('nativeCheckPassed') is True
         and all(row.get('itemId') == item and item in SUPPORTED for row in objects),
         'same_item_native_objects_within_approved_material_limit_required')
    budget = plan.get('itemBudget') or []
    need(len(budget) == 1 and budget[0].get('itemId') == item and budget[0].get('count') == count,
         'whole_batch_new_material_budget_not_exact')
    return dict(buildId=build['buildId'], itemId=item, count=count, planToken=plan['planToken'])


def observe_original(action, original, progress=None):
    need(all(action.get(k) == original.get(k) for k in ('actionId', 'idempotencyKey', 'sessionId', 'planetId', 'actionKind')),
         'only_original_action_may_be_observed')
    if action.get('state') == 'outcome_unknown':
        return dict(state='original_reconciliation_only', mayCreate=False, complete=False)
    if action.get('terminal') is not True:
        return dict(state='poll_same_original_action', mayCreate=False, complete=False)
    if action.get('succeeded') is not True or action.get('state') != 'completed':
        return dict(state='original_reconciliation_only', mayCreate=False, complete=False)
    control = action.get('constructionControl') or {}
    need(action.get('blueprintBuildId') == original.get('buildId')
         and control.get('phase') == 'completed_idle' and control.get('physicalIdleVerified') is True
         and control.get('exactBindingVerified') is True,
         'disabled_dispatch_or_terminal_flag_is_not_native_idle')
    progress = progress or {}; rows = progress.get('objects') or []
    need(progress.get('buildId') == original['buildId'] and progress.get('phase') == 'completed'
         and progress.get('freshWorldReconciled') is True and progress.get('persistenceHealthy') is True
         and bool(progress.get('stateHash')) and 1 <= len(rows) <= progress_limit(progress)
         and all(row.get('state') == 'completed' and type(row.get('entityId')) is int and row['entityId'] > 0 for row in rows)
         and len({row['entityId'] for row in rows}) == len(rows),
         'exact_fresh_completed_build_progress_required')
    pairs = {(row.get('inventoryBefore'), row.get('inventoryAfter')) for row in rows}
    need(control.get('wholeBatchDebitSharedByObjectReceipts') is True and len(pairs) == 1,
         'one_shared_native_batch_debit_required')
    before, after = next(iter(pairs))
    need(type(before) is int and type(after) is int and before - after == len(rows),
         'shared_debit_must_equal_new_object_count')
    return dict(state='exact_completed_native_idle', mayCreate=False, complete=True,
                materialDebit=before - after, completedCount=len(rows))


def resume_args(context, player, progress):
    exact_actor(context, player)
    control = progress.get('constructionControl') or {}; rows = progress.get('objects') or []
    need(bool(progress.get('buildId')) and bool(progress.get('stateHash'))
         and progress.get('freshWorldReconciled') is True and progress.get('persistenceHealthy') is True
         and progress.get('phase') != 'outcome_unknown' and control.get('physicalIdleVerified') is True
         and 1 <= len(rows) <= progress_limit(progress) and any(row.get('state') == 'pending_construction' for row in rows)
         and all(row.get('state') in ('completed', 'pending_construction') for row in rows),
         'fresh_exact_idle_pending_build_required')
    # The Plugin retains the original work clock. No new code/site/deadline exists here.
    return dict(sessionId=context['sessionId'], planetId=context['planetId'], resumeBuildId=progress['buildId'],
                expectedStateHash=progress['stateHash'], expectedPlayerStateHash=player['stateHash'],
                maximumObjectsToSubmit=len(rows), stateHashVersion=1)
