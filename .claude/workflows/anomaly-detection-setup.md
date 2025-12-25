# Workflow: Anomaly Detection

## Objectif
Détecter anomalies dans données capteurs (Z-score + Isolation Forest).

## Référence
- **User Story:** US-010
- **Skills:** `ml-predictions`

## Étapes

### 1. Z-Score Detection
```python
def detect_anomalies_zscore(data, threshold=3.0):
    mean = np.mean(data)
    std = np.std(data)
    z_scores = np.abs((data - mean) / std)
    return z_scores > threshold
```

### 2. Isolation Forest
```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.1)
model.fit(X)
anomalies = model.predict(X_new)  # -1 = anomaly
```

### 3. Alert on Anomaly
```python
if is_anomaly:
    create_alert('anomaly_detected', value, sensor_id)
```

## Critères
- [ ] Anomalies détectées
- [ ] Alertes créées
- [ ] UI affiche anomalies
