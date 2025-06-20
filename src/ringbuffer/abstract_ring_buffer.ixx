export module ringbuffer.abstract_ring_buffer;

#include <cstddef>

export class AbstractRingBuffer {
public:
    virtual ~AbstractRingBuffer() = default;
    virtual void push(int value) = 0;
    virtual bool pop(int& value) = 0;
    virtual size_t size() const = 0;
    virtual size_t capacity() const = 0;
};
