import threading
import collections
import datetime

class VMPool:
    class Timeout(Exception):
        def __str__(self):
            return "Operation timed out."

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

    def put(self, vm, timeout = None):
        # Note that even if timeout is false here, we still acquire the lock. So
        # there may be a non-negligible waiting time.
        self.not_full.acquire()

        try:
            self.wait_for_not_full(timeout = timeout)
            self._queue.appendleft(vm)
            self.not_empty.notify()
        finally:
            self.not_full.release()

    def get(self, key, timeout = None):
        # Note that even if timeout is false here, we still acquire the lock. So
        # there may be a non-negligible waiting time.
        self.not_empty.acquire()

        try:
            assert key not in self._map
            self.wait_for_not_empty(timeout = timeout)
            vm = self._queue.pop()
            self._map[key] = vm
            self.not_full.notify()
            return vm
        finally:
            self.not_empty.release()

    def __len__(self):
        with self._rlock:
            return len(self._queue) + len(self._map)

    def full(self):
        with self._rlock:
            return len(self) >= self.max_size

    def empty(self):
        with self._rlock:
            return len(self._queue) == 0

    def _wait_for_condition(self, condition, expression, timeout = None,
            release = True):
        condition.acquire()

        if timeout is None:
            deadline = datetime.datetime.max
        else:
            deadline = datetime.datetime.today() + timeout

        while True:
            now = datetime.datetime.today()
            if expression() or now >= deadline:
                break

            # Replacement of datetime's total_seconds method compatible with
            # Pythons < 2.7.
            total_seconds = \
                lambda td: (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10.0**6

            condition.wait(
                timeout = min(1, total_seconds(deadline - now))
            )

        if release:
            condition.release()

        if not expression():
            raise VMPool.Timeout()

    def wait_for_not_empty(self, timeout = None, release = True):
        return self._wait_for_condition(
            self.not_empty, lambda: not self.empty(), timeout, release
        )

    def wait_for_not_full(self, timeout = None, release = True):
        return self._wait_for_condition(
            self.not_full, lambda: not self.full(), timeout, release
        )

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
shutdown = False
def main():
    pool = VMPool(10)

    def produce():
        for i in xrange(9999):
            print "Adding", i
            pool.put(i)

        while len(pool) != 0:
            time.sleep(1)

        global shutdown
        shutdown = True

    def consume():
        current_thread = threading.current_thread()
        while not shutdown:
            try:
                a = pool.get(current_thread, timeout = datetime.timedelta(seconds = 1))
            except VMPool.Timeout:
                continue

            print "Consuming", a

            pool.destroy(current_thread)

    producers = []
    for i in xrange(1):
        t = threading.Thread(target = produce)
        #t.daemon = True
        t.start()

    consumers = []
    for i in xrange(100):
        t = threading.Thread(target = consume)
        #t.daemon = True
        t.start()

    print producers, consumers

if __name__ == "__main__":
    main()
