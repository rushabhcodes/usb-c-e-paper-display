#!/usr/bin/env python3
"""Build the UF2 with a project-local Arduino-Pico 6.4.0 installation; never flash."""
import argparse
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FQBN=("rp2040:rp2040:generic_rp2350:flash=2097152_0,freq=150,usbstack=picosdk,"
      "arch=arm,variantchip=RP2350B,opt=Small")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--install',action='store_true',help='Download pinned core/toolchain into .toolchains')
    args=p.parse_args()
    cli=shutil.which('arduino-cli')
    if not cli:raise SystemExit('Install arduino-cli and put it on PATH')
    env=ROOT/'.toolchains/arduino'
    for name in ['data','downloads','user']:(env/name).mkdir(parents=True,exist_ok=True)
    config=env/'arduino-cli.yaml'
    # JSON is valid YAML and preserves paths with spaces.
    config.write_text(json.dumps({'board_manager':{'additional_urls':[
      'https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json']},
      'directories':{n:str(env/n) for n in ['data','downloads','user']}},indent=2))
    command=[cli,'--config-file',str(config)]
    if args.install:
        subprocess.run(command+['core','update-index'],check=True)
        subprocess.run(command+['core','install','rp2040:rp2040@6.4.0'],check=True)
    installed=json.loads(subprocess.check_output(command+['core','list','--format','json']))
    versions=[x.get('installed_version') for x in installed.get('platforms',[]) if x['id']=='rp2040:rp2040']
    if versions!=['6.4.0']:
        raise SystemExit('Expected isolated Arduino-Pico 6.4.0; run build.py --install')
    vendor=ROOT/'firmware/usb_epaper/src/vendor'
    lock=json.loads((ROOT/'firmware/vendor-lock.json').read_text())
    for name,sha in lock['vendored_sha256'].items():
        if hashlib.sha256((vendor/name).read_bytes()).hexdigest()!=sha:
            raise SystemExit(f'Vendored driver checksum mismatch: {name}')
    release=ROOT/'firmware/releases/rp2354b'
    release.mkdir(parents=True,exist_ok=True)
    subprocess.run(command+['compile','--fqbn',FQBN,'--output-dir',str(release),
      '--build-path',str(ROOT/'.toolchains/firmware-build-rp2354b'),str(ROOT/'firmware/usb_epaper')],check=True)
    # Preserve the tool's originals and provide a clearly named flash image.
    shutil.copyfile(release/'usb_epaper.ino.uf2',release/'USB-Epaper-RevC-RP2354B-v1.1.0.uf2')
    uf2=(release/'usb_epaper.ino.uf2').read_bytes()
    from audit_uf2 import audit
    audit(release)
    manifest={'core':'rp2040:rp2040@6.4.0','fqbn':FQBN,'mcu':'RP2354B','physical_board_tested':False,
      'usb':{'vid':'2e8a','pid':'f00f','configuration_max_power_ma':250},
      'source_files_sha256':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [ROOT/'firmware/usb_epaper/usb_epaper.ino',ROOT/'firmware/usb_epaper/src/protocol.h',ROOT/'firmware/vendor-lock.json']},
      'artifacts':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in release.iterdir()
                   if x.is_file() and x.suffix in ['.uf2','.elf','.bin']}}
    (release/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
