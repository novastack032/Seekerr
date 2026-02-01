import random
import string

def generate_otp(length=6):
    """
    Generate a random OTP (One-Time Password)
    For hackathon: Simple numeric OTP
    For production: Integrate with SMS gateway like Twilio
    """
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp_sms(phone_number, otp):
    """
    Send OTP via SMS
    For hackathon: Just print to console
    For production: Integrate with Twilio or similar service
    
    Example Twilio integration:
    from twilio.rest import Client
    
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        body=f'Your Lost&Found AI verification code is: {otp}',
        from_='+1234567890',
        to=phone_number
    )
    """
    print(f"[SMS] Sending OTP {otp} to {phone_number}")
    return True

def verify_otp(entered_otp, actual_otp):
    """
    Verify if entered OTP matches the actual OTP
    """
    return entered_otp == actual_otp

def send_match_notification(phone_number, item_name, match_count):
    """
    Send notification about new matches
    For hackathon: Print to console
    For production: Send SMS/Email
    """
    message = f"Good news! We found {match_count} potential matches for your {item_name}. Check Lost&Found AI now!"
    print(f"[NOTIFICATION] To {phone_number}: {message}")
    return True