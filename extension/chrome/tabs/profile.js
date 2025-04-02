// Create a namespace for Profile page functions
window.LPFJS_Profile = (function() {
    // Initialize profile page functionality
    const initProfilePage = function(sidebar) {
      console.log('Initializing profile page functionality');
      
      // Get the content container from the sidebar
      const contentContainer = sidebar.querySelector('.lpfjs-content');
      
      // Create profile actions section
      const profileSection = LPFJS_UI.createSection('Profile Actions');
      
      // Add message about functionality
      const message = LPFJS_UI.createMessage('Extract data from this LinkedIn profile and send to your backend');
      profileSection.appendChild(message);
      
      // Create extract profile button
      const extractButton = LPFJS_UI.createButton('Extract Profile Data', async () => {
        try {
          // Get full page HTML content for backend processing
          const profileData = {
            url: window.location.href,
            html: document.documentElement.outerHTML,
            timestamp: new Date().toISOString()
          };
          
          // Show extraction in progress
          LPFJS_UI.showNotification('Extracting profile data...', 'info');
          
          // Send to Flask backend
          const result = await LPFJS_API.sendToFlask('/api/profile', profileData);
          
          // Show success message
          LPFJS_UI.showNotification('Profile data sent to backend successfully!', 'success');
          
          console.log('Profile data sent to backend:', result);
        } catch (error) {
          console.error('Error sending profile data:', error);
          LPFJS_UI.showNotification('Error sending profile data: ' + error.message, 'error');
        }
      });
      
      profileSection.appendChild(extractButton);
      
      // Create extract connections button
      const connectionsButton = LPFJS_UI.createButton('Extract Connections', async () => {
        try {
          // First check if we're on a connections page
          if (!window.location.href.includes('/connections')) {
            LPFJS_UI.showNotification('Please navigate to the connections page first', 'error');
            return;
          }
          
          // Get connections page content
          const connectionsData = {
            url: window.location.href,
            html: document.documentElement.outerHTML,
            timestamp: new Date().toISOString()
          };
          
          // Show extraction in progress
          LPFJS_UI.showNotification('Extracting connections data...', 'info');
          
          // Send to Flask backend
          const result = await LPFJS_API.sendToFlask('/api/connections', connectionsData);
          
          // Show success message
          LPFJS_UI.showNotification('Connections data sent to backend successfully!', 'success');
          
          console.log('Connections data sent to backend:', result);
        } catch (error) {
          console.error('Error sending connections data:', error);
          LPFJS_UI.showNotification('Error sending connections data: ' + error.message, 'error');
        }
      });
      
      profileSection.appendChild(connectionsButton);
      
      // Add API status info
      const statusInfo = document.createElement('div');
      statusInfo.style.fontSize = '12px';
      statusInfo.style.marginTop = '12px';
      statusInfo.style.color = 'var(--linkedin-secondary-text)';
      profileSection.appendChild(statusInfo);
      
      // Check API connection
      chrome.storage.sync.get(['apiUrl'], function(data) {
        if (data.apiUrl) {
          statusInfo.textContent = `API: ${data.apiUrl}`;
        } else {
          statusInfo.textContent = 'API not configured. See extension options.';
          statusInfo.style.color = '#dc3545';
        }
      });
      
      // Add the section to the content container
      contentContainer.appendChild(profileSection);
      
      // Add custom actions section
      const customSection = LPFJS_UI.createSection('Custom Actions');
      
      // Add message button - for sending messages through the backend
      const messageButton = LPFJS_UI.createButton('Compose Follow-up', () => {
        // Get profile name (basic extraction on client side)
        const nameElement = document.querySelector('.text-heading-xlarge');
        const name = nameElement ? nameElement.textContent.trim() : 'this person';
        
        // Create a simple form for entering message
        const form = document.createElement('div');
        form.style.marginTop = '10px';
        
        const textarea = document.createElement('textarea');
        textarea.placeholder = `Write your follow-up message to ${name}...`;
        textarea.style.width = '100%';
        textarea.style.padding = '8px';
        textarea.style.borderRadius = '4px';
        textarea.style.border = '1px solid var(--linkedin-border-color)';
        textarea.style.minHeight = '100px';
        textarea.style.resize = 'vertical';
        textarea.style.marginBottom = '10px';
        
        const sendBtn = LPFJS_UI.createButton('Generate & Copy', async () => {
          try {
            // Get the entered message
            const messageText = textarea.value.trim();
            
            if (!messageText) {
              LPFJS_UI.showNotification('Please enter some context for your message', 'error');
              return;
            }
            
            // Show processing message
            LPFJS_UI.showNotification('Generating follow-up message...', 'info');
            
            // Get page data for context
            const profileData = {
              url: window.location.href,
              name: name,
              messageContext: messageText,
              html: document.documentElement.outerHTML,
              timestamp: new Date().toISOString()
            };
            
            // Send to Flask backend
            const result = await LPFJS_API.sendToFlask('/api/generate-followup', profileData);
            
            if (result && result.message) {
              // Create a temporary textarea to copy the text
              const tempTextarea = document.createElement('textarea');
              tempTextarea.value = result.message;
              document.body.appendChild(tempTextarea);
              tempTextarea.select();
              document.execCommand('copy');
              document.body.removeChild(tempTextarea);
              
              // Show success message
              LPFJS_UI.showNotification('Message generated and copied to clipboard!', 'success');
              
              // Clear the form
              textarea.value = '';
            } else {
              throw new Error('No message returned from backend');
            }
          } catch (error) {
            console.error('Error generating message:', error);
            LPFJS_UI.showNotification('Error generating message: ' + error.message, 'error');
          }
        });
        
        form.appendChild(textarea);
        form.appendChild(sendBtn);
        
        // Add to section
        customSection.appendChild(form);
      });
      
      customSection.appendChild(messageButton);
      contentContainer.appendChild(customSection);
    };
    
    // Return public functions
    return {
      initProfilePage: initProfilePage
    };
  })();