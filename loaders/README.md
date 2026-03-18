# JSON loaders (PostgreSQL + Redis)

Loadery w tym katalogu importuja dane z plikow `*.json` (np. `data/500000/patients.json`) do:
- PostgreSQL (`loaders/postgresql_loader.py`)
- Redis (`loaders/redis_loader.py`)

## Szybki start

Instalacja zaleznosci (z katalogu projektu):

```powershell
pip install -r requirements.txt
```

Uruchomienie pojedynczego loadera:

```powershell
python -m loaders.postgresql_loader --size 250k
python -m loaders.redis_loader --size 250k
```

Uruchomienie przez wspolny runner:

```powershell
python -m loaders.load_data --db postgresql --size 250k
python -m loaders.load_data --db redis --size 250k
```

## Parametry danych

Kazdy loader przyjmuje:
- `--size` - alias (`500k`, `1m`, `10m`) lub liczba (`500000`, `1000000`, `10000000`)
- `--data-dir` - jawna sciezka katalogu danych (ma pierwszenstwo nad `--size`)

Aktualnie w repo widoczne sa katalogi `data/10000` i `data/250000`. Dla `500k`, `1m`, `10m` trzeba miec odpowiednie katalogi (`data/500000`, `data/1000000`, `data/10000000`).

## PostgreSQL

Domyslne polaczenie:
- host: `localhost`
- port: `5432`
- user: `postgres`
- password: `haslo`
- database: `medical`
- schema: `medical`

Mozesz nadpisac przez parametry CLI lub zmienne srodowiskowe `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGSCHEMA`.

## Redis

Domyslne polaczenie:
- host: `localhost`
- port: `6379`
- db: `0`
- namespace: `medical`

Loader czyta dane zgodnie z `schemas/redis.txt`:
- rekordy encji jako HASH (`medical:{table}:{id}`)
- zbiory ID (`medical:set:{table}`)
- indeksy relacyjne i osie czasu (`medical:idx:*`, `medical:timeline:*`)

