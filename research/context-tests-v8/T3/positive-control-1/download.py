import urllib.request,sys
u=sys.argv[1];p=sys.argv[2]
with urllib.request.urlopen(u,timeout=45) as r: data=r.read()
open(p,'wb').write(data)
print(len(data),p)
