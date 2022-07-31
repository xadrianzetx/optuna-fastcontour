# cython: language_level=3
# distutils: language=c++

cimport cython
from libc.math cimport INFINITY
from libcpp cimport bool
from libcpp.vector cimport vector

from fastcontour._queue cimport clear_queue
from fastcontour._queue cimport create_node
from fastcontour._queue cimport insert_descending
from fastcontour._queue cimport QueueNode

import numpy as np

cimport numpy as np


np.import_array()
ctypedef np.float64_t DOUBLE_t


cdef struct Point:
    DOUBLE_t value
    bool is_queued
    bool has_value


@cython.boundscheck(False)
@cython.wraparound(False)
def _interpolate(
    DOUBLE_t[::1] x_values,
    DOUBLE_t[::1] y_values,
    DOUBLE_t[::1] z_values,
    DOUBLE_t[::1] xaxis,
    DOUBLE_t[::1] yaxis,
    int n_points
):

    cdef:
        vector[Point] p
        Py_ssize_t i, index
        unsigned int known, missing, xindex, yindex, iter = 100
        DOUBLE_t delta = 1.0, threshold = 0.01

    known = z_values.shape[0]
    missing = n_points**2
    p = vector[Point](n_points**2)
    for i in range(known):
        xindex = _snap_to_grid(xaxis, x_values[i])
        yindex = _snap_to_grid(yaxis, y_values[i])
        index = yindex * n_points + xindex

        if not p[index].has_value:
            # It's possible to "snap" into already occupied space on grid.
            # Conflicting z-values should be close, so we can forget one.
            p[index].value = z_values[i]
            p[index].has_value = True
            p[index].is_queued = True
            missing -= 1

    q = _set_interpolation_order(p, n_points, missing)
    _run_iteration(p, q, delta, n_points)
    for i in range(iter):
        if delta > threshold:
            delta = 0.5 - 0.25 * min(1, delta * 0.5)
            delta = _run_iteration(p, q, delta, n_points)
        else:
            break

    result = np.zeros(n_points**2, dtype=np.float64)
    cdef DOUBLE_t [::1] result_view = result
    for i in range(n_points**2):
        result_view[i] = p[i].value

    return result


cdef int _snap_to_grid(DOUBLE_t[::1] axis, DOUBLE_t value):

    cdef:
        int pos = 0
        Py_ssize_t tick, ticks = axis.shape[0]
        DOUBLE_t diff, min_diff = INFINITY

    for tick in range(ticks):
        diff = abs(axis[tick] - value)
        if diff < min_diff:
            pos = tick
            min_diff = diff

    return pos


@cython.cdivision(True)
cdef vector[int] _set_interpolation_order(vector[Point]& p, int n_points, unsigned int missing):

    cdef:
        int index, adjacent, offset
        unsigned int n_adjacent, queued = 0
        vector[int] order, offsets
        QueueNode* current
        QueueNode* inserted
        QueueNode* queue_head = NULL

    # Offsets -1 and 1 are xaxis, -n_points and n_points are yaxis.
    offsets = (-1, 1, -1 * n_points, n_points)
    order.reserve(missing)
    while queued != missing:
        clear_queue(&queue_head)
        for index in range(n_points**2):
            if p[index].is_queued:
                continue

            n_adjacent = 0
            for offset in offsets:
                adjacent = index + offset
                if (offset == 1 and adjacent % n_points == 0) or (offset == -1 and index % n_points == 0):
                    # Ignore adjacent as it's overflow from previous or next column.
                    continue

                if adjacent >= 0 and adjacent < n_points**2:
                    if p[adjacent].is_queued:
                        n_adjacent += 1

            if n_adjacent > 0:
                inserted = create_node(index, n_adjacent)
                insert_descending(&queue_head, inserted)

        current = queue_head
        while current:
            p[current.index].is_queued = True
            order.push_back(current.index)
            queued += 1
            current = current.next

    clear_queue(&queue_head)
    return order


@cython.cdivision(True)
cdef DOUBLE_t _run_iteration(vector[Point]& p, vector[int]& q, DOUBLE_t delta, int n_points):

    cdef:
        bool has_value
        int index, adjacent, offset
        DOUBLE_t min_adjacent, max_adjacent, sum_adjacent, n_adjacent
        DOUBLE_t interp, current, new_delta, max_delta = 1.0
        vector[int] offsets

    offsets = (-1, 1, -1 * n_points, n_points)
    for index in q:
        max_adjacent = INFINITY
        min_adjacent = -INFINITY
        sum_adjacent = 0.0
        n_adjacent = 0.0
        has_value = p[index].has_value

        for offset in offsets:
            adjacent = index + offset
            if (offset == 1 and adjacent % n_points == 0) or (offset == -1 and index % n_points == 0):
                continue

            if adjacent >= 0 and adjacent < n_points**2:
                if p[adjacent].has_value:
                    n_adjacent += 1.0
                    sum_adjacent += p[adjacent].value

            if has_value:
                max_adjacent = max(max_adjacent, p[adjacent].value)
                min_adjacent = min(min_adjacent, p[adjacent].value)

        interp = sum_adjacent / n_adjacent
        if not has_value:
            p[index].value = interp
            max_delta = 1.0
        else:
            current = p[index].value
            p[index].value = (1 + delta) * interp - delta * current
            if max_adjacent > min_adjacent:
                new_delta = abs(interp - current) / (max_adjacent - min_adjacent)
                max_delta = max(delta, new_delta)

        p[index].has_value = True

    return max_delta
