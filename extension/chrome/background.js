// background.js - Background script for the extension
// Handles events that happen in the background

// Set default settings when the extension is installed
chrome.runtime.onInstalled.addListener(function() {
    // Set default values
    chrome.storage.sync.set({
      apiUrl: 'http://localhost:5000', // Default API URL (user should change this)
      sidebarExpanded: true,           // Default sidebar state
      enableNotifications: true        // Enable notifications by default
    }, function() {
      console.log('LPFJS: Default settings installed');
    });
  });
  
  // Listen for messages from content scripts
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    // Handle different message types
    switch (request.type) {
      case 'notification':
        // Show a Chrome notification
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon128.png',
          title: request.title || 'LPFJS Notification',
          message: request.message || '',
          priority: 1
        });
        sendResponse({success: true});
        break;
        
      case 'getSettings':
        // Return settings to the requesting script
        chrome.storage.sync.get(null, function(data) {
          sendResponse({success: true, settings: data});
        });
        return true; // Keep the message channel open for async response
        
      default:
        sendResponse({success: false, error: 'Unknown message type'});
    }
  });