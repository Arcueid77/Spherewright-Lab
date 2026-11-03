"""Interpret public DTO variants without inventing missing evidence."""

def consumer_network(entity):
    if entity.get('componentKind') == 'power-node':
        return None  # not applicable: membership needs complete power topology
    return entity.get('powerNetworkId')


def powered_consumers_share_network(entities, network_id):
    consumers=[e for e in entities if e.get('componentKind') != 'power-node']
    return bool(consumers) and all(consumer_network(e)==network_id for e in consumers)


