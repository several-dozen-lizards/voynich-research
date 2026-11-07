import execute as b
if __name__=='__main__':
 b.verify()
 note=b.json.loads((b.RUN/'AUDIT-HARNESS-FREEZE.json').read_text());assert all(b.sha(p)==h for p,h in note['hashes'].items())
 # Cache only the immutable frozen job manifest; do not change generator, oracle or decisions.
 jobpath=b.R/'JOBS.json';text=jobpath.read_text();original=b.Path.read_text
 def cached(self,*args,**kwargs):
  return text if self==jobpath else original(self,*args,**kwargs)
 b.Path.read_text=cached
 b.audit()
