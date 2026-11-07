from source_cut_probe import get
from source_cut2 import CUT,dump
from core import sha
p=CUT/'gatmuza-README.md'
p.write_bytes(get('https://raw.githubusercontent.com/LostMa-ERC/gatmuza/e5f6397ce18b4ff68103ba7088d31ad4d99bade1/README.md'))
dump(CUT/'GATMUZA-METADATA.json',dict(repository='LostMa-ERC/gatmuza',commit='e5f6397ce18b4ff68103ba7088d31ad4d99bade1',readme_sha256=sha(p),
    attribution='Camps, Jean-Baptiste. Lo GAT MUZA: CATMUS-conformant HTR Ground-Truth Data for Medieval Occitan.',license='CC BY4.0',
    body_access='README metadata only. No reserved XML body parsed. Word segmentation declared modernised; abbreviations unexpanded. Separate native-page control; transfer method not qualified.'))
print('Pinned reserve-source attribution/license metadata retained without reading reserve bodies.')
