document.addEventListener('DOMContentLoaded', function() {
    // Load saved settings
    chrome.storage.sync.get(['apiUrl'], function(data) {
      if (data.apiUrl) {
        document.getElementById('apiUrl').value = data.apiUrl;
      }
    });
    
    // Save settings
    document.getElementById('saveSettings').addEventListener('click', function() {
      const apiUrl = document.getElementById('apiUrl').value.trim();
      
      if (!apiUrl) {
        showStatus('Please enter the API URL', 'error');
        return;
      }
      
      // Save to Chrome storage
      chrome.storage.sync.set({
        apiUrl: apiUrl
      }, function() {
        showStatus('Settings saved successfully!', 'success');
      });
    });
    
    // Show status message
    function showStatus(message, type) {
      const status = document.getElementById('status');
      status.textContent = message;
      status.className = 'status ' + type;
      status.style.display = 'block';
      
      // Hide after 3 seconds
      setTimeout(function() {
        status.style.display = 'none';
      }, 3000);
    }
  });
  