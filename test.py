import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get email configuration
EMAIL = os.getenv('EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

print("Email Configuration Test")
print("-" * 50)
print(f"EMAIL: {EMAIL}")
print(f"EMAIL_PASSWORD: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'Not set'}")
print("-" * 50)

# Test configuration
if EMAIL and EMAIL_PASSWORD:
    print("✓ Email configuration loaded successfully!")
else:
    print("✗ Email configuration missing!")
    if not EMAIL:
        print("  - EMAIL not found")
    if not EMAIL_PASSWORD:
        print("  - EMAIL_PASSWORD not found")
