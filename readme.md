# Matrix Sync Service

[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

## 🚀 Overview
This service synchronizes **IDP user groups** with **Matrix rooms** using:

- **Webhook Sync:** Updates rooms in real-time based on IDP events
- **Scheduled Sync Job:** Periodically updates all users in the background (in case of missed events)
- **Efficient Group Tracking:** Only updates users who changed groups since the last sync (for Scheduled Sync)

## 📌 Features
- **Auto-assign Matrix rooms** based on IDP groups
- **Remove users from rooms** if they leave/are removed from a group


## 🔧 Installation & Setup
To be added...

## 🚀 Deployment
### Docker Compose

```sh
docker-compose up -d
```

### Logs & Monitoring
Check **container logs**:
```sh
docker logs -f synapse-group-sync
```

## 🛠️ Development
### Install Locally (Without Docker)
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📜 License
This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## 📞 Support
For issues & feature requests, open a GitHub issue or PR!
