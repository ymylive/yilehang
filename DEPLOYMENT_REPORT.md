# Deployment Report (Latest)

Date: 2026-02-05

## Server
- IP: 82.158.88.34
- Domain: yilehang.cornna.xyz

## Status
- Docker services are running (postgres + api + nginx)
- SSL issued successfully via Cloudflare DNS-01
- HTTPS is enabled on 443

## Containers
- yilehang-nginx
- yilehang-api
- yilehang-postgres

## Access
- Client: https://yilehang.cornna.xyz/
- Admin: https://yilehang.cornna.xyz/admin
- API docs: https://yilehang.cornna.xyz/docs

## Notes
- Cloudflare DNS-01 used, no need to expose port 80 during issuance
- HTTP->HTTPS redirect is enabled
