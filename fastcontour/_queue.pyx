# cython: language_level=3
# distutils: language=c++

from libc.stdlib cimport free
from libc.stdlib cimport malloc


cdef QueueNode* create_node(unsigned int index, unsigned int n_adjacent):

    cdef QueueNode* node = <QueueNode *> malloc(sizeof(QueueNode))

    if not node:
        raise MemoryError()
    
    node.index = index
    node.n_adjacent = n_adjacent
    node.next = NULL
    return node


cdef void insert_descending(QueueNode** head_ptr, QueueNode* inserted):

    cdef QueueNode* node = head_ptr[0]

    if not node:
        head_ptr[0] = inserted
        return

    if node.n_adjacent < inserted.n_adjacent:
        head_ptr[0] = inserted
        head_ptr[0].next = node
        return

    while node.next:
        if node.next.n_adjacent < inserted.n_adjacent:
            break
        node = node.next

    inserted.next = node.next
    node.next = inserted
    return


cdef void clear_queue(QueueNode** head_ptr):

    cdef QueueNode* node = head_ptr[0]
    cdef QueueNode* next

    if not node:
        return

    while node:
        next = node.next
        free(node)
        node = next

    head_ptr[0] = NULL
    return
