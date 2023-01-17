from datetime import datetime
from freezegun import freeze_time

from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries

from datadog_threadstats import ThreadStats


@freeze_time()
def test_gauge():
    stats = ThreadStats()
    stats.gauge("mymetric", 2.0)

    assert stats.metric_series == [
        MetricSeries(
            metric="mymetric",
            type=MetricIntakeType.GAUGE,
            points=[
                MetricPoint(
                    timestamp=int(datetime.now().timestamp()),
                    value=2.0,
                )
            ],
        )
    ]

    stats.gauge("mymetric", 3.0)

    assert stats.metric_series == [
        MetricSeries(
            metric="mymetric",
            type=MetricIntakeType.GAUGE,
            points=[
                MetricPoint(
                    timestamp=int(datetime.now().timestamp()),
                    value=2.0,
                )
            ],
        ),
        MetricSeries(
            metric="mymetric",
            type=MetricIntakeType.GAUGE,
            points=[
                MetricPoint(
                    timestamp=int(datetime.now().timestamp()),
                    value=3.0,
                )
            ],
        )
    ]

    calls = []
    stats.metrics_api.submit_metrics = calls.append

    stats.flush()
    assert calls == [
        MetricPayload(series=[
            MetricSeries(
                metric="mymetric",
                type=MetricIntakeType.GAUGE,
                points=[
                    MetricPoint(
                        timestamp=int(datetime.now().timestamp()),
                        value=2.0,
                    )
                ],
            ),
            MetricSeries(
                metric="mymetric",
                type=MetricIntakeType.GAUGE,
                points=[
                    MetricPoint(
                        timestamp=int(datetime.now().timestamp()),
                        value=3.0,
                    )
                ],
            )
        ])
    ]

    assert stats.metric_series == []


@freeze_time()
def test_log():
    stats = ThreadStats()
    stats.log("First log", source="python")
    assert stats.log_items == [HTTPLogItem(message="First log", ddsource="python")]

    stats.log("Second log", service="myapp")
    assert stats.log_items == [HTTPLogItem(message="First log", ddsource="python"), HTTPLogItem(message="Second log", service="myapp")]

    calls = []
    stats.logs_api.submit_log = calls.append

    stats.flush()
    assert calls == [
        HTTPLog([HTTPLogItem(message="First log", ddsource="python"), HTTPLogItem(message="Second log", service="myapp")])
    ]

    assert stats.log_items == []
