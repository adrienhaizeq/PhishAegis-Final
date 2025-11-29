import pandas as pd
import random
from datetime import datetime

class SyntheticDataGenerator:
    def __init__(self):
        self.legitimate_templates = [
            "Meeting scheduled for {date} regarding {topic}",
            "Your order #{order_id} has been confirmed and shipped",
            "Weekly newsletter: {news} updates and announcements", 
            "Project {project_name} status report - {progress}% complete",
            "Reminder: {event} on {date} at {location}",  # ← INI YANG MASALAH
            "Invoice #{invoice_id} for {amount} is now available",
            "Team building event this {day} at {venue}",
            "Software update available for {software_name}",
            "Holiday schedule announcement for {month}",
            "Training session scheduled for {topic} on {date}",
            "Monthly performance review for {department}",
            "New feature release: {feature_name} now available",
            "Client meeting rescheduled to {new_date}",
            "Budget approval required for {project}",
            "Office maintenance scheduled for {date}"
        ]
        
        self.phishing_templates = [
            "URGENT: Your {service} account will be suspended in {hours} hours",
            "Click here to verify your {service} account immediately", 
            "Security alert: Unusual login detected from {location}",
            "Your {bank} account has been locked - verify now to unlock",
            "Payment overdue: Click to avoid service interruption",
            "You won a {prize}! Claim your free gift now",
            "Account verification required to prevent deletion",
            "Suspicious activity detected on your {account_type}",
            "Reset your password immediately - security breach",
            "Confirm your identity to unlock {service} features",
            "IMPORTANT: Your membership will expire in {days} days",
            "Action Required: Verify your contact information",
            "Security breach detected - change password now",
            "Your package delivery failed - update address now",
            "Tax refund available - claim immediately"
        ]
    
    def generate_dataset(self, num_samples=200):
        """Generate synthetic training dataset"""
        legitimate_data = []
        phishing_data = []
        
        # Generate legitimate emails
        for i in range(num_samples // 2):
            template = random.choice(self.legitimate_templates)
            subject = template.format(
                date=random.choice(['Monday', 'Tuesday', 'next week', 'tomorrow', 'Friday']),
                topic=random.choice(['project discussion', 'budget review', 'team sync', 'Q4 planning']),
                order_id=random.randint(1000, 9999),
                news=random.choice(['new features', 'company updates', 'industry trends', 'product launches']),
                project_name=random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Phoenix', 'Orion']),
                progress=random.randint(10, 95),
                event=random.choice(['company party', 'team lunch', 'conference', 'workshop']),
                location=random.choice(['conference room', 'main office', 'cafeteria', 'auditorium']),  # ← TAMBAH INI
                invoice_id=random.randint(10000, 99999),
                amount=random.choice(['$99.99', '$149.50', '$299.00', '$499.99']),
                day=random.choice(['Friday', 'Saturday', 'next week']),
                venue=random.choice(['conference room', 'main office', 'online', 'cafeteria']),
                software_name=random.choice(['Windows', 'MacOS', 'Linux', 'Android', 'iOS']),
                month=random.choice(['December', 'January', 'July', 'March', 'August']),
                department=random.choice(['Engineering', 'Marketing', 'Sales', 'HR']),
                feature_name=random.choice(['dark mode', 'advanced analytics', 'mobile app']),
                new_date=random.choice(['next Tuesday', 'tomorrow 2 PM', 'Friday morning']),
                project=random.choice(['website redesign', 'mobile app', 'cloud migration'])
            )
            
            body = f"Hello, this is regarding {subject}. Please let us know if you have any questions or need additional information. We appreciate your attention to this matter."
            
            legitimate_data.append({
                'subject': subject,
                'body': body,
                'label': 'legitimate'
            })
        
        # Generate phishing emails  
        for i in range(num_samples // 2):
            template = random.choice(self.phishing_templates)
            subject = template.format(
                service=random.choice(['Google', 'Microsoft', 'Apple', 'Facebook', 'Netflix', 'Amazon']),
                hours=random.randint(24, 72),
                location=random.choice(['China', 'Russia', 'Brazil', 'Unknown location', 'New York']),
                bank=random.choice(['Bank', 'PayPal', 'Credit Card', 'eWallet']),
                prize=random.choice(['iPhone', 'MacBook', '$1000', 'gift card', 'shopping spree']),
                account_type=random.choice(['email', 'social media', 'banking', 'shopping']),
                days=random.randint(1, 7)
            )
            
            body = f"Dear user, {subject}. Click here to take immediate action: http://fake-security-{random.randint(1000,9999)}.com. Do not ignore this important message."
            
            phishing_data.append({
                'subject': subject, 
                'body': body,
                'label': 'phishing'
            })
        
        # Combine and shuffle
        all_data = legitimate_data + phishing_data
        random.shuffle(all_data)
        
        # Save to CSV
        df = pd.DataFrame(all_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f'synthetic_training_data_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"✅ Generated {len(all_data)} synthetic training emails!")
        print(f"📁 Saved as: {filename}")
        
        return filename

# Usage
if __name__ == '__main__':
    generator = SyntheticDataGenerator()
    generator.generate_dataset(300)  # Generate 300 samples