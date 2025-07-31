# SLA Agent

**SLA Agent** is a lightweight self-hosted tool to monitor network reliability using ICMP ping. It records **ping time**, **jitter**, and **packet loss**, visualizes the data via a web dashboard, and calculates SLA percentages over the last 30 days.

---

## 📊 Features

- ✅ ICMP ping monitoring for multiple destinations
- 📈 Real-time charts with Chart.js
- 🕰️ SLA calculation over the past 30 days
- 💾 Data stored in SQLite
- 🖥️ Clean dashboard interface using Flask + Bootstrap
- 🐳 Fully Dockerized

---

## ⚙️ Configuration

The app is configured via environment variables:

| Variable         | Required | Type   | Description                                                | Example                            |
|------------------|----------|--------|------------------------------------------------------------|------------------------------------|
| `TARGET_HOSTS`   | ✅       | JSON   | List of target hosts (IP or DNS) to ping                   | `["8.8.8.8", "1.1.1.1"]`           |
| `PING_INTERVAL`  | ✅       | Int    | Time between pings in seconds                              | `60`                               |
| `SLA_THRESHOLD`  | ❌       | Int    | Target SLA % (used for future alerts, currently unused)    | `95`                               |

---

## 🐳 Docker Usage

You can run the SLA Agent easily via Docker:

### 🧪 Basic run

```bash
docker run -d -p 5000:5000 \
  -e TARGET_HOSTS='["8.8.8.8", "1.1.1.1"]' \
  -e PING_INTERVAL=60 \
  -e SLA_THRESHOLD=95 \
  --name sla-agent \
  rednovember/sla-agent

## 👤 Author red-november-ce
🔗 GitHub: github.com/red-november-ce
🐳 Docker Hub: hub.docker.com/rednovember/sla-agent