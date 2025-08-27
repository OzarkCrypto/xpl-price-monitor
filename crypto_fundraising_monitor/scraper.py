"""
Web scraper module for Crypto Fundraising Monitor
"""
import requests
import time
import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from .models import FundraisingProject, Investor, ScrapedData
from .config import BASE_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)


class CryptoFundraisingScraper:
    """Scrape fundraising data from crypto-fundraising.info"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _make_request(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if retries < MAX_RETRIES:
                logger.warning(f"Request failed (attempt {retries + 1}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY * (2 ** retries))  # Exponential backoff
                return self._make_request(url, retries + 1)
            else:
                logger.error(f"Request failed after {MAX_RETRIES} attempts: {e}")
                return None
    
    def _parse_amount(self, amount_str: str) -> int:
        """Parse amount string to USD integer"""
        if not amount_str or amount_str.strip() == '':
            return 0
        
        amount_str = amount_str.strip().replace(',', '').replace('$', '')
        
        # Handle special cases
        if amount_str.upper() == 'TBD':
            return 0
        
        # Handle K, M, B suffixes
        multiplier = 1
        if amount_str.endswith('K'):
            multiplier = 1000
            amount_str = amount_str[:-1]
        elif amount_str.endswith('M'):
            multiplier = 1000000
            amount_str = amount_str[:-1]
        elif amount_str.endswith('B'):
            multiplier = 1000000000
            amount_str = amount_str[:-1]
        
        try:
            return int(float(amount_str) * multiplier)
        except ValueError:
            logger.warning(f"Could not parse amount: {amount_str}")
            return 0
    
    def _parse_investors(self, investors_col) -> List[Investor]:
        """Parse investor elements to list of Investor objects"""
        investors = []
        
        # First try to get investors from the mobile-only text list
        mobile_list = investors_col.find('div', class_='mob-only investlist')
        if mobile_list:
            investor_text = mobile_list.get_text(strip=True)
            if investor_text:
                # Split by comma and clean up
                investor_names = [name.strip() for name in investor_text.split(',')]
                for name in investor_names:
                    if name:
                        # Check if this is a lead investor (usually first in list)
                        is_lead = len(investors) == 0  # First investor is usually lead
                        investors.append(Investor(name=name, is_lead=is_lead))
        
        # If no text investors found, try to get from image elements
        if not investors:
            investor_elements = investors_col.find_all('a', class_='investlogo-small')
            for element in investor_elements:
                # Get investor name from title attribute
                title = element.get('title', '')
                if title:
                    # Check if this is a lead investor
                    is_lead = 'Lead investor' in title
                    # Clean the name
                    name = title.replace(' | Lead investor', '').strip()
                    if name:
                        investors.append(Investor(name=name, is_lead=is_lead))
        
        return investors
    
    def _extract_project_from_row(self, row) -> Optional[FundraisingProject]:
        """Extract project data from a table row"""
        try:
            # Find all columns
            cols = row.find_all('div', class_=lambda x: x and x.startswith('hpt-col'))
            
            if len(cols) < 6:
                return None
            
            # Extract data from each column
            # Column 1: Number (skip)
            # Column 2: Project name and info
            project_col = row.find('div', class_='hpt-col2')
            if not project_col:
                return None
            
            # Get project name
            title_elem = project_col.find('h5', class_='cointitle')
            if not title_elem:
                return None
            
            name = title_elem.get_text(strip=True)
            
            # Get project URL
            link_elem = project_col.find('a', class_='t-project-link')
            url = link_elem.get('href') if link_elem else None
            if url and not url.startswith('http'):
                url = f"https://crypto-fundraising.info{url}"
            
            # Column 3: Round type
            round_col = row.find('div', class_='hpt-col3')
            round_type = round_col.get_text(strip=True) if round_col else ''
            
            # Column 4: Date (second hpt-col3)
            date_cols = row.find_all('div', class_='hpt-col3')
            date = date_cols[1].get_text(strip=True) if len(date_cols) > 1 else ''
            
            # Column 5: Amount (hpt-col4)
            amount_col = row.find('div', class_='hpt-col4')
            amount_str = ''
            if amount_col:
                amount_elem = amount_col.find('span', class_='abbrusd')
                if amount_elem:
                    amount_str = amount_elem.get_text(strip=True)
            
            # Column 6: Category (hpt-col5)
            category_col = row.find('div', class_='hpt-col5')
            category = ''
            if category_col:
                cat_elem = category_col.find('span', class_='catitem')
                if cat_elem:
                    category = cat_elem.get_text(strip=True)
            
            # Column 7: Investors (hpt-col6)
            investors_col = row.find('div', class_='hpt-col6')
            investors = []
            if investors_col:
                investors = self._parse_investors(investors_col)
            
            # Skip if essential fields are missing
            if not name:
                return None
            
            # Parse amount
            amount_usd = self._parse_amount(amount_str)
            
            # Create project object
            project = FundraisingProject(
                name=name,
                round_type=round_type,
                date=date,
                amount_usd=amount_usd,
                project_category=category,
                investors=investors,
                url=url
            )
            
            return project
            
        except Exception as e:
            logger.error(f"Error parsing project row: {e}")
            return None
    
    def scrape_fundraising_data(self) -> Optional[ScrapedData]:
        """Scrape fundraising data from the website"""
        logger.info("Starting to scrape crypto-fundraising.info")
        
        response = self._make_request(BASE_URL)
        if not response:
            logger.error("Failed to fetch website")
            return None
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            projects = []
            
            # Look for project rows with class 'hp-table-row hpt-data'
            project_rows = soup.find_all('div', class_=['hp-table-row', 'hpt-data'])
            
            logger.info(f"Found {len(project_rows)} potential project rows")
            
            for row in project_rows:
                # Check if this row has the data-eid attribute (indicates it's a project row)
                if row.get('data-eid'):
                    project = self._extract_project_from_row(row)
                    if project:
                        projects.append(project)
            
            if not projects:
                logger.warning("No projects found on the page")
                return None
            
            logger.info(f"Successfully scraped {len(projects)} projects")
            return ScrapedData(projects=projects)
            
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return None
    
    def close(self):
        """Close the session"""
        self.session.close() 