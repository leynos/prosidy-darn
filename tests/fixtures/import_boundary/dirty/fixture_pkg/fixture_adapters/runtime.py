"""Dirty-tree adapter importing an allowed outward-to-inward edge to domain.

This edge is legitimate and must not be reported; it is present so the dirty
tree exercises an allowed adapter dependency alongside the forbidden ones.
"""

import fixture_pkg.fixture_domain.model as _domain

DOMAIN = _domain
