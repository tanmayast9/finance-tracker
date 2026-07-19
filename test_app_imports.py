# Test app imports to debug the AccountType issue
try:
    from enhanced_app import app
    print("✅ Successfully imported app")
    
    # Test creating app context
    with app.app_context():
        from enhanced_models import AccountType
        print("✅ AccountType in app context:", AccountType)
        
        # Test form import
        from enhanced_forms import BankAccountForm
        form = BankAccountForm()
        print("✅ BankAccountForm created successfully")
        print("✅ Form account_type choices:", form.account_type.choices)
        
except Exception as e:
    print("❌ Error:", e)
    import traceback
    traceback.print_exc()
