"""Complete collection fields before MCP SDK binding; Native still validates the cut.

Some SDK object binders replace omitted nested collection initializers with null.
Send both collections explicitly, even when one side of the cut is empty.
补齐显式集合，避免SDK把省略的嵌套集合绑定成null；不替代原生几何校验。
"""


def complete_geometry_arrays(request):
    if not isinstance(request, dict):
        raise ValueError('geometry must be an explicit object')
    result = dict(request)
    for field in ('objectIds', 'terrainPoints'):
        value = result.setdefault(field, [])
        if not isinstance(value, list):
            raise ValueError(f'{field} must be an explicit array')
        result[field] = list(value)
    ids = result['objectIds']
    if any(type(value) is not int for value in ids) or len(set(ids)) != len(ids):
        raise ValueError('objectIds must contain distinct integer identities')
    if len(ids) > 256 or len(result['terrainPoints']) > 64:
        raise ValueError('geometry selection exceeds the published collection bounds')
    if not result['objectIds'] and not result['terrainPoints'] and not result.get('nativeBeltSegments'):
        raise ValueError('an empty geometry cut has no observation target')
    return result
