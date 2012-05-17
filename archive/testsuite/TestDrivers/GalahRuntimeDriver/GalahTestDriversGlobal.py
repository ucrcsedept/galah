# Licensed under PSF, replace with own code to avoid conflictions.
## {{{ http://code.activestate.com/recipes/473878/ (r1)
def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None
            self.daemon = True

        def run(self):
            #try:
                self.result = func(*args, **kwargs)
            #except:
            #    self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
		return default
    else:
        return it.result
## end of http://code.activestate.com/recipes/473878/ }}}
