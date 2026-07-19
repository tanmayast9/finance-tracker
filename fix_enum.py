from enhanced_models import db, User, ProfileType
from enhanced_app import app

def fix_enum_values():
    with app.app_context():
        # Update all lowercase enum values to uppercase
        users = User.query.all()
        for user in users:
            if user.profile_type and hasattr(user.profile_type, 'upper'):
                # Convert string to enum if needed
                if isinstance(user.profile_type, str):
                    try:
                        user.profile_type = ProfileType[user.profile_type.upper()]
                        print(f"Fixed user {user.username}: {user.profile_type}")
                    except KeyError:
                        # If invalid value, set to PERSONAL
                        user.profile_type = ProfileType.PERSONAL
                        print(f"Set default for user {user.username}: {user.profile_type}")
        
        db.session.commit()
        print("Enum values fixed successfully!")

if __name__ == '__main__':
    fix_enum_values()
