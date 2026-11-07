"""Config-driven local <=5M-parameter autoregressive measuring instruments.

Content targets are identical for baseline and position variants. Position bits
refer to events observed BEFORE the target: SOL, previous EOL, explicit paragraph
start. No future line-ending/line-length/last-word feature is supplied.
"""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path=[p for p in sys.path if Path(p or '.').resolve()!=ROOT/'src']
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'.runtime'))
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
import csv,hashlib,json,math,random,time
from collections import Counter,defaultdict
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from src.tokenize import tokenize_line
from src.phase3 import dump,table

def read_rows(name):
    if name in ['ZL_running','LSI_H_running']:
        path=ROOT/f'data/voynich/{name}.csv'
    else:
        c,version=name.rsplit('_',1);path=ROOT/f'data/controls/{c}/{version}.csv'
    with path.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    for r in rows:
        r['is_para_start']=None if r.get('is_para_start','')=='' else r['is_para_start']=='True'
    return rows

def split_for(name):
    filename='C13_page_split.json' if name.startswith('C13_') else 'page_split.json'
    return json.loads((ROOT/'configs'/filename).read_text())

def piece_words(text,scheme,clusters,merges):
    tokens=[];word_ids=[]
    for wi,w in enumerate(text.split()):
        if wi and scheme!='T3':tokens.append(' ');word_ids.append(None)
        parts=tokenize_line(w,scheme,clusters,merges)
        tokens.extend(parts);word_ids.extend([wi]*len(parts))
    return tokens,word_ids

def prepare(name,scheme,config,rows=None,split=None,fit_bpe=False,vocabulary_override=None,merges_override=None,allow_empty=False):
    rows=read_rows(name) if rows is None else rows
    split=split_for(name) if split is None else split
    clusters=json.loads((ROOT/'configs/phase3.json').read_text())['clusters']
    bpes=json.loads((ROOT/'configs/control_bpe_extended.json').read_text())
    merges=bpes.get(name.split('_')[0])
    if merges_override is not None:merges=merges_override
    if fit_bpe and name.startswith('C'):
        from src.tokenize import train_bpe
        merges=train_bpe([w for r in rows if split[r['folio']]=='train' for w in r['text_eva'].split()],13)
    counts=Counter()
    for r in rows:
        if split.get(r['folio'])=='train':counts.update(tokenize_line(r['text_eva'],scheme,clusters,merges))
    cap=config['word_vocab_cap'] if scheme=='T3' else config['symbol_vocab_cap']
    vocabulary=vocabulary_override or (['<PAD>','<UNK>','<BOS>']+[t for t,_ in sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:cap]])
    lookup={t:i for i,t in enumerate(vocabulary)}
    page_rows=defaultdict(list)
    for r in rows:page_rows[r['folio']].append(r)
    blocks={'train':[],'validation':[],'test':[]};metadata=[]
    escape={'train':[],'validation':[],'test':[]};character_counts={'train':0,'validation':0,'test':0}
    width=config['context_length']
    for page,rs in page_rows.items():
        tokens=[];positions=[];metas=[]
        for li,r in enumerate(rs):
            if li and scheme!='T3':
                tokens.append(' ');positions.append(0);metas.append(None)
            parts,word_ids=piece_words(r['text_eva'],scheme,clusters,merges)
            for i,(token,wi) in enumerate(zip(parts,word_ids)):
                flags=(1+(2 if li else 0)+(4 if r['is_para_start'] else 0)) if i==0 else 0
                tokens.append(token);positions.append(flags)
                metas.append((r['line_id'],wi,token,r['folio'],r.get('currier_lang','')))
        ys=[lookup.get(t,1) for t in tokens];xs=[2]+ys[:-1]
        for start in range(0,len(ys),width):
            length=min(width,len(ys)-start)
            block=(xs[start:start+width]+[0]*(width-length),ys[start:start+width]+[0]*(width-length),
                   positions[start:start+width]+[0]*(width-length))
            label=split.get(page,'test')
            blocks[label].append(block)
            original=tokens[start:start+width]
            escape[label].append([32+8*len(t.encode('utf-8')) if lookup.get(t,1)==1 else 0 for t in original]+[0]*(width-length))
            character_counts[label]+=sum(len(t.replace(' ','')) for t in original)
            metadata.append(dict(split=label,page=page,start=start,length=length,
                metadata=metas[start:start+width],block_index=len(blocks[label])-1))
    tensors={k:torch.tensor(v,dtype=torch.long).reshape(-1,3,width) for k,v in blocks.items()}
    for k,v in tensors.items():
        if v.numel()==0 and not allow_empty:raise ValueError(f'{name} {k}: no page-held-out tokens')
    oov={k:dict(tokens=int((v[:,1]!=0).sum()),unknown=int((v[:,1]==1).sum())) for k,v in tensors.items()}
    return dict(name=name,scheme=scheme,rows=rows,split=split,vocabulary=vocabulary,lookup=lookup,
                merges=merges,clusters=clusters,tensors=tensors,metadata=metadata,oov=oov,
                escape={k:np.array(v,dtype=np.float32) for k,v in escape.items()},character_counts=character_counts)

