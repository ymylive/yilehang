# Deployment Report (Latest)

Date: 2026-02-05

## Server
- IP: 82.158.88.34
- Domain: yilehang.cornna.xyz

## Status
- Docker services are running (postgres + api + nginx)
- HTTP is available on port 80
- SSL is pending (DNS does not resolve to 82.158.88.34 yet)

## Containers
- yilehang-nginx
- yilehang-api
- yilehang-postgres

## Access
- Client: http://82.158.88.34/
- Admin: http://82.158.88.34/admin
- API docs: http://82.158.88.34/docs

## DNS Check
- Current DNS result: 198.18.4.148
- Expected: 82.158.88.34

## Next steps
1. Update DNS for yilehang.cornna.xyz -> 82.158.88.34
2. Re-run `python scripts/setup_ssl.py`
