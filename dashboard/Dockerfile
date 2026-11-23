FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY dashboard/requirements.txt /app/dashboard/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r dashboard/requirements.txt
COPY dashboard /app/dashboard
ENV DASHBOARD_BIND=0.0.0.0 DASHBOARD_PORT=5000
EXPOSE 5000
CMD ["python", "-m", "dashboard.app"]
