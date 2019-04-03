from renderers import (
    render_test,
    render_test_case,
)

from random import Random

from ssz.sedes import (
    Boolean,
    Container,
    UInt,
    boolean,
)


random = Random(0)

UINT_SIZES = tuple(8 * 2**exponent for exponent in range(0, 6))  # 8, 16, ..., 256
LENGTHS = (1, 2, 3, 4, 5, 7, 8, 9, 15, 16, 17, 32)
NUM_TESTS_PER_LENGTH = 8


def get_random_basic_value(sedes):
    if isinstance(sedes, Boolean):
        return random.choice((True, False))
    elif isinstance(sedes, UInt):
        return random.randint(0, 8**sedes.size)
    else:
        raise ValueError("Neither bool nor UInt")


def get_random_basic_sedes():
    return random.choice((
        boolean,
    ) + tuple(
        UInt(bit_size)
        for bit_size in UINT_SIZES
    ))


def generate_basic_container_test_cases():
    for _ in range(NUM_TESTS_PER_LENGTH):
        for length in LENGTHS:
            field_names = tuple(
                f"field{index}" for index in range(length)
            )
            field_sedes_objects = tuple(
                get_random_basic_sedes() for _ in range(length)
            )
            sedes = Container(tuple(
                (field_name, field_sedes)
                for field_name, field_sedes in zip(field_names, field_sedes_objects)
            ))
            value = {
                field_name: get_random_basic_value(field_sedes)
                for field_name, field_sedes in zip(field_names, field_sedes_objects)
            }
            yield render_test_case(
                sedes=sedes,
                value=value,
                tags=["container", "basic"]
            )


def generate_basic_container_test():
    return render_test(
        title="Basic Containers",
        summary="Tree hash tests for containers of basic types",
        version="0.1",
        test_cases=generate_basic_container_test_cases(),
    )
