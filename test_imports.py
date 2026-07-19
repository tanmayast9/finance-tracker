# Test imports to debug the AccountType issue
try:
    from enhanced_models import AccountType, ProfileType, TransactionType, PaymentMode
    print("✅ Successfully imported AccountType:", AccountType)
    print("✅ AccountType values:", [t.value for t in AccountType])
except ImportError as e:
    print("❌ Import error:", e)

try:
    from enhanced_forms import BankAccountForm
    print("✅ Successfully imported BankAccountForm")
except ImportError as e:
    print("❌ Form import error:", e)
