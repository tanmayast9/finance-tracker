"""
Financial Calculators
EMI, Interest, Net Worth, SIP calculators
"""

from datetime import datetime, timedelta
import math

class EMICalculator:
    """Calculate EMI for loans"""
    
    @staticmethod
    def calculate_emi(principal, annual_rate, tenure_months):
        """
        Calculate EMI (Equated Monthly Installment)
        
        Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        where P = Principal, r = monthly rate, n = number of months
        """
        monthly_rate = annual_rate / 12 / 100
        
        if monthly_rate == 0:
            return principal / tenure_months
        
        emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / (
            (1 + monthly_rate) ** tenure_months - 1
        )
        
        return round(emi, 2)
    
    @staticmethod
    def calculate_total_interest(principal, annual_rate, tenure_months):
        """Calculate total interest payable"""
        emi = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
        total_amount = emi * tenure_months
        return round(total_amount - principal, 2)
    
    @staticmethod
    def get_amortization_schedule(principal, annual_rate, tenure_months):
        """Get month-wise amortization schedule"""
        emi = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
        monthly_rate = annual_rate / 12 / 100
        
        schedule = []
        remaining_balance = principal
        
        for month in range(1, tenure_months + 1):
            interest = round(remaining_balance * monthly_rate, 2)
            principal_part = round(emi - interest, 2)
            remaining_balance = round(remaining_balance - principal_part, 2)
            
            schedule.append({
                'month': month,
                'emi': emi,
                'principal': principal_part,
                'interest': interest,
                'remaining_balance': remaining_balance
            })
        
        return schedule

class InterestCalculator:
    """Calculate various types of interest"""
    
    @staticmethod
    def simple_interest(principal, rate, years):
        """Calculate simple interest"""
        return (principal * rate * years) / 100
    
    @staticmethod
    def compound_interest(principal, rate, years, compounds_per_year=12):
        """
        Calculate compound interest
        Formula: A = P(1 + r/n)^(nt)
        """
        n = compounds_per_year
        t = years
        r = rate / 100
        
        amount = principal * (1 + r / n) ** (n * t)
        interest = amount - principal
        
        return {
            'principal': principal,
            'interest': round(interest, 2),
            'total_amount': round(amount, 2),
            'rate': rate,
            'years': years
        }

class SIPCalculator:
    """Calculate SIP (Systematic Investment Plan) returns"""
    
    @staticmethod
    def calculate_sip_value(monthly_investment, annual_return, years):
        """
        Calculate future value of SIP
        Formula: FV = PMT * (((1 + r)^n - 1) / r)
        where PMT = monthly investment, r = monthly return rate, n = number of months
        """
        monthly_rate = annual_return / 12 / 100
        num_months = years * 12
        
        if monthly_rate == 0:
            future_value = monthly_investment * num_months
        else:
            future_value = monthly_investment * (
                ((1 + monthly_rate) ** num_months - 1) / monthly_rate
            )
        
        total_invested = monthly_investment * num_months
        returns = future_value - total_invested
        
        return {
            'total_invested': round(total_invested, 2),
            'returns': round(returns, 2),
            'future_value': round(future_value, 2)
        }

class NetWorthCalculator:
    """Calculate and track net worth"""
    
    @staticmethod
    def calculate_net_worth(assets, liabilities):
        """Calculate net worth"""
        return {
            'total_assets': sum(assets.values()),
            'total_liabilities': sum(liabilities.values()),
            'net_worth': sum(assets.values()) - sum(liabilities.values()),
            'assets': assets,
            'liabilities': liabilities
        }

class DebtPayoffPlanner:
    """Plan debt payoff strategies"""
    
    @staticmethod
    def get_payoff_timeline(debts):
        """
        Get payoff timeline using avalanche method (highest interest first)
        debts: list of {'name': str, 'balance': float, 'rate': float, 'min_payment': float}
        """
        # Sort by interest rate (descending)
        sorted_debts = sorted(debts, key=lambda x: x['rate'], reverse=True)
        
        timeline = []
        
        for debt in sorted_debts:
            emi = EMICalculator.calculate_emi(debt['balance'], debt['rate'], 12)
            months_to_payoff = math.ceil(debt['balance'] / emi) if emi > 0 else 0
            
            timeline.append({
                'name': debt['name'],
                'balance': debt['balance'],
                'rate': debt['rate'],
                'monthly_payment': emi,
                'months_to_payoff': months_to_payoff,
                'payoff_date': (datetime.now() + timedelta(days=months_to_payoff*30)).strftime('%Y-%m-%d')
            })
        
        return timeline

# Helper functions
def calculate_savings_recommendation(income, expenses, current_savings):
    """Recommend savings amount based on income and expenses"""
    recommended_savings = income * 0.20  # 20% of income
    emergency_fund_months = 6
    emergency_fund_target = (expenses / 30) * emergency_fund_months
    
    return {
        'recommended_monthly_savings': recommended_savings,
        'current_monthly_savings': current_savings,
        'emergency_fund_target': emergency_fund_target,
        'emergency_fund_months': emergency_fund_months
    }
