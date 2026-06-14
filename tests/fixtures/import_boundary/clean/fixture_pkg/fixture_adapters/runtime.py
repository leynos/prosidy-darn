"""Clean-tree adapter importing an allowed outward-to-inward edge to domain.

The import is bound to a module-level name so the repository linter does not
flag it as unused; hecate observes the ``fixture_adapters -> fixture_domain``
edge by parsing the source with ``ast``.
"""

import fixture_pkg.fixture_domain.model as _domain

DOMAIN = _domain
