"""
Anomaly Detection Model
Detects unusual spending patterns that might indicate fraud
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detect anomalies in spending patterns"""
    
    def __init__(self, model_path='ml_models/models'):
        self.model_path = model_path
        self.detector = None
        self.scaler = None
        
        os.makedirs(model_path, exist_ok=True)
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load or create anomaly detector"""
        detector_path = os.path.join(self.model_path, 'anomaly_detector.pkl')
        scaler_path = os.path.join(self.model_path, 'anomaly_scaler.pkl')
        
        if os.path.exists(detector_path):
            try:
                self.detector = joblib.load(detector_path)
                self.scaler = joblib.load(scaler_path)
                logger.info("Anomaly detector loaded")
            except:
                self.create_new_model()
        else:
            self.create_new_model()
    
    def create_new_model(self):
        """Create new anomaly detector"""
        self.detector = IsolationForest(contamination=0.05, random_state=42)
        self.scaler = StandardScaler()
        logger.info("New anomaly detector created")
    
    def prepare_features(self, transactions_df):
        """Prepare features for anomaly detection"""
        features = []
        
        for idx, row in transactions_df.iterrows():
            date = pd.to_datetime(row['transaction_date'])
            
            feature_dict = {
                'amount': row['amount'],
                'hour': date.hour,
                'day_of_week': date.dayofweek,
                'day_of_month': date.day,
            }
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def train(self, transactions_data):
        """Train anomaly detector"""
        try:
            df = pd.DataFrame(transactions_data)
            
            if len(df) < 20:
                logger.warning("Insufficient data for anomaly detection")
                return False
            
            X = self.prepare_features(df)
            X_scaled = self.scaler.fit_transform(X)
            
            self.detector.fit(X_scaled)
            
            joblib.dump(self.detector, os.path.join(self.model_path, 'anomaly_detector.pkl'))
            joblib.dump(self.scaler, os.path.join(self.model_path, 'anomaly_scaler.pkl'))
            
            logger.info("Anomaly detector trained")
            return True
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")
            return False
    
    def detect(self, transaction_data):
        """Detect if transaction is anomalous"""
        try:
            if self.detector is None:
                return False
            
            df = pd.DataFrame([transaction_data])
            X = self.prepare_features(df)
            X_scaled = self.scaler.transform(X)
            
            # -1 indicates anomaly
            prediction = self.detector.predict(X_scaled)[0]
            
            return prediction == -1
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return False

# Global anomaly detector instance
anomaly_detector = AnomalyDetector()

def get_anomaly_detector():
    """Get the global anomaly detector"""
    return anomaly_detector
