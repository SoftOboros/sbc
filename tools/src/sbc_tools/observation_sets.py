"""Approved observation-set v1 structure and identity; no Git or filesystem IO."""
import hashlib
import json
import re
import unicodedata

from .canonical import canonical_json
from .configuration import _path

_SET = {'schema_version','root_repository_id','complete','selection_sha256','participants','relations'}
_PARTICIPANT = {'repository_id','availability','observed_head','checkout_state','corpus_sha256'}
_RELATION = {'parent_repository_id','path','repository_id','parent_commit','recorded_child_commit','pin_state'}


def _fields(value, keys):
    if not isinstance(value,dict) or set(value) != keys:
        raise ValueError('Unexpected observation fields')


def _name(value):
    if not isinstance(value,str) or not value or unicodedata.normalize('NFC',value) != value:
        raise ValueError('Invalid repository identity')


def _hex(value, pattern):
    if not isinstance(value,str) or not re.fullmatch(pattern,value):
        raise ValueError('Invalid observation digest or commit')


def observation_set_bytes(value):
    """Validate relational consistency and digest, returning immutable canonical bytes.

    Git-object truth, capture stability and registration authorization are host
    obligations. This validator cannot turn caller-provided context into proof.
    """
    raw = canonical_json(value)
    value = json.loads(raw)
    _fields(value,_SET)
    if type(value['schema_version']) is not int or value['schema_version'] != 1 or type(value['complete']) is not bool:
        raise ValueError('Invalid observation version or completeness')
    _name(value['root_repository_id'])
    participants,relations = value['participants'],value['relations']
    if not isinstance(participants,list) or not participants or not isinstance(relations,list):
        raise ValueError('Invalid observation members')
    by_id = {}
    for row in participants:
        _fields(row,_PARTICIPANT)
        owner = row['repository_id']
        _name(owner)
        if owner in by_id:
            raise ValueError('Duplicate participant')
        by_id[owner] = row
        availability = row['availability']
        if availability == 'available':
            _hex(row['observed_head'],r'(?:[0-9a-f]{40}|[0-9a-f]{64})')
            _hex(row['corpus_sha256'],r'[0-9a-f]{64}')
            if row['checkout_state'] not in ('clean','dirty'):
                raise ValueError('Available checkout state required')
        elif availability in ('missing_checkout','unavailable_history','blocked_by_ancestor'):
            if row['observed_head'] is not None or row['corpus_sha256'] is not None or row['checkout_state'] != 'unknown':
                raise ValueError('Unavailable participant cannot claim observed content')
        else:
            raise ValueError('Unknown availability')
    if list(by_id) != sorted(by_id) or value['root_repository_id'] not in by_id:
        raise ValueError('Unsorted participants or missing root')
    root = value['root_repository_id']
    if by_id[root]['availability'] == 'blocked_by_ancestor':
        raise ValueError('Root has no ancestor')
    parents,keys = {},[]
    for edge in relations:
        _fields(edge,_RELATION)
        parent,child,path = edge['parent_repository_id'],edge['repository_id'],edge['path']
        _name(parent); _name(child); _path(path)
        if parent not in by_id or child not in by_id or child == root or child in parents:
            raise ValueError('Invalid relation ownership')
        parents[child] = parent
        keys.append((parent,path))
        state = edge['pin_state']
        if state not in ('match','mismatch','unavailable'):
            raise ValueError('Unknown pin state')
        for key in ('parent_commit','recorded_child_commit'):
            if edge[key] is not None:
                _hex(edge[key],r'(?:[0-9a-f]{40}|[0-9a-f]{64})')
        parent_available = by_id[parent]['availability'] == 'available'
        child_available = by_id[child]['availability'] == 'available'
        if not parent_available:
            if (by_id[child]['availability'] != 'blocked_by_ancestor' or state != 'unavailable'
                    or edge['parent_commit'] is not None or edge['recorded_child_commit'] is not None):
                raise ValueError('Unavailable ancestor must block descendant evidence')
        elif by_id[child]['availability'] == 'blocked_by_ancestor':
            raise ValueError('Available parent does not block its direct child')
        if state != 'unavailable':
            if not parent_available or not child_available or edge['parent_commit'] is None or edge['recorded_child_commit'] is None:
                raise ValueError('Pin comparison requires available evidence')
            expected = 'match' if edge['recorded_child_commit'] == by_id[child]['observed_head'] else 'mismatch'
            if state != expected:
                raise ValueError('False pin comparison')
        if parent_available and parent != root and edge['parent_commit'] is not None:
            if edge['parent_commit'] != by_id[parent]['observed_head']:
                raise ValueError('Nested relation must use immediate parent observed HEAD')
    if keys != sorted(set(keys)) or set(parents) != set(by_id)-{root}:
        raise ValueError('Duplicate/unsorted relations or missing participant parent')
    for child in parents:
        seen = set()
        while child != root:
            if child in seen or child not in parents:
                raise ValueError('Observation relation cycle')
            seen.add(child)
            child = parents[child]
    if value['complete']:
        if any(row['availability'] != 'available' for row in participants) or any(edge['pin_state'] == 'unavailable' for edge in relations):
            raise ValueError('Incomplete evidence cannot claim complete selection')
        _hex(value['selection_sha256'],r'[0-9a-f]{64}')
        payload = {key:item for key,item in value.items() if key != 'selection_sha256'}
        if hashlib.sha256(canonical_json(payload)).hexdigest() != value['selection_sha256']:
            raise ValueError('Observation selection digest mismatch')
    elif value['selection_sha256'] is not None:
        raise ValueError('Incomplete selection has no digest')
    return raw


def build_observation_set(*, root_repository_id, participants, relations, complete):
    """Order copied metadata, compute its context digest, and validate the result."""
    value = json.loads(canonical_json(dict(schema_version=1,root_repository_id=root_repository_id,
        participants=participants,relations=relations,complete=complete,selection_sha256=None)))
    value['participants'].sort(key=lambda row:row['repository_id'])
    value['relations'].sort(key=lambda row:(row['parent_repository_id'],row['path']))
    if complete:
        payload = {key:item for key,item in value.items() if key != 'selection_sha256'}
        value['selection_sha256'] = hashlib.sha256(canonical_json(payload)).hexdigest()
    return observation_set_bytes(value)
