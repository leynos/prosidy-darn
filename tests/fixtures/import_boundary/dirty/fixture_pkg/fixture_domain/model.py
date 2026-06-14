"""Dirty-tree domain module that keeps a single allowed inward edge to ports.

This allowed edge is present so the dirty tree proves hecate flags only the
forbidden edges (see ``adapter_breach`` and ``external_breach``) and not the
legitimate ``fixture_domain -> fixture_ports`` dependency.
"""

import fixture_pkg.fixture_ports.protocols as _ports

PORTS = _ports
