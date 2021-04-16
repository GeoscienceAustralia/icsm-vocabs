from pathlib import Path
from pyshacl import validate
import httpx
import sys

# get the validator
r = httpx.get("https://w3id.org/profile/vocpub/validator")
assert r.status_code == 200

# for all vocabs...
invalid_vocabs = []
vocabs_dir = Path(__file__).parent.parent / "vocabularies"
for f in vocabs_dir.iterdir():
    # validate each file
    if f.name.endswith(".ttl"):
        v = validate(str(f), shacl_graph=r.text, shacl_graph_format="ttl")
        if not v[0]:
            invalid_vocabs.append(f.name)

if len(invalid_vocabs) > 0:
    print("Invalid Vocabs:")
    for iv in invalid_vocabs:
        print("\t- {}".format(iv))

assert len(invalid_vocabs) == 0
