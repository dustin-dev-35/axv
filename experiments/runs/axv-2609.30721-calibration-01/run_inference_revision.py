"""Post-review locked, independent paired calibration; never modifies defaults.

Prepare -> test/smoke -> run. Preparation writes all DGP settings, streams and
input hashes before formal output. Frozen source snapshots accompany this file.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, platform, sys, time
from datetime import datetime, timezone
from pathlib import Path
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_key] = '1'
import numpy as np
import pandas as pd
from scipy.stats import norm, t
sys.path.insert(0, str(Path(__file__).resolve().parent / 'inference_frozen_code'))
import simulation as sim
import calibration_engine as ce
import real_data_v2_inference as rdi

Z = float(norm.ppf(.975))
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def seed_for(master, condition, rep, purpose='formal_evaluation'):
    return int.from_bytes(hashlib.sha256(f'{master}\x1f{condition}\x1f{rep}\x1f{purpose}'.encode()).digest()[:16], 'big')
def bandwidths(lengths, overlap):
    lengths = np.asarray(lengths, dtype=int)
    k0 = int(np.ceil(1/(1-overlap/100))-1)
    global_k = min(int(lengths.max()-1), max(int(np.floor(4*(lengths.mean()/100)**(2/9))), 2*k0))
    local_k = np.minimum(lengths-1, np.maximum(np.floor(4*(lengths/100)**(2/9)).astype(int), 2*k0))
    return k0, global_k, local_k
def make_plan(lengths, overlap):
    lengths = np.asarray(lengths, dtype=int)
    offsets = np.r_[0, lengths.cumsum()]
    k0, kg, kl = bandwidths(lengths, overlap)
    session = np.repeat(np.arange(len(lengths)), lengths)
    pairs = []
    for h in range(1, max(kg, int(kl.max()))+1):
        left = np.flatnonzero(session[:-h] == session[h:])
        subjects = session[left]
        wg = np.full(len(left), max(0., 1-h/(kg+1)))
        wl = np.maximum(0., 1-h/(kl[subjects]+1))
        pairs.append((h,left,wg,wl))
    return dict(lengths=lengths, offsets=offsets, k0=k0, global_k=kg, local_k=kl,
                pairs=pairs, N=int(lengths.sum()), R=len(lengths))
def two_hac_variances(diff, plan):
    means = np.add.reduceat(diff, plan['offsets'][:-1])/plan['lengths']
    u = diff - np.repeat(means, plan['lengths'])
    vg = vl = float(np.dot(u,u))
    for h,left,wg,wl in plan['pairs']:
        products = u[left]*u[left+h]
        vg += 2*np.dot(wg,products)
        vl += 2*np.dot(wl,products)
    correction = plan['N']/(plan['N']-plan['R'])
    return float(vg*correction/plan['N']**2), float(vl*correction/plan['N']**2)
def evaluate(diff, plan, truth, subject_index=None):
    point = float(diff.mean())
    vg, vl = two_hac_variances(diff, plan)
    triples=[('iid_z', point, float(diff.var(ddof=1)/len(diff)),Z),
             ('original_global_bandwidth',point,vg,Z),('per_session_bandwidth',point,vl,Z)]
    if subject_index is not None:
        session_sums=np.add.reduceat(diff,plan['offsets'][:-1])
        subject_index=np.asarray(subject_index)
        ss=np.bincount(subject_index,weights=session_sums)
        sn=np.bincount(subject_index,weights=plan['lengths'])
        sd=ss/sn
        triples.append(('equal_subject_t',float(sd.mean()),float(sd.var(ddof=1)/len(sd)),float(t.ppf(.975,len(sd)-1))))
    out=[]
    for method,p,v,crit in triples:
        valid=bool(np.isfinite(v) and v>=0)
        lo=p-crit*np.sqrt(v) if valid else np.nan
        hi=p+crit*np.sqrt(v) if valid else np.nan
        out.append(dict(method=method,point=p,variance=v,ci_lower=lo,ci_upper=hi,
                        ci_width=hi-lo,reject_null=int(lo>0 or hi<0) if valid else -1,
                        coverage=int(lo<=truth<=hi) if valid else -1,valid=int(valid)))
    return out
def prepare(root, output, repetitions):
    output.mkdir(parents=True,exist_ok=True)
    path=output/'locked_config.json'
    if path.exists():
        raise RuntimeError('Configuration already exists; no overwriting of locked protocol.')
    conditions=[]
    for overlap in [0,50,75]:
        for effect in [0.,.02]:
            conditions.append(dict(id=f'balanced_ar1_o{overlap}_d{effect:.2f}',kind='balanced',regime='long_memory',overlap=overlap,effect=effect,phi=.6,
                subject_count=24, sessions_per_subject=2,window_size=64,base_nonoverlap_windows=64))
    for effect in [0.,.02]:
        conditions.append(dict(id=f'balanced_hierarchy_o75_d{effect:.2f}',kind='balanced',regime='mixed_hierarchy',overlap=75,effect=effect,phi=0.,
            subject_count=24,sessions_per_subject=2,window_size=64,base_nonoverlap_windows=64))
    manifest_path=root/'results/final_variance_diagnostics/preanalysis_manifest.json'
    original=json.loads(manifest_path.read_text(encoding='utf-8'))
    # Both empirical templates were already present before review. HARTH is a
    # contiguous-grid length stress test; it does not reconstruct purity holes.
    for dataset,seconds in [('WISDM',5),('HARTH',10)]:
        template=next(x for x in original['simulation']['length_templates'] if x['dataset']==dataset and x['window_seconds']==seconds and x['overlap_percent']==75)
        for effect in [0.,.02]:
            conditions.append(dict(id=f'{dataset.lower()}_{seconds}s_lengths_o75_d{effect:.2f}',kind='empirical_lengths',regime='long_memory',overlap=75,effect=effect,phi=.6,
                lengths=template['session_lengths'],subject_index=template['session_subject_index'],subject_count=len(template['subject_labels']),window_size=64,
                limitation='Length template only; contiguous simulated grid without empirical purity holes.'))
    inputs=[manifest_path,root/'results/final_figure3_formal_hac/preanalysis_manifest.json',root/'results/calibration_v4/run_metadata.json']
    frozen=Path(__file__).resolve().parent/'inference_frozen_code'
    sources=[Path(__file__).resolve(),*frozen.glob('*.py')]
    config=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),analysis_status='POST_REVIEW_ADDITIONAL_ANALYSIS; frozen before formal outcomes',
        repetitions=repetitions,master_seed=202609080862,smoke_master_seed=202609080863,seed_derivation='uint128 first 16 SHA256 bytes of master, condition, replication, purpose joined by U+001F',
        confidence_level=.95,model_accuracy_b=.80,model_accuracy_a='.80 + effect',rho_pair=.5,
        original_bandwidth='K=min(max(T)-1,max(floor(4*(mean(T)/100)^(2/9)),2*K0))',
        sensitivity_bandwidth='K_r=min(T_r-1,max(floor(4*(T_r/100)^(2/9)),2*K0)); Bartlett weight 1-h/(K_r+1)',
        short_sessions='Retain every session. T_r=1 gives K_r=0 and centered residual zero. If all T=1, no HAC (N<=R). No additional dropping.',
        finite_correction='N/(N-R) remains identical in both HAC variants',
        comparisons='All methods consume the identical paired A-B array per condition/replication. Same seed not shared across distinct conditions.',
        estimand='Window-weighted fixed-record for AR(1); new-subject for mixed hierarchy. IID/HAC mismatched for mixed hierarchy.',
        decision='Do not replace original default, select a new rule, or retune based on these evaluation data.',
        scope='12 conditions x M independent draws; empirical length sensitivities use frozen exact block-state Gaussian generator; 2 pp alternatives.',
        conditions=conditions,
        input_manifest=[dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=digest(p)) for p in inputs],
        code_manifest=[dict(path=p.name if p.parent!=frozen else 'inference_frozen_code/'+p.name,bytes=p.stat().st_size,sha256=digest(p)) for p in sources])
    path.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(prepared=str(path),sha256=digest(path),conditions=len(conditions),M=repetitions)),flush=True)
def draw(c,rng):
    if c['kind']=='balanced':
        scales=(dict(sigma_subject=0.,sigma_session=0.,sigma_window=np.sqrt(.75),sigma_model=.5)
                if c['regime']=='long_memory' else dict(sigma_subject=np.sqrt(.1),sigma_session=np.sqrt(.1),sigma_window=np.sqrt(.6),sigma_model=np.sqrt(.2)))
        cfg=sim.SimulationConfig(n_subjects=24,n_sessions=2,base_nonoverlap_windows=64,window_size=64,overlap=c['overlap']/100,
            accuracy_a=.8+c['effect'],accuracy_b=.8,rho_pair=.5,raw_ar_phi=c['phi'],**scales)
        prediction=sim.simulate_predictions(cfg,rng)
        return (prediction.correct_a.astype(float)-prediction.correct_b.astype(float)).ravel()
    lengths=np.asarray(c['lengths'],dtype=int)
    wa,wb=ce.paired_ar1_window_aggregates(lengths,c['overlap'],c['phi'],.5,rng)
    ma,mb=ce.paired_standard_normal((int(lengths.sum()),),.5,rng)
    a=norm.ppf(.8+c['effect'])+np.sqrt(.75)*wa+.5*ma
    b=norm.ppf(.8)+np.sqrt(.75)*wb+.5*mb
    return (a>0).astype(float)-(b>0).astype(float)
def condition_arrays(c):
    if c['kind']=='balanced':
        stride=round(64*(1-c['overlap']/100))
        count=1+(4096-64)//stride
        return np.full(48,count),np.repeat(np.arange(24),2)
    return np.asarray(c['lengths']),np.asarray(c['subject_index'])
def run_condition(task):
    config,c,output,smoke=task
    output=Path(output)
    path=output/(c['id']+'.csv')
    if path.exists():
        raise RuntimeError('Refuse to overwrite result '+str(path))
    lengths,subjects=condition_arrays(c)
    plan=make_plan(lengths,c['overlap'])
    rows=[]; started=time.perf_counter()
    count=3 if smoke else config['repetitions']
    master=config['smoke_master_seed'] if smoke else config['master_seed']
    purpose='smoke_only' if smoke else 'formal_evaluation'
    for rep in range(count):
        seed=seed_for(master,c['id'],rep,purpose)
        diff=draw(c,np.random.default_rng(seed))
        results=evaluate(diff,plan,c['effect'],subjects if c['regime']=='mixed_hierarchy' else None)
        for row in results:
            rows.append(dict(condition=c['id'],regime=c['regime'],kind=c['kind'],overlap=c['overlap'],true_difference=c['effect'],
                replication=rep,seed=str(seed),N=plan['N'],R=plan['R'],G=c['subject_count'],K0=plan['k0'],global_K=plan['global_k'],
                local_K_min=int(plan['local_k'].min()),local_K_max=int(plan['local_k'].max()),status='smoke' if smoke else 'formal',**row))
    pd.DataFrame(rows).to_csv(path,index=False)
    result=dict(condition=c['id'],replications=count,rows=len(rows),seconds=time.perf_counter()-started,result_sha256=digest(path))
    print(json.dumps(result),flush=True)
    return result
def summarize(raw_dir,output):
    raw=pd.concat([pd.read_csv(p,dtype={'seed':str}) for p in sorted(raw_dir.glob('*.csv'))],ignore_index=True)
    summaries=[]; comparisons=[]
    for (cid,method),g in raw.groupby(['condition','method'],sort=True):
        valid=g[g.valid.eq(1)]; M=len(g); m=len(valid)
        truth=g.true_difference.iloc[0]
        row=dict(condition=cid,method=method,overlap=g.overlap.iloc[0],true_difference=truth,M=M,valid_M=m,invalid_M=M-m,
                 mean_width=valid.ci_width.mean(),width_mcse=valid.ci_width.std(ddof=1)/np.sqrt(m),mean_point=g.point.mean(),point_sd=g.point.std(ddof=1))
        for col,name in [('reject_null','type_i_error' if truth==0 else 'power'),('coverage','coverage')]:
            phat=valid[col].mean(); k=int(valid[col].sum())
            lo,hi=ce.wilson_interval(k,m)
            row.update({name:phat,name+'_count':k,name+'_mcse':np.sqrt(phat*(1-phat)/m),name+'_wilson_low':lo,name+'_wilson_high':hi})
        summaries.append(row)
    for cid,g in raw.groupby('condition',sort=True):
        base=g[g.method.eq('original_global_bandwidth')].set_index('replication')
        local=g[g.method.eq('per_session_bandwidth')].set_index('replication')
        assert base.index.equals(local.index) and base.seed.equals(local.seed)
        for measure in ['reject_null','coverage','ci_width']:
            a=local[measure].to_numpy();b=base[measure].to_numpy();d=a-b
            comparisons.append(dict(condition=cid,contrast='per_session minus original',measure=measure,M=len(d),mean_difference=d.mean(),
                paired_mcse=d.std(ddof=1)/np.sqrt(len(d)),mc_low=d.mean()-Z*d.std(ddof=1)/np.sqrt(len(d)),mc_high=d.mean()+Z*d.std(ddof=1)/np.sqrt(len(d))))
    pd.DataFrame(summaries).to_csv(output/'formal_summary.csv',index=False)
    pd.DataFrame(comparisons).to_csv(output/'paired_comparisons.csv',index=False)
    print(pd.DataFrame(summaries).to_string(index=False),flush=True)
def test(output):
    tests=[]
    for lens,overlap in [([1,2,7,23],75),([5,8,18],0),([64]*4,0),([253]*4,75)]:
        plan=make_plan(lens,overlap)
        d=np.random.default_rng(932).normal(size=sum(lens))
        vg,vl=two_hac_variances(d,plan)
        f=pd.DataFrame({'subject_id':np.repeat(np.arange(len(lens)),lens),'session_id':np.repeat(np.arange(len(lens)),lens),
            'window_start_time':np.concatenate([np.arange(n) for n in lens]),'value':d})
        old=rdi.session_centered_bartlett_hac(f,'value',plan['global_k'])
        assert np.isclose(vg,old.variance,rtol=1e-12,atol=1e-16)
        direct=0.
        for ix,n in enumerate(lens):
            u=d[plan['offsets'][ix]:plan['offsets'][ix+1]];u=u-u.mean();k=plan['local_k'][ix]
            direct+=np.dot(u,u)+2*sum((1-h/(k+1))*np.dot(u[:-h],u[h:]) for h in range(1,k+1))
        direct*=sum(lens)/(sum(lens)-len(lens))/sum(lens)**2
        assert np.isclose(vl,direct,rtol=1e-12,atol=1e-16)
        if len(set(lens))==1: assert vg==vl
        tests.append(dict(test='independent direct sum and frozen implementation',lengths=lens,overlap=overlap,global_error=vg-old.variance,local_error=vl-direct,passed=True))
    assert len({seed_for(202609080862,'condition',i) for i in range(1000)})==1000
    assert seed_for(202609080862,'a',0)!=seed_for(20260714,'a',0)
    tests.append(dict(test='unique formal seeds and distinct historical master stream',passed=True))
    # Independent CR1 and t construction, deliberately unequal sessions/subject.
    frame=pd.DataFrame({'subject_id':[0,0,1,2,2,2],'value':[.1,.2,-.3,.4,.1,-.1]})
    got=rdi.subject_clustered_session_inference(frame,'value');mean=np.mean(frame.value)
    sums=np.array([sum(v-mean for v in frame[frame.subject_id.eq(i)].value) for i in range(3)])
    expected=3/2*np.dot(sums,sums)/36
    assert np.isclose(got.variance,expected) and got.degrees_of_freedom==2 and got.distribution=='t'
    tests.append(dict(test='CR1 manual cluster sums and G-1 reference',passed=True,variance=got.variance,df=got.degrees_of_freedom))
    (output/'inference_tests.json').write_text(json.dumps(tests,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(tests),flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','test','smoke','run']);p.add_argument('--project-root',type=Path);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--repetitions',type=int,default=1000);p.add_argument('--workers',type=int,default=2)
    a=p.parse_args();output=a.output_dir;output.mkdir(parents=True,exist_ok=True)
    if a.mode=='prepare': return prepare(a.project_root,output,a.repetitions)
    if a.mode=='test': return test(output)
    config=json.loads((output/'locked_config.json').read_text(encoding='utf-8'))
    for entry in config['code_manifest']:
        assert digest(Path(__file__).resolve().parent/entry['path'])==entry['sha256'], 'Code changed after lock'
    smoke=a.mode=='smoke';raw_dir=output/('smoke_raw' if smoke else 'formal_raw');raw_dir.mkdir(exist_ok=True)
    started=datetime.now(timezone.utc).isoformat();begin=time.perf_counter()
    tasks=[(config,c,str(raw_dir),smoke) for c in config['conditions']]
    if smoke:
        results=[run_condition(x) for x in tasks]
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
            results=list(pool.map(run_condition,tasks))
        summarize(raw_dir,output)
    (output/('smoke_run_metadata.json' if smoke else 'formal_run_metadata.json')).write_text(json.dumps(dict(started_at_utc=started,ended_at_utc=datetime.now(timezone.utc).isoformat(),seconds=time.perf_counter()-begin,
        command=sys.argv,python=sys.version,platform=platform.platform(),numpy=np.__version__,pandas=pd.__version__,config_sha256=digest(output/'locked_config.json'),results=results),indent=2)+'\n',encoding='utf-8')
if __name__=='__main__': main()
