// options.js - Settings logic for the options page

// Load saved settings when the options page is opened
document.addEventListener('DOMContentLoaded', function() {
    // Get form and status elements
    const form = document.getElementById('settingsForm');
    const status = document.getElementById('status');
    const apiUrlInput = document.getElementById('apiUrl');
    const enableNotificationsCheckbox = document.getElementById('enableNotifications');
    
    // Load saved settings from Chrome storage
    chrome.storage.sync.get(['apiUrl', 'enableNotifications'], function(data) {
      // Set form values from storage
      if (data.apiUrl) {
        apiUrlInput.value = data.apiUrl;
      }
      
      enableNotificationsCheckbox.checked = data.enableNotifications !== false;
    });
    
    // Handle form submission
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      
      // Get values from form
      const apiUrl = apiUrlInput.value.trim();
      const enableNotifications = enableNotificationsCheckbox.checked;
      
      // Validate API URL
      if (!apiUrl) {
        showStatus('Please enter a valid API URL', 'error');
        return;
      }
      
      // Save settings to Chrome storage
      chrome.storage.sync.set({
        apiUrl: apiUrl,
        enableNotifications: enableNotifications
      }, function() {
        // Show success message
        showStatus('Settings saved successfully', 'success');
        
        // Test API connection
        testApiConnection(apiUrl);
      });
    });
    
    // Function to show status messages
    function showStatus(message, type) {
      status.textContent = message;
      status.className = 'status ' + type;
      status.style.display = 'block';
      
      // Hide the status message after 3 seconds
      setTimeout(function() {
        status.style.display = 'none';
      }, 3000);
    }
    
    // Test connection to the API endpoint
    function testApiConnection(apiUrl) {
      // Try to connect to the API
      fetch(apiUrl + '/ping', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('API connection failed with status: ' + response.status);
      })
      .then(data => {
        console.log('API connection successful:', data);
      })
      .catch(error => {
        console.error('API connection error:', error);
        showStatus('Warning: Could not connect to API server. Please check the URL and ensure the server is running.', 'error');
      });
    }
  });