"""Read-only cold-install verification using the current full backup, never a historic floor."""
from pathlib import Path
import sys
from evidence import read,sha,need
from runtime import Runtime

def main():
    target=read(sys.argv[1]);runtime=Runtime(target['configPath'],target['configSha256'])
    c=runtime.config;runtime.stopped();runtime.verify_backup()
    need(target['scope']=='same_owned_native_cold_installation','installation_scope_changed')
    need(read(c['labSourceLock'])['spherewright']['sourceSha']==target['sourceSha'],'selected_source_changed')
    for key in ('dspRoot','pluginDestination','mcpDestination'):need(Path(target[key]).resolve()==Path(c[key]).resolve(),'registered_target_changed')
    need(sha(target['cohortIndexPath'])==target['cohortIndexSha256'],'qualified_cohort_changed')
    need(sha(Path(c['dspRoot'])/'DSPGAME_Data/Managed/Assembly-CSharp.dll')==c['nativeAssemblySha256'],'native_version_changed')
    runtime.stopped();print('Current exact cold-install prerequisites verified.')

if __name__=='__main__':main()
