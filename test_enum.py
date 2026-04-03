#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

# Test the enum conversion
from models import RiskProfile, KYCStatus

test_values = ['moderate', 'conservative', 'aggressive', 'pending', 'verified']

for val in test_values:
    try:
        if val in ['moderate', 'conservative', 'aggressive']:
            result = RiskProfile(val)
            print(f"✅ RiskProfile('{val}') = {result}")
        else:
            result = KYCStatus(val)
            print(f"✅ KYCStatus('{val}') = {result}")
    except Exception as e:
        print(f"❌ Error with '{val}': {e}")
        import traceback
        traceback.print_exc()
