# Afororo Backend Assignment (Round 2)

## Celery
Start the worker:
```
celery -A aforro_backend worker -l info
```

Tasks are triggered on successful order confirmation in `POST /orders/`.
