# Afororo Backend Assignment (Round 2)

Small but complete Django backend module demonstrating data modeling, REST APIs, caching, async processing, and Dockerized development.

## Tech Stack
- Django + Django REST Framework
- PostgreSQL (Docker) / SQLite (local dev)
- Redis (cache + Celery broker)
- Celery

## Local Setup
```
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Run Redis locally (example using Docker):
```
docker run --name aforro-redis -p 6379:6379 -d redis:7
```

Run Celery worker:
```
celery -A aforro_backend worker -l info
```

Seed data:
```
python manage.py seed_data
```

## Docker Setup
```
docker compose up --build
docker compose exec web python manage.py migrate
```

Optional seed:
```
docker compose exec web python manage.py seed_data
```

## API Endpoints
- `POST /orders/`
- `GET /stores/<store_id>/orders/`
- `GET /stores/<store_id>/inventory/`
- `GET /api/search/products/`
- `GET /api/search/suggest/?q=xxx`

## Sample Requests
Create order:
```
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "items": [
      { "product_id": 1, "quantity_requested": 2 },
      { "product_id": 2, "quantity_requested": 1 }
    ]
  }'
```

List store orders:
```
curl http://localhost:8000/stores/1/orders/
```

List store inventory:
```
curl http://localhost:8000/stores/1/inventory/
```

Search products:
```
curl "http://localhost:8000/api/search/products/?q=milk&sort=relevance&page=1&page_size=10"
```

Autocomplete:
```
curl "http://localhost:8000/api/search/suggest/?q=mil"
```

## Caching
Inventory listing (`GET /stores/<store_id>/inventory/`) is cached for 60 seconds using Redis.
Cache is invalidated automatically when inventory rows change.

## Async Processing
Celery task `send_order_confirmation` is triggered on successful order confirmation.

Run worker:
```
celery -A aforro_backend worker -l info
```

## Tests
Run tests:
```
python manage.py test
```

Included tests:
- Order confirmation deducts stock
- Order rejection leaves stock unchanged
- Inventory uniqueness constraint
- Inventory list sorting

## Scalability Considerations
- Indexes on product title and created time to support search and sorting.
- Use `select_related` and `annotate` to avoid N+1 queries.
- Caching for read-heavy inventory endpoint.
- Async tasks for non-blocking workflows (e.g., notifications).
- For larger scale: full-text search (Postgres), background indexing, rate limiting, and horizontal scaling via containers.
