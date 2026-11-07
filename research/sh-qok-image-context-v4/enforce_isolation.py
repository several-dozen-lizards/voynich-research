"""Freeze authorized v4.2 exception; qualify restrictive native permission profiles."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,sys,shutil
import prepare as core
import isolated_cli as cli

def freeze():
    amendment=core.R/'AMENDMENT-v4.2-effect-scale.md'
    assert core.sha(amendment)=='9f43ca33c39496d1c4a02b4743983170d40fe46457d091bca798d062ee2478d1'
    core.save('V4.2-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        authority='User in this chat: Freeze v4.2 with the timing exception explicitly recorded, lift the hold, and finish enforcing isolation so you can start the independent registration and rating.',
        active_design=['ORIGINAL-SPEC.txt','AMENDMENT-v4.1.txt','MANUAL-CORRECTION.json','AMENDMENT-v4.2-effect-scale.md'],
        hashes={n:core.sha(core.R/n) for n in ['ORIGINAL-SPEC.txt','AMENDMENT-v4.1.txt','MANUAL-CORRECTION.json','MANUAL.md','AMENDMENT-v4.2-effect-scale.md']},
        primary_scale='MH log odds ratio; H-IMG descriptive Q uses Robins-Breslow-Greenland variance; within-folio line-label permutation inference.',
        risk_difference='Secondary and descriptive; report both OR and RD without choosing whichever passes.',
        base_rate_null='Equal OR, different label base rates; gate both hypotheses on OR scale. RD demonstration only.',
        positives='H-IMG OR1 in one label versus OR2.5 in others; H-PLANT OR1.2 PL versus OR2.5 non-PL; real label base rates.',
        qok_support='Post-join abstain-only >=10 qok events per label in supported strata; never adds an eligible cell.',
        timing_exception='Separate image-context-v4 folder contains pre-amendment registration artifacts, as recorded in AMENDMENT-v4.2-RECEIVED.json. Global pre-registration timing CANNOT be certified. User explicitly authorizes proceeding with this exception retained.',
        timing_this_chat='Before this freeze: metadata inventories, packet construction, one exposed registrar refusal before input access, and no-inference prompt rendering only. Zero eligible registrations, zero rating calls, zero outcome joins or tests.',
        other_work_preserved=True,reuse_of_other_registration=False,
        hold='LIFTED by direct user instruction; no inference until isolation qualification passes.',
        v4_1='Stands; amended picture-element-only manual unchanged.',v103='PARKED; no Rosettes leave-out grids or retrospective companion authorized here.'))
    core.seal('v4_2_frozen_timing_exception_explicit_hold_lifted',['V4.2-FREEZE.json','enforce_isolation.py'])

def permissions(folder):
    mapping={':root':'deny',':minimal':'read',str(folder):'read'}
    table='{'+','.join(json.dumps(k)+'='+json.dumps(v) for k,v in mapping.items())+'}'
    return {'default_permissions':'"blind"','permissions.blind.filesystem':table,'permissions.blind.network.enabled':'false'}

def role_flags(folder):
    return cli.flags()+[part for k,v in permissions(folder).items() for part in ('-c',k+'='+v)]

def boundary_probe(backend=None):
    root=cli.BASE/'control/boundary-probe'
    allowed=root/'input';allowed.mkdir(parents=True,exist_ok=True)
    outside=root/'outside';outside.mkdir(exist_ok=True)
    (allowed/'CANARY.txt').write_text('PERMITTED-NEUTRAL-CANARY',encoding='utf-8')
    (outside/'CANARY.txt').write_text('FORBIDDEN-NEUTRAL-CANARY',encoding='utf-8')
    script=allowed/'check.ps1'
    script.write_text("param([string]$AllowedPath,[string]$DeniedPath)\n$ErrorActionPreference='Stop'\n$result=@{allowed_read=$false; outside_read_denied=$false; outside_write_denied=$false}\ntry { $value=Get-Content -LiteralPath $AllowedPath -Raw; $result.allowed_read=$value -eq 'PERMITTED-NEUTRAL-CANARY' } catch { $result.allowed_error=$_.Exception.Message }\ntry { $null=Get-Content -LiteralPath $DeniedPath -Raw; $result.outside_read_denied=$false } catch { $result.outside_read_denied=$true; $result.denied_error=$_.Exception.Message }\ntry { Set-Content -LiteralPath ($DeniedPath+'.write-test') -Value 'NEUTRAL'; $result.outside_write_denied=$false } catch { $result.outside_write_denied=$true }\n$result | ConvertTo-Json -Compress\n",encoding='utf-8')
    home=root/'empty-home';home.mkdir(exist_ok=True)
    env=dict(os.environ);env['CODEX_HOME']=str(home)
    ps=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    backend_flags=['-c','windows.sandbox='+json.dumps(backend)] if backend else []
    quote=lambda value:"'"+str(value).replace("'","''")+"'"
    inline=script.read_text(encoding='utf-8').replace('param([string]$AllowedPath,[string]$DeniedPath)',
        '$AllowedPath='+quote(allowed/'CANARY.txt')+'; $DeniedPath='+quote(outside/'CANARY.txt'))
    cmd=[str(cli.CODEX),'sandbox',*role_flags(allowed),*backend_flags,'-P','blind','-C',str(allowed),'--',str(ps),'-NoProfile','-NonInteractive','-Command',inline]
    run=subprocess.run(cmd,cwd=allowed,env=env,capture_output=True,timeout=120)
    suffix=(backend or 'default')+'-inline'
    (root/('stdout-'+suffix+'.txt')).write_bytes(run.stdout);(root/('stderr-'+suffix+'.txt')).write_bytes(run.stderr)
    try: result=json.loads(run.stdout)
    except Exception:result=None
    passed=run.returncode==0 and result and all(result.get(k) for k in ['allowed_read','outside_read_denied','outside_write_denied'])
    core.save('ISOLATION-BOUNDARY-PROBE-'+suffix+'.json',dict(status='PASS' if passed else 'FAILED',returncode=run.returncode,backend=backend,
        profile_overrides=permissions(allowed),result=result,
        stdout_file=str(root/('stdout-'+suffix+'.txt')),stderr_file=str(root/('stderr-'+suffix+'.txt')),
        note='Neutral canaries only. No project files, results, credentials or annotations are read by this test. A refused sandbox is a failed execution route, not a pass.'))
    print(json.dumps(dict(status='PASS' if passed else 'FAILED',returncode=run.returncode,result=result,stderr=run.stderr.decode('utf-8',errors='replace')[-2500:]),ensure_ascii=True))

if __name__=='__main__':{'freeze':freeze,'probe':boundary_probe,'probe-elevated':lambda:boundary_probe('elevated'),'probe-mxc':lambda:boundary_probe('mxc')}[sys.argv[1]]()
