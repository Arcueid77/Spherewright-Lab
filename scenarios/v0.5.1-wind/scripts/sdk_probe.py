"""Qualify the installed wind acceptance interface while the game is stopped."""
from pathlib import Path
import sys

voyager = Path(__file__).resolve().parents[2] / 'v0.5-voyager' / 'scripts'
sys.path[:0] = [str(voyager / 'live'), str(voyager)]
from evidence import need, put, read, sha
from mcp_client import Client
from runtime import Runtime


def main():
    config_path, config_sha, output = sys.argv[1:]
    runtime = Runtime(config_path, config_sha)
    runtime.stopped()
    runtime.cohort()
    runtime.verify_revision_stamps()
    executable = runtime.mcp_executable()
    output = Path(output)
    output.mkdir(exist_ok=False)
    client = Client(str(executable), output / 'client', maximum=32, seconds=60)
    proof = None
    try:
        _, tools, _, _ = client.initialize()
        schemas = {tool['name']: tool['inputSchema'] for tool in tools}
        need(len(tools) == 74, 'installed_wind_tool_count_changed')
        wind = schemas['spherewright_prepare_dismantle']['properties'].get('previewOnly') or {}
        need(wind.get('type') == 'boolean' and wind.get('default') is False,
             'installed_wind_preview_schema_missing')
        context = {'sessionId': 'synthetic-offline-session', 'planetId': 104}
        state_hash = 'sha256:' + 'a' * 64
        cases = [
            ('spherewright_list_factory_entities', {'itemId': 2203, 'limit': 100}),
            ('spherewright_get_power_summary', {}),
            ('spherewright_get_player_state', {}),
            ('spherewright_get_progression_state', {}),
            ('spherewright_inspect_factory_entity', {'objectId': 31}),
            ('spherewright_get_action_result', {'actionId': '11111111-1111-4111-8111-111111111111'}),
            ('spherewright_prepare_resume_owned_game', {'resumeToken': 'synthetic-offline-token', 'recoveryMode': 'default'}),
            ('spherewright_prepare_transfer', {'direction': 'storage-to-player', 'storageEntityId': 114,
                'itemId': 1109, 'count': 1, 'expectedPlayerStateHash': state_hash, 'expectedStorageStateHash': state_hash}),
            ('spherewright_prepare_dismantle', {'objectId': 31, 'previewOnly': True,
                'expectedEndpointStateHash': state_hash, 'expectedPlayerStateHash': state_hash}),
            ('spherewright_prepare_dismantle', {'objectId': 31, 'previewOnly': False,
                'expectedEndpointStateHash': state_hash, 'expectedPlayerStateHash': state_hash}),
            ('spherewright_prepare_build', {'buildingItemId': 2203, 'preferredPositionX': 0.0,
                'preferredPositionY': 200.0, 'preferredPositionZ': 0.0, 'expectedPlayerStateHash': state_hash}),
            ('spherewright_prepare_save', {'expectedRevision': 1}),
            ('spherewright_prepare_return_to_main_menu', {'expectedRevision': 1}),
        ]
        checked = []
        for name, supplied in cases:
            schema = schemas[name]
            arguments = {key: value for key, value in context.items() if key in schema['properties']}
            arguments.update(supplied)
            need(set(schema.get('required', [])) <= set(arguments) <= set(schema['properties']),
                 'installed_wind_sdk_argument_contract_mismatch:' + name)
            result, _ = client.call(name, arguments)
            code = (result.get('error') or {}).get('code')
            need(code in ('BRIDGE_UNAVAILABLE', 'BRIDGE_NOT_READY'),
                 'installed_wind_sdk_arguments_not_admitted:' + name + ':' + str(code))
            checked.append({'tool': name, 'previewOnly': supplied.get('previewOnly'), 'argumentsAdmitted': True})
        for name in ('spherewright_commit_dismantle', 'spherewright_commit_build',
                     'spherewright_commit_transfer', 'spherewright_commit_save',
                     'spherewright_commit_return_to_main_menu', 'spherewright_commit_resume_owned_game'):
            schema = schemas[name]
            need(set(schema.get('required', [])) <= {'sessionId', 'planetId', 'planToken', 'idempotencyKey'},
                 'installed_wind_commit_schema_changed:' + name)
        proof = {'passed': True, 'sourceSha': runtime.config['sourceSha'], 'executableSha256': sha(executable),
                 'toolCount': len(tools), 'cases': checked, 'gameLaunches': 0, 'gameCommits': 0}
    except Exception as error:
        put(output / 'failure.private.json', {'error': str(error), 'gameLaunches': 0, 'gameCommits': 0})
        raise
    finally:
        closed = client.close()
        put(output / 'client-close.private.json', closed)
    need(closed.get('normalEof') is True and closed.get('processExitCode') == 0
         and closed.get('readerThreadsStopped') is True, 'installed_wind_sdk_client_not_closed')
    put(output / 'result.private.json', proof)
    print('Installed wind SDK admitted all bounded offline cases.')


if __name__ == '__main__':
    main()
