# Afororo Backend Assignment (Round 2)

This project implements the required backend module using Django and Django REST Framework. It covers the data models, transactional order creation, query-optimized listings, search and autocomplete, caching with Redis, Celery async tasks, a data seeder, and full Dockerization ,

## Clone Repository
First create  A folder then open in vs code 
...
```
git clone https://github.com/getabalewKemaw/AforroBackendAssignment-Round-2-.git

```

## Tech Stack
- Django + Django REST Framework
- PostgreSQL (Docker) / SQLite (local dev)
- Redis (cache + Celery broker)
- Celery

## Project Structure
- `apps/products`: Category + Product models and seed command
- `apps/stores`: Store + Inventory models, inventory listing, caching + invalidation
- `apps/orders`: Order creation, order items, order listing, async confirmation task
- `apps/search`: Product search and autocomplete endpoints
- `aforro_backend`: project settings, URLs, Celery configuration

## Folder Structure (including tests)
```
aforro_backend/
  settings.py
  urls.py
  celery.py
apps/
  products/
    models.py
    tests.py
    management/commands/seed_data.py
  stores/
    models.py
    tests.py
    views.py
    signals.py
  orders/
    models.py
    tests.py
    views.py
    tasks.py
  search/
    views.py
    tests.py
tests/
  __init__.py
```

## Quick Start (Local)
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

Seed data (creates 10+ categories, 1000+ products, 20+ stores, 300+ inventory items per store):
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

## Environment Notes
- Local dev defaults to SQLite when `POSTGRES_DB` is not set.
- Docker uses PostgreSQL, Redis, and Celery via `docker-compose.yml`.
- Redis is used for caching and as the Celery broker.

## API Endpoints
- `POST /orders/`
- `GET /stores/<store_id>/orders/`
- `GET /stores/<store_id>/inventory/`
- `GET /api/search/products/`
- `GET /api/search/suggest/?q=xxx`

## Order Flow (POST /orders/)
Behavior:
- Validates the store and products.
- Checks inventory for each requested product.
- All operations run in a single `transaction.atomic()` block.
- If any item is insufficient, order is `REJECTED` and inventory is unchanged.
- If all items are sufficient, inventory is deducted and order is `CONFIRMED`.
- On success, a Celery task is triggered to send a confirmation.

Example:
```bash
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

## Orders Listing (GET /stores/<store_id>/orders/)
Returns:
- order id
- status
- created_at
- total number of items

Sorted newest first. Efficient aggregation prevents N+1 queries.

Example:
```bash
curl http://localhost:8000/stores/1/orders/
```

## Inventory Listing (GET /stores/<store_id>/inventory/)
Returns:
- product title
- price
- category name
- quantity

Sorted alphabetically by product title.

Example:
```bash
curl http://localhost:8000/stores/1/inventory/
```

## Product Search (GET /api/search/products/)
Features:
- Keyword search on title, description, and category name
- Filters: `category`, `min_price`, `max_price`, `store_id`, `in_stock`
- Sorting: `price`, `newest`, `relevance`
- Pagination: `page`, `page_size`
- If `store_id` is provided, `inventory_quantity` is included per product

Example:
```bash
curl "http://localhost:8000/api/search/products/?q=milk&sort=relevance&page=1&page_size=10"
```

## Autocomplete (GET /api/search/suggest/?q=xxx)
Rules:
- Minimum 3 characters
- Returns up to 10 product titles
- Prefix matches appear before general matches

Example:
```bash
curl "http://localhost:8000/api/search/suggest/?q=mil"
```

## Caching (Redis)
Inventory listing (`GET /stores/<store_id>/inventory/`) is cached for 60 seconds.
Cache is invalidated automatically on inventory create/update/delete.

## Async Processing (Celery)
Celery task `send_order_confirmation` is triggered after a confirmed order.
Worker command:
```
celery -A aforro_backend worker -l info
```

## Tests
Run tests:
```
python manage.py test
```

Current tests:
- Order confirmation deducts stock
- Order rejection leaves stock unchanged
- Inventory uniqueness constraint
- Inventory list sorting

## Test Coverage Map
- `apps/orders/tests.py`: order creation success and rejection paths, inventory deduction behavior it contain more than one tests.
- `apps/stores/tests.py`: inventory uniqueness constraint and inventory listing sort order.
- 

## Scalability Considerations
- Indexes on product title and created_at to support search/sorting.
- `select_related` + aggregation to avoid N+1 queries.
- Caching for read-heavy inventory listing.
- Async tasks to keep request latency low.
- Natural upgrade path to full-text search (Postgres), rate limiting, and horizontal scaling.
