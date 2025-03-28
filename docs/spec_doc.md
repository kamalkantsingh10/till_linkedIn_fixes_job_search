# **LinkedIn Chrome Extension Specification**

## **Overview**

This document outlines the specifications for a Chrome extension called "LPFJS" (LinkedIn Please Fix Job Search) that enhances LinkedIn functionality by adding custom tools for job search, profile analysis, and integration with external systems like Notion.

## **Architecture**

### **High-Level Architecture**

\+---------------------+    	\+---------------------+  
|                 	|    	|                 	|  
|  Chrome Extension   |  HTTP  |	Python Backend   |  
|  (JavaScript/HTML)  |\<------\>| 	(API Server)	|  
|                 	|    	|                 	|  
\+---------------------+    	\+---------------------+  
    	|                          	|  
    	| DOM                      	| API  
    	| Interaction              	| Requests  
    	v                          	v  
\+---------------------+    	\+---------------------+  
|                 	|    	|                 	|  
| 	LinkedIn    	|    	|  External Services  |  
| 	Website     	|    	|  (Notion, etc.) 	|  
|                 	|    	|                 	|  
\+---------------------+    	\+---------------------+

### **Extension Components**

1. **Router System (content.js)**  
   * Main entry point  
   * Page detection  
   * Module loading  
   * Sidebar management  
   * Navigation event handling  
2. **Core Module Structure**  
   * Sidebar UI (core/sidebar.js)  
   * Styles (core/styles.js)  
   * Storage management (core/storage.js)  
   * API communication (core/api.js)  
3. **Page-Specific Modules**  
   * Profile page (pages/profile.js)  
   * Job description page (pages/jobDescription.js)  
   * Job search results page (pages/jobSearch.js)  
   * Future page types can be added modularly  
4. **Utility Modules**  
   * DOM manipulation (utils/dom.js)  
   * Data extraction (utils/parser.js)  
   * Settings management (utils/settings.js)

### **Backend Components**

1. **API Endpoints**  
   * `/api/save-profile`: Process LinkedIn profile data  
   * `/api/save-job`: Process job listing data  
   * `/api/settings`: Manage user configuration  
2. **Processing Modules**  
   * Data normalization and cleaning  
   * Notion API integration  
   * Analytics (optional)  
3. **Authentication & Security**  
   * API key management  
   * Request validation

## **File Structure**

extension/  
├── manifest.json  
├── background.js  
├── content.js (main router)  
├── modules/  
│   ├── core/  
│   │   ├── sidebar.js  
│   │   ├── styles.js  
│   │   ├── storage.js  
│   │   └── api.js  
│   ├── pages/  
│   │   ├── profile.js  
│   │   ├── jobDescription.js  
│   │   └── jobSearch.js  
│   └── utils/  
│   	├── dom.js  
│   	├── parser.js  
│   	└── settings.js  
├── popup/  
│   ├── popup.html  
│   └── popup.js  
└── assets/  
	└── icons/

backend/  
├── app.py (main API server)  
├── requirements.txt  
├── config.py  
├── services/  
│   ├── notion\_service.py  
│   ├── profile\_service.py  
│   └── job\_service.py  
├── models/  
│   ├── profile.py  
│   └── job.py  
└── utils/  
	├── data\_cleaner.py  
	└── auth.py

## **Functional Requirements**

### **Core Functionality**

1. **Sidebar UI**  
   * Spans full height of LinkedIn page  
   * Takes 25% of viewport width with minimum 150px  
   * Collapses to show only toggle button  
   * Automatically refreshes on page navigation  
   * Footer with three-column layout and help button  
2. **Page Detection & Adaptation**  
   * Automatically detect current LinkedIn page type  
   * Load appropriate module for each page type  
   * Display relevant tools for the current page  
3. **LinkedIn Integration**  
   * Respect LinkedIn's layout without breaking functionality  
   * Adjust sidebar position to avoid covering content  
   * Adapt to LinkedIn's design language for visual coherence

### **Page-Specific Functionality**

1. **Profile Pages**  
   * Extract key profile information  
   * Option to save profile to Notion  
   * Future: Profile analysis and insights  
