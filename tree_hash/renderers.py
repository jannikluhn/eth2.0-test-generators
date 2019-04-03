from collections.abc import (
    Mapping,
    Sequence,
)

from eth_utils import (
    encode_hex,
    to_dict,
)

import ssz
from ssz.sedes import (
    BaseSedes,
    Boolean,
    Container,
    List,
    UInt,
    Vector,
)


def render_value(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, bytes):
        return encode_hex(value)
    elif isinstance(value, Sequence):
        return tuple(render_value(element) for element in value)
    elif isinstance(value, Mapping):
        return render_dict_value(value)
    else:
        raise ValueError(f"Cannot render value {value}")


@to_dict
def render_dict_value(value):
    for key, value in value.items():
        yield key, render_value(value)


def render_type_definition(sedes):
    if isinstance(sedes, Boolean):
        return "bool"

    elif isinstance(sedes, UInt):
        return f"uint{sedes.size * 8}"

    elif isinstance(sedes, Vector):
        return [render_type_definition(sedes.element_sedes), sedes.length]

    elif isinstance(sedes, List):
        return [render_type_definition(sedes.element_sedes)]

    elif isinstance(sedes, Container):
        return {
            field_name: render_type_definition(field_sedes)
            for field_name, field_sedes in sedes.fields
        }

    elif isinstance(sedes, BaseSedes):
        raise Exception("Unreachable: All sedes types have been checked")

    else:
        raise TypeError("Expected BaseSedes")


@to_dict
def render_test_case(*, sedes, value, tags=None):
    yield "type", render_type_definition(sedes)
    yield "value", render_value(value)
    yield "root", encode_hex(ssz.hash_tree_root(value, sedes))
    yield "tags", tags or []


@to_dict
def render_test(*, title, summary, version, test_cases):
    yield "title", title,
    if summary is not None:
        yield "summary", summary
    yield "version", version
    yield "test_cases", tuple(test_cases)
