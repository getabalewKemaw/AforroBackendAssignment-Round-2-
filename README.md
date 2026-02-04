# Afororo Backend Assignment (Round 2)

## Celery
Start the worker:
```
celery -A aforro_backend worker -l info
```

Tasks are triggered on successful order confirmation in `POST /orders/`.

## Docker
Start everything:
```
docker compose up --build
```

Then run migrations:
```
docker compose exec web python manage.py migrate
```
