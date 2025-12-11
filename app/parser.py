"""
Parser for customer session data from text format.
"""

import re
from typing import Dict, Optional


def parse_session_data(text: str) -> Optional[Dict]:
    """
    Parse customer session data from text format.
    
    Expected format:
    Customer: mediconas.cz [15 mins]
    Region: EU
    Sessions: 5
    Source: FB Pages
    Destination: BQ
    Observation: ...
    
    Args:
        text: Raw text input
        
    Returns:
        Dictionary with parsed data or None if parsing fails
    """
    if not text or not text.strip():
        return None
    
    # Normalize line endings and clean up text
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = text.strip()
    
    data = {}
    
    # Extract Customer (with optional time in brackets)
    customer_match = re.search(r'Customer:\s*(.+?)(?:\s*\[.*?\])?\s*$', text, re.MULTILINE | re.IGNORECASE)
    if customer_match:
        data['customer'] = customer_match.group(1).strip()
    
    # Extract Region
    region_match = re.search(r'Region:\s*(.+?)\s*$', text, re.MULTILINE | re.IGNORECASE)
    if region_match:
        data['region'] = region_match.group(1).strip()
    
    # Extract Sessions (number)
    sessions_match = re.search(r'Sessions:\s*(\d+)\s*$', text, re.MULTILINE | re.IGNORECASE)
    if sessions_match:
        data['sessions'] = int(sessions_match.group(1))
    
    # Extract Source
    source_match = re.search(r'Source:\s*(.+?)\s*$', text, re.MULTILINE | re.IGNORECASE)
    if source_match:
        data['source'] = source_match.group(1).strip()
    
    # Extract Destination
    destination_match = re.search(r'Destination:\s*(.+?)\s*$', text, re.MULTILINE | re.IGNORECASE)
    if destination_match:
        data['destination'] = destination_match.group(1).strip()
    
    # Extract Time Consumed (optional, can be in brackets like [15 mins] or separate line)
    time_match = re.search(r'Time\s*Consumed:\s*(\d+)\s*(?:mins?|minutes?)?\s*$', text, re.MULTILINE | re.IGNORECASE)
    if not time_match:
        # Also check for time in brackets after Customer (e.g., [15 mins] or [15])
        time_match = re.search(r'Customer:.*?\[(\d+)\s*(?:mins?|minutes?)?\]', text, re.MULTILINE | re.IGNORECASE)
    if time_match:
        try:
            time_value = int(time_match.group(1).strip())
            if 1 <= time_value <= 120:
                data['time_consumed'] = time_value
        except ValueError:
            pass  # Ignore if not a valid integer
    
    # Extract Observation (everything after "Observation:" until end of text)
    observation_match = re.search(r'Observation:\s*(.+)$', text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if observation_match:
        observation_text = observation_match.group(1).strip()
        # Only add if observation has content
        if observation_text:
            data['observation'] = observation_text
    else:
        # Observation is optional, set empty string if not found
        data['observation'] = ''
    
    # Validate required fields
    required_fields = ['customer', 'region', 'sessions', 'source', 'destination']
    if all(field in data for field in required_fields):
        return data
    
    return None

