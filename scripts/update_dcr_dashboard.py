#!/usr/bin/env python3
"""
DCR Dashboard Automation Script
Updates the Mumbai & Maharashtra DCR dashboard with verified amendments.
Validates data, updates HTML, and sends email notifications.
"""

import json
import os
import sys
import smtplib
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# Configuration
DATA_DIR = Path('data')
UPDATES_FILE = DATA_DIR / 'updates.json'
STATE_FILE = DATA_DIR / 'state.json'
DASHBOARD_FILE = 'mumbai-maharashtra-dcr-dashboard.html'

class DCRDashboardUpdater:
    """Main orchestrator for dashboard updates."""
    
    def __init__(self):
        self.updates = []
        self.state = {}
        self.new_verified_entry = None
        self.html_changed = False
        self.smtp_config = self._load_smtp_config()
    
    def _load_smtp_config(self):
        """Load SMTP configuration from environment."""
        return {
            'host': os.getenv('SMTP_HOST'),
            'port': int(os.getenv('SMTP_PORT', 587)),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD'),
            'from_addr': os.getenv('SMTP_FROM'),
            'dashboard_url': os.getenv('DASHBOARD_URL', 'https://Anandpatel245.github.io/dcr-dashboard/')
        }
    
    def load_data(self):
        """Load updates and state JSON files."""
        print("📂 Loading data files...")
        
        try:
            with open(UPDATES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.updates = data.get('updates', [])
            print(f"   ✓ Loaded {len(self.updates)} entries from updates.json")
        except Exception as e:
            print(f"   ✗ Error loading updates.json: {e}")
            sys.exit(1)
        
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
            print(f"   ✓ Loaded state from state.json")
        except Exception as e:
            print(f"   ✗ Error loading state.json: {e}")
            sys.exit(1)
    
    def find_new_verified_entry(self):
        """Find the newest verified entry."""
        verified_entries = [u for u in self.updates if u.get('verified') is True]
        
        if not verified_entries:
            print("ℹ️  No verified entries found")
            return None
        
        # Sort by date descending (newest first)
        verified_entries.sort(key=lambda x: x['date'], reverse=True)
        newest = verified_entries[0]
        
        # Check if this is truly new (not already in dashboard)
        # by comparing with stored state
        last_processed = self.state.get('last_verified_date')
        if newest['date'] > last_processed:
            print(f"✓ Found new verified entry: {newest['date']} - {newest['regulation']}")
            return newest
        else:
            print("ℹ️  No new verified entries since last run")
            return None
    
    def update_html_dashboard(self):
        """Update the dashboard HTML with latest data."""
        print(f"📝 Updating {DASHBOARD_FILE}...")
        
        if not Path(DASHBOARD_FILE).exists():
            print(f"   ✗ {DASHBOARD_FILE} not found")
            sys.exit(1)
        
        try:
            with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Update last verified run date
            run_date_elem = soup.find(id='runDate')
            if run_date_elem:
                run_date_elem.string = datetime.now().strftime('%d %b %Y')
                self.html_changed = True
            
            # Update state text
            state_text = self.state.get('update_state', 'No updates yet')
            state_elem = soup.find(id='stateText')
            if state_elem:
                state_elem.string = state_text
                self.html_changed = True
            
            # Update verified updates table (most recent first)
            self._update_verified_table(soup)
            
            # Update verified amendment log
            self._update_amendment_log(soup)
            
            # Write updated HTML
            with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            
            print("   ✓ HTML updated successfully")
        
        except Exception as e:
            print(f"   ✗ Error updating HTML: {e}")
            sys.exit(1)
    
    def _update_verified_table(self, soup):
        """Update the verified updates table."""
        verified_entries = [u for u in self.updates if u.get('verified') is True]
        verified_entries.sort(key=lambda x: x['date'], reverse=True)
        
        if not verified_entries:
            return
        
        # Find the verified updates table
        table = soup.find('table', {'class': 'table'})
        if not table:
            print("   ⚠️  Verified updates table not found")
            return
        
        tbody = table.find('tbody')
        if not tbody:
            tbody = BeautifulSoup('', 'lxml').new_tag('tbody')
            table.append(tbody)
        
        # Clear existing rows (keep header)
        for row in tbody.find_all('tr'):
            row.decompose()
        
        # Add verified entries
        for entry in verified_entries:
            row = BeautifulSoup('', 'lxml').new_tag('tr')
            
            cells = [
                entry['date'],
                entry['regulation'],
                entry['status'],
                f'<a href="{entry["verified_link"]}" target="_blank" rel="noopener noreferrer">Report</a>'
            ]
            
            for cell_content in cells:
                td = BeautifulSoup('', 'lxml').new_tag('td')
                td.append(BeautifulSoup(cell_content, 'lxml'))
                row.append(td)
            
            tbody.append(row)
        
        self.html_changed = True
        print(f"   ✓ Updated verified table with {len(verified_entries)} entries")
    
    def _update_amendment_log(self, soup):
        """Update the verified amendment log list."""
        verified_entries = [u for u in self.updates if u.get('verified') is True]
        verified_entries.sort(key=lambda x: x['date'], reverse=True)
        
        log_elem = soup.find(id='log')
        if not log_elem:
            print("   ⚠️  Amendment log not found")
            return
        
        # Clear existing items
        for li in log_elem.find_all('li'):
            li.decompose()
        
        # Add verified entries to log
        if verified_entries:
            for entry in verified_entries:
                li = BeautifulSoup('', 'lxml').new_tag('li')
                log_text = f"{entry['date']} – {entry['regulation']}: {entry['status']}"
                li.string = log_text
                log_elem.append(li)
        else:
            li = BeautifulSoup('', 'lxml').new_tag('li')
            li.string = 'No verified amendments yet.'
            log_elem.append(li)
        
        self.html_changed = True
        print(f"   ✓ Updated amendment log")
    
    def send_email_notification(self):
        """Send email notification if email config available."""
        if not all([self.smtp_config['host'], self.smtp_config['username']]):
            print("ℹ️  Email configuration not set. Skipping email.")
            return
        
        print("📧 Sending email notification...")
        
        try:
            # Determine email subject and body
            if self.new_verified_entry:
                subject = "DCR update: verified amendment"
                body = self._build_email_body_with_update()
            else:
                subject = "DCR update: no update"
                body = "No update today"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_config['from_addr']
            msg['To'] = 'anand.patel@quantumrealty.co.in'
            
            # Plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            print(f"   ✓ Email sent: {subject}")
        
        except Exception as e:
            print(f"   ⚠️  Email send failed: {e}")
            # Don't fail the workflow for email issues
    
    def _build_email_body_with_update(self):
        """Build email body for new verified amendment."""
        e = self.new_verified_entry
        return f"""DCR Dashboard Update

Amendment Date: {e['date']}
Regulation: {e['regulation']}
Status: {e['status']}

Verified Link: {e['verified_link']}

View full dashboard: {self.smtp_config['dashboard_url']}
"""
    
    def update_state(self):
        """Update state.json with current run info."""
        print("💾 Updating state.json...")
        
        if self.new_verified_entry:
            self.state['last_verified_date'] = self.new_verified_entry['date']
            self.state['update_state'] = f"Verified amendment: {self.new_verified_entry['regulation']}"
        
        self.state['last_run'] = datetime.now().isoformat()
        self.state['total_updates'] = len([u for u in self.updates if u.get('verified')])
        
        try:
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            print("   ✓ State saved")
        except Exception as e:
            print(f"   ✗ Error saving state: {e}")
            sys.exit(1)
    
    def run(self):
        """Execute the full update workflow."""
        print("=" * 60)
        print("🚀 DCR Dashboard Automation")
        print("=" * 60)
        
        # 1. Load data
        self.load_data()
        
        # 2. Find new verified entry
        self.new_verified_entry = self.find_new_verified_entry()
        
        # 3. Update HTML dashboard
        self.update_html_dashboard()
        
        # 4. Update state
        self.update_state()
        
        # 5. Send email (only if state and dashboard updated successfully)
        self.send_email_notification()
        
        print("=" * 60)
        if self.html_changed:
            print("✓ Dashboard updated. Commit changes in next step.")
        else:
            print("ℹ️  No changes made to dashboard.")
        print("=" * 60)

def main():
    """Entry point."""
    try:
        updater = DCRDashboardUpdater()
        updater.run()
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
