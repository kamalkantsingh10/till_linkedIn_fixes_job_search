from datetime import datetime
from typing import Dict, List, Optional, Any
from notion_client import Client
from framework.connectors.notion.connector import NotionConnection


class JobApplicationManager:
    """
    A class to manage job applications in a Notion database.
    Built on top of the NotionConnection class for API interactions.
    """
    
    # Status options for job applications
    STATUS_OPTIONS = [
        "Applied", 
        "Screening", 
        "Interview", 
        "Final Round", 
        "Offer", 
        "Rejected", 
        "Withdrawn"
    ]
    
    # Confidence level options
    CONFIDENCE_OPTIONS = ["Low", "Medium", "High"]
    
    # Referral options
    REFERRAL_OPTIONS = ["Yes", "No"]
    
    def __init__(self, notion_connection: NotionConnection, database_id: str):
        """
        Initialize the JobApplicationManager with a NotionConnection instance
        and the ID of the job applications database.
        
        Args:
            notion_connection (NotionConnection): An initialized NotionConnection
            database_id (str): The ID of the job applications database in Notion
        """
        self.notion = notion_connection
        self.database_id = database_id
    
    def add_application(self, company: str, role: str, url: str, 
                        status: str = "Applied", confidence: str = "Low", 
                        referral: str = "No", contact_person: str = "", 
                        location: str = "", job_description: str = "") -> Dict:
        """
        Add a new job application to the database.
        
        Args:
            company (str): Company name
            role (str): Job title/role
            url (str): URL of the job posting
            status (str, optional): Application status. Defaults to "Applied".
            confidence (str, optional): Confidence level. Defaults to "Low".
            referral (str, optional): Whether you have a referral. Defaults to "No".
            contact_person (str, optional): Recruiter or hiring manager. Defaults to "".
            location (str, optional): Job location. Defaults to "".
            job_description (str, optional): Description of the job. Defaults to "".
            
        Returns:
            Dict: The created application
            
        Raises:
            ValueError: If status, confidence, or referral is invalid
            ValueError: If application with same company and role already exists
        """
        # Validate status
        if status not in self.STATUS_OPTIONS:
            raise ValueError(f"Status must be one of: {', '.join(self.STATUS_OPTIONS)}")
        
        # Validate confidence
        if confidence not in self.CONFIDENCE_OPTIONS:
            raise ValueError(f"Confidence must be one of: {', '.join(self.CONFIDENCE_OPTIONS)}")
        
        # Validate referral
        if referral not in self.REFERRAL_OPTIONS:
            raise ValueError(f"Referral must be one of: {', '.join(self.REFERRAL_OPTIONS)}")
        
        # Check for existing application with same company and role (case insensitive)
        existing_apps = self.search_applications(company=company, role=role)
        for app in existing_apps:
            # Extract company and role from the existing application
            app_company = self._extract_text_property(app, "Company")
            app_role = self._extract_text_property(app, "Role")
            
            # Case insensitive comparison
            if (app_company.lower() == company.lower() and 
                app_role.lower() == role.lower()):
                raise ValueError(f"Application for {company} - {role} already exists")
        
        # Create the title: "Company - Role"
        title = f"{company} - {role}"
        
        # Get current date in ISO format with timezone information
        current_date = datetime.now().astimezone().isoformat()
        
        # Create properties for the new application
        properties = {
            "title": self.notion.title_property(title),
            "Company": self.notion.text_property(company),
            "Role": self.notion.text_property(role),
            "URL": self.notion.url_property(url),
            "Application Date": self.notion.date_property(current_date),
            "Status": self.notion.select_property(status),
            "Confidence": self.notion.select_property(confidence),
            "Referral": self.notion.select_property(referral),
            "Contact Person": self.notion.text_property(contact_person),
            "Location": self.notion.text_property(location),
            "Job Description": self.notion.text_property(job_description)
        }
        
        # Add the application to the database
        return self.notion.add_row(self.database_id, properties)
    
    def update_status(self, page_id: str, new_status: str) -> Dict:
        """
        Update the status of a job application.
        
        Args:
            page_id (str): The ID of the application page
            new_status (str): The new status
            
        Returns:
            Dict: The updated application
        """
        # Validate status
        if new_status not in self.STATUS_OPTIONS:
            raise ValueError(f"Status must be one of: {', '.join(self.STATUS_OPTIONS)}")
        
        # Update the status
        properties = {
            "Status": self.notion.select_property(new_status)
        }
        
        return self.notion.update_row(page_id, properties)
    
    def get_applications(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        Get all job applications, optionally filtered by status.
        
        Args:
            status_filter (str, optional): Filter by this status. Defaults to None.
            
        Returns:
            List[Dict]: Matching applications
        """
        # Create filter if status is provided
        filter_params = None
        if status_filter:
            if status_filter not in self.STATUS_OPTIONS:
                raise ValueError(f"Status must be one of: {', '.join(self.STATUS_OPTIONS)}")
            
            filter_params = {
                "property": "Status",
                "select": {
                    "equals": status_filter
                }
            }
        
        # Sort by application date, newest first
        sorts = [
            {
                "property": "Application Date",
                "direction": "descending"
            }
        ]
        
        # Get the applications
        return self.notion.get_all_rows(self.database_id, filter_params, sorts)
    
    def search_applications(self, company: Optional[str] = None, 
                            role: Optional[str] = None) -> List[Dict]:
        """
        Search for applications by company name, role, or both.
        
        Args:
            company (str, optional): Company name to search for. Defaults to None.
            role (str, optional): Role to search for. Defaults to None.
            
        Returns:
            List[Dict]: Matching applications
        """
        if not company and not role:
            # If neither is provided, return all applications
            return self.get_applications()
        
        filter_params = {}
        
        # Create filters based on provided search criteria
        if company and role:
            # Search for both company AND role
            filter_params = {
                "and": [
                    {
                        "property": "Company",
                        "rich_text": {
                            "contains": company
                        }
                    },
                    {
                        "property": "Role",
                        "rich_text": {
                            "contains": role
                        }
                    }
                ]
            }
        elif company:
            # Search only by company
            filter_params = {
                "property": "Company",
                "rich_text": {
                    "contains": company
                }
            }
        elif role:
            # Search only by role
            filter_params = {
                "property": "Role",
                "rich_text": {
                    "contains": role
                }
            }
        
        # Sort by application date, newest first
        sorts = [
            {
                "property": "Application Date",
                "direction": "descending"
            }
        ]
        
        # Get the matching applications
        return self.notion.get_all_rows(self.database_id, filter_params, sorts)
    
    # Helper method for extracting text from Notion properties
    def _extract_text_property(self, page: Dict, property_name: str) -> str:
        """
        Helper method to extract text from a Notion page property.
        
        Args:
            page (Dict): The Notion page
            property_name (str): Name of the property
            
        Returns:
            str: Extracted text or empty string if not found
        """
        try:
            prop = page.get("properties", {}).get(property_name, {})
            
            # Handle rich_text properties
            if prop.get("type") == "rich_text":
                rich_text = prop.get("rich_text", [])
                if rich_text:
                    return rich_text[0].get("plain_text", "")
            
            # Handle title properties
            elif prop.get("type") == "title":
                title = prop.get("title", [])
                if title:
                    return title[0].get("plain_text", "")
                    
            return ""
        except (KeyError, IndexError):
            return ""