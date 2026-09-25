"""Lazy, explicitly registered checkout readers with caller-owned lifetimes."""
from collections.abc import Mapping
from pathlib import Path

from .configuration import _reject_linked_components
from .git_reader import GitCommitReader
from .local_checkout import _ordinary_directory


class RegisteredCheckoutReaders(Mapping):
    """Open only a requested registered checkout, never search for repositories.

    Membership probes acquire a reader so an absent checkout behaves as a missing
    mapping entry. Iteration lists registrations, not proven available checkouts.
    Missing results are retained for this operation. The supplied ExitStack closes
    every acquired reader, including when a later read fails.
    """
    def __init__(self, paths, stack, *, reader_factory=GitCommitReader):
        self._paths = {owner: Path(path) for owner, path in paths.items()}
        if any(not isinstance(owner, str) or not owner or not path.is_absolute()
               or '..' in path.parts for owner, path in self._paths.items()):
            raise ValueError('Explicit absolute registered checkout paths required')
        self._stack, self._factory, self._cache = stack, reader_factory, {}

    def __iter__(self):
        return iter(self._paths)

    def __len__(self):
        return len(self._paths)

    def __getitem__(self, owner):
        if owner not in self._paths:
            raise KeyError(owner)
        if owner not in self._cache:
            from dulwich.errors import NotGitRepository
            path = self._paths[owner]
            try:
                current = Path(path.anchor)
                for part in path.parts[1:]:
                    current = current / part
                    _ordinary_directory(current)
                _reject_linked_components(path, '.git')
                self._cache[owner] = self._stack.enter_context(self._factory(str(path)))
            except (FileNotFoundError, NotGitRepository):
                self._cache[owner] = None
        result = self._cache[owner]
        if result is None:
            raise KeyError(owner)
        return result
