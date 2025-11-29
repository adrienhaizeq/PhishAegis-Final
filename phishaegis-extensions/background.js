// Background script - toggle extension state
let isActive = false;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "toggle") {
    isActive = !isActive;
    chrome.storage.local.set({ isActive: isActive });
    
    // Send status to content script
    chrome.tabs.query({url: "https://mail.google.com/*"}, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          action: "statusChange", 
          isActive: isActive
        });
      });
    });
    
    sendResponse({status: isActive ? "activated" : "deactivated"});
  }
  
  if (request.action === "getStatus") {
    sendResponse({isActive: isActive});
  }
});