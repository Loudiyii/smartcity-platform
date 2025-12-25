# Workflow: Final Touches

## Objectif
Optimisations finales, monitoring, tests.

## Référence
- **Prompts:** F12-F14
- **Skills:** Tous

## Étapes

### 1. Performance Optimization
- Cache API responses (Redis/in-memory)
- Optimize DB queries (indexes)
- Lazy load components

### 2. Monitoring
```python
# Prometheus metrics
from prometheus_client import Counter

requests_total = Counter('requests_total', 'Total requests')
```

### 3. Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smartcity")
```

### 4. Mobile Responsiveness
- Test on mobile devices
- Fix layout issues
- Optimize images

### 5. Testing
```bash
# Backend tests
pytest backend/tests/ -v

# Frontend tests
npm test
```

## Critères
- [ ] Load time < 2s
- [ ] Mobile responsive
- [ ] Monitoring actif
- [ ] Tests passent
