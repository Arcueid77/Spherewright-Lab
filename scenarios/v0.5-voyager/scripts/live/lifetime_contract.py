"""Read-only OS job evidence; application jobs need not contain each caller."""


def terminating_groups(snapshot):
    return [job for job in snapshot['queriedJobs']
            if job['killOnClose'] and (
                job['memberships'].get('caller') is True
                or any(member is True for name, member in job['memberships'].items()
                       if name.startswith('codex-')))]


def qualifies(snapshot):
    groups = terminating_groups(snapshot)
    owners = {job['ownerPid'] for job in groups}
    ancestry = snapshot['callerAncestry']
    indices = [ancestry.index(owner) for owner in owners if owner in ancestry]
    if not indices or len(groups) < 3:
        return False
    if not {8192, 10240, 15360}.issubset({job['limitFlags'] for job in groups}):
        return False
    caller_owners = set(ancestry[:max(indices) + 1]) | owners
    if any(query['ownerPid'] in caller_owners for query in snapshot['refusedQueries']):
        return False
    return all(job['memberships'].get('game') is False
               and job['memberships'].get('steam') is False for job in groups)
