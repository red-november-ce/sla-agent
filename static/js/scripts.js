function fetchData() {
    fetch('/api/ping')
        .then(response => response.json())
        .then(data => {
            const chartsContainer = document.getElementById("charts-container");
            chartsContainer.innerHTML = '';

            data.nodes.forEach(node => {
                const safeId = node.destination.replace(/[^a-zA-Z0-9-_]/g, "_");

                // Защита: если SLA нет — пропускаем
                if (!node.sla) return;

                const sla = parseFloat(node.sla.percent).toFixed(2);
                let slaColor = 'gray';
                if (sla >= 99) slaColor = 'limegreen';
                else if (sla >= 95) slaColor = 'orange';
                else slaColor = 'red';

                const chartDiv = document.createElement("div");
                chartDiv.classList.add("chart-container");
                chartDiv.innerHTML = `
                    <h3>
                        ${node.destination}
                        <span style="display:inline-block;width:12px;height:12px;margin-left:10px;border-radius:50%;background-color:${slaColor};"></span>
                        SLA: ${sla}%
                    </h3>
                    <canvas id="chart-${safeId}" width="400" height="200"></canvas>
                    <table style="margin-top:10px;font-size:14px;">
                        <tr><td><b>Avg Ping:</b></td><td>${node.sla.avg_ping} ms</td></tr>
                        <tr><td><b>Avg Jitter:</b></td><td>${node.sla.avg_jitter} ms</td></tr>
                        <tr><td><b>Avg Loss:</b></td><td>${node.sla.avg_loss}%</td></tr>
                    </table>
                `;
                chartsContainer.appendChild(chartDiv);

                new Chart(document.getElementById(`chart-${safeId}`), {
                    type: 'line',
                    data: {
                        labels: node.timestamps,
                        datasets: [
                            {
                                label: 'Ping Time (ms)',
                                data: node.ping_times,
                                borderColor: 'rgba(75, 192, 192, 1)',
                                fill: false,
                            },
                            {
                                label: 'Packet Loss (%)',
                                data: node.packet_losses,
                                borderColor: 'rgba(255, 99, 132, 1)',
                                fill: false,
                            },
                            {
                                label: 'Jitter (ms)',
                                data: node.jitters,
                                borderColor: 'rgba(153, 102, 255, 1)',
                                fill: false,
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                labels: { color: 'black' }
                            }
                        },
                        scales: {
                            x: {
                                type: 'category',
                                ticks: {
                                    color: 'black',
                                    autoSkip: true,
                                    maxTicksLimit: 20
                                }
                            },
                            y: {
                                ticks: {
                                    color: 'black'
                                }
                            }
                        }
                    }
                });
            });
        });
}

window.onload = function () {
    fetchData();
    setInterval(fetchData, 60000);
};
