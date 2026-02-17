"""
XGBoost Model for Investment Return Prediction
Predicts expected returns based on multiple features
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from typing import Dict, List
import joblib
import os

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError as e:
    HAS_XGBOOST = False
    xgb = None
    print(f"⚠️ XGBoost not available: {e}")


class InvestmentReturnPredictor:
    """XGBoost model for predicting investment returns"""
    
    def __init__(self):
        """Initialize predictor"""
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'investment_amount',
            'duration_months',
            'risk_level',
            'market_trend',
            'asset_type',
            'historical_return',
            'volatility',
            'expense_ratio',
            'aum',
            'fund_age_years'
        ]
    
    def build_model(self):
        """Build XGBoost model"""
        if not HAS_XGBOOST:
            return None
            
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            objective='reg:squarederror'
        )
        return model
    
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for training/prediction"""
        for feature in self.feature_names:
            if feature not in data.columns:
                data[feature] = 0
        return data[self.feature_names].values
    
    def train(self, training_data: pd.DataFrame, target_column: str = 'actual_return'):
        """Train the XGBoost model"""
        if not HAS_XGBOOST:
            print("⚠️ XGBoost not available, skipping training")
            return
            
        X = self.prepare_features(training_data)
        y = training_data[target_column].values
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = self.build_model()
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        self.is_trained = True
        print(f"✅ Model trained! MSE: {mse:.4f}, R²: {r2:.4f}")
    
    def predict_return(self, investment_features: Dict) -> float:
        """Predict investment return"""
        if not self.is_trained or self.model is None:
            return self._fallback_prediction(investment_features)
        
        feature_array = np.array([[
            investment_features.get('investment_amount', 10000),
            investment_features.get('duration_months', 12),
            investment_features.get('risk_level', 1),
            investment_features.get('market_trend', 0),
            investment_features.get('asset_type', 1),
            investment_features.get('historical_return', 10),
            investment_features.get('volatility', 15),
            investment_features.get('expense_ratio', 1.5),
            investment_features.get('aum', 1000),
            investment_features.get('fund_age_years', 5)
        ]])
        
        scaled_features = self.scaler.transform(feature_array)
        prediction = self.model.predict(scaled_features)
        
        return round(float(prediction[0]), 2)
    
    def _fallback_prediction(self, features: Dict) -> float:
        """Rule-based fallback prediction"""
        risk_level = features.get('risk_level', 1)
        
        base_returns = {
            0: 6.5,      # Low risk
            1: 10.0,     # Medium risk
            2: 14.0      # High risk
        }
        
        base_return = base_returns.get(risk_level, 10.0)
        market_trend = features.get('market_trend', 0)
        predicted_return = base_return + (market_trend * 2)
        
        return round(predicted_return, 2)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores"""
        if not self.is_trained or self.model is None:
            return pd.DataFrame()
        
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return feature_importance
    
    def save_model(self, path: str = "ml_models/saved_models/"):
        """Save trained model and scaler"""
        os.makedirs(path, exist_ok=True)
        
        if self.model:
            joblib.dump(self.model, f"{path}xgboost_returns.pkl")
            joblib.dump(self.scaler, f"{path}xgboost_scaler.pkl")
            print(f"✅ Model saved to {path}")
    
    def load_model(self, path: str = "ml_models/saved_models/"):
        """Load trained model and scaler"""
        if not HAS_XGBOOST:
            print("⚠️ XGBoost not available, cannot load model")
            return
            
        try:
            self.model = joblib.load(f"{path}xgboost_returns.pkl")
            self.scaler = joblib.load(f"{path}xgboost_scaler.pkl")
            self.is_trained = True
            print(f"✅ Model loaded from {path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")


def predict_investment_return(
    investment_amount: float,
    duration_months: int,
    risk_level: str,
    asset_type: str = "Hybrid"
) -> Dict:
    """
    Convenience function to predict investment return
    
    Args:
        investment_amount: Investment amount in INR
        duration_months: Investment duration in months
        risk_level: "Low", "Medium", or "High"
        asset_type: "Debt", "Hybrid", or "Equity"
    
    Returns:
        Dictionary with prediction details
    """
    predictor = InvestmentReturnPredictor()
    
    risk_map = {"Low": 0, "Medium": 1, "High": 2}
    asset_map = {"Debt": 0, "Hybrid": 1, "Equity": 2}
    
    features = {
        'investment_amount': investment_amount,
        'duration_months': duration_months,
        'risk_level': risk_map.get(risk_level, 1),
        'market_trend': 0,
        'asset_type': asset_map.get(asset_type, 1),
        'historical_return': 10.0,
        'volatility': 15.0,
        'expense_ratio': 1.5,
        'aum': 1000,
        'fund_age_years': 5
    }
    
    predicted_return = predictor.predict_return(features)
    
    years = duration_months / 12
    future_value = investment_amount * ((1 + predicted_return/100) ** years)
    
    return {
        "investment_amount": investment_amount,
        "duration_months": duration_months,
        "risk_level": risk_level,
        "predicted_annual_return": predicted_return,
        "estimated_future_value": round(future_value, 2),
        "estimated_gains": round(future_value - investment_amount, 2)
    }
