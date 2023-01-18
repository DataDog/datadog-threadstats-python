# datadog-threadstats

This repository contains a Python library wrapper for the Datadog API client to integrate into your application.

## Requirements

- Python >= v3.7

## Installation

```shell
pip install datadog-threadstats
```

## Usage

As the underlying API client, this library will use the `DD_API_KEY` and `DD_APP_KEY` environment variables to authenticate against the Datadog API.

First you need to initialize and start the `ThreadStats` object.
```python
from datadog_threadstats import ThreadStats

stats = ThreadStats()
stats.start()
```

After that you can use it to send metric points and logs.

```python
stats.count("namespace.metric")
stats.log("Log message")
stats.gauge("namespace.othermetric", 2.0)
```

## Author

support@datadoghq.com

