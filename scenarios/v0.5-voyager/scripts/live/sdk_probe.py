"""Exercise the real packaged MCP SDK while the game is stopped."""
from pathlib import Path
import sys,datetime as dt
from evidence import need,put
from mcp_client import Client

def main():
    executable,output=sys.argv[1:];out=Path(output);out.mkdir(exist_ok=False)
    c=Client(executable,out/'client',maximum=32,seconds=60)
    try:
        _,tools,_,_=c.initialize();schemas={t['name']:t['inputSchema'] for t in tools}
        ctx=dict(sessionId='synthetic-offline-session',planetId=402);h='sha256:'+'a'*64
        cases=[
            ('spherewright_prepare_build',dict(ctx,buildingItemId=2101,expectedPlayerStateHash=h,preferredPositionX=1.,preferredPositionY=199.,preferredPositionZ=1.)),
            ('spherewright_prepare_build',dict(ctx,buildingItemId=2001,expectedPlayerStateHash=h,sourceObjectId=18,expectedSourceStateHash=h,pathEndX=1.,pathEndY=199.,pathEndZ=1.)),
            ('spherewright_prepare_build',dict(ctx,buildingItemId=2011,expectedPlayerStateHash=h,sourceObjectId=18,destinationObjectId=21,expectedSourceStateHash=h,expectedDestinationStateHash=h,initialSorterFilterItemId=1011)),
            ('spherewright_prepare_configure_building',dict(ctx,entityId=21,recipeId=32,mode='production',expectedFactoryStateHash=h)),
            ('spherewright_prepare_configure_building',dict(ctx,entityId=25,recipeId=0,mode='sorter-filter',filterItemId=1301,expectedFactoryStateHash=h)),
            ('spherewright_prepare_resume_owned_game',dict(resumeToken='synthetic-offline-token',recoveryMode='authorize_remote_primary_recovery',minimumRecoveryGameTick=100,expectedRecoveryGameTick=100,
                recoveryDeadlineUtc=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=3)).isoformat(),recoveryScope='continue_original_finite_task',maximumChargeGameTicks=18000,maximumChargeWallSeconds=300,
                additionalVoyagerGameTicks=432000,surfaceRecoveryTargetX=1.,surfaceRecoveryTargetY=199.,surfaceRecoveryTargetZ=1.))]
        proof=[]
        for tool,args in cases:
            schema=schemas[tool];need(set(schema.get('required',[]))<=set(args),'sdk_required_field_missing')
            need(set(args)<=set(schema['properties']),'sdk_unknown_field')
            r,bad=c.call(tool,args);code=(r.get('error') or {}).get('code')
            need(code in ('BRIDGE_UNAVAILABLE','BRIDGE_NOT_READY'),'sdk_arguments_not_admitted:'+tool+':'+str(code))
            proof.append(dict(tool=tool,argumentsAdmitted=True,bridgeUnavailableAsExpected=True))
        put(out/'result.private.json',dict(passed=True,cases=proof,gameLaunches=0,gameCommits=0))
    finally:put(out/'client-close.private.json',c.close())

if __name__=='__main__':main()
