from typing import List
import argparse
from pathlib import Path
import httpx
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SKOS
import os


def add_vocabs(vocabs: List[Path], mappings: dict):
    for vocab in vocabs:
        r = httpx.post(
            "http://fuseki.surroundaustralia.com/icsm-vocabs/data",
            params={"graph": str(mappings[vocab.name])},
            headers={"Content-Type": "text/turtle"},
            content=open(vocab, "rb").read(),
            auth=(os.environ["DB_USERNAME"], os.environ["DB_PASSWORD"])
        )
        assert 200 <= r.status_code <= 300, "Status code was {}".format(r.status_code)


def remove_vocabs(vocabs: List[Path], mappings: dict):
    for vocab in vocabs:
        r = httpx.post(
            "http://fuseki.surroundaustralia.com/icsm-vocabs/update",
            data={"update": "DROP GRAPH <{}>".format(mappings[vocab.name])},
            auth=(os.environ["DB_USERNAME"], os.environ["DB_PASSWORD"])
        )
        assert 200 <= r.status_code <= 300, "Status code was {}".format(r.status_code)


def get_graph_uri_for_vocab(vocab: Path) -> URIRef:
    """We can get the Graph URI for a vocab from the vocab file as we know that all VocPub-conformant vocabs
    have one and only one ConceptScheme per file and that the ICSM VocPrez installation uses the ConceptScheme URI
    as the Graph URI"""
    g = Graph().parse(str(vocab), format="ttl")
    for s in g.subjects(predicate=RDF.type, object=SKOS.ConceptScheme):
        return s


def get_all_vocabs_uris(vocabs: List[Path]) -> dict:
    mappings = {}
    for vocab in vocabs:
        mappings[vocab.name] = get_graph_uri_for_vocab(vocab)

    return mappings


if __name__ == "__main__":
    # for testing (until exit()):
    # add_vocabs([Path(__file__).parent.parent / "vocabularies" / "valid.ttl"], {"valid.ttl": URIRef("http://test.com")})
    # add_vocabs([Path(__file__).parent.parent / "vocabularies" / "valid.ttl"], {"valid.ttl": URIRef("http://test.com")})
    # remove_vocabs([Path(__file__).parent.parent / "vocabularies" / "valid.ttl"], {"valid.ttl": URIRef("http://test.com")})
    # exit()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--modified",
        help="Vocabs to be updated in the DB",
    )

    parser.add_argument(
        "-a",
        "--added",
        help="Vocabs to be added to the DB",
    )

    parser.add_argument(
        "-r",
        "--removed",
        help="Vocabs to be removed from the DB",
    )

    args = parser.parse_args()

    modified = []
    if args.modified is not None:
        for f in args.modified.split(","):
            # if the file is in the vocabularies/ folder and ends with .ttl, it's a vocab file
            if f.startswith("vocabularies/") and f.endswith(".ttl"):
                modified.append(Path(f))

    added = []
    if args.added is not None:
        for f in args.added.split(","):
            # if the file is in the vocabularies/ folder and ends with .ttl, it's a vocab file
            if f.startswith("vocabularies/") and f.endswith(".ttl"):
                added.append(Path(f))

    removed = []
    if args.removed is not None:
        for f in args.removed.split(","):
            # if the file is in the vocabularies/ folder and ends with .ttl, it's a vocab file
            if f.startswith("vocabularies/") and f.endswith(".ttl"):
                removed.append(Path(f))

    # map vocab files to graph_uris
    mappings = get_all_vocabs_uris(list(set(modified + added + removed)))

    # remove all removed and modified vocabs
    remove_vocabs(removed + modified, mappings)

    # add all added and modified vocabs
    add_vocabs(added + modified, mappings)

    # print for testing
    print("modified:")
    print([str(x) for x in modified])
    print("added:")
    print([str(x) for x in added])
    print("removed:")
    print([str(x) for x in removed])

