# cython: language_level=3
# distutils: language=c++

cdef struct QueueNode:
    unsigned int index
    unsigned int n_adjacent
    QueueNode* next


cdef:
    QueueNode* create_node(unsigned int index, unsigned int n_adjacent)
    void insert_descending(QueueNode** head_ptr, QueueNode* inserted)
    void clear_queue(QueueNode** head_ptr)
