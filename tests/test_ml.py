"""
Tests for ML/AI modules
"""

import pytest
import pandas as pd
from ml_models.expense_predictor import ExpensePredictionModel
from ml_models.anomaly_detector import AnomalyDetector
from ml_models.calculators import (
    EMICalculator, SIPCalculator, 
    InterestCalculator, DebtPayoffPlanner
)

class TestExpensePredictor:
    """Test expense prediction model"""
    
    def test_prepare_features(self):
        """Test feature preparation"""
        model = ExpensePredictionModel()
        
        transactions = pd.DataFrame([
            {
                'transaction_date': '2024-01-15 10:30:00',
                'amount': 50.0,
                'description': 'Lunch',
                'notes': 'With colleagues'
            }
        ])
        
        features = model.prepare_features(transactions)
        
        assert len(features) == 1
        assert 'day_of_week' in features.columns
        assert 'amount' in features.columns

class TestAnomalyDetector:
    """Test anomaly detection"""
    
    def test_anomaly_detection_initialization(self):
        """Test detector initialization"""
        detector = AnomalyDetector()
        
        assert detector.detector is not None
        assert detector.scaler is not None

class TestCalculators:
    """Test financial calculators"""
    
    def test_emi_calculation(self):
        """Test EMI calculation"""
        emi = EMICalculator.calculate_emi(
            principal=100000,
            annual_rate=10,
            tenure_months=60
        )
        
        assert emi > 0
        assert isinstance(emi, float)
    
    def test_sip_calculation(self):
        """Test SIP calculation"""
        result = SIPCalculator.calculate_sip_value(
            monthly_investment=5000,
            annual_return=12,
            years=10
        )
        
        assert result['future_value'] > result['total_invested']
        assert result['returns'] > 0
    
    def test_compound_interest(self):
        """Test compound interest"""
        result = InterestCalculator.compound_interest(
            principal=10000,
            rate=10,
            years=5
        )
        
        assert result['interest'] > 0
        assert result['total_amount'] > result['principal']
    
    def test_debt_payoff_plan(self):
        """Test debt payoff planning"""
        debts = [
            {
                'name': 'Credit Card',
                'balance': 5000,
                'rate': 20,
                'min_payment': 200
            },
            {
                'name': 'Personal Loan',
                'balance': 50000,
                'rate': 12,
                'min_payment': 1000
            }
        ]
        
        timeline = DebtPayoffPlanner.get_payoff_timeline(debts)
        
        assert len(timeline) == 2
        assert all('payoff_date' in item for item in timeline)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
