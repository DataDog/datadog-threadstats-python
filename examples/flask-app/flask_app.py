from flask import Flask

from datadog_threadstats import ThreadStats

stats = ThreadStats()
stats.start()
app = Flask(__name__)


@app.route("/")
def hello_world():
    stats.increment("home.page.hits")
    return "<p>Hello, World!</p>"
