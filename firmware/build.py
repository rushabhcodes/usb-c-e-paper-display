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
FQBN=("rp2040:rp2040:generic:flash=2097152_0,freq=125,usbstack=picosdk,"
      "boot2=boot2_generic_03h_4_padded_checksum,opt=Small")

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
    release=ROOT/'firmware/releases'
    release.mkdir(exist_ok=True)
    subprocess.run(command+['compile','--fqbn',FQBN,'--output-dir',str(release),
      '--build-path',str(ROOT/'.toolchains/firmware-build'),str(ROOT/'firmware/usb_epaper')],check=True)
    # Preserve the tool's originals and provide a clearly named flash image.
    shutil.copyfile(release/'usb_epaper.ino.uf2',release/'USB-Epaper-RevA-v1.0.0.uf2')
    uf2=(release/'usb_epaper.ino.uf2').read_bytes()
    assert len(uf2)%512==0
    count=len(uf2)//512
    blocks={}
    for i in range(count):
        b=uf2[i*512:(i+1)*512]
        m0,m1,flags,addr,size,idx,total,family=struct.unpack('<8I',b[:32])
        assert (m0,m1)==(0x0a324655,0x9e5d5157) and struct.unpack('<I',b[-4:])[0]==0x0ab16f30
        assert flags&0x2000 and family==0xe48bff56 and total==count and size==256 and idx not in blocks
        assert 0x10000000<=addr<0x10200000
        blocks[idx]=(addr,b[32:32+size])
    assert set(blocks)==set(range(count))
    assert all(blocks[i][0]==0x10000000+i*256 for i in range(count))
    binary=(release/'usb_epaper.ino.bin').read_bytes()
    assert b''.join(blocks[i][1] for i in range(count))[:len(binary)]==binary
    audit={'result':'PASS','uf2_family':'RP2040 / 0xe48bff56','blocks':count,
           'payload_size':256,'flash_base':'0x10000000','uf2_matches_bin':True,'physical_board_tested':False}
    (release/'uf2-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    manifest={'core':'rp2040:rp2040@6.4.0','fqbn':FQBN,'physical_board_tested':False,
      'artifacts':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in release.iterdir()
                   if x.is_file() and x.suffix in ['.uf2','.elf','.bin']}}
    (release/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
