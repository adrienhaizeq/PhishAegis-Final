from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_dance.contrib.google import make_google_blueprint, google
import pandas as pd
import re
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import imaplib
import email
from email.header import decode_header
import csv
from datetime import datetime

# ----------------- CORS Fix -----------------
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/phisaegish_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ ENABLE CORS FOR EXTENSION
CORS(app, origins=["http://127.0.0.1:5000", "https://mail.google.com"])

db = SQLAlchemy(app)

# ----------------- Google OAuth -----------------
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

google_bp = make_google_blueprint(
    client_id="557627648501-mfbpd2g45f1bh1pge57vf80k6m2qlkh4.apps.googleusercontent.com",
    client_secret="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",
    scope=["profile", "email"],
    redirect_to="google_callback"
)

app.register_blueprint(google_bp, url_prefix="/login")

# ----------------- ML Model Simple -----------------
class SimpleMLDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.model = None
        self.is_trained = False
    
    def clean_text(self, text):
        """Simple text cleaning"""
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def train_from_csv(self):
        """Train from available datasets"""
        try:
            # Try to load master dataset first
            if os.path.exists('master_training_dataset.csv'):
                df = pd.read_csv('master_training_dataset.csv')
                print(f"✅ Loaded MASTER dataset: {len(df)} emails")
            elif os.path.exists('enron_legit.csv'):
                df = pd.read_csv('enron_legit.csv')
                print(f"✅ Loaded original dataset: {len(df)} emails")
            else:
                print("❌ No training data found!")
                return 0
            
            # Prepare data
            emails = []
            labels = []
            
            for _, row in df.iterrows():
                # Combine subject and body
                combined_text = f"{row['subject']} {row['body']}"
                emails.append(combined_text)
                labels.append(0 if row['label'] == 'legitimate' else 1)  # 0=legit, 1=phishing
            
            # If not enough data, add synthetic examples
            if len(emails) < 100:
                print("Adding synthetic examples...")
                synthetic_legit = [
                    "meeting tomorrow please bring reports team discussion",
                    "thank you for your order confirmation number 12345",
                    "weekly newsletter updates new features available now",
                    "project status report progress update completion",
                    "reminder team event Friday 3pm conference room",
                    "invoice payment received thank you business",
                    "customer survey feedback please share experience",
                    "holiday schedule announcement office closed",
                    "training session new employees orientation",
                    "software update available security patches"
                ]
                
                synthetic_phishing = [
                    "urgent verify account immediately suspension",
                    "click reset password security alert",
                    "bank account locked verify unlock",
                    "invoice overdue payment required click",
                    "suspicious login verify identity",
                    "subscription canceled update payment",
                    "security breach verify account",
                    "prize winner claim free gift",
                    "account verification prevent deletion",
                    "unusual activity confirm login"
                ]
                
                emails.extend(synthetic_legit + synthetic_phishing)
                labels.extend([0]*10 + [1]*10)
            
            # Clean texts
            cleaned_emails = [self.clean_text(email) for email in emails]
            
            # Train model
            X = self.vectorizer.fit_transform(cleaned_emails)
            self.model = MultinomialNB()
            self.model.fit(X, labels)
            
            self.is_trained = True
            accuracy = np.mean(self.model.predict(X) == labels)
            
            # Save model
            joblib.dump({'model': self.model, 'vectorizer': self.vectorizer}, 'simple_model.pkl')
            
            print(f"✅ Model trained with {len(emails)} examples. Accuracy: {accuracy:.2f}")
            return accuracy
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            return 0
    
    def load_model(self):
        """Load trained model"""
        try:
            if os.path.exists('simple_model.pkl'):
                data = joblib.load('simple_model.pkl')
                self.model = data['model']
                self.vectorizer = data['vectorizer']
                self.is_trained = True
                return True
        except:
            pass
        return False
    
    def predict(self, text):
        """Predict using ML model - OPTIMIZED FOR LESS FALSE POSITIVES"""
        if not self.is_trained:
            if not self.load_model():
                # If no model, use rule-based
                return self.rule_based_detector(text)
        
        try:
            cleaned_text = self.clean_text(text)
            text_vector = self.vectorizer.transform([cleaned_text])
            probability = self.model.predict_proba(text_vector)[0]
            
            phishing_prob = probability[1] * 100  # Probability of phishing
            
            # ✅ FIX 1: Round to 2 decimal places only
            phishing_prob = round(phishing_prob, 2)
            
            # ✅ FIX 2: VERY CONSERVATIVE THRESHOLD - Less false positives
            # Only mark as phishing if very confident
            if phishing_prob > 90:  # Very high confidence phishing
                label = "phishing"
            elif phishing_prob < 20:  # Very high confidence legitimate
                label = "legitimate" 
            else:
                # For middle range, bias heavily toward legitimate
                # Check sender domain for legitimacy
                legit_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'edu.my', 'gov.my']
                has_legit_domain = any(domain in text.lower() for domain in legit_domains)
                
                # Strong legitimate indicators
                strong_legit_terms = ['meeting', 'thank you', 'newsletter', 'reminder', 'invoice', 'order', 
                                    'project', 'team', 'update', 'report', 'confirmed', 'schedule']
                strong_phishing_terms = ['urgent action required', 'verify immediately', 'click here to secure', 
                                       'account suspended', 'password expired', 'limited time offer']
                
                legit_count = sum(1 for word in strong_legit_terms if word in cleaned_text)
                phishing_count = sum(1 for word in strong_phishing_terms if word in cleaned_text)
                
                # Decision making with heavy legitimate bias
                if legit_count > 0 and phishing_count == 0:
                    label = "legitimate"
                elif phishing_count >= 2:
                    label = "phishing"
                elif has_legit_domain and legit_count > 0:
                    label = "legitimate"
                else:
                    # Default to legitimate for safety
                    label = "legitimate"
            
            return phishing_prob, label
            
        except Exception as e:
            print(f"ML prediction failed: {e}")
            return self.rule_based_detector(text)
    
    def rule_based_detector(self, text):
        """Fallback rule-based detector - OPTIMIZED FOR LESS FALSE POSITIVES"""
        text = (text or "").lower()
        
        # More specific phishing terms
        phishing_terms = {"urgent action required", "verify immediately", "click here to secure", 
                         "account suspended", "password expired", "limited time offer", "you have won"}
        
        # More legitimate terms
        legit_terms = {"meeting", "thank you", "newsletter", "update", "reminder", "confirmed", 
                      "invoice", "order", "project", "team", "discussion", "report", "schedule"}
        
        phishing_count = sum(1 for word in phishing_terms if word in text)
        legit_count = sum(1 for word in legit_terms if word in text)
        
        # Conservative scoring - start biased toward legitimate
        base_score = 30  # Start with legitimate bias
        score = base_score + (phishing_count * 20) - (legit_count * 10)
        score = max(0, min(100, score))
        score = round(score, 2)  # ✅ Round to 2 decimal places
        
        # Very conservative threshold - only mark phishing if strong evidence
        label = "phishing" if score > 80 else "legitimate"
        
        return score, label

