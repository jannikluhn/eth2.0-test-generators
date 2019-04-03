import random
from functools import (
    partial,
)
from itertools import (
    product,
)

from ssz.sedes import (
    boolean,
    Boolean,
    Container,
    List,
    UInt,
    Vector,
)

from renderers import (
    render_test_case,
    render_test,
)


NUM_TEST_CASES_PER_TYPE = 8
UINT_SIZES = tuple(8 * 2**exponent for exponent in range(0, 6))  # 8, 16, ..., 256
MAX_LENGTH = 8


def get_random_basic_sedes():
    return random.choice((
        boolean,
    ) + tuple(
        UInt(bit_size)
        for bit_size in UINT_SIZES
    ))


def get_random_list_sedes(element_sedes_factory):
    element_sedes = element_sedes_factory()
    return List(element_sedes)


def get_random_vector_sedes(element_sedes_factory):
    length = random.randint(1, MAX_LENGTH)
    element_sedes = element_sedes_factory()
    return Vector(element_sedes, length)


def get_random_container_sedes(element_sedes_factory):
    length = random.randint(1, MAX_LENGTH)
    fields = tuple(
        (f"field{index}", element_sedes_factory())
        for index in range(length)
    )
    return Container(fields)


def get_random_value(sedes):
    if isinstance(sedes, Boolean):
        return random.choice((True, False))
    elif isinstance(sedes, UInt):
        return random.randint(0, 8**sedes.size)
    elif isinstance(sedes, Vector):
        return tuple(
            get_random_value(sedes.element_sedes)
            for _ in range(sedes.length)
        )
    elif isinstance(sedes, List):
        length = random.randint(1, MAX_LENGTH)
        return tuple(
            get_random_value(sedes.element_sedes)
            for _ in range(length)
        )
    elif isinstance(sedes, Container):
        return {
            field_name: get_random_value(field_sedes)
            for field_name, field_sedes in sedes.fields
        }
    else:
        raise ValueError(f"Cannot generate random value for sedes {sedes}")


def generate_two_layer_composite_test_cases():
    composite_sedes_factories = tuple((
        get_random_list_sedes,
        get_random_vector_sedes,
        get_random_container_sedes,
    ))

    inner_sedes_factories = tuple(
        partial(sedes_factory, get_random_basic_sedes)
        for sedes_factory in composite_sedes_factories
    )
    inner_and_outer_sedes_factories = product(inner_sedes_factories, composite_sedes_factories)
    for inner_sedes_factory, outer_sedes_factory in inner_and_outer_sedes_factories:
        for _ in range(NUM_TEST_CASES_PER_TYPE):
            outer_sedes = outer_sedes_factory(inner_sedes_factory)

            yield render_test_case(
                sedes=outer_sedes,
                value=get_random_value(outer_sedes),
                tags=["composite", "nested"]
            )


def generate_nested_test():
    return render_test(
        title="Nested Composites",
        summary="Tree hash tests for nested composite types",
        version="0.1",
        test_cases=generate_two_layer_composite_test_cases(),
    )
