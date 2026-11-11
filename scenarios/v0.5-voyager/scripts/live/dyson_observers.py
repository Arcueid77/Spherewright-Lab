"""Finite, identity-bound samples of actual ray-receiver electricity."""
import time
from evidence import need


def observe_receiver_power(adapter, step):
    entity_id = adapter.object_id(step['entity'])
    samples = []
    first_tick = None
    last_tick = None
    generator_id = None
    largest_gap = 0
    passed = False
    deadline = min(time.monotonic() + step['maximumSeconds'], adapter.c.deadline - 60)
    try:
        while time.monotonic() < deadline:
            session = adapter.state()
            entity = adapter.entity(entity_id)
            samples.append(entity)
            remaining_wall = deadline - time.monotonic()
            need(remaining_wall >= 0, 'finite_receiver_observation_expired')
            receiver = entity.get('rayReceiver') or {}
            tick = receiver.get('capturedAtGameTick')
            component = receiver.get('generatorComponentId')
            need(entity.get('sessionId') == adapter.ctx['sessionId']
                 and entity.get('planetId') == adapter.ctx['planetId']
                 and entity.get('objectId') == entity_id and entity.get('itemId') == 2208
                 and receiver.get('nativeBindingVerified') is True
                 and receiver.get('planetId') == adapter.ctx['planetId']
                 and receiver.get('starId') == step['starId']
                 and receiver.get('entityId') == entity_id and receiver.get('itemId') == 2208
                 and receiver.get('networkId') == step['networkId']
                 and type(component) is int and component > 0,
                 'receiver_native_identity_unproved')
            need(type(tick) is int and tick == entity.get('capturedAtGameTick')
                 and tick >= session['gameTick'], 'receiver_current_native_cut_unproved')
            need(receiver.get('mode') == 'electricity' and receiver.get('productItemId') == 0
                 and type(receiver.get('generatedEnergyPerTick')) is int
                 and receiver['generatedEnergyPerTick'] > 0,
                 'receiver_sample_not_electricity_output')
            if first_tick is None:
                first_tick = tick
                generator_id = component
            else:
                need(component == generator_id, 'receiver_generator_changed')
                gap = tick - last_tick
                need(0 <= gap <= step['maximumSampleGapGameTicks'],
                     'receiver_sample_coverage_lost')
                largest_gap = max(largest_gap, gap)
            last_tick = tick
            if tick - first_tick >= step['gameTicks']:
                passed = True
                break
            time.sleep(min(step['pollSeconds'], remaining_wall))
        need(passed, 'finite_receiver_observation_expired')
    finally:
        # Keep every cut, including a zero-output or invalid final sample.
        adapter.runtime.put(step['role'] + '-samples.private.json', dict(
            passed=passed, declaration=dict(step), firstGameTick=first_tick,
            lastGameTick=last_tick, samples=samples))
    proof = dict(
        passed=True, sessionId=adapter.ctx['sessionId'], planetId=adapter.ctx['planetId'],
        entityId=entity_id, generatorComponentId=generator_id,
        networkId=step['networkId'], starId=step['starId'],
        firstGameTick=first_tick, declaredEndGameTick=first_tick + step['gameTicks'],
        lastGameTick=last_tick, sampleCount=len(samples),
        largestSampleGapGameTicks=largest_gap,
        minimumSampledPowerWatts=min(
            sample['rayReceiver']['generatedEnergyPerTick'] for sample in samples) * 60,
        gameActionsSubmitted=0)
    adapter.runtime.put(step['role'] + '-proof.private.json', proof)
    return proof
