from itertools import chain
from random import Random
import math

from ssz.constants import (
    CHUNK_SIZE
)
from ssz.sedes import (
    UInt,
    Vector,
)

from renderers import (
    render_test_case,
    render_test,
)


random = Random(0)


ELEMENT_SIZES = (1, 2, 8, 32)
MAX_SIZE = 1024
MAX_NUM_CHUNKS = MAX_SIZE // CHUNK_SIZE

NUM_TESTS_PER_TYPE_AND_SIZE = 8


def get_random_vector_value(sedes):
    uint_size = sedes.element_sedes.size
    return tuple(
        random.randint(0, 8**uint_size - 1)
        for _ in range(sedes.length)
    )


def generate_single_element_vector_tests():
    for _ in range(NUM_TESTS_PER_TYPE_AND_SIZE):
        for element_size in ELEMENT_SIZES:
            sedes = Vector(UInt(element_size * 8), 1)
            for _ in range(MAX_NUM_CHUNKS):
                yield render_test_case(
                    sedes=sedes,
                    value=get_random_vector_value(sedes),
                    tags=["vector", "basic", "single-element"]
                )


def generate_single_chunk_vector_tests():
    for _ in range(NUM_TESTS_PER_TYPE_AND_SIZE):
        for element_size in ELEMENT_SIZES:
            length = CHUNK_SIZE // element_size
            sedes = Vector(UInt(element_size * 8), length)
            yield render_test_case(
                sedes=sedes,
                value=get_random_vector_value(sedes),
                tags=["vector", "basic", "single-chunk"]
            )


def generate_no_padding_vector_tests():
    for element_size in ELEMENT_SIZES:
        element_sedes = UInt(element_size * 8)

        for _ in range(NUM_TESTS_PER_TYPE_AND_SIZE):
            elements_per_chunk = CHUNK_SIZE // element_size
            num_chunks = random.randint(1, MAX_NUM_CHUNKS)
            length = num_chunks * elements_per_chunk

            sedes = Vector(element_sedes, length)
            yield render_test_case(
                sedes=sedes,
                value=get_random_vector_value(sedes),
                tags=["vector", "basic", "no-padding"]
            )


def generate_chunk_padding_vector_tests():
    for element_size in tuple(size for size in ELEMENT_SIZES if size != CHUNK_SIZE):
        element_sedes = UInt(element_size * 8)

        for _ in range(NUM_TESTS_PER_TYPE_AND_SIZE):
            num_chunks_approximate = random.randint(1, MAX_NUM_CHUNKS)
            num_chunks = int(2**math.log2(num_chunks_approximate))  # round to nearest power of two

            num_elements_in_full_chunks = CHUNK_SIZE // element_size
            num_elements_in_last_chunk = random.randint(1, num_elements_in_full_chunks - 1)

            length = num_elements_in_full_chunks * num_chunks + num_elements_in_last_chunk
            sedes = Vector(element_sedes, length)
            yield render_test_case(
                sedes=sedes,
                value=get_random_vector_value(sedes),
                tags=["vector", "basic", "chunk-padding"]
            )


def generate_leaf_padding_vector_tests():
    for element_size in ELEMENT_SIZES:
        element_sedes = UInt(element_size * 8)

        for _ in range(NUM_TESTS_PER_TYPE_AND_SIZE):
            num_chunks = random.randint(1, MAX_NUM_CHUNKS)

            length = num_chunks * CHUNK_SIZE // element_size
            sedes = Vector(element_sedes, length)
            yield render_test_case(
                sedes=sedes,
                value=get_random_vector_value(sedes),
                tags=["vector", "basic", "leaf-padding"]
            )


def generate_leaf_and_chunk_padding_vector_tests():
    for element_size in ELEMENT_SIZES:
        element_sedes = UInt(element_size * 8)

        for _ in range(NUM_TESTS_PER_TYPE_AND_SIZE):
            length = random.randint(1, MAX_SIZE // element_size)
            sedes = Vector(element_sedes, length)
            yield render_test_case(
                sedes=sedes,
                value=get_random_vector_value(sedes),
                tags=["vector", "basic", "chunk-padding", "leaf-padding"]
            )


def generate_basic_vector_test():
    return render_test(
        title="Basic Vectors",
        summary="Tree hash tests for vectors of basic types",
        version="0.1",
        test_cases=chain(
            generate_single_element_vector_tests(),
            generate_single_chunk_vector_tests(),
            generate_no_padding_vector_tests(),
            generate_chunk_padding_vector_tests(),
            generate_leaf_padding_vector_tests(),
            generate_leaf_and_chunk_padding_vector_tests(),
        )
    )
