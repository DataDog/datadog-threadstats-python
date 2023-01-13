from datetime import datetime

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries


class ThreadStats:

    def __init__(self):
        self.api_client = ApiClient(Configuration())
        self.metrics_api = MetricsApi(self.api_client)

    def start(self):
        pass

    def increment(self, metric):
        payload = MetricPayload(
            series=[
                MetricSeries(
                    metric=metric,
                    type=MetricIntakeType.COUNT,
                    points=[
                        MetricPoint(
                            timestamp=int(datetime.now().timestamp()),
                            value=1,
                        ),
                    ],
                ),
            ],
        )
        self.metrics_api.submit_metrics(payload)
