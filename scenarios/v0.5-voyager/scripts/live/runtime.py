"""One immutable private run config; no imports from historical execution packets."""
from pathlib import Path
from types import MappingProxyType
import datetime as dt, json, shutil, subprocess
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
        paths.update(Path(p).resolve() for p in c['protectedExtraFiles'])
        for root in map(Path, c['durableRoots']):
            for pattern in ('owned-world-resume*.json','owned-world-reauthorization-attempt-*.json',
                            'flight-checkpoint.json','voyager-journey.json','voyager-return-source-*.json'):
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

    def native_proofs(self):
        c=self.config; identity=Path(c['savePaths']['primary']).stem
        return {role:native_file_proof(p,identity) for role,p in c['savePaths'].items()}

    def verify_backup(self):
        c=self.config; m=read(c['backupManifest'])
        need(m['complete'] and m['verified'] and len(m['nativeSaveRoles'])==4,'complete_backup_missing')
        need(self.protected_paths()=={Path(r['originalPath']).resolve() for r in m['rows']},'protected_set_changed')
        for r in m['rows']:
            p=Path(r['originalPath']);need(p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
                and sha(r['backupPath'])==r['sha256'],'protected_or_backup_bytes_changed')
        proofs=self.native_proofs();need(proofs==m['latest'],'native_progress_changed')
        need(proofs['lastExit']['gameTick']==c['sourceTick'] and proofs['primary']['gameTick']<=c['sourceTick'],
             'latest_no_loss_source_not_covered')
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