2. **Job Description Pages**  
   * Extract job details (title, company, description, etc.)  
   * Save job descriptions to Notion  
   * Future: Job matching and recommendation features  
3. **Job Search Results Pages**  
   * Enhanced filtering options  
   * Quick actions for job listings  
   * Future: Custom sorting and filtering tools

### **Backend Integration**

1. **Data Processing**  
   * Clean and normalize LinkedIn data  
   * Structure data for external system integration  
   * Error handling and validation  
2. **Notion Integration**  
   * Save profiles and job listings to Notion  
   * Maintain consistent structure for saved items  
   * Support configurable Notion templates

## **Technical Requirements**

### **Extension Requirements**

1. **Performance**  
   * Minimal impact on LinkedIn page load times  
   * Efficient DOM manipulation  
   * Throttled API requests  
2. **Compatibility**  
   * Support for Chrome browser (primary)  
   * Future consideration for Firefox/Edge  
3. **Responsiveness**  
   * Adapt to different screen sizes  
   * Maintain usability on smaller screens

### **Backend Requirements**

1. **API Design**  
   * RESTful API architecture  
   * Clear request/response formats  
   * Comprehensive error handling  
2. **Security**  
   * HTTPS for all communications  
   * API key validation  
   * Input sanitization  
3. **Scalability**  
   * Stateless design for horizontal scaling  
   * Caching where appropriate

## **User Interface Design**

### **Sidebar Components**

1. **Header**  
   * Title ("LPFJS")  
   * Toggle button for collapse/expand  
2. **Content Area**  
   * Dynamic content based on current page  
   * Section cards with clear headings  
   * Action buttons for core functionality  
3. **Footer**  
   * Three-column layout  
   * Help button in first column  
   * Reserved space for future controls

### **Visual Style**

1. **Integration with LinkedIn**  
   * Match LinkedIn's color scheme and typography  
   * Use similar card styles and shadows  
   * Maintain consistent spacing and padding  
2. **Interactive Elements**  
   * Clear button states (default, hover, active)  
   * Visual feedback for actions  
   * Consistent iconography

## **Implementation Plan**

### **Phase 1: Core Infrastructure**

* Setup extension boilerplate and module system  
* Implement sidebar UI framework  
* Create page detection and routing system  
* Establish communication with backend

### **Phase 2: Profile & Job Functionality**

* Implement profile data extraction  
* Create job description parser  
* Build basic Notion integration for both  
* Add user feedback mechanisms

### **Phase 3: Enhanced Features**

* Add job search results enhancements  
* Implement additional Notion templates  
* Develop user settings and customization  
* Polish UI and fix edge cases

### **Phase 4: Expansion**

* Support additional LinkedIn page types  
* Integrate with additional external services  
* Add analytics and insights features  
* Consider browser compatibility expansion

## **Testing Strategy**

1. **Unit Testing**  
   * Test individual modules in isolation  
   * Validate data extraction functionality  
   * Ensure proper error handling  
2. **Integration Testing**  
   * Test module interactions  
   * Verify communication with backend  
   * Validate Notion integration  
3. **User Testing**  
   * Test on various LinkedIn page types  
   * Validate on different screen sizes  
   * Collect user feedback on usability

## **Maintenance Considerations**

1. **LinkedIn Page Changes**  
   * Monitor LinkedIn DOM structure for changes  
   * Design selectors for resilience  
   * Implement version checking and updates  
2. **Notion API Updates**  
   * Monitor Notion API changes  
   * Maintain version compatibility  
   * Plan for migration as needed  
3. **Error Monitoring**  
   * Implement logging for extension errors  
   * Create error reporting mechanism  
   * Plan for quick fixes and updates

## **Future Enhancements**

1. **AI Integration**  
   * Job description analysis  
   * Profile optimization suggestions  
   * Custom matching algorithms  
2. **Additional Integrations**  
   * Support for CRM systems  
   * ATS integration  
   * Calendar scheduling  
3. **Advanced Analytics**  
   * Job search tracking  
   * Application success metrics  
   * Market insights

