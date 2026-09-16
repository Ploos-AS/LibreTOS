#!/usr/bin/env python3
"""Run M6.4 deterministic Falcon030 enhanced-interface qualification."""
from __future__ import annotations
import hashlib, json, os, re, shutil, signal, subprocess, sys
from pathlib import Path
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
 hd=OUT/'hd'; auto=hd/'AUTO'; auto.mkdir(parents=True,exist_ok=True); probe=auto/'M6FALE.PRG'; result=hd/'M6FALE.TXT'; log=OUT/'hatari.log'; trace=OUT/'hatari-trace.log'
 result.unlink(missing_ok=True); (hd/'EMUDESK.INF').unlink(missing_ok=True); trace.unlink(missing_ok=True)
 # Keep the diagnostic executable on the baseline 68000 ISA. As with M6.3,
 # this avoids the MiNT libc 68020 startup guard while the guest probe itself
 # qualifies Falcon capabilities through runtime cookies.
 cp=subprocess.run(['m68k-atari-mint-gcc','-m68000','-O2','-s',f'-DPROFILE_NAME="{profile["id"]}"','-DRESULT_FILE="C:\\\\M6FALE.TXT"','-o',str(probe),str(SOURCE)],cwd=ROOT)
 if cp.returncode:return fail(f'guest probe compile exit {cp.returncode}')
 run_vbls=max(int(q['minimum_vbls']),5000)
 effective={'profile_id':profile['id'],'machine':'falcon','cpu_level':3,'cpu_clock_mhz':16,'st_ram_mib':4,'addressing_bits':32,'mmu':True,'sound_hz':44100,'run_vbls':run_vbls,'guest_program':'C:\\AUTO\\M6FALE.PRG','guest_probe_isa':'68000','result_file':'C:\\M6FALE.TXT','launch':'gemdos-auto-with-gemdos-trace','trace':'gemdos','startup_margin':'5000-vbl-minimum','qualified':['VIDEL identification','Falcon sound capability discovery'],'observed':['FPU cookie'],'excluded':['DSP execution semantics','IDE read/write semantics','NVRAM persistence','external audio fidelity']}
 (OUT/'PROFILE.json').write_text(json.dumps(profile,indent=2,sort_keys=True)+'\n'); (OUT/'ROM.sha256').write_text(f'{sha256(ROM)}  {ROM.name}\n'); (OUT/'PROBE.sha256').write_text(f'{sha256(probe)}  {probe.name}\n'); (OUT/'HATARI_PROFILE.json').write_text(json.dumps(effective,indent=2,sort_keys=True)+'\n')
 cmd=['hatari','--tos',str(ROM),'--machine','falcon','--memsize','4','--cpulevel','3','--cpuclock','16','--addr24','no','--mmu','on','--compatible',yn(bool(q['compatible_mode'])),'--fast-boot',yn(bool(q['fast_boot'])),'--sound','44100','--confirm-quit','no','--benchmark','--run-vbls',str(run_vbls),'--harddrive',str(hd),'--protect-hd','off','--gemdos-case','upper','--trace','gemdos','--trace-file',str(trace),'--log-file',str(log)]
 command=cmd if not shutil.which('xvfb-run') else ['xvfb-run','-a',*cmd]; rc=bounded(command)
 if rc is None:return fail(f'Hatari timeout after {TIMEOUT}s')
 if rc:return fail(f'Hatari exit {rc}')
 text=log.read_text(errors='replace') if log.exists() else ''
 if FATAL.search(text):return fail('fatal TOS/ROM marker in Hatari log')
 if not result.is_file():return fail('guest result missing; inspect hatari-trace.log for GEMDOS boot/AUTO activity')
 f=fields_text(result.read_bytes())
 if f.get('schema')!='1' or f.get('profile')!=profile['id'] or f.get('status')!='PASS':return fail(f'guest verdict {f.get("status","missing")} stage={f.get("stage","unknown")}')
 try:vdo=int(f['vdo'],0); snd=int(f['snd'],0); fpu=int(f['fpu'],0)
 except (ValueError,KeyError) as e:return fail('invalid guest field: '+str(e))
 if ((vdo>>16)&0xffff)!=3:return fail(f'_VDO is not Falcon VIDEL: 0x{vdo:08x}')
 if snd<0 or (snd&7)==0:return fail(f'_SND lacks Falcon sound capabilities: 0x{snd:08x}')
 normalized='\n'.join(f'{k}={f[k]}' for k in sorted(f))+'\n'; (OUT/'GUEST_RESULT.txt').write_text(normalized)
 summary={'schema':1,'milestone':'M6.4','status':'PASS','profile':profile['id'],'vdo':f'0x{vdo:08x}','snd':f'0x{snd:08x}','fpu':f'0x{fpu:08x}','scope':effective}; (OUT/'RESULT.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); (OUT/'RESULT.txt').write_text(f'M6.4 Falcon030 enhanced qualification: PASS\nprofile_id={profile["id"]}\nvdo=0x{vdo:08x}\nsnd=0x{snd:08x}\nfpu=0x{fpu:08x}\n'); print('M6.4 Falcon030 enhanced qualification: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