# Initialize ML detector
ml_detector = SimpleMLDetector()

# ----------------- Models -----------------
class User(db.Model):
    __tablename__ = 'app_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    scans = db.relationship('Scan', backref='user', lazy=True)

class Scan(db.Model):
    __tablename__ = 'email_scans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_users.id'), nullable=False)
    sender = db.Column(db.String(200))
    subject = db.Column(db.String(400))
    email_text = db.Column(db.Text)
    label = db.Column(db.String(50))
    score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- Forms -----------------
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# ----------------- Phishing Detector -----------------
def simple_phish_detector(text):
    """Use ML model for detection"""
    return ml_detector.predict(text)

# ----------------- Routes -----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---- Google OAuth routes ----
@app.route("/google_login")
def google_login():
    print("🚀 Redirecting to Google login...")
    return redirect(url_for("google.login"))

@app.route("/google_callback")
def google_callback():
    try:
        print("🔄 Google callback reached!")
        
        if not google.authorized:
            flash("Google login failed or canceled.", "danger")
            return redirect(url_for("login"))

        # Get user info from Google
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google.", "danger")
            return redirect(url_for("login"))

        user_info = resp.json()
        email = user_info["email"]
        username = user_info.get("name", email.split("@")[0])

        print(f"✅ Google user: {email}")

        # Check if user exists, if not create new user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(os.urandom(16).hex())
            )
            db.session.add(user)
            db.session.commit()
            print(f"✅ New user created: {username}")

        # Login user
        session['user_id'] = user.id
        flash(f'Welcome, {username}! 🎉 (Google Login)', 'success')
        print("✅ Login successful!")
        return redirect(url_for("dashboard"))

    except Exception as e:
        print(f"❌ Google login error: {e}")
        flash(f"Google login error: {str(e)}", "danger")
        return redirect(url_for("login"))

# ---- Manual Register/Login ----
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter((User.email == form.email.data) | (User.username == form.username.data)).first()
        if existing:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # Clear Google session
    if google.authorized:
        try:
            google.token = None
        except:
            pass
    
    # Clear app session
    session.pop('user_id', None)
    session.pop('last_scan', None)
    
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# ---- ML Training Route ----
@app.route('/train_ml')
def train_ml():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    accuracy = ml_detector.train_from_csv()
    if accuracy > 0:
        flash(f'🤖 ML Model Trained! Accuracy: {accuracy:.1%}', 'success')
    else:
        flash('⚠️ Training failed. Using rule-based system.', 'warning')
    
    return redirect(url_for('dashboard'))

