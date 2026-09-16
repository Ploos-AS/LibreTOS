#!/usr/bin/env python3
"""Run M6.4 deterministic Falcon030 enhanced-interface qualification."""
from __future__ import annotations
import hashlib, json, os, re, shutil, signal, struct, subprocess, sys
from pathlib import Path
from make_auto_floppy import build_auto_floppy
ROOT=Path(__file__).resolve().parents[1]
PROFILE=ROOT/'config/m6-falcon030-68030.json'
ROM=ROOT/'build/m6/falcon030/LibreTOS-Falcon030-68030-512k-us.img'
SOURCE=ROOT/'tests/m6/falcon030_enhanced_probe.c'
OUT=ROOT/'build/m6/falcon030-enhanced'
TIMEOUT=int(os.environ.get('HATARI_TIMEOUT_SECONDS','60'))
FATAL=re.compile(r'^FATAL\s*:|cannot load.*tos|invalid.*tos|cannot load.*rom|invalid.*rom',re.I|re.M)
def sha256(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def yn(v): return 'yes' if v else 'no'
def fail(m):
 OUT.mkdir(parents=True,exist_ok=True); (OUT/'RESULT.txt').write_text(f'M6.4 Falcon030 enhanced qualification: FAIL\nreason={m}\n'); print(f'M6.4 Falcon030 enhanced qualification: FAIL ({m})',file=sys.stderr); return 1
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
 root=(reserved+fats*fat_sectors)*bps; data_sector=reserved+fats*fat_sectors+((root_entries*32+bps-1)//bps); base,dot,ext=name.upper().partition('.'); wanted=base.encode().ljust(8)+ext.encode().ljust(3)
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
 probe=OUT/'M6FALE.PRG'; floppy=OUT/'m6fale-auto.st'; log=OUT/'hatari.log'
 # Keep the diagnostic executable on the baseline 68000 ISA.  As with the
 # M6.3 probe, a -m68020-60 MiNT binary can terminate in libc's CPU startup
 # guard before main() under this EmuTOS/Falcon qualification profile.  The
 # enhanced probe qualifies Falcon capabilities through cookies at runtime.
 cp=subprocess.run(['m68k-atari-mint-gcc','-m68000','-O2','-s',f'-DPROFILE_NAME="{profile["id"]}"','-DRESULT_FILE="A:\\\\M6FALE.TXT"','-o',str(probe),str(SOURCE)],cwd=ROOT)
 if cp.returncode:return fail(f'guest probe compile exit {cp.returncode}')
 build_auto_floppy(floppy,'M6FALE.PRG',probe.read_bytes())
 run_vbls=max(int(q['minimum_vbls']),5000)
 effective={'profile_id':profile['id'],'machine':'falcon','cpu_level':3,'cpu_clock_mhz':16,'st_ram_mib':4,'addressing_bits':32,'mmu':True,'sound_hz':44100,'run_vbls':run_vbls,'guest_program':'A:\\AUTO\\M6FALE.PRG','guest_probe_isa':'68000','result_file':'A:\\M6FALE.TXT','launch':'floppy-plus-explicit-hatari-auto','floppy_write_protection':'off','startup_margin':'5000-vbl-minimum','qualified':['VIDEL identification','Falcon sound capability discovery'],'observed':['FPU cookie'],'excluded':['DSP execution semantics','IDE read/write semantics','NVRAM persistence','external audio fidelity']}
 (OUT/'PROFILE.json').write_text(json.dumps(profile,indent=2,sort_keys=True)+'\n'); (OUT/'ROM.sha256').write_text(f'{sha256(ROM)}  {ROM.name}\n'); (OUT/'PROBE.sha256').write_text(f'{sha256(probe)}  {probe.name}\n'); (OUT/'HATARI_PROFILE.json').write_text(json.dumps(effective,indent=2,sort_keys=True)+'\n')
 cmd=['hatari','--tos',str(ROM),'--machine','falcon','--memsize','4','--cpulevel','3','--cpuclock','16','--addr24','no','--mmu','on','--compatible',yn(bool(q['compatible_mode'])),'--fast-boot',yn(bool(q['fast_boot'])),'--sound','44100','--confirm-quit','no','--benchmark','--run-vbls',str(run_vbls),'--disk-a',str(floppy),'--protect-floppy','off','--auto','A:\\AUTO\\M6FALE.PRG','--log-file',str(log)]
 command=cmd if not shutil.which('xvfb-run') else ['xvfb-run','-a',*cmd]; rc=bounded(command)
 if rc is None:return fail(f'Hatari timeout after {TIMEOUT}s')
 if rc:return fail(f'Hatari exit {rc}')
 text=log.read_text(errors='replace') if log.exists() else ''
 if FATAL.search(text):return fail('fatal TOS/ROM marker in Hatari log')
 raw=extract_root_file(floppy,'M6FALE.TXT')
 if raw is None:return fail('guest result missing')
 f=fields_text(raw)
 if f.get('schema')!='1' or f.get('profile')!=profile['id'] or f.get('status')!='PASS':return fail(f'guest verdict {f.get("status","missing")} stage={f.get("stage","unknown")}')
 try:vdo=int(f['vdo'],0); snd=int(f['snd'],0); fpu=int(f['fpu'],0)
 except (ValueError,KeyError) as e:return fail('invalid guest field: '+str(e))
 if ((vdo>>16)&0xffff)!=3:return fail(f'_VDO is not Falcon VIDEL: 0x{vdo:08x}')
 if snd<0 or (snd&7)==0:return fail(f'_SND lacks Falcon sound capabilities: 0x{snd:08x}')
 normalized='\n'.join(f'{k}={f[k]}' for k in sorted(f))+'\n'; (OUT/'GUEST_RESULT.txt').write_text(normalized)
 summary={'schema':1,'milestone':'M6.4','status':'PASS','profile':profile['id'],'vdo':f'0x{vdo:08x}','snd':f'0x{snd:08x}','fpu':f'0x{fpu:08x}','scope':effective}; (OUT/'RESULT.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); (OUT/'RESULT.txt').write_text(f'M6.4 Falcon030 enhanced qualification: PASS\nprofile_id={profile["id"]}\nvdo=0x{vdo:08x}\nsnd=0x{snd:08x}\nfpu=0x{fpu:08x}\n'); print('M6.4 Falcon030 enhanced qualification: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
