import threading    


class SafeThread(threading.Thread):
    """
    Safe cyclic thread, with stop function 
    Args:
        threading (Thread): Thred object
    """

    def __init__(self, target):
        threading.Thread.__init__(self)
        self.daemon = True
        self.target = target
        self.stop_ev = threading.Event()

    def stop(self):
        self.stop_ev.set()

    def run(self):
        while not self.stop_ev.is_set():
            self.target()