import dataclasses
import json
from pathlib import Path
import unittest

from sbc_tools.documents import parse_document


def plain(value):
    if dataclasses.is_dataclass(value): return plain(dataclasses.asdict(value))
    if isinstance(value,dict): return {k:plain(v) for k,v in value.items()}
    if isinstance(value,(set,frozenset)): return sorted(plain(v) for v in value)
    if isinstance(value,(tuple,list)): return [plain(v) for v in value]
    return value


class DocumentParserTests(unittest.TestCase):
    def test_full_outputs_match_pinned_document_parser(self):
        vectors = json.loads((Path(__file__).parent/"fixtures/document-parser-vectors.json").read_bytes())
        for case in vectors["cases"]:
            with self.subTest(case=case["case"]):
                result = parse_document(case["text"].encode(),path=case["path"],family=case["family"],
                                        registered_prefixes=case["registered_prefixes"])
                self.assertEqual(case["expected"],plain(result))

    def test_explicit_path_family_and_byte_inputs_required(self):
        for override in ({"path":"../escape"},{"family":"a/b"},{"data":"not bytes"},
                         {"registered_prefixes":"VECT"},{"registered_prefixes":["PHASE"]}):
            args = dict(data=b"# Example\n",path="specs/A.md",family="example",registered_prefixes=[])
            args.update(override)
            with self.subTest(override=override),self.assertRaises(ValueError): parse_document(**args)

    def test_outputs_and_context_are_isolated(self):
        first = parse_document(b"# Example\n",path="specs/A.md",family="one",registered_prefixes=[])
        first[0].header["status"] = "changed"
        second = parse_document(b"# Example\n",path="specs/A.md",family="two",registered_prefixes=[])
        self.assertEqual("two",second[0].family)
        self.assertNotIn("status",second[0].header)

    def test_invalid_utf8_uses_pinned_replacement_rule(self):
        result = parse_document(b"# Example \xff\n",path="specs/A.md",family="example",registered_prefixes=[])
        self.assertEqual("Example \ufffd",result[0].title)


if __name__ == "__main__": unittest.main()
