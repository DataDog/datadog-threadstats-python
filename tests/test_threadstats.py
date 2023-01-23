# Unless explicitly stated otherwise all files in this repository are licensed under the Apache-2.0 License.
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2023-Present Datadog, Inc.

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

    assert stats._metric_series == [
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

    assert stats._metric_series == [
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
        ),
    ]

    calls = []
    stats._metrics_api.submit_metrics = calls.append

    stats._flush()
    assert calls == [
        MetricPayload(
            series=[
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
                ),
            ]
        )
    ]

    assert stats._metric_series == []


@freeze_time()
def test_count_tags():
    stats = ThreadStats()
    stats.count("mymetric", tags=["host:myhost"])

    assert stats._metric_series == [
        MetricSeries(
            metric="mymetric",
            tags=["host:myhost"],
            type=MetricIntakeType.COUNT,
            points=[
                MetricPoint(
                    timestamp=int(datetime.now().timestamp()),
                    value=1.0,
                )
            ],
        )
    ]


@freeze_time()
def test_log():
    stats = ThreadStats()
    stats.log("First log", source="python")
    assert stats._log_items == [HTTPLogItem(message="First log", ddsource="python")]

    stats.log("Second log", service="myapp")
    assert stats._log_items == [
        HTTPLogItem(message="First log", ddsource="python"),
        HTTPLogItem(message="Second log", service="myapp"),
    ]

    calls = []
    stats._logs_api.submit_log = calls.append

    stats._flush()
    assert calls == [
        HTTPLog(
            [HTTPLogItem(message="First log", ddsource="python"), HTTPLogItem(message="Second log", service="myapp")]
        )
    ]

    assert stats._log_items == []
