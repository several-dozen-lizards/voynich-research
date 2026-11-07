"""Portable Temurin8 JDK in this experiment only; verify API SHA256 before extraction."""
from pathlib import Path
import hashlib, json, urllib.request, zipfile

ROOT = Path(__file__).resolve().parent

def get(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()

def main():
    runtime = ROOT/'RUNTIME'
    runtime.mkdir(exist_ok=True)
    receipt = runtime/'MANIFEST.json'
    if receipt.exists():
        print(receipt.read_text()); return
    url = 'https://api.adoptium.net/v3/assets/latest/8/hotspot?architecture=x64&image_type=jdk&os=windows&vendor=eclipse'
    failures = []
    try:
        asset = json.loads(get(url))[0]
        package = asset['binary']['package']
        release = asset['release_name']
    except Exception as error:
        failures.append(dict(url=url, error=str(error)))
        url = 'https://api.github.com/repos/adoptium/temurin8-binaries/releases/latest'
        asset = json.loads(get(url))
        binary = next(a for a in asset['assets'] if a['name'].startswith('OpenJDK8U-jdk_x64_windows_hotspot_') and a['name'].endswith('.zip'))
        checksum = next(a for a in asset['assets'] if a['name'] == binary['name']+'.sha256.txt')
        package = dict(link=binary['browser_download_url'], checksum=get(checksum['browser_download_url']).decode().split()[0])
        release = asset['tag_name']
    archive = runtime/'temurin8.zip'
    request = urllib.request.Request(package['link'], headers={'User-Agent':'Voynich-sandbox/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response, archive.open('wb') as stream:
        size = 0
        while True:
            chunk = response.read(1024*1024)
            if not chunk: break
            stream.write(chunk)
            size += len(chunk)
            if size % (8*1024*1024) == 0: print(f'downloaded {size//(1024*1024)} MiB', flush=True)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != package['checksum']:
        raise RuntimeError('JDK checksum mismatch')
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            resolved = (runtime/item.filename).resolve()
            if not resolved.is_relative_to(runtime.resolve()):
                raise ValueError('unsafe zip member')
        z.extractall(runtime)
    java = next(runtime.glob('*/bin/java.exe'))
    javac = java.with_name('javac.exe')
    record = dict(api=url, release=release, download=package['link'], archive_sha256=digest, failed_attempts=failures,
                  java=str(java), javac=str(javac), portable=True, system_settings_changed=False)
    receipt.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record))

if __name__ == '__main__': main()
