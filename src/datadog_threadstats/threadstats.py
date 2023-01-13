from .periodic import PeriodicTask

from datetime import datetime

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries


class ThreadStats:

    def __init__(self):
        self.api_client = ApiClient(Configuration())
        self.metrics_api = MetricsApi(self.api_client)
        self.logs_api = LogsApi(self.api_client)
        self.periodic_task = PeriodicTask(self.flush)
        self.calls = []

    def start(self):
        self.periodic_task.start()

    def log(self, message):
        payload = HTTPLog(
            [
                HTTPLogItem(
                    message=message,
                ),
            ]
        )
        self.calls.append((self.logs_api.submit_log, (payload,)))

    def count(self, metric, value=1):
        payload = MetricPayload(
            series=[
                MetricSeries(
                    metric=metric,
                    type=MetricIntakeType.COUNT,
                    points=[
                        MetricPoint(
                            timestamp=int(datetime.now().timestamp()),
                            value=value,
                        ),
                    ],
                ),
            ],
        )
        self.calls.append((self.metrics_api.submit_metrics, (payload,)))

    def gauge(self, metric, value):
        payload = MetricPayload(
            series=[
                MetricSeries(
                    metric=metric,
                    type=MetricIntakeType.GAUGE,
                    points=[
                        MetricPoint(
                            timestamp=int(datetime.now().timestamp()),
                            value=value,
                        ),
                    ],
                ),
            ],
        )
        self.calls.append((self.metrics_api.submit_metrics, (payload,)))

    def flush(self):
        while self.calls:
            call, call_args = self.calls.pop(0)
            call(*call_args)
