# Unless explicitly stated otherwise all files in this repository are licensed under the Apache-2.0 License.
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2023-Present Datadog, Inc.

from .periodic import PeriodicTask

from datetime import datetime
from typing import Any, Dict, List, Optional

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
    """Asynchronous and aggregation manager for the Datadog API.

    This provides a non-blocking integration point for metrics and logs, with submission happening in a background thread.

    :param configuration: Configuration for the API client.
    :type configuration: Configuration

    :param flush_interval: Number of seconds between each flush.
    :type flush_interval: int
    """

    def __init__(self, configuration: Optional[Configuration] = None, flush_interval: int = 60):
        if configuration is None:
            configuration = Configuration()
        self._api_client = ApiClient(configuration)
        self._metrics_api = MetricsApi(self._api_client)
        self._logs_api = LogsApi(self._api_client)
        self._periodic_task = PeriodicTask(self._flush, flush_interval)
        self._metric_series: List[MetricSeries] = []
        self._log_items: List[HTTPLogItem] = []

    def start(self) -> None:
        """Start the background task."""
        self._periodic_task.start()

    def log(
        self,
        message: str,
        source: Optional[str] = None,
        hostname: Optional[str] = None,
        service: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Add a pending log to send.

        :param message: The log message.
        :type message: str

        :param source: The identified log source, which should match a known source in Datadog.
        :type source: str

        :param hostname: The host associated with the log.
        :type hostname: str

        :param service: The service identifier for the log.
        :type service: str

        :param tags: The tags associated with the log.
        :type log: list
        """
        kwargs: Dict[str, Any] = {"message": message}
        if source is not None:
            kwargs["ddsource"] = source
        if hostname is not None:
            kwargs["hostname"] = hostname
        if service is not None:
            kwargs["service"] = service
        if tags is not None:
            kwargs["ddtags"] = tags

        self._log_items.append(HTTPLogItem(**kwargs))

    def count(self, metric_name: str, value: float = 1, tags: Optional[List[str]] = None) -> None:
        """Add a pending count metric to send.

        :param metric_name: The name of the metric.
        :type metric_name: str

        :param value: The value for the data point.
        :type value: float

        :param tags: The tags associated with the data point.
        :type tags: list
        """
        self.metric(metric_name, MetricIntakeType.COUNT, value, tags)

    def gauge(self, metric_name: str, value: float, tags: Optional[List[str]] = None) -> None:
        """Add a pending gauge metric to send.

        :param metric_name: The name of the metric.
        :type metric_name: str

        :param value: The value for the data point.
        :type value: float

        :param tags: The tags associated with the data point.
        :type tags: list
        """
        self.metric(metric_name, MetricIntakeType.GAUGE, value, tags)

    def rate(self, metric_name: str, value: float, tags: Optional[List[str]] = None) -> None:
        """Add a pending rate metric to send.

        :param metric_name: The name of the metric.
        :type metric_name: str

        :param value: The value for the data point.
        :type value: float

        :param tags: The tags associated with the data point.
        :type tags: list
        """
        self.metric(metric_name, MetricIntakeType.RATE, value, tags)

    def metric(self, metric_name: str, metric_type: MetricIntakeType, value: float, tags: Optional[List[str]] = None) -> None:
        """Add a pending metric to send.

        :param metric_name: The name of the metric.
        :type metric_name: str

        :param metric_type: The type of the metric.
        :type metric_type: MetricIntakeType

        :param value: The value for the data point.
        :type value: float

        :param tags: The tags associated with the data point.
        :type tags: list
        """
        series_args = {
            "metric": metric_name,
            "type": metric_type,
            "points": [
                MetricPoint(
                    timestamp=int(datetime.now().timestamp()),
                    value=value,
                )
            ],
        }
        if tags is not None:
            series_args["tags"] = tags
        self._metric_series.append(MetricSeries(**series_args))

    def _flush(self) -> None:
        """Flush data points accumulated during last interval."""
        metric_series, self._metric_series = self._metric_series, []
        if metric_series:
            metric_payload = MetricPayload(series=metric_series)
            self._metrics_api.submit_metrics(metric_payload)

        log_items, self._log_items = self._log_items, []
        if log_items:
            log_payload = HTTPLog(log_items)
            self._logs_api.submit_log(log_payload)
