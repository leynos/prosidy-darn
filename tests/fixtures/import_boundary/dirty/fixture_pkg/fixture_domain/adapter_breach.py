"""Dirty-tree domain module importing a forbidden first-party adapter.

This edge violates the hexagonal dependency rule: the domain must never name an
adapter. hecate must classify it as ``fixture_domain -> fixture_adapters`` and
report it. The import is bound to a module-level name so the repository linter
does not flag it as unused; hecate never executes the module.
"""

import fixture_pkg.fixture_adapters.runtime as _forbidden_adapter

ADAPTER = _forbidden_adapter
