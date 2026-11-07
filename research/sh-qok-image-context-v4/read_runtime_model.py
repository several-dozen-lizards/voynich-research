"""Extract only model identifiers from the new isolated runtime logs."""
import json,re,sqlite3
import isolated_cli as cli
import prepare as core

out={}
for role in ['registrar','rater-A','rater-B']:
    p=cli.BASE/'control'/('runtime-'+role)/'logs_2.sqlite'
    if not p.exists():continue
    db=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    tables=[r[0] for r in db.execute("select name from sqlite_master where type='table'")]
    findings=set();columns={}
    for table in tables:
        if not re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*',table):continue
        names=[r[1] for r in db.execute('pragma table_info('+table+')')]
        columns[table]=names
        textual=[n for n in ['message','fields','message_json','json','body','feedback_log_body'] if n in names]
        for col in textual:
            for row in db.execute('select '+col+' from '+table):
                if isinstance(row[0],str):
                    findings.update(re.findall(r'\bgpt-[A-Za-z0-9][A-Za-z0-9._-]*',row[0]))
    out[role]=dict(identifiers_in_runtime_logs=sorted(findings),tables_and_columns=columns,
        caution='Presence in a generic log is not proof of selection. Do not infer an exact selected model without an explicit selected-model record.')
core.save('private/RUNTIME-MODEL-AUDIT.json',out)
print(json.dumps({r:v['identifiers_in_runtime_logs'] for r,v in out.items()}))
