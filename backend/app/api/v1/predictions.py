"""
Prediction API Endpoints
Handles ML model training and PM2.5 forecasting
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.config import get_supabase_client
from app.models.prediction import (
    PredictionResponse,
    TrainingRequest,
    TrainingResponse,
    FeatureImportanceResponse,
    FeatureImportance
)
from app.ml.trainer import PM25ModelTrainer
from app.ml.predictor import PM25Predictor

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


@router.post("/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Train a Random Forest model for PM2.5 prediction.

    This endpoint trains a new model on historical data and saves it to disk.
    Training takes 30-60 seconds depending on data volume.

    **Requirements:**
    - Minimum 30 days of historical data
    - Target: R² > 0.7, MAPE < 30%
    """
    try:
        trainer = PM25ModelTrainer(supabase)

        # Train model
        result = await trainer.train(
            city=request.city,
            days=request.days,
            n_estimators=request.n_estimators,
            max_depth=request.max_depth
        )

        # Save model
        model_path = trainer.save_model(request.city)

        # Generate status message
        r2 = result['metrics']['r2']
        mape = result['metrics']['mape']

        if r2 >= 0.7 and mape <= 30:
            message = f"Model trained successfully! R² = {r2:.4f}, MAPE = {mape:.2f}%"
        else:
            message = (
                f"Model trained but below target (R² = {r2:.4f}, MAPE = {mape:.2f}%). "
                f"Consider collecting more data."
            )

        return TrainingResponse(
            status=result['status'],
            metrics=result['metrics'],
            city=request.city,
            trained_at=result['trained_at'],
            message=message
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/pm25", response_model=PredictionResponse)
async def get_pm25_prediction(
    city: str = Query(..., description="City name"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get J+1 (24-hour ahead) PM2.5 prediction for a city.

    Returns predicted PM2.5 concentration, confidence score, and AQI level.

    **Requires:**
    - Trained model for the city (use POST /predictions/train first)
    - Recent data in database for feature extraction
    """
    try:
        predictor = PM25Predictor(supabase)
        prediction = await predictor.predict_j_plus_1(city)
        return PredictionResponse(**prediction)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/history", response_model=list[dict])
async def get_prediction_history(
    city: str = Query(..., description="City name"),
    limit: int = Query(10, ge=1, le=100, description="Number of predictions to return"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get recent prediction history for a city.

    Returns the last N predictions made, useful for tracking model performance
    over time and visualizing prediction accuracy.
    """
    try:
        predictor = PM25Predictor(supabase)
        predictions = await predictor.get_recent_predictions(city, limit)
        return predictions

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch predictions: {str(e)}"
        )


@router.get("/model/feature-importance", response_model=FeatureImportanceResponse)
async def get_feature_importance(
    city: str = Query(..., description="City name"),
    top_n: int = Query(10, ge=5, le=20, description="Number of top features"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get feature importance from trained model.

    Shows which features have the most impact on predictions.
    Useful for understanding model behavior and data requirements.
    """
    try:
        trainer = PM25ModelTrainer(supabase)
        trainer.load_model(city)

        importance_df = trainer.get_feature_importance(top_n)

        features = [
            FeatureImportance(
                feature=row['feature'],
                importance=row['importance']
            )
            for _, row in importance_df.iterrows()
        ]

        return FeatureImportanceResponse(
            city=city,
            features=features
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No trained model found for {city}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feature importance: {str(e)}"
        )
