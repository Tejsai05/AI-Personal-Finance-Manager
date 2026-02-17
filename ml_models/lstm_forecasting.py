"""
LSTM/BiLSTM Model for Net Worth Forecasting
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import List, Tuple, Dict
import joblib
import os

try:
    from tensorflow import keras
    from keras import layers, models
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False


class NetWorthForecaster:
    """LSTM model for net worth forecasting"""
    
    def __init__(self, lookback_period: int = 12, forecast_period: int = 6):
        self.lookback_period = lookback_period
        self.forecast_period = forecast_period
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
    
    def build_model(self, input_shape: Tuple):
        """Build BiLSTM model architecture"""
        if not HAS_TENSORFLOW:
            return None
            
        model = models.Sequential([
            layers.Bidirectional(
                layers.LSTM(64, return_sequences=True, activation='tanh'),
                input_shape=input_shape
            ),
            layers.Dropout(0.2),
            layers.Bidirectional(
                layers.LSTM(32, return_sequences=False, activation='tanh')
            ),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(self.forecast_period)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for training"""
        X, y = [], []
        
        for i in range(len(data) - self.lookback_period - self.forecast_period + 1):
            X.append(data[i:(i + self.lookback_period)])
            y.append(data[(i + self.lookback_period):(i + self.lookback_period + self.forecast_period)])
        
        return np.array(X), np.array(y)
    
    def train(self, net_worth_history: pd.DataFrame, epochs: int = 100, batch_size: int = 32):
        """Train the LSTM model"""
        if not HAS_TENSORFLOW:
            print("⚠️ TensorFlow not available")
            return
            
        values = net_worth_history['net_worth'].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(values)
        X, y = self.prepare_sequences(scaled_data.flatten())
        
        if len(X) == 0:
            print("⚠️ Insufficient data")
            return
        
        X = X.reshape((X.shape[0], X.shape[1], 1))
        self.model = self.build_model((self.lookback_period, 1))
        
        history = self.model.fit(X, y, epochs=epochs, batch_size=batch_size,
                                validation_split=0.2, verbose=0)
        
        self.is_trained = True
        print(f"✅ Model trained!")
    
    def predict(self, recent_net_worth: List[float]) -> List[float]:
        """Predict future net worth"""
        if not self.is_trained or self.model is None:
            return []
        
        input_data = recent_net_worth[-self.lookback_period:]
        
        if len(input_data) < self.lookback_period:
            return []
        
        input_array = np.array(input_data).reshape(-1, 1)
        scaled_input = self.scaler.transform(input_array)
        scaled_input = scaled_input.reshape((1, self.lookback_period, 1))
        
        scaled_prediction = self.model.predict(scaled_input, verbose=0)
        prediction = self.scaler.inverse_transform(scaled_prediction.reshape(-1, 1))
        
        return prediction.flatten().tolist()
    
    def save_model(self, path: str = "ml_models/saved_models/"):
        """Save trained model"""
        os.makedirs(path, exist_ok=True)
        if self.model:
            self.model.save(f"{path}lstm_net_worth.h5")
            joblib.dump(self.scaler, f"{path}lstm_scaler.pkl")
            print(f"✅ Model saved")
    
    def load_model(self, path: str = "ml_models/saved_models/"):
        """Load trained model"""
        if not HAS_TENSORFLOW:
            print("⚠️ TensorFlow not available")
            return
            
        try:
            self.model = keras.models.load_model(f"{path}lstm_net_worth.h5")
            self.scaler = joblib.load(f"{path}lstm_scaler.pkl")
            self.is_trained = True
            print(f"✅ Model loaded")
        except Exception as e:
            print(f"❌ Error: {e}")


def forecast_net_worth(net_worth_history: pd.DataFrame, months: int = 6) -> Dict:
    """Forecast net worth"""
    forecaster = NetWorthForecaster(lookback_period=12, forecast_period=months)
    
    if len(net_worth_history) < 18:
        recent_values = net_worth_history['net_worth'].tail(6).values
        if len(recent_values) < 2:
            return {"method": "constant", "predictions": [0] * months}
        
        trend = np.polyfit(range(len(recent_values)), recent_values, 1)
        predictions = [round(trend[0] * (len(recent_values) + i) + trend[1], 2) 
                      for i in range(1, months + 1)]
        return {"method": "linear", "predictions": predictions}
    
    if HAS_TENSORFLOW:
        forecaster.train(net_worth_history, epochs=50)
        recent_values = net_worth_history['net_worth'].tail(12).tolist()
        predictions = forecaster.predict(recent_values)
        return {"method": "lstm", "predictions": [round(p, 2) for p in predictions]}
    else:
        recent_values = net_worth_history['net_worth'].tail(6).values
        trend = np.polyfit(range(len(recent_values)), recent_values, 1)
        predictions = [round(trend[0] * (len(recent_values) + i) + trend[1], 2) 
                      for i in range(1, months + 1)]
        return {"method": "linear", "predictions": predictions}
