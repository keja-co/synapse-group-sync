# Matrix Synapse SCIM

[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
[![Hits-of-Code](https://hitsofcode.com/github/keja-co/synapse-scim?branch=main)](https://hitsofcode.com/github/keja-co/synapse-scim/view?branch=main)
[![LOC](https://tokei.rs/b1/github/keja-co/synapse-scim)](https://github.com/keja-co/synapse-scim)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ca0469df52fc4a3ab9ba4705c38f3260)](https://app.codacy.com/gh/keja-co/synapse-scim/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

**Note:** This relies heavily on Synapse Admin APIs. This will **not** work with other home servers.
<br>
Additionally, this has _only_ been tested against Authentik. It likely isn't spec compliant SCIM, so if you run into
issues with other IDPs, please open an issue.

## 🚀 Overview

This service synchronizes **IDP user groups** with **Matrix rooms** using:

- **SCIM Sync:** Updates users in real-time based on IDP events

## 📌 Features

- **Auto-assign Matrix rooms** based on IDP groups
- **Remove users from rooms** if they leave/are removed from a group

## 🚀 Deployment

**NOTE:** If using a room alias (i.e. `#general:example.com` instead of `!abc123:example.com`), replace the `#` with
`%23`.

### Docker Compose

Copy the `docker-compose.example.yml` file to your server and customise it to your needs.

Copy the `.env.example` file to `.env` and fill in required env vars.
<br>
I recommend creating a group-map.jsonc file somewhere (maybe even in Git), which contains your group mappings. Then copy
and paste this (minus the comments) into the IDP_GROUP_TO_ROOM env var.

Then run:

```sh
docker-compose up -d
```

### Logs & Monitoring

Check container logs (if in same directory as `docker-compose.yml`, otherwise specify the path to docker-compose file):

```sh
docker compose logs
```

### Env Vars

`LOG_LEVEL`: The log level for the application. (i.e. `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Currently only DEBUG does anything, INFO and above are always logged.

`WEBHOOK_SECRET`: The secret key for the SCIM webhook. When setting up SCIM in your IDP select 'Bearer Token' and paste
this key.

`MATRIX_ADMIN_TOKEN`: The access token for a Synapse Admin account. Most Matrix clients will show this in the settings
somewhere.
<br>
`MATRIX_ADMIN_USER_ID`: The user ID of the Synapse Admin account. (i.e. `@admin:example.com`)
<br>
`MATRIX_URL`: The URL of your Synapse server. (i.e. `https://matrix.example.com`)
<br>
`MATRIX_SERVER_NAME`: The server name of your Synapse server. (i.e. `example.com`)

`IDP_NAME`: The name of your IDP as it appears in the Synapse Admin API. Note this is slightly different to the idp_id in the homeserver.yaml file. (i.e. `authentik` --> `oidc-authentik`). Use something like [Synapse Admin](https://admin.etke.cc/) to find the correct IDP ID.
<br>
`IDP_GROUP_TO_ROOM`: A JSON object mapping IDP groups to Matrix rooms. For Example: 
```json
 {"group1": ["#room1:example.com"], "group2": ["#room2:example.com"]}
```
_Note_: This is mapped on group externalId, not name. You can find this in the SCIM webhook payload, or your IDP may display it in the UI.

`AUTHENTIK_API_URL`: Deprecated. The URL of your Authentik server. (i.e. `https://auth.example.com`)
<br>
`AUTHENTIK_TOKEN`: Deprecated. The token for an account on your Authentik server. (i.e. `abc123`)

`DATA_DIR`: The directory which stores persistent data. If running in Docker, this should be a volume. (i.e. `/data`)

## 🛠️ Development

### Install Locally (Without Docker)

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## ❓ FAQ

## 📝 TODO
- [ ] Remove users from rooms if they leave/are removed from a group
- [ ] Add support for/test more IDPs
- [ ] Make adding groups/room maps easier (possibly via a web interface to allow certain users to add mappings)
- [ ] Clean up code
- [ ] Add support for more SCIM operations (currently only the minimum GET/POST/PUT is supported, PATCH and DELETE are not)

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## 📞 Support

For issues & feature requests, open a GitHub issue or PR!
