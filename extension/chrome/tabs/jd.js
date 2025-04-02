// Create a namespace for Job page functions
window.LPFJS_Job = (function() {
    // Initialize job page functionality
    const initJobPage = function(sidebar) {
      console.log('Initializing job page functionality');
      
      // Get the content container from the sidebar
      const contentContainer = sidebar.querySelector('.lpfjs-content');
      
      // Create job description actions section
      const jobSection = LPFJS_UI.createSection('Job Description Actions');
      
      // Add message about functionality
      const message = LPFJS_UI.createMessage('Extract job description data and send to your backend');
      jobSection.appendChild(message);
      
      // Create extract job description button
      const extractButton = LPFJS_UI.createButton('Extract Job Data', async () => {
        try {
          // Get full page HTML content for backend processing
          const jobData = {
            url: window.location.href,
            html: document.documentElement.outerHTML,
            timestamp: new Date().toISOString()
          };
          
          // Show extraction in progress
          LPFJS_UI.showNotification('Extracting job data...', 'info');
          
          // Send to Flask backend
          const result = await LPFJS_API.sendToFlask('/api/job', jobData);
          
          // Show success message
          LPFJS_UI.showNotification('Job data sent to backend successfully!', 'success');
          
          console.log('Job data sent to backend:', result);
        } catch (error) {
          console.error('Error sending job data:', error);
          LPFJS_UI.showNotification('Error sending job data: ' + error.message, 'error');
        }
      });
      
      jobSection.appendChild(extractButton);
      
      // Create save job button
      const saveButton = LPFJS_UI.createButton('Save Job to Database', async () => {
        try {
          // Get job title and company (basic extraction on client side)
          const jobTitleElement = document.querySelector('.job-details-jobs-unified-top-card__job-title');
          const jobTitle = jobTitleElement ? jobTitleElement.textContent.trim() : 'Unknown Job Title';
          
          const companyElement = document.querySelector('.job-details-jobs-unified-top-card__company-name');
          const companyName = companyElement ? companyElement.textContent.trim() : 'Unknown Company';
          
          // Get full page HTML content for backend processing
const jobData = {
    title: jobTitle,
    company: companyName,
    url: window.location.href,
    html: document.documentElement.outerHTML,
    timestamp: new Date().toISOString(),
    action: 'save'
  };
  
  // Show saving in progress
  LPFJS_UI.showNotification('Saving job to database...', 'info');
  
  // Send to Flask backend
  const result = await LPFJS_API.sendToFlask('/api/save-job', jobData);
  
  // Show success message
  LPFJS_UI.showNotification('Job saved to database successfully!', 'success');
  
  console.log('Job saved to database:', result);
} catch (error) {
  console.error('Error saving job:', error);
  LPFJS_UI.showNotification('Error saving job: ' + error.message, 'error');
}
});

jobSection.appendChild(saveButton);

// Add API status info
const statusInfo = document.createElement('div');
statusInfo.style.fontSize = '12px';
statusInfo.style.marginTop = '12px';
statusInfo.style.color = 'var(--linkedin-secondary-text)';
jobSection.appendChild(statusInfo);

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
contentContainer.appendChild(jobSection);

// Create application tools section
const applicationSection = LPFJS_UI.createSection('Application Tools');

// Create generate cover letter button
const coverLetterButton = LPFJS_UI.createButton('Generate Cover Letter', async () => {
try {
  // Get job title and company (basic extraction on client side)
  const jobTitleElement = document.querySelector('.job-details-jobs-unified-top-card__job-title');
  const jobTitle = jobTitleElement ? jobTitleElement.textContent.trim() : 'Unknown Job Title';
  
  const companyElement = document.querySelector('.job-details-jobs-unified-top-card__company-name');
  const companyName = companyElement ? companyElement.textContent.trim() : 'Unknown Company';
  
  // Create a form for entering resume info
  const form = document.createElement('div');
  form.style.marginTop = '10px';
  
  const textarea = document.createElement('textarea');
  textarea.placeholder = `Enter key points from your resume relevant to this ${jobTitle} position at ${companyName}...`;
  textarea.style.width = '100%';
  textarea.style.padding = '8px';
  textarea.style.borderRadius = '4px';
  textarea.style.border = '1px solid var(--linkedin-border-color)';
  textarea.style.minHeight = '100px';
  textarea.style.resize = 'vertical';
  textarea.style.marginBottom = '10px';
  
  const generateBtn = LPFJS_UI.createButton('Generate & Copy', async () => {
    try {
      // Get the entered resume points
      const resumePoints = textarea.value.trim();
      
      if (!resumePoints) {
        LPFJS_UI.showNotification('Please enter your key resume points', 'error');
        return;
      }
      
      // Show processing message
      LPFJS_UI.showNotification('Generating cover letter...', 'info');
      
      // Get job data for context
      const jobData = {
        title: jobTitle,
        company: companyName,
        resumePoints: resumePoints,
        url: window.location.href,
        html: document.documentElement.outerHTML,
        timestamp: new Date().toISOString()
      };
      
      // Send to Flask backend
      const result = await LPFJS_API.sendToFlask('/api/generate-cover-letter', jobData);
      
      if (result && result.coverLetter) {
        // Create a temporary textarea to copy the text
        const tempTextarea = document.createElement('textarea');
        tempTextarea.value = result.coverLetter;
        document.body.appendChild(tempTextarea);
        tempTextarea.select();
        document.execCommand('copy');
        document.body.removeChild(tempTextarea);
        
        // Show success message
        LPFJS_UI.showNotification('Cover letter generated and copied to clipboard!', 'success');
        
        // Clear the form
        textarea.value = '';
      } else {
        throw new Error('No cover letter returned from backend');
      }
    } catch (error) {
      console.error('Error generating cover letter:', error);
      LPFJS_UI.showNotification('Error generating cover letter: ' + error.message, 'error');
    }
  });
  
  form.appendChild(textarea);
  form.appendChild(generateBtn);
  
  // Add to section
  applicationSection.appendChild(form);
} catch (error) {
  console.error('Error setting up cover letter form:', error);
  LPFJS_UI.showNotification('Error setting up cover letter form: ' + error.message, 'error');
}
});

applicationSection.appendChild(coverLetterButton);

// Create resume match analysis button
const resumeMatchButton = LPFJS_UI.createButton('Resume Match Analysis', () => {
LPFJS_UI.showNotification('Resume match analysis feature coming soon!', 'info');
});

applicationSection.appendChild(resumeMatchButton);
contentContainer.appendChild(applicationSection);
};

// Return public functions
return {
initJobPage: initJobPage
};
})();