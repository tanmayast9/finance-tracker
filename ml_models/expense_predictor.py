"""
Expense Prediction ML Model
Uses scikit-learn to predict expenses and categorize transactions
"""

import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpensePredictionModel:
    """ML model for predicting and categorizing expenses"""
    
    def __init__(self, model_path='ml_models/models'):
        self.model_path = model_path
        self.category_model = None
        self.amount_model = None
        self.label_encoder = None
        self.scaler = None
        self.feature_names = None
        
        os.makedirs(model_path, exist_ok=True)
        self.load_or_create_models()
    
    def load_or_create_models(self):
        """Load saved models or create new ones"""
        category_model_path = os.path.join(self.model_path, 'category_model.pkl')
        encoder_path = os.path.join(self.model_path, 'label_encoder.pkl')
        scaler_path = os.path.join(self.model_path, 'scaler.pkl')
        
        if os.path.exists(category_model_path):
            try:
                self.category_model = joblib.load(category_model_path)
                self.label_encoder = joblib.load(encoder_path)
                self.scaler = joblib.load(scaler_path)
                logger.info("Models loaded from disk")
            except Exception as e:
                logger.warning(f"Error loading models: {e}. Creating new models.")
                self.create_new_models()
        else:
            self.create_new_models()
    
    def create_new_models(self):
        """Create new ML models"""
        self.category_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        logger.info("New models created")
    
    def prepare_features(self, transactions_df):
        """Prepare features from transaction data"""
        features = []
        
        if len(transactions_df) == 0:
            return pd.DataFrame()
        
        # Extract features
        for idx, row in transactions_df.iterrows():
            date = pd.to_datetime(row['transaction_date'])
            
            feature_dict = {
                'day_of_week': date.dayofweek,
                'hour': date.hour,
                'day_of_month': date.day,
                'month': date.month,
                'amount': row['amount'],
                'amount_log': np.log1p(row['amount']),
                'description_length': len(str(row.get('description', ''))),
                'has_notes': 1 if row.get('notes') else 0,
            }
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def train(self, transactions_data):
        """Train the model with transaction data"""
        try:
            # Convert to dataframe
            df = pd.DataFrame(transactions_data)
            
            if len(df) < 10:
                logger.warning("Insufficient data to train model")
                return False
            
            # Prepare features
            X = self.prepare_features(df)
            
            # Prepare target
            y = df['category']
            
            # Encode labels
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.category_model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.category_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Model trained with accuracy: {accuracy:.2f}")
            
            # Save models
            self.save_models()
            
            return True
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def predict(self, transaction_data):
        """Predict category for a transaction"""
        try:
            if self.category_model is None:
                return None, 0
            
            # Prepare single transaction
            df = pd.DataFrame([transaction_data])
            X = self.prepare_features(df)
            
            if X.empty:
                return None, 0
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict
            prediction = self.category_model.predict(X_scaled)[0]
            probability = max(self.category_model.predict_proba(X_scaled)[0])
            
            # Decode prediction
            category = self.label_encoder.inverse_transform([prediction])[0]
            
            return category, float(probability)
        except Exception as e:
            logger.error(f"Error predicting: {e}")
            return None, 0
    
    def save_models(self):
        """Save models to disk"""
        try:
            joblib.dump(self.category_model, os.path.join(self.model_path, 'category_model.pkl'))
            joblib.dump(self.label_encoder, os.path.join(self.model_path, 'label_encoder.pkl'))
            joblib.dump(self.scaler, os.path.join(self.model_path, 'scaler.pkl'))
            logger.info("Models saved to disk")
        except Exception as e:
            logger.error(f"Error saving models: {e}")

# Global model instance
expense_model = ExpensePredictionModel()

def get_expense_model():
    """Get the global expense prediction model"""
    return expense_model
