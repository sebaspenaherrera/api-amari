# 📶 Amari 5G Network-in-a-Box API

This project provides a FastAPI-based asynchronous API to interact with the Amarisoft Remote API, enabling programmable control of a 5G/4G network-in-a-box setup.

It exposes endpoints over HTTP/JSON for:

  - Starting/stopping/resetting AMARI services
  - Configuring gNB/eNB parameters (PRB, MCS, gain, noise, timers, etc.)
  - Collecting statistics from gNBs, channels, UEs, and the core network (MME)
  - Managing UEs and retrieving core network information

The API is designed to simplify operations and automation for Amarisoft-based deployments.

**Note:** All the content you can access from this API requires authentication. However, you can find a version without it in the history version. Additional information for each model, endpoint can be found in the docs of the API.


## 🚀 Features

  - Full set of management endpoints for gNB/eNB, UEs, and core (MME)
  - Generic message gateway to the Amarisoft Remote API
  - Statistics collection (RF, PRB allocation, channel logs, UE stats)
  - Service lifecycle control (start, stop, reset, status)
  - Built-in interactive documentation (Swagger UI & ReDoc)
  - Strong input validation with Pydantic models

# ⚙️ Configuration

The API can be configured via a JSON file or console arguments.

Example configuration (``config.json``):

```python
{
  "API_APP": "rest.main:app",
  "API_HOST": "0.0.0.0",
  "API_PORT": 8000,
  "API_RELOAD": true,
  "API_DATA_PATH": "./data",
  "AMARI_HOST": "127.0.0.1",
  "AMARI_PORT": 9001
}
```

📌 Console arguments **override** values defined in the JSON file.

## ▶️ Running the API

### Option 1: Run with configuration file
```bash
python api.py --config config.json
```

It is mandatory to first activate the right **conda environment**.

### Option 1: Run directly with Uvicorn

```bash
uvicorn rest.main:app --host 0.0.0.0 --port 8000 --reload
```
This is not recommended since you are loading the app with the default configuration.

### Option 3: Deploy in production (recommended)

Use a process manager like systemd, supervisord, or Docker.
Example with systemd (``/etc/systemd/system/amari-api.service``):

```ini
[Unit]
Description=Amari 5G Network-in-a-Box API
After=network.target

[Service]
User=amari
WorkingDirectory=/opt/amari-api
ExecStart=/usr/bin/uvicorn rest.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable amari-api
sudo systemctl start amari-api
```
**Note:** The API is currently running in [API container](http://192.168.159.160:8000/docs). 

## 📖 API Documentation

Once running, you can access:

- Swagger UI → [Docs](http://localhost:8000/docs)
- ReDoc → [Docs](http://localhost:8000/redoc)

Both interfaces allow interactive testing of all endpoints.

## 🔑 Endpoints Overview
### 🔹 Generic

* ``GET /get_help`` → list available Amarisoft API messages

* ``POST /{entity}`` → send arbitrary API messages (enb, mme, etc.)

### 🔹 Network Management

* ``GET /network/service_status`` → check AMARI service status
* ``GET /network/service_start`` → start AMARI service
* ``GET /network/service_stop`` → stop AMARI service
* ``GET /network/service_reset`` → reset AMARI service

### 🔹 gNB / eNB

* ``GET /enb/get_config`` → fetch configuration
* ``POST /enb/set_gain`` → set DL RF gain
* ``POST /enb/set_noise_level`` → configure noise
* ``POST /enb/set_inactivity_timer`` → set inactivity timer
* ``POST /enb/set_prb_allo``c → configure PRB allocation
* ``POST /enb/set_mcs`` → configure MCS values
* ``POST /enb/get_stats`` → collect statistics
* ``POST /enb/get_channel_stats`` → retrieve channel logs
* ``GET /enb/reset_log`` → reset gNB logs

### 🔹 UE

* ``POST /ue/get_stats`` → fetch UE statistics (all or by UE ID)

### 🔹 Core Network (MME)

* ``GET /core/get_config`` → fetch MME configuration
* ``GET /core/get_stats`` → retrieve MME statistics
* ``GET /core/get_attached_gnb`` → list attached gNBs
* ``POST /core/get_ue`` → get UE info (filter by IMSI/IMEI)

## 📌 Example Usage
### Start AMARI service
```bash
curl http://localhost:8000/network/service_start
```

### Set DL PRB allocation
```bash
curl -X POST http://localhost:8000/enb/set_prb_alloc \
  -H "Content-Type: application/json" \
  -d '{"cells": {"1": {"pdsch_fixed_l_crb": 20, "pdsch_fixed_rb_alloc": true, "pdsch_fixed_rb_start": 0}}}'
```

### Fetch UE stats
```bash
curl -X POST http://localhost:8000/ue/get_stats \
  -H "Content-Type: application/json" \
  -d '{"stats": true, "ue_id": 1}'
```

## 🧾 Data Models

All requests are validated with Pydantic models.
Examples:

### * Set Gain

```json
{
  "gain": -10,
  "cell_id": 1
}
```

### * Noise Level
```json
{
  "noise_level": -20,
  "channel": 0
}
```

### * MCS Allocation
```json
{
  "cells": {"1": {"pdsch_mcs": 28}}
}
```

### * UE Stats
```json
{
  "stats": true,
  "ue_id": 1001
}
```


## 📜 References

This API has been developed at the University of Málaga. To get useful information on how this can be utilized, please take a read of:

[A Framework to boost the potential of network-in-a-box solutions](https://ieeexplore.ieee.org/abstract/document/9609861)
[Measuring key quality indicators in cloud gaming: Framework and assessment over wireless networks](https://www.mdpi.com/1424-8220/21/4/1387)
[Measuring and estimating key quality indicators in cloud gaming services](https://www.sciencedirect.com/science/article/pii/S1389128623002530)
[KQI assessment of VR services: A case study on 360-video over 4G and 5G](https://ieeexplore.ieee.org/abstract/document/9833911)

Additional information can be found in:

[Amarisoft Remote API Documentation](https://tech-academy.amarisoft.com/RemoteAPI.html)

[Amarisoft eNB/gNB Remote API](https://tech-academy.amarisoft.com/lteenb.doc#Remote-API-1)

[FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🛠️ Operator Roadmap

 + Extend Amarisoft CLI command coverage
 + Add Grafana/Prometheus integration for stats monitoring
