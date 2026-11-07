"""Engineering verification with a bounded JVM heap scoped to this Python process."""
import os,unittest,json,io
from pathlib import Path
from source_cut2 import ROOT,CUT,dump
os.environ['_JAVA_OPTIONS']=os.environ.get('_JAVA_OPTIONS','')+' -Xms8m -Xmx64m -XX:+UseSerialGC -XX:ReservedCodeCacheSize=16m -XX:MaxMetaspaceSize=64m'
stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT),pattern='test_*.py');result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
(CUT/'TEST-LOG.txt').write_text(stream.getvalue(),encoding='utf-8')
record=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),
    command='python system-types-v5/check_source_cut2.py',process_scoped_java_options=os.environ['_JAVA_OPTIONS'],
    initial_attempt=dict(tests=50,failures=0,errors=1,reason='G5 JVM default 4108288KB heap could not allocate128384KB parallel GC bitmap; process did not initialize.'),
    intermediate_attempt=dict(tests=50,failures=0,errors=1,java_options='-Xmx256m -XX:ParallelGCThreads=2',reason='JVM could not reserve enough space for object heap; process did not initialize.'),
    generator_source_modified=False,H3='UNRESOLVED',held_scoring=False)
dump(CUT/'TEST-RESULTS.json',record);print(json.dumps(record));print(stream.getvalue()[-2600:])
raise SystemExit(0 if result.wasSuccessful() else 1)