class LanguageModel(nn.Module):
    def __init__(self,vocab_size,architecture,with_position,config):
        super().__init__();self.architecture=architecture;self.with_position=with_position
        d=config['embedding_dim'];self.embedding=nn.Embedding(vocab_size,d,padding_idx=0)
        self.events=nn.Embedding(8,d)
        nn.init.normal_(self.embedding.weight,std=.04)
        nn.init.normal_(self.events.weight,std=.02)
        self.dropout=nn.Dropout(config['dropout'])
        if architecture=='lstm':
            self.core=nn.LSTM(d,config['lstm_hidden'],num_layers=2,batch_first=True,dropout=config['dropout'])
            self.project=nn.Linear(config['lstm_hidden'],d)
        elif architecture=='transformer':
            self.position=nn.Embedding(config['context_length'],d)
            layer=nn.TransformerEncoderLayer(d,config['heads'],dim_feedforward=config['ff_dim'],
                dropout=config['dropout'],batch_first=True,norm_first=True,activation='gelu')
            self.core=nn.TransformerEncoder(layer,4,enable_nested_tensor=False);self.project=nn.LayerNorm(d)
        else:raise ValueError(architecture)
        self.output_bias=nn.Parameter(torch.zeros(vocab_size))
        self.count=sum(p.numel() for p in self.parameters())
        if self.count>5_000_000:raise ValueError(f'Model exceeds 5M: {self.count}')

    def forward(self,x,events,return_hidden=False):
        h=self.embedding(x)
        if self.with_position:h=h+self.events(events)
        if self.architecture=='transformer':
            h=h*math.sqrt(h.shape[-1])+self.position(torch.arange(x.shape[1],device=x.device))
            mask=torch.ones(x.shape[1],x.shape[1],device=x.device,dtype=torch.bool).triu(1)
            h=self.core(self.dropout(h),mask=mask,is_causal=True)
        else:h,_=self.core(self.dropout(h))
        h=self.project(h)
        logits=F.linear(h,self.embedding.weight,self.output_bias)
        return (logits,h) if return_hidden else logits

def initialize(seed):
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
    torch.set_num_threads(2)
    torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
    torch.use_deterministic_algorithms(True)

def autocast():
    return torch.autocast('cuda',dtype=torch.bfloat16,enabled=torch.cuda.is_available())

@torch.no_grad()
def evaluate(model,data,batch_size,details=False):
    model.eval();losses=[]
    for start in range(0,len(data),batch_size):
        b=data[start:start+batch_size]
        with autocast():logits=model(b[:,0],b[:,2])
        nll=F.cross_entropy(logits.float().reshape(-1,logits.shape[-1]),b[:,1].reshape(-1),ignore_index=0,reduction='none').reshape(b.shape[0],-1)
        losses.append(nll.cpu())
    losses=torch.cat(losses);mask=(data[:,1].cpu()!=0)
    result=dict(bits_per_token=float(losses.sum()/mask.sum()/math.log(2)),tokens=int(mask.sum()),
        unknown_tokens=int((data[:,1]==1).sum()),unknown_rate=float((data[:,1]==1).sum()/mask.sum()))
    if details:result['losses']=losses.numpy()/math.log(2)
    return result

