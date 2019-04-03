from itertools import (
    chain,
)
from random import Random

from ssz.sedes import (
    boolean,
    UInt,
)

from renderers import (
    render_test_case,
    render_test,
)


random = Random(0)

UINT_SIZES = tuple(8 * 2**exponent for exponent in range(0, 6))  # 8, 16, ..., 256
NUM_UINT_VALUES = 8


def generate_uint_test_cases():
    for bit_size in UINT_SIZES:
        sedes = UInt(bit_size)
        max_int = 2**bit_size - 1

        values = tuple(
            random.randint(0, max_int) for _ in range(NUM_UINT_VALUES)
        )

        for value in values:
            yield render_test_case(
                sedes=sedes,
                value=value,
                tags=["basic", "uint"],
            )


def generate_bool_test_cases():
    for value in (True, False):
        yield render_test_case(
            sedes=boolean,
            value=value,
            tags=["basic", "bool"],
        )


def generate_basic_test():
    return render_test(
        title="Basic Types",
        summary="Tree hash tests for bools and uints",
        version="0.1",
        test_cases=chain(
            generate_bool_test_cases(),
            generate_uint_test_cases(),
        )
    )
