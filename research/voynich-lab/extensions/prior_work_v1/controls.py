"""Pinned C8/C14–C18 controls; native text, origin labels and noise receipts."""
import ast,types,unicodedata,xml.etree.ElementTree as ET,zipfile,subprocess,shutil
from collections import Counter
from .common import *
from src.noise import inject

def macaronic(first,second,template,granularity,phrase_words=5,seed=1729):
    """Alternate intact source runs; a single shared alphabet, no source relabeling."""
    pointers=[0,0];out=[];truth=[];para=-1;position=0
    for r in template:
        if r['is_para_start']:para+=1
        row_truth=[]
        for _ in r['text_eva'].split():
            source=(position if granularity=='word' else position//phrase_words if granularity=='phrase' else max(0,para))%2
            words=[first,second][source];out.append(words[pointers[source]]);pointers[source]+=1
            row_truth.append(source);position+=1
        truth.append(dict(line_id=r['line_id'],word_sources=row_truth,vernacular_fraction=sum(row_truth)/len(row_truth)))
    return layout(out,template,'C14'),truth

def noisy_truth(text,word_sources,rates,alphabet,rng):
    """Replay the frozen IID channel, carrying source labels across boundary edits."""
    symbols=sorted(set(alphabet)|{' '});s,i,d=(rates[k] for k in ['substitution','insertion','deletion'])
    origins=[]
    for wi,word in enumerate(text.split()):
        if wi:origins.append(None)
        origins.extend([word_sources[wi]]*len(word))
    assert len(origins)==len(text)
    out=[]
    for c,label in zip(text,origins):
        x=rng.random()
        if x<s:out.append((rng.choice([a for a in symbols if a!=c]),label))
        elif x<s+d:continue
        elif x<s+d+i:out.extend([(rng.choice(symbols),label),(c,label)])
        else:out.append((c,label))
    groups=[];word=[]
    for c,label in out+[(' ',None)]:
        if c.isspace():
            if word:groups.append(word);word=[]
        else:word.append((c,label))
    fractions=[]
    for group in groups:
        known=[v for _,v in group if v is not None]
        fractions.append(sum(known)/len(known) if known else None)
    return ' '.join(''.join(c for c,_ in group) for group in groups),fractions

def naibbe_module(seed):
    """Run the author's naibbe.py functions verbatim; adapt CSV I/O and RNG only."""
    path=EXT/'raw/greshko/naibbe.py';tree=ast.parse(path.read_text(encoding='utf-8'))
    selected=[]
    for node in tree.body:
        if isinstance(node,ast.Import):
            node.names=[n for n in node.names if n.name not in ['pandas','random']]
            if not node.names:continue
        if isinstance(node,ast.If):continue # CLI and final print only
        selected.append(node)
    module=types.ModuleType('pinned_naibbe')
    def read_csv(ignored):
        with (EXT/'raw/greshko/references/naibbe_tables.csv').open(encoding='utf-8-sig',newline='') as f:data=list(csv.DictReader(f))
        return {k:[r[k] for r in data] for k in data[0]}
    module.__dict__.update(random=random.Random(seed),pd=types.SimpleNamespace(read_csv=read_csv))
    exec(compile(ast.fix_missing_locations(ast.Module(body=selected,type_ignores=[])),str(path),'exec'),module.__dict__)
    return module

def naibbe(words,deck,seed,n):
    mod=naibbe_module(seed);units=[];original=mod.respace_plaintext
    def capture(*args,**kwargs):
        value=original(*args,**kwargs);units.extend(value);return value
    mod.respace_plaintext=capture
    plain=mod.clean_line(' '.join(words))
    encrypted=mod.encrypt_naibbe(plain,mod.naibbe_tables,mod.placeholder_to_glyph,use_78=deck==78)
    assert len(encrypted)>=n
    return encrypted[:n],dict(deck=deck,respacing_unigram_probability=17/36,unambiguous_unigram_rejection=True,
        cross_bigram_collision_rejection=False,implementation='author naibbe.py, not later naibbe_v2.py',
        optional_space_removal=0,input_characters_consumed=sum(map(len,units[:n])),
        generated_words=len(encrypted),selected_words=n,ambiguity_retries=mod.ambiguity_retries,
        code_sha256=sha(EXT/'raw/greshko/naibbe.py'))

def hebrew_words():
    result=[];sources=[]
    for book in ['Gen','Exod','Lev','Num','Deut']:
        path=EXT/f'raw/openscriptures/wlc/{book}.xml'
        root=ET.fromstring(path.read_bytes());count=0
        for element in root.iter():
            if element.tag.split('}')[-1]!='w':continue
            # WLC base text only. OSHB lemma/morph attributes are not imported.
            text=''.join(element.itertext());word=''.join(c for c in unicodedata.normalize('NFD',text)
                if '\u05d0'<=c<='\u05ea' or '\u05b0'<=c<='\u05bc' or c in '\u05c1\u05c2\u05c7')
            if word:result.append(word);count+=1
        sources.append(dict(book=book,words=count,sha256=sha(path)))
    return result,sources

def strip_vowels(word,language):
    if language=='Latin':return ''.join(c for c in word if c not in 'aeiou')
    return ''.join(c for c in word if not ('\u05b0'<=c<='\u05bb' or c=='\u05c7'))

def alphagram(word,language,remove_vowels=False):
    if remove_vowels:word=strip_vowels(word,language)
    # Sort grapheme clusters by base letter, retaining pointing on its own letter.
    clusters=[]
    for char in word:
        if unicodedata.combining(char) and clusters:clusters[-1]+=char
        else:clusters.append(char)
    return ''.join(sorted(clusters)) or '\u2205' # retained empty-consonant word slot

def participant_rows():
    archive=EXT/'raw/danielgaskell/data/gibberish_transcriptions.zip';result=[];inventory=[]
    with zipfile.ZipFile(archive) as z:
        for name in sorted(z.namelist()):
            if not name.endswith('.txt') or name.startswith('__MACOSX/'):continue
            participant=Path(name).stem.replace('Gibberish - ','');text=z.read(name).decode('utf-8-sig')
            selected=[]
            for i,line in enumerate(text.splitlines()):
                # Drop separator-only lines, retain original lines and participant IDs.
                words=[''.join(c for c in w.casefold() if c.isalpha() or unicodedata.combining(c)) for w in line.split()]
                words=[w for w in words if w]
                if not words:continue
                selected.append(dict(folio='participant_'+participant,line_id=participant+':'+str(i),text_eva=' '.join(words),
                    text_raw=line,is_para_start=None,is_label=False,section=None,currier_lang=None,hand_scribe=None,
                    source_group=participant,participant=participant,metadata_origin='participant-separated original transcription lines'))
            result.extend(selected);inventory.append(dict(participant=participant,lines=len(selected),words=sum(len(r['text_eva'].split()) for r in selected),source_file=name))
    return result,inventory

def published_c8(n,seed=1729):
    java=next((EXT/'runtime').glob('*/bin/java.exe'))
    folder=EXT/'runs/C8_published_generator';folder.mkdir(exist_ok=True)
    config=(EXT/'raw/TorstenTimm/executable/conf.properties').read_text()
    config=re.sub(r'(?m)^text.lines_to_create=.*$', 'text.lines_to_create=6500',config)
    config=re.sub(r'(?m)^method.random.pseudo.seed=.*$',f'method.random.pseudo.seed={seed}',config)
    config=re.sub(r'(?m)^save.path=.*$','save.path=./generate/',config)
    (folder/'conf.properties').write_text(config,encoding='ascii');(folder/'generate').mkdir(exist_ok=True)
    output=folder/'generate/generated_text.txt'
    if not output.exists():
        jar=EXT/'raw/TorstenTimm/executable/text-generator.jar'
        libraries=list((EXT/'raw/TorstenTimm/executable/lib').glob('*.jar'))
        cp=';'.join([str(folder),str(jar)]+list(map(str,libraries)))
        result=subprocess.run([str(java),'-cp',cp,'de.voynich.text.SelfCitationTextGenerator'],cwd=folder,capture_output=True,text=True)
        (folder/'stdout.txt').write_text(result.stdout,encoding='utf-8');(folder/'stderr.txt').write_text(result.stderr,encoding='utf-8')
        if result.returncode:raise RuntimeError(result.stderr)
    text=output.read_text(encoding='utf-8');words=' '.join(line for line in text.splitlines() if not line.startswith('#')).split()
    # Java output has no folio labels; source strings are retained, with native EVA.
    assert len(words)>=n
    return words[:n],dict(implementation='published Java executable, unmodified',seed=seed,generated_words=len(words),selected_words=n,
        initial_line='published default f103v.P.9; manuscript-derived initial seed is a material source dependence',
        config_sha256=sha(folder/'conf.properties'),jar_sha256=sha(EXT/'raw/TorstenTimm/executable/text-generator.jar'))

def build():
    cfg=json.loads((ROOT/'configs/phase3.json').read_text());primary=rows(ROOT/'data/voynich/ZL_running.csv')
    n=sum(len(r['text_eva'].split()) for r in primary);native={c:load_words(cfg['source_slices'][c],n)[0] for c in ['C1','C2','C3']}
    oldsplit=json.loads((ROOT/'configs/page_split.json').read_text());reg={}
    for name in ['ZL_running','LSI_H_running']+[f'C{i}_{v}' for i in range(1,14) for v in ['clean','noise']]:
        path=ROOT/f'data/voynich/{name}.csv' if not name.startswith('C') else ROOT/'data/controls'/name.split('_')[0]/(name.split('_')[1]+'.csv')
        sp=json.loads((ROOT/'configs/C13_page_split.json').read_text()) if name.startswith('C13_') else oldsplit
        reg[name]=dict(path=str(path.relative_to(ROOT)),split=sp,family=name.split('_')[0],legacy=True)
    rates=json.loads((ROOT/'report/noise_model.json').read_text())['rates']
    sizes=[]
    def save(code,selected,meta,truth=None,identity=False,word_match=True,alphabet_extra=''):
        folder=EXT/'data'/code;folder.mkdir(exist_ok=True);table(folder/'native.csv',selected)
        if identity:mapping={c:c for r in selected for c in r['text_eva'] if c!=' '};clean=selected
        else:
            clean,mapping=relabel(selected+([dict(text_eva=alphabet_extra)] if alphabet_extra else []))
            if alphabet_extra:clean=clean[:-1]
        alpha=set(mapping.values());rng=rng_for(1729,code+':noise');noise=[];ops=Counter()
        noise_truth=[];truth_by_line={r['line_id']:r for r in (truth or [])}
        for r in clean:
            state=rng.getstate();text,counts,raw=inject(r['text_eva'],rates,alpha,rng);ops.update(counts);noise.append({**r,'text_eva':text})
            if truth is not None:
                replay=random.Random();replay.setstate(state)
                observed,fractions=noisy_truth(r['text_eva'],truth_by_line[r['line_id']]['word_sources'],rates,alpha,replay)
                assert observed==text and replay.getstate()==rng.getstate()
                noise_truth.append(dict(line_id=r['line_id'],word_sources=fractions))
        sp=oldsplit if {r['folio'] for r in clean}<=set(oldsplit) else stable_split(clean,code)
        for version,current in [('clean',clean),('noise',noise)]:
            path=folder/(version+'.csv');table(path,current);name=code+'_'+version
            reg[name]=dict(path=str(path.relative_to(ROOT)),split=sp,family=code.split('_')[0],legacy=False,
                native_path=str((folder/'native.csv').relative_to(ROOT)),symbol_mapping=mapping,version=version)
            if truth is not None:reg[name]['truth_path']=str((folder/f'truth_{version}.json').relative_to(ROOT))
            words=sum(len(r['text_eva'].split()) for r in current);characters=sum(len(r['text_eva'].replace(' ','')) for r in current)
            if word_match and version=='clean':assert words==n,(code,words,n)
            sizes.append(dict(corpus=name,words=words,characters=characters,word_ratio=words/n,character_ratio=characters/172280,word_match_exception=not word_match))
        dump(folder/'metadata.json',dict(**meta,symbol_mapping=mapping,noise_rates=rates,realized_operations=dict(ops),clean_sha256=sha(folder/'clean.csv'),noise_sha256=sha(folder/'noise.csv')))
        if truth is not None:
            dump(folder/'truth_clean.json',truth);dump(folder/'truth_noise.json',noise_truth)
    for grain in ['word','phrase','paragraph']:
        selected,truth=macaronic(native['C1'],native['C3'],primary,grain)
        save('C14_'+grain,selected,dict(granularity=grain,phrase_words=5,language_sources=['C1 Latin','C3 German']),truth)
    label_template=rows(ROOT/'data/voynich/ZL_labels.csv');label_n=sum(len(r['text_eva'].split()) for r in label_template)
    save('C14_labeltext',layout(native['C1'],primary,'C14'),dict(running_source='C1 Latin',labels_source='C3 German'),
        truth=[dict(line_id=r['line_id'],word_sources=[0]*len(r['text_eva'].split())) for r in primary],alphabet_extra=''.join(native['C3'][:label_n]))
    label_rows=layout(native['C3'][:label_n],label_template,'C14')
    # Use the SAME native-to-display mapping as the running half, not a language-specific alphabet.
    mapping=reg['C14_labeltext_clean']['symbol_mapping']
    for r in label_rows:r['is_label']=True
    table(EXT/'data/C14_labeltext/labels_native.csv',label_rows)
    for version in ['clean','noise']:
        current=[];rng=rng_for(1729,'C14_labeltext:labels:noise')
        for r in label_rows:
            text=''.join(mapping.get(c,c) for c in r['text_eva'])
            if version=='noise':text,_,_=inject(text,rates,set(mapping.values()),rng)
            current.append({**r,'text_eva':text})
        table(EXT/f'data/C14_labeltext/labels_{version}.csv',current)
        combined=rows(EXT/f'data/C14_labeltext/{version}.csv')+current
        path=EXT/f'data/C14_labeltext/combined_{version}.csv';table(path,combined)
        allocation=dict(oldsplit);leaf_parts={re.match(r'f\d+',p)[0]:part for p,part in oldsplit.items() if re.match(r'f\d+',p)}
        for r in combined:
            if r['folio'] not in allocation:
                match=re.match(r'f\d+',r['folio']);key=match[0] if match else r['folio']
                if key not in leaf_parts:
                    x=rng_for(1729,key+':extra_leaf').random();leaf_parts[key]='train' if x<.8 else 'validation' if x<.9 else 'test'
                allocation[r['folio']]=leaf_parts[key]
        name='C14_labeltext_withlabels_'+version
        reg[name]=dict(path=str(path.relative_to(ROOT)),split=allocation,family='C14',legacy=False,analysis_only=True,version=version)
        truth=json.loads((EXT/f'data/C14_labeltext/truth_{version}.json').read_text())
        truth += [dict(line_id=r['line_id'],word_sources=[1]*len(r['text_eva'].split())) for r in current]
        truth_path=EXT/f'data/C14_labeltext/truth_withlabels_{version}.json';dump(truth_path,truth);reg[name]['truth_path']=str(truth_path.relative_to(ROOT))
    for language in ['Latin','Italian']:
        for deck in [52,78]:
            output,meta=naibbe(native['C1' if language=='Latin' else 'C2'],deck,1729,n)
            save(f'C15_{language}_{deck}',layout(output,primary,'C15'),dict(language=language,**meta),identity=True)
    hebrew,source=hebrew_words();assert len(hebrew)>n
    (EXT/'dictionaries/Hebrew_heldout.txt').write_text('\n'.join(hebrew[n:]),encoding='utf-8')
    # Latin dictionary is source-disjoint Agrippa, never C1 transformed back into itself.
    latin_dict=(EXT/'raw/chirila/Corpora/Historical_texts/Agrippa_Book1').read_text(encoding='utf-8-sig')
    (EXT/'dictionaries/Latin_independent.txt').write_text(latin_dict,encoding='utf-8')
    for language,words in [('Latin',native['C1']),('Hebrew',hebrew[:n])]:
        for remove in [False,True]:
            output=[alphagram(w,language,remove) for w in words]
            save(f'C16_{language}_'+('novowels' if remove else 'vowels'),layout(output,primary,'C16'),
                dict(language=language,remove_vowels=remove,empty_consonant_slots=sum(w=='\u2205' for w in output),hebrew_source=source if language=='Hebrew' else None))
    human,inventory=participant_rows();table(EXT/'report/C17_participants.csv',inventory)
    save('C17_human',human,dict(source='Gaskell & Bowern 2022',participants=len(inventory),size_exception='Use complete available participants, never repeat or pool source boundaries',inventory=inventory),word_match=False)
    for variant in ['bigraph2','addB']:
        mapping={'a':'ci','e':'cc','o':'ic','t':'ch','s':'sh','n':'uc'} if variant=='bigraph2' else {c:c+'B' for c in set(''.join(native['C1']))}
        output=[''.join(mapping.get(c,c) for c in w) for w in native['C1']]
        save('C18_'+variant,layout(output,primary,'C18'),dict(source='Bowern & Gaskell 2022 Table 1',variant=variant,codebook=mapping))
    output,meta=published_c8(n)
    save('C8_published',layout(output,primary,'C8'),meta,identity=True)
    dump(EXT/'data/registry.json',reg);table(EXT/'report/size_matching.csv',sizes)
    progress('controls generated',corpora=len(reg),new_corpora=sum(not r['legacy'] for r in reg.values()))

if __name__=='__main__':build()
