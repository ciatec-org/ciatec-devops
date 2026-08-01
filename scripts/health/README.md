# Scripts de health check

| Script | O que verifica |
|--------|----------------|
| `check-webgl.sh` | TrunkTilt, Bubbles, Downhill (HTTP 200) |
| `check-docker.sh` | API (`/health` + `"status":"ok"`) e App |
| `check-db.sh` | RDS via `pg_isready` ou TCP (`DB_HOST`) |
| `check-all.sh` | Chama os três acima |

Variáveis: `TRUNKTILT_URL`, `BUBBLES_URL`, `DOWNHILL_URL`, `API_URL`, `APP_URL`, `DB_HOST`, `DB_PORT`.

```bash
export API_URL=https://api.exemplo/health
./check-all.sh
```

Exit `0` se tudo OK, `1` se qualquer check falhar.
