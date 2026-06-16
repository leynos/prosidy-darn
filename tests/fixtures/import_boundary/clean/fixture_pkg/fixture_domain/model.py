"""Clean-tree domain module importing an allowed inward edge to ports.

hecate classifies imports by parsing this file with the standard-library
``ast`` module; the module is never executed. The import is bound to a
module-level name so the repository's own linter does not report it as unused
while hecate still observes the ``fixture_domain -> fixture_ports`` edge.
"""

import fixture_pkg.fixture_ports.protocols as _ports

PORTS = _ports
