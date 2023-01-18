# Unless explicitly stated otherwise all files in this repository are licensed under the Apache-2.0 License.
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2023-Present Datadog, Inc.

from threading import Thread, Event
from typing import Callable


class PeriodicTask:
    """Manages a periodic task in a thread.

    :param task: The task to periodically run.
    :type task: callable

    :param interval: The interval between each task run, in seconds.
    :type interval: int
    """

    def __init__(self, task: Callable, interval: int = 60):
        self._task = task
        self._interval = interval
        self._event = Event()

    def start(self) -> None:
        """Start the periodic task."""
        thread = Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self) -> None:
        """Loop to run in the thread."""
        while not self._event.wait(self._interval):
            self._task()
