from threading import Thread, Event


class PeriodicTask:

    def __init__(self, task):
        self.task = task
        self.interval = 60
        self.event = Event()

    def start(self):
        thread = Thread(target=self.run, daemon=True)
        thread.start()

    def run(self):
        while not self.event.wait(self.interval):
            self.task()
