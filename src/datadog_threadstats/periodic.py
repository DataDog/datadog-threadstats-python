# Unless explicitly stated otherwise all files in this repository are licensed under the Apache-2.0 License.
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2023-Present Datadog, Inc.

from threading import Thread, Event


class PeriodicTask:
    def __init__(self, task, interval=60):
        self.task = task
        self.interval = interval
        self.event = Event()

    def start(self):
        thread = Thread(target=self.run, daemon=True)
        thread.start()

    def run(self):
        while not self.event.wait(self.interval):
            self.task()
