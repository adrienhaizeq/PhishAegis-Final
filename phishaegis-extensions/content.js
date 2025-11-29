// PhishAegis Gmail Scanner - WITH FLASK API INTEGRATION
console.log('🛡️ PhishAegis Extension Loaded!');

class GmailScanner {
    constructor() {
        this.scannedEmails = new Set();
        this.apiUrl = 'http://127.0.0.1:5000/extension_scan';
        this.isActive = true;
        
        console.log('🚀 GmailScanner Initialized!');
        
        // Load saved state
        chrome.storage.local.get(['isActive'], (result) => {
            this.isActive = result.isActive !== false;
            console.log(`🛡️ Scanner started as ${this.isActive ? 'ACTIVE' : 'INACTIVE'}`);
        });

        // Message listener for toggle
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            console.log('📩 Received message:', request);
            
            if (request.action === "statusChange") {
                this.isActive = request.isActive;
                console.log(`🛡️ Scanner ${this.isActive ? 'ACTIVATED' : 'DEACTIVATED'}`);
                
                this.showWarning(
                    this.isActive ? '🟢 Scanner ACTIVATED' : '🔴 Scanner DEACTIVATED',
                    this.isActive ? '#e8f5e8' : '#ffebee',
                    this.isActive ? '#4CAF50' : '#f44336'
                );
                
                sendResponse({success: true});
            }
            
            if (request.action === "manualScan") {
                this.scanForEmail();
                sendResponse({success: true});
            }
            
            return true;
        });
        
        this.startEnhancedMonitoring();
        console.log('✅ Monitoring started!');
    }

    startEnhancedMonitoring() {
        console.log('⏰ Starting enhanced monitoring...');
        
        // Scan every 3 seconds
        setInterval(() => {
            if (this.isActive) {
                console.log('⏰ Periodic scan running...');
                this.scanForEmail();
            }
        }, 3000);

        // Also scan on click (user opens email)
        document.addEventListener('click', () => {
            setTimeout(() => {
                if (this.isActive) {
                    console.log('🖱️ Click detected - scanning...');
                    this.scanForEmail();
                }
            }, 1000);
        });

        // Scan when URL changes (user opens different email)
        let lastUrl = window.location.href;
        setInterval(() => {
            if (window.location.href !== lastUrl && this.isActive) {
                console.log('🔗 URL changed - scanning...');
                lastUrl = window.location.href;
                setTimeout(() => this.scanForEmail(), 2000);
            }
        }, 1000);
    }

    scanForEmail() {
        if (!this.isActive) {
            console.log('⏸️ Scanner inactive - skipping scan');
            return;
        }
        
        console.log('🔍 Scanning for email content...');
        
        try {
            // Try multiple selectors for Gmail
            const subject = this.findElement([
                'h2[data-thread-id]',
                'h1', 'h2', 'h3',
                '[data-subject]',
                '.ha h2'
            ]);
            
            const body = this.findElement([
                '.a3s', 
                '.ii', 
                '[role="main"]',
                'div[dir="ltr"]',
                '.gs'
            ]);
            
            const sender = this.findElement([
                '.gD', 
                '[email]',
                '.go', 
                '.g2'
            ]);

            console.log('📧 Email elements found:', {
                subject: !!subject,
                body: !!body,
                sender: !!sender
            });

            if (subject && body) {
                const emailData = {
                    sender: sender || 'Unknown',
                    subject: subject,
                    body: body.substring(0, 2000),
                    timestamp: new Date().toISOString()
                };
                
                const emailId = subject.substring(0, 50) + Date.now();
                
                if (!this.scannedEmails.has(emailId)) {
                    this.scannedEmails.add(emailId);
                    console.log('🎯 NEW EMAIL DETECTED!');
                    console.log('Subject:', subject);
                    console.log('From:', sender);
                    this.analyzeEmailWithAPI(emailData);
                } else {
                    console.log('📭 Email already scanned, skipping...');
                }
            } else {
                console.log('❌ No complete email content found');
            }
        } catch (error) {
            console.log('❌ Scan error:', error);
        }
    }

    findElement(selectors) {
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element && element.textContent && element.textContent.trim().length > 5) {
                const text = element.textContent.trim();
                console.log(`✅ Found element with selector: ${selector}`, text.substring(0, 100));
                return text;
            }
        }
        return null;
    }

    async analyzeEmailWithAPI(emailData) {
        console.log('🔍 ANALYZING EMAIL WITH FLASK API...');
        
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sender: emailData.sender,
                    subject: emailData.subject,
                    body: emailData.body
                })
            });

            console.log('📡 API Response status:', response.status);

            const result = await response.json();
            console.log('📊 API Result:', result);
            
            if (result.success) {
                console.log(`📊 FINAL RESULT: ${result.label.toUpperCase()} (${result.score}%)`);
                
                if (result.label === 'phishing') {
                    this.showWarning(`🚨 PHISHING DETECTED! (${result.score}%)`, '#ffebee', '#f44336');
                } else {
                    this.showWarning(`✅ Email appears safe (${result.score}%)`, '#e8f5e8', '#4caf50');
                }
            } else {
                console.error('❌ API Error:', result.error);
                this.showWarning('⚠️ Analysis failed', '#fff3cd', '#ffc107');
            }
            
        } catch (error) {
            console.error('❌ API Call Failed:', error);
            this.analyzeEmailFallback(emailData);
        }
    }

    analyzeEmailFallback(emailData) {
        console.log('🔍 USING FALLBACK DETECTION...');
        
        const phishingKeywords = ['urgent', 'verify', 'password', 'account', 'click here', 'limited time', 'suspended'];
        const legitKeywords = ['meeting', 'thank you', 'newsletter', 'update', 'reminder', 'confirmed', 'invoice'];
        
        const phishingCount = phishingKeywords.filter(keyword => 
            emailData.body.toLowerCase().includes(keyword) ||
            emailData.subject.toLowerCase().includes(keyword)
        ).length;
        
        const legitCount = legitKeywords.filter(keyword => 
            emailData.body.toLowerCase().includes(keyword) ||
            emailData.subject.toLowerCase().includes(keyword)
        ).length;
        
        const score = Math.max(0, Math.min(100, (phishingCount * 20) - (legitCount * 10) + 50));
        const isPhishing = score > 60;
        
        console.log(`📊 FALLBACK RESULT: ${isPhishing ? 'PHISHING' : 'SAFE'} (score: ${score}%)`);
        console.log('Keywords:', { phishingCount, legitCount });
        
        if (isPhishing) {
            this.showWarning(`🚨 PHISHING DETECTED! (${score}%)`, '#ffebee', '#f44336');
        } else {
            this.showWarning(`✅ Email appears safe (${score}%)`, '#e8f5e8', '#4caf50');
        }
    }

    showWarning(message, bgColor, borderColor) {
        // Remove existing warning
        const existing = document.getElementById('phish-debug-alert');
        if (existing) existing.remove();
        
        const alert = document.createElement('div');
        alert.id = 'phish-debug-alert';
        alert.style.cssText = `
            background: ${bgColor};
            border: 3px solid ${borderColor};
            border-radius: 10px;
            padding: 15px;
            margin: 15px;
            color: #333;
            font-family: Arial, sans-serif;
            font-size: 16px;
            font-weight: bold;
            z-index: 10000;
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 300px;
            word-wrap: break-word;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        `;
        alert.textContent = message;
        
        document.body.appendChild(alert);
        console.log('📢 Warning displayed:', message);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
                console.log('🗑️ Warning removed');
            }
        }, 5000);
    }
}

// Start scanner with error handling
console.log('🔧 Starting PhishAegis scanner...');
try {
    if (window.location.hostname === 'mail.google.com') {
        console.log('📧 Gmail detected - initializing scanner...');
        setTimeout(() => {
            try {
                new GmailScanner();
                console.log('✅ PhishAegis successfully started!');
            } catch (error) {
                console.error('❌ Failed to start GmailScanner:', error);
            }
        }, 3000);
    } else {
        console.log('🌐 Not Gmail - scanner not started');
    }
} catch (error) {
    console.error('❌ Global error starting scanner:', error);
}