#!/usr/bin/env python3
"""
Validate JSON files for DCR dashboard updates.
Ensures required fields and data integrity before processing.
"""

import json
import sys
from pathlib import Path

REQUIRED_UPDATE_FIELDS = {'date', 'regulation', 'status', 'verified_link', 'source_type', 'verified'}
REQUIRED_STATE_FIELDS = {'last_verified_run', 'update_state', 'total_updates'}

def validate_updates_json(file_path):
    """Validate data/updates.json structure and content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict) or 'updates' not in data:
            raise ValueError("updates.json must contain 'updates' key with list value")
        
        if not isinstance(data['updates'], list):
            raise ValueError("'updates' must be a list")
        
        for idx, update in enumerate(data['updates']):
            if not isinstance(update, dict):
                raise ValueError(f"Update {idx} is not a dictionary")
            
            missing = REQUIRED_UPDATE_FIELDS - set(update.keys())
            if missing:
                raise ValueError(f"Update {idx} missing required fields: {missing}")
            
            if not isinstance(update['verified'], bool):
                raise ValueError(f"Update {idx} 'verified' must be boolean")
            
            if not update['date']:
                raise ValueError(f"Update {idx} 'date' cannot be empty")
            
            if not update['verified_link'].startswith(('http://', 'https://')):
                raise ValueError(f"Update {idx} 'verified_link' must be valid URL")
        
        print(f"✓ updates.json is valid ({len(data['updates'])} entries)")
        return True
    
    except json.JSONDecodeError as e:
        print(f"✗ JSON parse error in updates.json: {e}")
        return False
    except (KeyError, ValueError, TypeError) as e:
        print(f"✗ Validation error in updates.json: {e}")
        return False

def validate_state_json(file_path):
    """Validate data/state.json structure."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            raise ValueError("state.json must be a dictionary")
        
        missing = REQUIRED_STATE_FIELDS - set(data.keys())
        if missing:
            raise ValueError(f"state.json missing required fields: {missing}")
        
        print(f"✓ state.json is valid")
        return True
    
    except json.JSONDecodeError as e:
        print(f"✗ JSON parse error in state.json: {e}")
        return False
    except (KeyError, ValueError, TypeError) as e:
        print(f"✗ Validation error in state.json: {e}")
        return False

def main():
    """Run all validations."""
    updates_path = Path('data/updates.json')
    state_path = Path('data/state.json')
    
    all_valid = True
    
    if not updates_path.exists():
        print(f"✗ {updates_path} not found")
        all_valid = False
    else:
        all_valid = validate_updates_json(updates_path) and all_valid
    
    if not state_path.exists():
        print(f"✗ {state_path} not found")
        all_valid = False
    else:
        all_valid = validate_state_json(state_path) and all_valid
    
    if not all_valid:
        print("\n✗ Validation failed. Exiting.")
        sys.exit(1)
    
    print("\n✓ All validations passed")
    sys.exit(0)

if __name__ == '__main__':
    main()
