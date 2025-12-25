# Workflow: ML Pipeline Setup

## Objectif
Implémenter le pipeline ML pour prédire PM2.5 à J+1 avec précision > 70%.

## Référence
- **User Story:** US-009
- **Skills:** `ml-predictions`, `backend-api`

## Étapes

### 1. Feature Engineering
```python
# backend/app/ml/feature_engineering.py
def engineer_features(df):
    df['pm25_mean_7d'] = df['pm25'].rolling(7*24).mean()
    df['pm25_std_7d'] = df['pm25'].rolling(7*24).std()
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    return df
```

### 2. Train Model
```python
# backend/app/ml/trainer.py
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(n_estimators=100, max_depth=20)
model.fit(X_train, y_train)

# Save
joblib.dump(model, 'models/pm25_model.pkl')
```

### 3. Prediction Endpoint
```python
@router.post("/predictions/pm25")
async def predict_pm25(features: PredictionRequest):
    model = joblib.load('models/pm25_model.pkl')
    prediction = model.predict([features.to_array()])
    return {"predicted_pm25": prediction[0]}
```

## Critères
- [ ] Model R² > 0.7
- [ ] MAPE < 30%
- [ ] Endpoint fonctionnel
