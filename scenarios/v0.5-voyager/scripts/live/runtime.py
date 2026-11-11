"""One immutable private run config; no imports from historical execution packets."""
from pathlib import Path
from types import MappingProxyType
import datetime as dt, json, shutil, subprocess,uuid
from evidence import need, read, sha, put, native_file_proof


def freeze(x):
    if isinstance(x, dict): return MappingProxyType({k: freeze(v) for k, v in x.items()})
    if isinstance(x, list): return tuple(map(freeze, x))
    return x


class Runtime:
    def __init__(self, config_path, config_sha, output=None):
        need(sha(config_path) == config_sha.upper(), 'immutable_config_changed')
        self.config = freeze(read(config_path))
        if output is None:
            self.output=None;return
        self.output = Path(output).resolve()
        need(not self.output.exists(), 'run_output_already_exists_no_replay')
        self.output.mkdir(parents=True)
        put(self.output/'run-config-reference.private.json', dict(path=str(config_path), sha256=config_sha))

    def put(self, name, value): put(self.output/name, value)

    def stopped(self):
        r = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
            "if (@(Get-Process DSPGAME -ErrorAction SilentlyContinue).Count) {exit 11}; if (@(Get-Process Spherewright.Mcp -ErrorAction SilentlyContinue).Count) {exit 12}"],
            capture_output=True, timeout=20, creationflags=0x08000000)
        need(r.returncode == 0, 'game_or_mcp_running')

    def protected_paths(self):
        c=self.config; paths={Path(p).resolve() for p in c['savePaths'].values()}
        paths.update(self.native_paths().values())
        paths.update(Path(p).resolve() for p in c['protectedExtraFiles'])
        for root in map(Path, c['durableRoots']):
            for pattern in ('owned-world-resume*.json','owned-world-reauthorization-attempt-*.json',
                            'flight-checkpoint.json','voyager-journey.json','voyager-return-source-*.json',
                            'stopped-space-return-*.json'):
                paths.update(p.resolve() for p in root.glob(pattern))
            paths.update(p.resolve() for p in (root/'journals').glob('*.json'))
            for folder in ('foundry','overseer','governor'):
                paths.update(p.resolve() for p in (root/folder).rglob('*') if p.is_file())
        need(0<len(paths)<=8192,'protected_set_outside_bound')
        for p in paths:
            need(p.is_file() and not p.is_symlink() and not (p.stat().st_file_attributes & 0x400)
                 and 0<p.stat().st_size<=64*1024*1024,'protected_file_not_bounded_regular')
        return paths

    def cohort(self):
        c=self.config; index=read(c['cohortIndex'])
        need(index['sourceSha']==c['sourceSha'] and sha(c['cohortIndex'])==c['cohortIndexSha256'],'cohort_identity_changed')
        for role in ('plugin','mcp'):
            root=Path(c[role+'Destination']); rows=[r for r in index['files'] if r['role']==role]
            need(rows and len({r['relativePath'] for r in rows})==len(rows),'cohort_inventory_invalid')
            expected={r['relativePath'] for r in rows}
            actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
                    and not (role=='plugin' and p.relative_to(root).parts[0]=='runtime-handoff')}
            need(actual==expected,'installed_inventory_changed')
            for r in rows:
                p=root/r['relativePath'];need(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'installed_bytes_changed')
        return index

    def verify_revision_stamps(self):
        c=self.config;stamps=read(c['revisionStamps'])
        need(stamps.get('passed') is True and stamps.get('sourceSha')==c['sourceSha'],'revision_stamp_source_changed_before_launch')
        expected={'Spherewright.Bridge.Core','Spherewright.Contracts','Spherewright.Plugin'}
        rows=stamps.get('modules',[])
        need(len(rows)==3 and {row['assemblyName'] for row in rows}==expected,'revision_stamp_module_set_changed')
        for row in rows:
            need(isinstance(row.get('moduleVersionId'),str) and uuid.UUID(row['moduleVersionId']).int!=0,'revision_stamp_mvid_missing')
            need(row.get('informationalVersion')==c.get('productVersion','0.5.0')+'+'+c['sourceSha']
                 and row.get('sha256')==sha(Path(c['pluginDestination'])/(row['assemblyName']+'.dll')),
                 'revision_stamp_module_bytes_changed_before_launch')
        native=stamps.get('native',{})
        need(isinstance(native.get('moduleVersionId'),str) and uuid.UUID(native['moduleVersionId']).int!=0,'revision_stamp_native_mvid_missing')
        need(native.get('assemblyName')=='Assembly-CSharp' and native.get('sha256')==c['nativeAssemblySha256']
             and native.get('sha256')==sha(Path(c['dspRoot'])/'DSPGAME_Data/Managed/Assembly-CSharp.dll'),
             'revision_stamp_native_changed_before_launch')
        return stamps

    def mcp_executable(self):
        c=self.config
        selected=Path(c.get('mcpExecutable',str(Path(c['pluginDestination'])/'Spherewright.Mcp.exe'))).resolve()
        index=read(c['cohortIndex'])
        need(index['sourceSha']==c['sourceSha'] and sha(c['cohortIndex'])==c['cohortIndexSha256'],'mcp_cohort_source_changed')
        matches=[row for row in index['files'] if row['relativePath']=='Spherewright.Mcp.exe'
                 and (Path(c[row['role']+'Destination'])/row['relativePath']).resolve()==selected]
        need(len(matches)==1 and selected.is_file() and selected.stat().st_size==matches[0]['bytes']
             and sha(selected)==matches[0]['sha256'],'mcp_executable_not_in_qualified_layout')
        return selected

    def native_paths(self):
        c=self.config;paths={k:Path(p).resolve() for k,p in c['savePaths'].items()}
        primary=paths['primary'];identity=primary.stem;version=read(c['labSourceLock'])['native']['version']
        candidates=set()
        for root in map(Path,c['durableRoots']):
            ticket=root/'flight-checkpoint.json'
            if not ticket.exists():continue
            value=read(ticket);name=value.get('checkpointSaveName')
            need(value.get('ownedSaveName')==identity and value.get('gameVersion')==version,'current_checkpoint_identity_changed')
            need(isinstance(name,str) and name.startswith('Spherewright_PreFlight_') and Path(name).name==name
                 and not any(ch in name for ch in '/\\:'),'current_checkpoint_name_unproved')
            target=(primary.parent/(name+'.dsv')).resolve()
            need(target.parent==primary.parent and target.is_file(),'current_checkpoint_save_missing')
            candidates.add(target)
        need(len(candidates)<=1,'multiple_current_native_checkpoints')
        if candidates:paths['currentCheckpoint']=next(iter(candidates))
        return paths

    def native_proofs(self):
        c=self.config; identity=Path(c['savePaths']['primary']).stem
        return {role:native_file_proof(p,identity) for role,p in self.native_paths().items()}

    def verify_backup(self):
        c=self.config; m=read(c['backupManifest'])
        need(m['complete'] and m['verified'] and len(m['nativeSaveRoles'])==4,'complete_backup_missing')
        need(self.protected_paths()=={Path(r['originalPath']).resolve() for r in m['rows']},'protected_set_changed')
        for r in m['rows']:
            p=Path(r['originalPath']);need(p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
                and sha(r['backupPath'])==r['sha256'],'protected_or_backup_bytes_changed')
        proofs=self.native_proofs();need(proofs==m['latest'],'native_progress_changed')
        role=c.get('sourceRole','lastExit')
        need(role in ('primary','lastExit') and proofs[role]['gameTick']==c['sourceTick']
             and max(proofs[k]['gameTick'] for k in ('primary','lastExit'))==c['sourceTick'],
             'latest_no_loss_source_not_covered')
        if c.get('recoveryProfile')=='ordinary-owned-home':
            quarantined_exit=(role=='lastExit' and c['recoveryMode']=='default' and c.get('quarantinedDefaultLastExit') is True
                              and bool(c.get('isolatedPaidBeltBuilds') or c.get('quarantinedNavigationOriginals'))
                              and proofs['primary']['gameTick']<c['originalQuarantineMinimumTick']<=c['sourceTick'])
            need((role=='primary' and c['recoveryMode'] in ('default','reauthorize_expired_primary')) or quarantined_exit or (role=='lastExit' and c['recoveryMode']=='verified_newer_lastexit'
                 and proofs['primary']['gameTick']<c['sourceTick']),'ordinary_home_source_mode_mismatch')
        return m

    def backup_after_normal_close(self, name='after-normal-close-complete-backup'):
        self.stopped(); c=self.config; prior=read(c['backupManifest'])
        cache={Path(r['originalPath']).resolve():r for r in prior['rows']}
        dest=(self.output/name).resolve();dest.mkdir(exist_ok=False); rows=[]
        paths=self.protected_paths(); proofs=self.native_proofs()
        need(max(proofs[k]['gameTick'] for k in ('primary','lastExit'))>=c['sourceTick'],'progress_loss_refused')
        for i,p in enumerate(sorted(paths,key=lambda p:str(p).casefold())):
            h=sha(p);size=p.stat().st_size;old=cache.get(p)
            if old and old['bytes']==size and old['sha256']==h and sha(old['backupPath'])==h: row=dict(old)
            else:
                target=dest/f'{i:05d}.protected';shutil.copyfile(p,target)
                need(sha(target)==h and target.stat().st_size==size,'backup_copy_failed')
                row=dict(originalPath=str(p),backupPath=str(target),bytes=size,sha256=h)
            need(sha(p)==h,'protected_changed_during_backup');rows.append(row)
        need(paths==self.protected_paths() and proofs==self.native_proofs(),'backup_cut_changed')
        m=dict(complete=True,verified=True,sourceSha=c['sourceSha'],nativeSaveRoles=list(c['savePaths']),
               createdAtUtc=dt.datetime.now(dt.timezone.utc).isoformat(),latest=proofs,rows=rows)
        put(dest/'manifest.private.json',m)
        latest=max(proofs[k]['gameTick'] for k in ('primary','lastExit'))
        self.put('preservation-summary.private.json',dict(passed=True,files=len(rows),latestKnownFloor=latest,
            spentGameTicks=c['spentGameTicks']+latest-c['sourceTick'],returnReserveGameTicks=c['returnReserveGameTicks']))
        return m