# ---- Dashboard ----
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    total_scanned = Scan.query.filter_by(user_id=user.id).count()
    phishing_count = Scan.query.filter_by(user_id=user.id, label='phishing').count()
    recent_results = Scan.query.filter_by(user_id=user.id).order_by(Scan.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', user=user,
                           total_scanned=total_scanned,
                           phishing_count=phishing_count,
                           recent_results=recent_results)

# ---- Scan ----
@app.route('/scan', methods=['POST'])
def scan():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    sender = request.form.get('sender', '').strip()
    subject = request.form.get('subject', '').strip()
    email_text = request.form.get('email_text', '').strip()
    text = f"{subject} {email_text}".strip()

    # Use ML detector
    score_percentage, label = simple_phish_detector(text)
    
    new_scan = Scan(
        user_id=session['user_id'],
        sender=sender,
        subject=subject,
        email_text=email_text,
        label=label,
        score=score_percentage / 100
    )
    db.session.add(new_scan)
    db.session.commit()

    session['last_scan'] = {
        'sender': sender,
        'subject': subject,
        'label': label,
        'score': round(score_percentage, 2)
    }
    return redirect(url_for('result'))

@app.route('/result')
def result():
    if 'user_id' not in session or 'last_scan' not in session:
        flash('No recent scan found. Please scan an email first.', 'warning')
        return redirect(url_for('dashboard'))
    data = session['last_scan']
    return render_template('result.html', data=data)

# ----------------- Init DB -----------------
def create_demo_account():
    """Create demo account for presentation"""
    demo_user = User.query.filter_by(email='demo@phishaegis.com').first()
    if not demo_user:
        demo_user = User(
            username='demo',
            email='demo@phishaegis.com', 
            password=generate_password_hash('demo123')
        )
        db.session.add(demo_user)
        db.session.commit()
        print("✅ Demo account created: demo@phishaegis.com / demo123")

# Add this class after your ML detector
class DatasetManager:
    def __init__(self):
        self.dataset_file = 'email_dataset.csv'
        self.init_dataset()
    
    def init_dataset(self):
        if not os.path.exists(self.dataset_file):
            with open(self.dataset_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'sender', 'subject', 'email_text', 'label', 'score', 'source'])
            print(f"✅ CSV dataset created: {self.dataset_file}")
    
    def save_to_dataset(self, sender, subject, email_text, label, score, source="extension"):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.dataset_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, sender, subject, email_text, label, score, source])
            
            print(f"💾 Saved to CSV: {label} ({score}%) - {subject[:30]}...")
            return True
        except Exception as e:
            print(f"❌ CSV save error: {e}")
            return False

# Initialize dataset manager
dataset_manager = DatasetManager()

# Add these routes after your existing routes
@app.route('/extension_scan', methods=['POST', 'OPTIONS'])
@cross_origin(origins=["https://mail.google.com"])
def extension_scan():
    """API endpoint for Chrome extension - FIXED VERSION"""
    try:
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        data = request.get_json()
        print(f"📧 Received email from extension: {data.get('subject', 'No subject')}")
        
        sender = data.get('sender', '')
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        if not subject and not body:
            return jsonify({'success': False, 'error': 'No email content'})
        
        # ✅ FIXED: Remove the extra 'sender' parameter
        score, label = ml_detector.predict(f"{subject} {body}")
        
        # Save to database
        scan = Scan(
            user_id=1,  # Default user for extension scans
            sender=sender,
            subject=subject,
            email_text=body,
            label=label,
            score=score/100
        )
        db.session.add(scan)
        db.session.commit()
        
        # Save to CSV dataset
        dataset_manager.save_to_dataset(sender, subject, body, label, score, "chrome_extension")
        
        print(f"✅ Extension scan result: {label} ({score}%)")
        
        return jsonify({
            'success': True,
            'label': label,
            'score': score,
            'message': f'{label.upper()} ({score:.1f}%)'
        })
        
    except Exception as e:
        print(f"❌ Extension scan error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/extension_stats')
def extension_stats():
    """Get stats for extension popup"""
    try:
        total = Scan.query.count()
        phishing = Scan.query.filter_by(label='phishing').count()
        
        return jsonify({
            'total_scanned': total,
            'phishing_detected': phishing
        })
    except Exception as e:
        return jsonify({'total_scanned': 0, 'phishing_detected': 0})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_demo_account()
        # Auto-train ML model on startup if datasets exist
        if os.path.exists('master_training_dataset.csv') or os.path.exists('enron_legit.csv'):
            print("🤖 Training ML model from available datasets...")
            ml_detector.train_from_csv()
    app.run(debug=True)