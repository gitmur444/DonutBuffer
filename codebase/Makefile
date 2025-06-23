all: ring_buffer

mutex_ring_buffer.o: ../src/ringbuffer/mutex_ring_buffer.cpp
	g++ -std=c++17 -I../src -c ../src/ringbuffer/mutex_ring_buffer.cpp -o mutex_ring_buffer.o

ring_buffer: ring_buffer.cpp mutex_ring_buffer.o
	g++ -std=c++17 -I../src ring_buffer.cpp mutex_ring_buffer.o -o ring_buffer

clean:
	rm -f ring_buffer mutex_ring_buffer.o
