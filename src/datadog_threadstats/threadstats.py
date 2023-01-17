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
        self.metric_series = []
        self.log_items = []

    def start(self):
        self.periodic_task.start()

    def log(self, message, source=None, hostname=None, service=None, tags=None):
        kwargs = {"message": message}
        if source is not None:
            kwargs["ddsource"] = source
        if hostname is not None:
            kwargs["hostname"] = hostname
        if service is not None:
            kwargs["service"] = service
        if tags is not None:
            kwargs["ddtags"] = tags

        self.log_items.append(HTTPLogItem(**kwargs))

    def rate(self, metric_name, value, tags=None):
        self.metric(metric_name, MetricIntakeType.RATE, value, tags)

    def count(self, metric_name, value=1, tags=None):
        self.metric(metric_name, MetricIntakeType.COUNT, value, tags)

    def gauge(self, metric_name, value, tags=None):
        self.metric(metric_name, MetricIntakeType.GAUGE, value, tags)

    def metric(self, metric_name, metric_type, value, tags=None):
        self.metric_series.append(
            MetricSeries(
                metric=metric_name,
                type=metric_type,
                points=[
                    MetricPoint(
                        timestamp=int(datetime.now().timestamp()),
                        value=value,
                    )
                ],
            )
        )

    def flush(self):
        metric_series, self.metric_series = self.metric_series, []
        if metric_series:
            payload = MetricPayload(series=metric_series)
            self.metrics_api.submit_metrics(payload)

        log_items, self.log_items = self.log_items, []
        if log_items:
            payload = HTTPLog(log_items)
            self.logs_api.submit_log(payload)
