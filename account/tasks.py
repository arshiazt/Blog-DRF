from celery import shared_task
import time

@shared_task
def send_otp_code_task(phone, otp_code):
    print(f"OTP {otp_code} sent to {phone}")