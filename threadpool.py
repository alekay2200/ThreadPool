from threading import Thread, Lock, Semaphore
from typing import List, Any, Tuple, Union

class ThreadPool:

    __queue_task: List[Tuple[callable, List[Any]]] # List of task to execute
    __max_workers: int
    __queue_lock: Lock

    def __init__(self, workers: int):
        self.__max_workers = workers
        self.__queue_lock = Lock()
        self.__queue_task = list()
        self.__stop = False
        self.__stop_lock = Lock()
        self.__sem_task = Semaphore(workers)
        self.__join_lock = Lock()
        self.__join_lock.acquire()
        Thread(target=self.__execute_next_task).start()


    def __get_next_task_sync(self) -> Union[None, Tuple[callable, List[Any]]]:
        self.__queue_lock.acquire()
        task: Tuple[callable, List[Any]] = self.__queue_task.pop(0) if len(self.__queue_task) > 0 else None
        self.__queue_lock.release()
        return task

    def __get_stop(self) -> bool:
        self.__stop_lock.acquire()
        stop = self.__stop
        self.__stop_lock.release()
        return stop

    def __set_stop(self, b: bool):
        self.__stop_lock.acquire()
        self.__stop = b
        self.__stop_lock.release()

    def __tasks_empty(self) -> bool:
        self.__queue_lock.acquire()
        empty = len(self.__queue_task) == 0
        self.__queue_lock.release()
        return empty

    def __execute_task(self, callback, args):
        callback(*args)
        # When the tasks is finished release the permission
        self.__sem_task.release()

    def __execute_next_task(self):
        while not self.__get_stop() or not self.__tasks_empty():
            task = self.__get_next_task_sync()
            if task is not None:
                callback, args = task
                self.__sem_task.acquire()
                Thread(target=self.__execute_task, args=[callback, args]).start()

        for _ in range(self.__max_workers):
            # Get all permissions in order to wait until all threads finished
            self.__sem_task.acquire()

        self.__join_lock.release()

    def execute(self, target: callable, args: List[Any] = []):
        if not self.__get_stop():
            self.__queue_lock.acquire()
            self.__queue_task.append((target, args))
            self.__queue_lock.release()

    def join(self):
        """
        Wait until all tasks are finished 
        """
        self.__set_stop(True)    
        self.__join_lock.acquire()
        self.__join_lock.release()

    def __del__(self):
        # Wait until all tasks are finished before destroy the object
        self.join()


def printer(number: int):
    print("Im thread ", number, flush=True)

if __name__ == "__main__":

    pool = ThreadPool(5)
    
    for i in range(20):
        pool.execute(printer, args=[i])

    pool.join()