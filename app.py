import os
import time
import json
from threading import Thread
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from ping3 import ping
import numpy as np


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sla_agent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class PingResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.Column(db.String(100))
    packet_loss = db.Column(db.Float)
    jitter = db.Column(db.Float)
    ping_time = db.Column(db.Float)


with app.app_context():
    db.create_all()


try:
    target_hosts = json.loads(os.environ['TARGET_HOSTS'])
    if not isinstance(target_hosts, list):
        raise ValueError("TARGET_HOSTS должен быть JSON-массивом строк")
    ping_interval = int(os.environ['PING_INTERVAL'])
    sla_threshold = int(os.environ['SLA_THRESHOLD'])  
except Exception as e:
    raise RuntimeError(f"Ошибка конфигурации: {e}")


def ping_target(destination):
    ping_times = []

    while True:
        try:
            response_time = ping(destination)
            if response_time is not None:
                response_time_ms = round(response_time * 1000)
                ping_times.append(response_time_ms)
            else:
                response_time_ms = 0

            jitter = round(np.std(ping_times), 2) if len(ping_times) > 1 else 0
            packet_loss = 0 if response_time_ms > 0 else 100

        except Exception:
            response_time_ms, packet_loss, jitter = 0, 100, 0

        with app.app_context():
            db.session.add(PingResult(
                destination=destination,
                packet_loss=packet_loss,
                jitter=jitter,
                ping_time=response_time_ms
            ))
            db.session.commit()

        time.sleep(ping_interval)


def run_ping_threads_once():
    if not getattr(app, "_ping_started", False):
        print("Запуск потоков пинга...")
        for host in target_hosts:
            thread = Thread(target=ping_target, args=(host,))
            thread.daemon = True
            thread.start()
        app._ping_started = True


@app.route('/api/ping')
def get_ping_status():
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    results = PingResult.query.all()

    nodes = {}

    for r in results:
        node = nodes.setdefault(r.destination, {
            "destination": r.destination,
            "timestamps": [],
            "ping_times": [],
            "packet_losses": [],
            "jitters": [],
            "last30": []
        })

        ts = r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        node["timestamps"].append(ts)
        node["ping_times"].append(r.ping_time or 0)
        node["packet_losses"].append(r.packet_loss or 0)
        node["jitters"].append(r.jitter or 0)

        if r.timestamp >= month_ago:
            node["last30"].append({
                "ping_time": r.ping_time or 0,
                "jitter": r.jitter or 0,
                "packet_loss": r.packet_loss or 0
            })

    for node in nodes.values():
        last = node["last30"]
        total = len(last)
        success = len([r for r in last if r["ping_time"] > 0])

        if total > 0:
            avg_ping = round(sum(r["ping_time"] for r in last if r["ping_time"] > 0) / success, 2) if success else 0
            avg_jitter = round(sum(r["jitter"] for r in last) / total, 2)
            avg_loss = round(sum(r["packet_loss"] for r in last) / total, 2)
            sla = round(success / total * 100, 2)
        else:
            avg_ping = avg_jitter = avg_loss = sla = 0

        node["sla"] = {
            "percent": sla,
            "avg_ping": avg_ping,
            "avg_jitter": avg_jitter,
            "avg_loss": avg_loss
        }

        del node["last30"]

    return jsonify({"nodes": list(nodes.values())})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204


run_ping_threads_once()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
