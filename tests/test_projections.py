import json
from pathlib import Path
import unittest

from sbc_tools.projections import build_document_projections


class ProjectionTests(unittest.TestCase):
    def test_exact_pinned_wire_bytes(self):
        fixtures = Path(__file__).parent / "fixtures"
        sources = json.loads((fixtures / "producer-source-vectors.json").read_bytes())
        expected = json.loads((fixtures / "projection-wire-vectors.json").read_bytes())
        for case in sources["cases"]:
            documents = [(p, "vectors", text.encode()) for p, text in sorted(case["inputs"].items())
                         if p.startswith("docs/todo/vectors/")]
            wanted = next(c["files"] for c in expected["cases"] if c["name"] == case["name"])
            wanted = {p: text.encode() for p, text in wanted.items() if not p.startswith("locations/")}
            with self.subTest(case=case["name"]):
                self.assertEqual(wanted, build_document_projections(documents, registered_prefixes=["VECT"]))

    def test_duplicate_and_invalid_context_rejected(self):
        for sources in ([('a.md', 'one', b''), ('a.md', 'two', b'')],
                        [('../a.md', 'one', b'')], [('a.md', 'one', 'text')]):
            with self.subTest(sources=sources), self.assertRaises(ValueError):
                build_document_projections(sources, registered_prefixes=[])

    def test_context_and_outputs_are_not_retained(self):
        first = build_document_projections([], registered_prefixes=[])
        wanted = dict(first)
        first.clear()
        self.assertEqual(wanted, build_document_projections([], registered_prefixes=[]))

    def test_standalone_layout_and_exact_locator_membership(self):
        from sbc_tools import _producer_parser as producer
        path = 'specs/EX-00.md'
        result = build_document_projections([(path, 'example', b'# No document ID\n')], registered_prefixes=[])
        self.assertIn(path.encode(), result['diagnostics/example.json'])
        with self.assertRaises(producer.ProjectionError):
            producer._safe_locator(path, 1, admitted_documents=frozenset({'other.md'}))
        with self.assertRaises(producer.ProjectionError):
            producer._safe_locator(path + '/child.md', 1, admitted_documents=frozenset({path}))


if __name__ == '__main__': unittest.main()
