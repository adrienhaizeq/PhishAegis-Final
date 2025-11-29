document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('toggle');
    const statusCard = document.getElementById('statusCard');
    const statusText = document.getElementById('statusText');
    const websiteBtn = document.getElementById('websiteBtn');

    // Load current status
    chrome.storage.local.get(['isActive'], function(result) {
        const isActive = result.isActive !== false;
        toggle.checked = isActive;
        updateUI(isActive);
    });

    // Toggle handler
    toggle.addEventListener('change', function() {
        const isActive = this.checked;
        chrome.storage.local.set({ isActive: isActive });
        updateUI(isActive);
        
        // Send to all Gmail tabs
        chrome.tabs.query({url: "https://mail.google.com/*"}, function(tabs) {
            tabs.forEach(tab => {
                chrome.tabs.sendMessage(tab.id, {
                    action: "statusChange", 
                    isActive: isActive
                });
            });
        });
    });

    // Website button
    websiteBtn.addEventListener('click', function() {
        chrome.tabs.create({url: 'http://127.0.0.1:5000'});
    });

    function updateUI(isActive) {
        if (isActive) {
            statusText.textContent = 'PROTECTION ACTIVE';
            statusCard.className = 'status-card';
            statusCard.style.borderLeftColor = '#4CAF50';
        } else {
            statusText.textContent = 'PROTECTION OFF';
            statusCard.className = 'status-card off';
            statusCard.style.borderLeftColor = '#f44336';
        }
    }
});