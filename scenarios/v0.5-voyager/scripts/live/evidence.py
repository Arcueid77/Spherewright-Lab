"""Append-only private evidence and read-only exact Native file proof."""
from pathlib import Path
import pathlib,datetime as dt,hashlib,importlib.util,json,os,struct
from collections.abc import Mapping
NATIVE='0.10.35.29151'
def need(ok,why):
    if not ok: raise RuntimeError(why)
require=need
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def actual_prior_rpc_count(prior,closed):
    """Carry nested caller counts from their original attachment receipt."""
    base=closed.get('priorRpcCount',0)
    source=Path(prior)/'run-config-reference.private.json'
    if 'priorRpcCount' not in closed and source.exists():
        reference=read(source)
        need(sha(reference['path'])==reference['sha256'].upper(),'original_caller_config_changed')
        config=read(reference['path']);base=config.get('priorRpcCount',0)
        need(closed['maximumRequests']==config['maximumRpc']-base,'original_caller_allowance_mismatch')
    proof=Path(prior)/'attached-existing-session.private.json'
    if proof.exists():
        attached=read(proof);observed=attached['priorRpcCount']
        need(attached['passed'] and attached['noStartupClockReset'] and observed>=base,
             'attached_prior_rpc_accounting_unproved')
        base=observed
    count=closed['requestCount']
    need(type(base)is int and base>=0 and type(count)is int and count>=0,'actual_rpc_counts_invalid')
    return base+count
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest().upper()
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:
        json.dump(json_value(x),f,ensure_ascii=False,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
def json_value(x):
    if isinstance(x,Mapping):return {k:json_value(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [json_value(v) for v in x]
    return x
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def native_file_proof(path, expected_identity):
    """Bounded ordinary file read; mirrors the audited v7/v13 identity prefix,
    then independently hashes the complete file and the canonical lease proof.
    No account value or save identity is returned or printed.
    """
    path = pathlib.Path(path)
    before = path.stat()
    require(52 <= before.st_size <= 64 * 1024 * 1024, 'Primary file outside bounded native prefix size.')
    raw = path.read_bytes()
    after = path.stat()
    require(before.st_size == after.st_size == len(raw) and before.st_mtime_ns == after.st_mtime_ns,
            'Native file changed during full-file verification.')
    at = 0

    def read(count):
        nonlocal at
        require(0 <= count <= len(raw) - at, 'Truncated native identity prefix.')
        value = raw[at:at + count]
        at += count
        return value

    def number(fmt):
        return struct.unpack(fmt, read(struct.calcsize(fmt)))[0]

    def string_bytes(maximum):
        length = 0
        for index in range(5):
            byte = number('<B')
            require(index != 4 or byte & 0xf0 == 0, 'Invalid native string bound.')
            length |= (byte & 0x7f) << (index * 7)
            if byte & 0x80 == 0:
                require((index == 0 or byte != 0) and length <= maximum, 'Noncanonical native string bound.')
                return read(length)
        raise RuntimeError('Invalid native string prefix.')

    def skip_account():
        require(number('<i') == 0, 'Unsupported native account prefix.')
        read(12)
        string_bytes(4096)

    require(read(6) == b'VFSAVE' and number('<q') == len(raw) and number('<i') == 7, 'Unsupported native save header.')
    sandbox, peaceful = number('<B'), number('<B')
    require(sandbox == 0 and peaceful == 1, 'Original peaceful ordinary world required.')
    version = '.'.join(str(number('<i')) for _ in range(4))
    tick, saved_ticks = number('<q'), number('<q')
    require(version == NATIVE and tick >= 0 and saved_ticks >= 0, 'Exact same-Native file required.')
    screenshot = number('<i')
    require(0 <= screenshot <= 16 * 1024 * 1024, 'Native screenshot prefix exceeds bound.')
    read(screenshot)
    skip_account()
    read(8)
    require(number('<i') == 13 and number('<i') == 23, 'Unsupported native data/patch tuple.')
    skip_account()
    require(string_bytes(1024).decode('utf-8', errors='strict') == expected_identity,
            'Primary embedded identity differs from original owned world.')
    require(number('<i') == 10, 'Unsupported native descriptor prefix.')
    saved = dt.datetime(1, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(microseconds=saved_ticks // 10)
    written = dt.datetime.fromtimestamp(after.st_mtime_ns // 1000000000, dt.timezone.utc)
    # DateTimeOffset's invariant default form used by CanonicalStateHash.Append.
    def invariant_stamp(value):
        return value.strftime('%m/%d/%Y %H:%M:%S') + ' +00:00'
    content_hash = hashlib.sha256(raw).hexdigest().upper()
    fields = ['action-v1', 'verified-owned-last-exit-v1', str(len(raw)), str(tick), invariant_stamp(saved),
              version, 'True', 'False', 'True', str(at), invariant_stamp(written), content_hash]
    canonical = ''.join(str(len(value)) + ':' + value + '|' for value in fields)
    return dict(gameTick=tick, bytes=len(raw), sha256=content_hash,
                fingerprint='sha256:' + hashlib.sha256(canonical.encode('utf-8')).hexdigest())
