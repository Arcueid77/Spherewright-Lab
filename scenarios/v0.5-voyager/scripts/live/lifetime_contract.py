"""Complete application-owned job coverage, independent of host group counts."""
from job_lifetime_capture import application_scope,ancestry

def cleanup_groups(snapshot):
    scope=set(snapshot['scopePids']);names=['caller']+['scope-'+str(pid) for pid in snapshot['callerAncestry']]
    return [job for job in snapshot['queriedJobs'] if scope.intersection(job['ownerPids'])
            or job['killOnClose'] and any(job['memberships'].get(name) is True for name in names)]

def terminating_groups(snapshot):
    return [job for job in cleanup_groups(snapshot) if job['killOnClose']]

def qualifies(snapshot,*,expected_target_kind='game'):
    try:
        if (snapshot.get('schemaVersion')!=2 or snapshot.get('targetKind')!=expected_target_kind
            or snapshot.get('gameIdentityVerified') is not True or snapshot.get('processIdentitiesStable') is not True
            or snapshot.get('jobMetadataEnumerationComplete') is not True or snapshot.get('queryOnlyJobAccess')!=4
            or any(snapshot.get(k)!=0 for k in ('gameMemoryReads','jobAssignments','jobLimitChanges','processTerminations'))):return False
        root,scope,chain=application_scope(snapshot['processes'],snapshot['callerProcessId'])
        if root!=snapshot['scopeRootPid'] or scope!=set(snapshot['scopePids']) or chain!=snapshot['callerAncestry']:return False
        byid={p['ProcessId']:p for p in snapshot['processes']}
        if any(snapshot[k] not in byid for k in ('gameProcessId','steamProcessId','callerProcessId')):return False
        for target in ('gameProcessId','steamProcessId'):
            if scope.intersection(ancestry(snapshot['processes'],snapshot[target])):return False
        if any(type(snapshot['anyJobMembership'].get(name))is not bool for name in ('game','steam')):return False
        inventory={j['objectKey']:set(j['ownerPids']) for j in snapshot['enumeratedJobs']}
        rows={j['objectKey']:j for j in snapshot['queriedJobs']}
        unresolved={j['objectKey']:set(j['ownerPids']) for j in snapshot['unresolvedJobObjects']}
        if (len(inventory)!=len(snapshot['enumeratedJobs']) or len(rows)!=len(snapshot['queriedJobs'])
            or len(unresolved)!=len(snapshot['unresolvedJobObjects']) or set(rows)&set(unresolved)
            or set(rows)|set(unresolved)!=set(inventory)):return False
        owned={key for key,owners in inventory.items() if scope.intersection(owners)}
        if not owned or not owned.issubset(rows):return False
        if any(owners!=inventory[key] for key,owners in unresolved.items()):return False
        names=['caller']+['scope-'+str(pid) for pid in chain]
        for key,row in rows.items():
            if set(row['ownerPids'])!=inventory[key] or row['killOnClose']!=bool(row['limitFlags']&0x2000):return False
            if any(type(row['memberships'].get(name))is not bool for name in names):return False
            for target in ('game','steam'):
                if snapshot['anyJobMembership'][target] is False and row['memberships'].get(target) is True:return False
        return all(job['memberships'].get('game') is False and job['memberships'].get('steam') is False
                   for job in cleanup_groups(snapshot))
    except (KeyError,TypeError,ValueError,RuntimeError):return False
