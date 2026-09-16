#!/usr/bin/env python3
"""Run M6.3 guest-side platform qualification for canonical Atari Falcon030."""
from __future__ import annotations
import hashlib, json, os, re, shutil, signal, subprocess, sys
from pathlib import Path
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
def fields(p):
 d={}
 for line in p.read_text(encoding='ascii',errors='replace').replace('\r\n','\n').splitlines():
  if '=' in line:
   k,v=line.split('=',1); d[k.strip()]=v.strip()
 return d
def main():
 for c in ('m68k-atari-mint-gcc','hatari'):
  if not shutil.which(c): return fail(c+' missing')
 for p in (PROFILE,ROM,SOURCE):
  if not p.is_file(): return fail('missing '+str(p))
 profile=json.loads(PROFILE.read_text()); q=profile['qualification']
 hd=OUT/'hd'; hd.mkdir(parents=True,exist_ok=True); probe=hd/'M6FAL.TOS'; result=hd/'M6FAL.TXT'; result.unlink(missing_ok=True); log=OUT/'hatari.log'
 cp=subprocess.run(['m68k-atari-mint-gcc','-m68020-60','-O2','-s',f'-DPROFILE_NAME="{profile["id"]}"','-DRESULT_FILE="C:\\\\M6FAL.TXT"','-o',str(probe),str(SOURCE)],cwd=ROOT)
 if cp.returncode:return fail(f'guest probe compile exit {cp.returncode}')
 run_vbls=max(int(q['minimum_vbls']),5000)
 guest_program='C:\\M6FAL.TOS'
 effective={'profile_id':profile['id'],'machine':'falcon','cpu_level':3,'cpu_clock_mhz':16,'st_ram_mib':4,'addressing_bits':32,'mmu':True,'run_vbls':run_vbls,'guest_program':guest_program,'result_file':'C:\\M6FAL.TXT','launch':'hatari-auto-root','startup_margin':'5000-vbl-minimum'}
 OUT.mkdir(parents=True,exist_ok=True); (OUT/'PROFILE.json').write_text(json.dumps(profile,indent=2,sort_keys=True)+'\n'); (OUT/'ROM.sha256').write_text(f'{sha256(ROM)}  {ROM.name}\n'); (OUT/'PROBE.sha256').write_text(f'{sha256(probe)}  {probe.name}\n'); (OUT/'HATARI_PROFILE.json').write_text(json.dumps(effective,indent=2,sort_keys=True)+'\n')
 cmd=['hatari','--tos',str(ROM),'--machine','falcon','--memsize','4','--cpulevel','3','--cpuclock','16','--addr24','no','--mmu','on','--compatible',yn(bool(q['compatible_mode'])),'--fast-boot',yn(bool(q['fast_boot'])),'--sound','off','--confirm-quit','no','--benchmark','--run-vbls',str(run_vbls),'--harddrive',str(hd),'--protect-hd','off','--gemdos-case','upper','--auto',guest_program,'--log-file',str(log)]
 command=cmd if not shutil.which('xvfb-run') else ['xvfb-run','-a',*cmd]; rc=bounded(command)
 if rc is None:return fail(f'Hatari timeout after {TIMEOUT}s')
 if rc:return fail(f'Hatari exit {rc}')
 text=log.read_text(errors='replace') if log.exists() else ''
 if FATAL.search(text):return fail('fatal marker in Hatari log')
 if not result.is_file():return fail('guest result missing')
 f=fields(result)
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
