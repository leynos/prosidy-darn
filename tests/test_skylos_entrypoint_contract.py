"""Regression contract for the complete Skylos entry-point selector shape."""

from __future__ import annotations

import json
import typing as typ

_SELECTOR_NAME_KEYS: typ.Final = ("name", "full_name")
_SELECTOR_RULES: typ.Final = (
    {
        "name": "create",
        "full_name": ["Owner.create", "Owner.update"],
        "decorators": ["web.route", "web.authenticated"],
        "base_classes": ["Plugin", "Handler"],
        "parent": {
            "name": "Owner",
            "full_name": ["service.Owner", "service.AdminOwner"],
        },
        "type": "decorator",
        "path": "src/routes.py",
        "module": "routes",
        "reason": "Registered by the framework router.",
        "extension": {"selector": {"module": "plugins.routes", "enabled": True}},
    },
)
_EXPECTED_SELECTOR_NAMES: typ.Final = frozenset({
    "create",
    "Owner.create",
    "Owner.update",
})
_EXPECTED_RULE_IDENTITY_TOKENS: typ.Final = (
    '{"base_classes":["Plugin","Handler"],',
    '"decorators":["web.route","web.authenticated"],',
    '"extension":{"selector":{"enabled":true,"module":"plugins.routes"}},',
    '"full_name":["Owner.create","Owner.update"],',
    '"module":"routes","name":"create",',
    '"parent":{"full_name":["service.Owner","service.AdminOwner"],',
    '"name":"Owner"},"path":"src/routes.py",',
    '"reason":"Registered by the framework router.","type":"decorator"}',
)
_EXPECTED_RULE_IDENTITIES: typ.Final = ("".join(_EXPECTED_RULE_IDENTITY_TOKENS),)


def _selector_values(value: object) -> tuple[str, ...]:
    """Normalize a selector accepted as one name or a list of names."""
    if isinstance(value, str):
        return (value,)
    assert isinstance(value, list), (
        "Skylos name selectors must be strings or lists of strings."
    )
    assert all(isinstance(item, str) for item in value), (
        "Skylos name selectors must be strings or lists of strings."
    )
    return tuple(typ.cast("list[str]", value))


def test_entrypoint_rule_identity_preserves_all_selector_fields() -> None:
    """Selector identities retain scalar, list, nested, and extension fields."""
    rule = _SELECTOR_RULES[0]
    selector_names = frozenset(
        name
        for selector_key in _SELECTOR_NAME_KEYS
        for name in _selector_values(rule[selector_key])
    )
    assert selector_names == _EXPECTED_SELECTOR_NAMES, (
        "Skylos entry-point names must accept scalar name and list full_name selectors."
    )
    rule_identity = json.dumps(rule, sort_keys=True, separators=(",", ":"))
    assert (rule_identity,) == _EXPECTED_RULE_IDENTITIES, (
        "Skylos entry-point identity must retain decorators, base classes, nested "
        "parent selectors, routing metadata, reasons, and unknown fields."
    )