def fit(prepared,architecture,with_position,seed,config,run_dir,save_weights=False):
    run_dir.mkdir(parents=True,exist_ok=True)
    spec=dict(corpus=prepared['name'],tokenization=prepared['scheme'],architecture=architecture,with_position=with_position,
              seed=seed,training=config,page_split=prepared['split'],vocabulary=prepared['vocabulary'],bpe_merges=prepared['merges'])
    dump(run_dir/'config.json',spec)
    initialize(seed);start_time=time.perf_counter();device='cuda' if torch.cuda.is_available() else 'cpu'
    model=LanguageModel(len(prepared['vocabulary']),architecture,with_position,config).to(device)
    data={k:v.to(device) for k,v in prepared['tensors'].items()}
    optimizer=torch.optim.AdamW(model.parameters(),lr=config['learning_rate'],weight_decay=config['weight_decay'],fused=device=='cuda')
    generator=torch.Generator(device=device).manual_seed(seed+29)
    best=float('inf');best_state=None;curve=[];seen=0
    steps=config['steps'];batch_size=config['batch_size']
    for step in range(1,steps+1):
        model.train();indices=torch.randint(len(data['train']),(batch_size,),generator=generator,device=device)
        batch=data['train'][indices];optimizer.zero_grad(set_to_none=True)
        warmup=config.get('warmup_steps',0)
        scale=min(1,step/max(1,warmup))*(.2+.8*(1+math.cos(math.pi*max(0,step-warmup)/max(1,steps-warmup)))/2)
        for group in optimizer.param_groups:group['lr']=config['learning_rate']*scale
        with autocast():
            logits=model(batch[:,0],batch[:,2])
            loss=F.cross_entropy(logits.reshape(-1,logits.shape[-1]),batch[:,1].reshape(-1),ignore_index=0)
        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),config['gradient_clip']);optimizer.step()
        seen+=int((batch[:,1]!=0).sum())
        if step in config['validation_steps'] or step==steps:
            validation=evaluate(model,data['validation'],batch_size)
            curve.append(dict(step=step,train_batch_bpt=float(loss.detach())/math.log(2),validation_bpt=validation['bits_per_token']))
            if validation['bits_per_token']<best:
                best=validation['bits_per_token'];best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
    model.load_state_dict(best_state)
    test=evaluate(model,data['test'],batch_size,details=True)
    validation_tokens=prepared['oov']['validation']['tokens']
    test_bpc=(test['bits_per_token']*test['tokens']+float(prepared['escape']['test'].sum()))/prepared['character_counts']['test']
    validation_bpc=(best*validation_tokens+float(prepared['escape']['validation'].sum()))/prepared['character_counts']['validation']
    result=dict(corpus=prepared['name'],tokenization=prepared['scheme'],architecture=architecture,with_position=with_position,
        seed=seed,parameter_count=model.count,validation_bpt=best,test_bpt=test['bits_per_token'],
        test_tokens=test['tokens'],test_unknown_rate=test['unknown_rate'],
        validation_bpc_with_escape=validation_bpc,test_bpc_with_escape=test_bpc,
        training_tokens_seen=seen,effective_token_epochs=seen/prepared['oov']['train']['tokens'],
        selected_step=min(curve,key=lambda r:r['validation_bpt'])['step'],
        still_improving_at_budget=(curve[-1]['validation_bpt']==best),seconds=time.perf_counter()-start_time,
        curve=curve,device=device,torch_version=torch.__version__,run_dir=str(run_dir.relative_to(ROOT)))
    if prepared['name'] in ['ZL_running','LSI_H_running']:
        by_language={lang:dict(bits=0.,tokens=0,unknown=0,escape_bits=0.,characters=0) for lang in ['A','B']}
        targets=prepared['tensors']['test'][:,1].numpy()
        for block in prepared['metadata']:
            if block['split']!='test':continue
            bi=block['block_index']
            for j,meta in enumerate(block['metadata']):
                if meta is None or meta[4] not in by_language:continue
                totals=by_language[meta[4]];totals['bits']+=float(test['losses'][bi,j]);totals['tokens']+=1
                totals['unknown']+=int(targets[bi,j]==1);totals['escape_bits']+=float(prepared['escape']['test'][bi,j])
                totals['characters']+=len(meta[2].replace(' ',''))
        result['currier_test']={lang:{**d,'bpt':d['bits']/d['tokens'],
            'bpc_with_escape':(d['bits']+d['escape_bits'])/d['characters']} for lang,d in by_language.items() if d['tokens']}
    dump(run_dir/'metrics.json',result)
    if prepared['scheme']=='T3' and not with_position and prepared['name'] in ['ZL_running','C1_clean','C5_clean','C8_clean']:
        np.savez_compressed(run_dir/'embeddings.npz',embedding=model.embedding.weight.detach().cpu().numpy())
    if save_weights:
        torch.save(dict(state_dict=best_state,spec=spec),run_dir/'model.pt')
    del optimizer,data
    return model,result

def load_model(path,config):
    saved=torch.load(path,map_location='cpu',weights_only=False);spec=saved['spec']
    model=LanguageModel(len(spec['vocabulary']),spec['architecture'],spec['with_position'],config)
    model.load_state_dict(saved['state_dict']);model.to('cuda' if torch.cuda.is_available() else 'cpu').eval()
    return model,spec

def benchmark():
    config=dict(embedding_dim=256,lstm_hidden=512,heads=4,ff_dim=1024,context_length=64,dropout=.1)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    report=dict(torch=torch.__version__,device=device,gpu=torch.cuda.get_device_name(0) if device=='cuda' else None)
    for architecture in ['lstm','transformer']:
        initialize(1729);model=LanguageModel(4099,architecture,False,config).to(device)
        optimizer=torch.optim.AdamW(model.parameters(),lr=.001,fused=device=='cuda')
        x=torch.randint(3,4099,(32,64),device=device);events=torch.zeros_like(x)
        times=[]
        for i in range(5):
            if device=='cuda':torch.cuda.synchronize()
            start=time.perf_counter();optimizer.zero_grad(set_to_none=True)
            with autocast():logits=model(x,events);loss=F.cross_entropy(logits.reshape(-1,4099),x.reshape(-1))
            loss.backward();optimizer.step()
            if device=='cuda':torch.cuda.synchronize()
            times.append(time.perf_counter()-start)
        report[architecture]=dict(parameters=model.count,step_seconds=times,warm_step_mean=sum(times[1:])/4)
        del model,optimizer
    dump(ROOT/'report/HARDWARE_BENCHMARK.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':
    if '--benchmark' in sys.argv:benchmark()
    else:raise SystemExit('Use python -m src.phase4 for the frozen matrix, or --benchmark.')
