import pandas as pd
import requests
import os

def download_sample_datasets():
    """Download sample phishing/legitimate email datasets"""
    
    # Sample legitimate emails (business communications)
    legitimate_emails = [
        {
            'subject': 'Weekly Team Meeting Agenda',
            'body': 'Hi team, please find the agenda for our weekly meeting attached. We will discuss project milestones and upcoming deadlines.',
            'label': 'legitimate'
        },
        {
            'subject': 'Project Status Report Q4 2024',
            'body': 'Dear stakeholders, enclosed is the quarterly project status report. The project is currently 75% complete and on track for December delivery.',
            'label': 'legitimate'
        },
        {
            'subject': 'Invoice #INV-2024-001',
            'body': 'Thank you for your business. Your invoice for services rendered is now available for download from the client portal.',
            'label': 'legitimate'
        },
        {
            'subject': 'Software Update Notification',
            'body': 'A new security update is available for your application. Please update at your earliest convenience to ensure optimal performance and security.',
            'label': 'legitimate'
        },
        {
            'subject': 'Office Holiday Schedule',
            'body': 'Please be informed of the upcoming office closures for the holiday season. The office will be closed from December 25th to January 1st.',
            'label': 'legitimate'
        },
        {
            'subject': 'Welcome to the New Project Team',
            'body': 'Hello everyone, welcome to the new project team. Our kickoff meeting will be held next Monday at 10 AM in Conference Room B.',
            'label': 'legitimate'
        },
        {
            'subject': 'Monthly Newsletter - November 2024',
            'body': 'Dear subscribers, here is your monthly newsletter featuring company updates, industry news, and upcoming events.',
            'label': 'legitimate'
        },
        {
            'subject': 'Training Session: Advanced Security Features',
            'body': 'We are hosting a training session on advanced security features next Friday. Please RSVP by Wednesday if you plan to attend.',
            'label': 'legitimate'
        }
    ]
    
    # Sample phishing emails
    phishing_emails = [
        {
            'subject': 'URGENT: Your Account Will Be Suspended',
            'body': 'Dear user, we detected suspicious activity on your account. Click here immediately to verify your identity: http://fake-security-login.com',
            'label': 'phishing'
        },
        {
            'subject': 'Password Reset Required Immediately',
            'body': 'Your password has been compromised. You must reset it within 24 hours or your account will be permanently locked. Reset now: http://password-reset-fake.net',
            'label': 'phishing'
        },
        {
            'subject': 'You Won a $1000 Gift Card!',
            'body': 'Congratulations! You have been selected to receive a $1000 Amazon gift card. Click to claim your prize: http://free-gift-scam.com',
            'label': 'phishing'
        },
        {
            'subject': 'Security Alert: Unusual Login Detected',
            'body': 'We noticed a login from unrecognized device. Verify if this was you: http://security-verification-fake.com. If not, secure your account now.',
            'label': 'phishing'
        },
        {
            'subject': 'Payment Failed - Update Your Billing Information',
            'body': 'Your recent payment could not be processed. Update your billing information immediately to avoid service interruption: http://billing-update-scam.com',
            'label': 'phishing'
        },
        {
            'subject': 'Your Subscription Will Be Canceled',
            'body': 'We are unable to process your payment. Your subscription will be canceled unless you update your payment method now: http://payment-update-scam.com',
            'label': 'phishing'
        },
        {
            'subject': 'Account Verification Required',
            'body': 'To prevent your account from being deleted, you must verify your email address within 48 hours: http://account-verify-scam.com',
            'label': 'phishing'
        },
        {
            'subject': 'Important Security Update Required',
            'body': 'A critical security update is required for your account. Click here to apply the update immediately: http://fake-security-update.com',
            'label': 'phishing'
        }
    ]
    
    # Combine and save
    all_emails = legitimate_emails + phishing_emails
    df = pd.DataFrame(all_emails)
    
    # Save to CSV
    df.to_csv('additional_training_data.csv', index=False)
    print(f"✅ Added {len(all_emails)} new training emails!")
    print(f"📁 Saved as: additional_training_data.csv")
    
    return len(all_emails)

if __name__ == '__main__':
    download_sample_datasets()