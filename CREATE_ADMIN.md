# Create Admin User Guide

## Quick Steps

1. **Activate your virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Run the admin creation script:**
   ```bash
   python scripts/create_admin.py <your_phone_number> <your_password>
   ```

## Examples

### Example 1: Create admin with phone number and default password
```bash
python scripts/create_admin.py +1234567890
```
This will create an admin with password: `admin123`

### Example 2: Create admin with custom password
```bash
python scripts/create_admin.py +1234567890 mySecurePassword123
```

### Example 3: Ethiopian phone number format
```bash
python scripts/create_admin.py +251912345678 mypassword
```

## What the Script Does

- Creates a new admin user if one doesn't exist
- If user exists, promotes them to admin and updates password
- Phone number format: Can include country code (e.g., +251, +1)
- Password: Will be hashed securely using bcrypt

## After Creating Admin

1. **Login to the frontend** at `http://localhost:3000/login`
2. Use your phone number and password
3. You'll have admin access to manage:
   - Crops
   - Markets
   - Prices
   - Users
   - Alerts

## Troubleshooting

**Error: ModuleNotFoundError**
- Make sure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

**Error: Database not found**
- Make sure backend server has been started at least once
- This creates the SQLite database automatically

**Error: User already exists**
- The script will automatically promote existing users to admin
- Or use a different phone number

## Security Note

⚠️ **Change the default password** after first login for security!
