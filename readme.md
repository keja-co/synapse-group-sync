# Matrix Synapse SCIM

[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

**Note:** This relies heavily on Synapse Admin APIs. This will **not** work with other home servers.

## 🚀 Overview

This service synchronizes **IDP user groups** with **Matrix rooms** using:

- **SCIM Sync:** Updates users in real-time based on IDP events

[//]: # (- **Webhook Sync:** Updates rooms in real-time based on IDP events)
[//]: # (- **Scheduled Sync Job:** Periodically updates all users in the background &#40;in case of missed events&#41;)
[//]: # (- **Efficient Group Tracking:** Only updates users who changed groups since the last sync &#40;for Scheduled Sync&#41;)

## 📌 Features

- **Auto-assign Matrix rooms** based on IDP groups
- **Remove users from rooms** if they leave/are removed from a group

## 🔧 Installation & Setup

**NOTE:** If using a room alias (i.e. `#general:example.com` instead of `!abc123:example.com`), replace the `#` with `%23`.

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

## ❓ FAQ


## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## 📞 Support

For issues & feature requests, open a GitHub issue or PR!
