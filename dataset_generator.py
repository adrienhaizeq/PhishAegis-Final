import pandas as pd
import os
import random
from datetime import datetime, timedelta

def generate_dataset():
    """Generate synthetic email dataset for training"""
    
    # Legitimate email templates
    legitimate_templates = [
        "Meeting scheduled for {date} regarding {topic}",
        "Your order #{order_id} has been confirmed",
        "Weekly newsletter: {news}",
        "Project update: {project} is {progress}% complete",
        "Reminder: {event} on {date} at {time}",
        "Thank you for your purchase of {product}",
        "Team building event this {day} at {location}",
        "Software update available for {software}",
        "Invoice #{invoice_id} for {amount}",
        "Holiday schedule announcement for {month}"
    ]
    
    # Phishing email templates
    phishing_templates = [
        "URGENT: Your account will be suspended in {hours} hours",
        "Click here to verify your {service} account",
        "Security alert: Unusual login from {location}",
        "Your {bank} account has been locked - verify now",
        "Payment overdue: Click to avoid service interruption",
        "You won a prize! Claim your {prize} now",
        "Account verification required to prevent deletion",
        "Suspicious activity detected on your {account}",
        "Reset your password immediately - security breach",
        "Confirm your identity to unlock {service}"
    ]
    
    legitimate_data = []
    phishing_data = []
    
    # Generate legitimate emails
    for i in range(500):
        template = random.choice(legitimate_templates)
        subject = template.format(
            date=random.choice(["Monday", "Tuesday", "next week", "tomorrow"]),
            topic=random.choice(["project discussion", "budget review", "team meeting"]),
            order_id=random.randint(1000, 9999),
            news=random.choice(["new features", "company updates", "industry news"]),
            project=random.choice(["Alpha", "Beta", "Gamma", "Delta"]),
            progress=random.randint(10, 95),
            event=random.choice(["company party", "team lunch", "conference"]),
            product=random.choice(["software license", "online course", "ebook"]),
            invoice_id=random.randint(10000, 99999),
            amount=random.choice(["$99.99", "$149.50", "$299.00"]),
            day=random.choice(["Friday", "Saturday", "next week"]),
            location=random.choice(["conference room", "main office", "online"]),
            software=random.choice(["Windows", "MacOS", "Linux"]),
            month=random.choice(["December", "January", "July"])
        )
        
        body = f"Hello, this is regarding {subject}. Please let us know if you have any questions."
        
        legitimate_data.append({
            'subject': subject,
            'body': body,
            'label': 'legitimate'
        })
    
    # Generate phishing emails
    for i in range(500):
        template = random.choice(phishing_templates)
        subject = template.format(
            hours=random.randint(24, 72),
            service=random.choice(["Google", "Microsoft", "Apple", "Facebook"]),
            location=random.choice(["China", "Russia", "Brazil", "Unknown"]),
            bank=random.choice(["Bank", "PayPal", "Credit Card"]),
            prize=random.choice(["iPhone", "MacBook", "$1000", "gift card"]),
            account=random.choice(["email", "social media", "banking"]),
            service=random.choice(["Netflix", "Spotify", "Amazon"])
        )
        
        body = f"Dear user, {subject}. Click here to take action: http://fake-link.com/secure"
        
        phishing_data.append({
            'subject': subject,
            'body': body,
            'label': 'phishing'
        })
    
    # Combine and save
    all_data = legitimate_data + phishing_data
    random.shuffle(all_data)
    
    df = pd.DataFrame(all_data)
    df.to_csv('training_dataset.csv', index=False)
    print(f"✅ Generated dataset with {len(df)} emails")
    
    return len(df)

# Generate dataset when needed
if __name__ == '__main__':
    generate_dataset()