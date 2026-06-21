"""Dirty-tree domain module importing a forbidden external framework.

``pretend_framework`` is a stand-in external prefix that is never installed; it
exists only so hecate can classify a ``fixture_domain -> pretend_framework``
edge and report it as a forbidden external dependency. The import is bound to a
module-level name so the repository linter does not flag it as unused.
"""

import pretend_framework as _forbidden_external  # ty: ignore[unresolved-import]

FRAMEWORK = _forbidden_external
