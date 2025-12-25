Train or retrain the PM2.5 prediction model:

1. Fetch historical data from Supabase (minimum 6 months)
2. Perform feature engineering (rolling stats, lag features, temporal)
3. Train Random Forest model with cross-validation
4. Evaluate metrics (RMSE, MAE, R², MAPE)
5. Save model to `backend/app/ml/models/`
6. Update model version in configuration

Target: R² > 0.7, MAPE < 30%
