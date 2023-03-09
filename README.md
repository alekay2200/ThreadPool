# ThreadPool
ThreadPool written in Python

This is a simple project just to define a pool with a maximum number of threads and use the execute method to queue tasks to be executed when the pool has slot available.

```python
if __name__ == "__main__":
    
    # Define a Thread Pool with 5 threads maximum
    pool = ThreadPool(5)
    
    for i in range(20):
        # 'execute method' enqueues tasks without blocking
        pool.execute(printer, args=[i])
    
    # wait until all tasks are completed
    pool.join()
```
