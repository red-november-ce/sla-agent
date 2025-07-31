FROM python:3.10-bullseye

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping ca-certificates && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./
RUN python -m venv /env && \
    /env/bin/pip install --upgrade pip && \
    /env/bin/pip install --no-cache-dir -r requirements.txt && \
    find /env -type d -name "__pycache__" -exec rm -r {} + && \
    find /env -type f -name "*.pyc" -delete


COPY . .


ENV PATH="/env/bin:$PATH"


RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
