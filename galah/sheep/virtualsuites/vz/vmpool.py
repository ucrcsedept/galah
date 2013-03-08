import threading
import collections

class VMPool:
    def __init__(self, max_size):
        self.max_size = max_size

        self._queue = collections.deque()
        self._map = {}
        self._rlock = threading.RLock()

        self.not_full = threading.Condition(self._rlock)
        self.not_empty = threading.Condition(self._rlock)

    def destroy(self, key):
        with self._rlock:
            del self._map[key]

    def add(self, vm):
        self.not_full.acquire()

        while len(self._queue) >= self.max_size:
            self.not_full.wait()

        try:
            self._queue.appendleft(vm)
            self.not_empty.notify()
        finally:
            self.not_full.release()

    def pop(self, key):
        self.not_empty.acquire()

        while not self._queue:
            self.not_empty.wait()

        try:          
            assert key not in self._map
            vm = self._queue.pop()
            self._map[key] = vm
            self.not_full.notify()
            return vm
        finally:
            self.not_empty.release()

    def __len__(self):
        with self._rlock:
            return len(self._queue) + len(self._map)

    def __getitem__(self, key):
        with self._rlock:
            return self._map[key]

    def __delitem__(self, key):
        with self._rlock:
            return destroy(key)

    def __contains__(self, key):
        with self._rlock:
            return key in self._map

import time
def main():
    pool = VMPool(10)

    def produce():
        for i in xrange(9999):
            pool.add(i)

    def consume():
        current_thread = threading.current_thread()
        while True:
            a = pool.pop(current_thread)
            print "Consuming", a

            pool.destroy(current_thread)

    producers = []
    for i in xrange(3):
        t = threading.Thread(target = produce)
        #t.daemon = True
        t.start()

    consumers = []
    for i in xrange(100):
        t = threading.Thread(target = consume)
        #t.daemon = True
        t.start()

    print producers, consumers
