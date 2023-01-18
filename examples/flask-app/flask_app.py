import resource

from flask import Flask

from datadog_threadstats import ThreadStats

stats = ThreadStats()
stats.start()
app = Flask(__name__)


@app.route("/")
def hello_world():
    stats.count("myflask.home.hits")
    stats.log("GET called on /")
    memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    stats.gauge("myflask.memory", memory_usage)
    return "<p>Hello, World!</p>"
