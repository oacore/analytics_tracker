from flask import *
import os

from flask import request
import multiprocessing
import json
import settings

app = Flask(__name__)

trackedEvents = []


def track(tracker_content):
    global trackedEvents
    trackedEvents.append(tracker_content)
    app.logger.debug(f"logged {len(trackedEvents)} events")
    if len(trackedEvents) == settings.BUFFER_SIZE:
        app.logger.info(f"reached {settings.BUFFER_SIZE} writing async")
        write_async(trackedEvents)
        trackedEvents.clear()


def write_async(tracked_events):
    thread = multiprocessing.Process(target=write_to_file, args=(tracked_events,))
    thread.start()


def write_to_file(tracked_events):
    with open(settings.OUTPUT_FILE, "a") as fw:
        for event in tracked_events:
            app.logger.debug("save event")
            fw.write(json.dumps(event) + "\n")


@app.route("/tracker", methods=['POST'])
def tracker():
    tracker_content = request.json
    track(tracker_content)
    return "OK"


@app.route("/")
def home():
    return "I am a tracker"


if __name__ == "__main__":
    if os.getenv("debug"):
        app.run(debug=True)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5050)
