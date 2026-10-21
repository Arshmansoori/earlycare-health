import zipfile
import urllib.request
import json
import base64
import time
from pathlib import Path

ROOT = Path.cwd()
OUT_DIR = ROOT / 'frontend' / 'out'
pkg_name = f'earlycare_googleauth_{int(time.time())}.zip'
ZIP_PATH = ROOT / pkg_name

print(f'1. Packaging {pkg_name}...')
with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
    for fp in OUT_DIR.rglob('*'):
        if fp.is_file():
            zf.write(fp, fp.relative_to(OUT_DIR).as_posix())

ZIP_BYTES = ZIP_PATH.read_bytes()
print(f'Zip size: {len(ZIP_BYTES)} bytes')

token = 'n9MdctTNHEPGgiiHxAVtAPZEG6lvPLnOpr7gapiVe082e288'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

print('2. Getting upload URL...')
data = json.dumps({'username': 'u658435137', 'domain': 'zyventools.com'}).encode()
req = urllib.request.Request('https://developers.hostinger.com/api/hosting/v1/files/upload-urls', data=data, headers=headers, method='POST')
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())

tus_url = res.get('url').rstrip('/') + f'/{pkg_name}'
auth_key = res.get('auth_key')
rest_auth_key = res.get('rest_auth_key')
meta_filename = base64.b64encode(pkg_name.encode()).decode()

print('3. Initiating TUS...')
tus_headers = {
    'Tus-Resumable': '1.0.0',
    'Upload-Length': str(len(ZIP_BYTES)),
    'Upload-Metadata': f'filename {meta_filename}',
    'X-Auth': auth_key,
    'X-Auth-Rest': rest_auth_key,
    'User-Agent': 'Mozilla/5.0'
}
req_init = urllib.request.Request(tus_url, data=b'', headers=tus_headers, method='POST')
with urllib.request.urlopen(req_init) as resp_init:
    loc = resp_init.headers.get('Location')
    loc_url = ('https://srv1835-files.hstgr.io/rest' + loc) if (loc and not loc.startswith('http')) else loc

    print('4. PATCHing archive...')
    patch_headers = {
        'Tus-Resumable': '1.0.0',
        'Upload-Offset': '0',
        'Content-Type': 'application/offset+octet-stream',
        'Content-Length': str(len(ZIP_BYTES)),
        'X-Auth': auth_key,
        'X-Auth-Rest': rest_auth_key,
        'User-Agent': 'Mozilla/5.0'
    }
    req_patch = urllib.request.Request(loc_url, data=ZIP_BYTES, headers=patch_headers, method='PATCH')
    with urllib.request.urlopen(req_patch) as resp_patch:
        print(f'Upload status: {resp_patch.status}')

print('5. Deploying static archive to Hostinger...')
deploy_url = 'https://developers.hostinger.com/api/hosting/v1/accounts/u658435137/websites/zyventools.com/deploy'
deploy_data = json.dumps({'archive_path': pkg_name}).encode()
deploy_req = urllib.request.Request(deploy_url, data=deploy_data, headers=headers, method='POST')
with urllib.request.urlopen(deploy_req) as deploy_resp:
    print(f'Deploy status: {deploy_resp.status}')

print('6. Clearing cache...')
purge_url = 'https://developers.hostinger.com/api/hosting/v1/accounts/u658435137/websites/zyventools.com/cache/clear'
purge_req = urllib.request.Request(purge_url, headers=headers, method='DELETE')
try:
    with urllib.request.urlopen(purge_req) as purge_resp:
        print(f'Cache status: {purge_resp.status}')
except Exception as e:
    print('Cache purge:', e)

ZIP_PATH.unlink(missing_ok=True)
print('SUCCESS: Hostinger deployment completed!')
