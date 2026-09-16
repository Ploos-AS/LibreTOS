#!/usr/bin/env python3
"""Run M6.3 guest-side platform qualification for canonical Atari Falcon030."""
from __future__ import annotations
import hashlib, json, os, re, shutil, signal, struct, subprocess, sys
from pathlib import Path
from make_auto_floppy import build_auto_floppy
ROOT=Path(__file__).resolve().parents[1]
PROFILE=ROOT/'config/m6-falcon030-68030.json'
ROM=ROOT/'build/m6/falcon030/LibreTOS-Falcon030-68030-512k-us.img'
SOURCE=ROOT/'tests/m6/falcon030_platform_probe.c'
OUT=ROOT/'build/m6/falcon030-platform'
TIMEOUT=int(os.environ.get('HATARI_TIMEOUT_SECONDS','60'))
FATAL=re.compile(r'(?:^|\n)FATAL\s*:|cannot load.*tos|invalid.*tos',re.I)
def sha256(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def yn(v): return 'yes' if v else 'no'
def fail(m):
 OUT.mkdir(parents=True,exist_ok=True); (OUT/'RESULT.txt').write_text(f'M6.3 Falcon030 platform qualification: FAIL\nreason={m}\n'); print(f'M6.3 Falcon030 platform qualification: FAIL ({m})',file=sys.stderr); return 1
def bounded(cmd):
 p=subprocess.Popen(cmd,cwd=ROOT,start_new_session=True)
 try:return p.wait(timeout=TIMEOUT)
 except subprocess.TimeoutExpired:
  try: os.killpg(p.pid,signal.SIGTERM); p.wait(timeout=5)
  except Exception:
   try: os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError: pass
  return None
def extract_root_file(image_path,name):
 image=image_path.read_bytes(); bps=struct.unpack_from('<H',image,11)[0]; reserved=struct.unpack_from('<H',image,14)[0]; fats=image[16]; root_entries=struct.unpack_from('<H',image,17)[0]; fat_sectors=struct.unpack_from('<H',image,22)[0]
 root=(reserved+fats*fat_sectors)*bps; data_sector=reserved+fats*fat_sectors+((root_entries*32+bps-1)//bps); wanted=name.upper().partition('.')[0].encode().ljust(8)+name.upper().partition('.')[2].encode().ljust(3)
 for off in range(root,root+root_entries*32,32):
  ent=image[off:off+32]
  if ent[0] in (0,0xe5) or ent[11]&0x18: continue
  if ent[:11]!=wanted: continue
  cluster=struct.unpack_from('<H',ent,26)[0]; size=struct.unpack_from('<I',ent,28)[0]; out=bytearray(); fat=image[reserved*bps:(reserved+fat_sectors)*bps]
  while 2<=cluster<0xff8 and len(out)<size:
   pos=(data_sector+cluster-2)*bps; out.extend(image[pos:pos+bps]); idx=cluster+cluster//2; pair=fat[idx]|(fat[idx+1]<<8); cluster=(pair>>4)&0xfff if cluster&1 else pair&0xfff
  return bytes(out[:size])
 return None
def fields_text(raw):
 d={}
 for line in raw.decode('ascii',errors='replace').replace('\r\n','\n').splitlines():
  if '=' in line:
   k,v=line.split('=',1); d[k.strip()]=v.strip()
 return d
def main():
 for c in ('m68k-atari-mint-gcc','hatari'):
  if not shutil.which(c): return fail(c+' missing')
 for p in (PROFILE,ROM,SOURCE):
  if not p.is_file(): return fail('missing '+str(p))
 profile=json.loads(PROFILE.read_text()); q=profile['qualification']; OUT.mkdir(parents=True,exist_ok=True)
 probe=OUT/'M6FAL.PRG'; floppy=OUT/'m6fal-auto.st'; log=OUT/'hatari.log'
 cp=subprocess.run(['m68k-atari-mint-gcc','-m68020-60','-O2','-s',f'-DPROFILE_NAME="{profile["id"]}"','-DRESULT_FILE="A:\\\\M6FAL.TXT"','-o',str(probe),str(SOURCE)],cwd=ROOT)
 if cp.returncode:return fail(f'guest probe compile exit {cp.returncode}')
 build_auto_floppy(floppy,'M6FAL.PRG',probe.read_bytes())
 run_vbls=max(int(q['minimum_vbls']),5000)
 effective={'profile_id':profile['id'],'machine':'falcon','cpu_level':3,'cpu_clock_mhz':16,'st_ram_mib':4,'addressing_bits':32,'mmu':True,'run_vbls':run_vbls,'guest_program':'A:\\AUTO\\M6FAL.PRG','result_file':'A:\\M6FAL.TXT','launch':'floppy-plus-explicit-hatari-auto','startup_margin':'5000-vbl-minimum'}
 (OUT/'PROFILE.json').write_text(json.dumps(profile,indent=2,sort_keys=True)+'\n'); (OUT/'ROM.sha256').write_text(f'{sha256(ROM)}  {ROM.name}\n'); (OUT/'PROBE.sha256').write_text(f'{sha256(probe)}  {probe.name}\n'); (OUT/'HATARI_PROFILE.json').write_text(json.dumps(effective,indent=2,sort_keys=True)+'\n')
 cmd=['hatari','--tos',str(ROM),'--machine','falcon','--memsize','4','--cpulevel','3','--cpuclock','16','--addr24','no','--mmu','on','--compatible',yn(bool(q['compatible_mode'])),'--fast-boot',yn(bool(q['fast_boot'])),'--sound','off','--confirm-quit','no','--benchmark','--run-vbls',str(run_vbls),'--disk-a',str(floppy),'--auto','A:\\AUTO\\M6FAL.PRG','--log-file',str(log)]
 command=cmd if not shutil.which('xvfb-run') else ['xvfb-run','-a',*cmd]; rc=bounded(command)
 if rc is None:return fail(f'Hatari timeout after {TIMEOUT}s')
 if rc:return fail(f'Hatari exit {rc}')
 text=log.read_text(errors='replace') if log.exists() else ''
 if FATAL.search(text):return fail('fatal marker in Hatari log')
 raw=extract_root_file(floppy,'M6FAL.TXT')
 if raw is None:return fail('guest result missing')
 f=fields_text(raw)
 if f.get('schema')!='1' or f.get('profile')!=profile['id'] or f.get('status')!='PASS':return fail(f'guest verdict {f.get("status","missing")} stage={f.get("stage","unknown")}')
 try:mch=int(f['mch'],0); cpu=int(f['cpu'],0); vdo=int(f['vdo'],0); phys=int(f['physbase'],0); logbase=int(f['logbase'],0)
 except (ValueError,KeyError) as e:return fail('invalid guest field: '+str(e))
 if ((mch>>16)&0xffff)!=3:return fail(f'_MCH is not Falcon family: 0x{mch:08x}')
 if cpu!=30:return fail(f'_CPU does not report 68030: {cpu}')
 if ((vdo>>16)&0xffff)!=3:return fail(f'_VDO is not Falcon video: 0x{vdo:08x}')
 if not phys or not logbase or (phys&1) or (logbase&1):return fail('invalid screen base')
 normalized='\n'.join(f'{k}={f[k]}' for k in sorted(f))+'\n'; (OUT/'GUEST_RESULT.txt').write_text(normalized)
 summary={'schema':1,'milestone':'M6.3','status':'PASS','profile':profile['id'],'mch':f'0x{mch:08x}','cpu':cpu,'vdo':f'0x{vdo:08x}','physbase':f'0x{phys:08x}','logbase':f'0x{logbase:08x}'}; (OUT/'RESULT.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); (OUT/'RESULT.txt').write_text(f'M6.3 Falcon030 platform qualification: PASS\nprofile_id={profile["id"]}\nmch=0x{mch:08x}\ncpu={cpu}\nvdo=0x{vdo:08x}\n'); print('M6.3 Falcon030 platform qualification: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
