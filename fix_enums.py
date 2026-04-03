"""Fix database enum values"""
import sys
sys.path.insert(0, 'd:/infosys/backend')
from sqlalchemy import text
from database import engine

with engine.begin() as conn:
    # Fix uppercase enum values to lowercase
    conn.execute(text("UPDATE users SET risk_profile = 'moderate' WHERE risk_profile = 'MODERATE'"))
    conn.execute(text("UPDATE users SET risk_profile = 'conservative' WHERE risk_profile = 'CONSERVATIVE'"))
    conn.execute(text("UPDATE users SET risk_profile = 'aggressive' WHERE risk_profile = 'AGGRESSIVE'"))
    conn.execute(text("UPDATE users SET kyc_status = 'verified' WHERE kyc_status = 'VERIFIED'"))
    conn.execute(text("UPDATE users SET kyc_status = 'pending' WHERE kyc_status = 'PENDING'"))
    conn.execute(text("UPDATE users SET kyc_status = 'rejected' WHERE kyc_status = 'REJECTED'"))
    
    # Fix investments
    conn.execute(text("UPDATE investments SET type = 'stock' WHERE type = 'STOCK'"))
    conn.execute(text("UPDATE investments SET type = 'etf' WHERE type = 'ETF'"))
    conn.execute(text("UPDATE investments SET type = 'mutual_fund' WHERE type = 'MUTUAL_FUND'"))
    conn.execute(text("UPDATE investments SET type = 'bond' WHERE type = 'BOND'"))
    conn.execute(text("UPDATE investments SET type = 'crypto' WHERE type = 'CRYPTO'"))
    
    # Fix transactions
    conn.execute(text("UPDATE transactions SET type = 'buy' WHERE type = 'BUY'"))
    conn.execute(text("UPDATE transactions SET type = 'sell' WHERE type = 'SELL'"))
    conn.execute(text("UPDATE transactions SET type = 'dividend' WHERE type = 'DIVIDEND'"))
    conn.execute(text("UPDATE transactions SET type = 'split' WHERE type = 'SPLIT'"))
    
    # Fix goals
    conn.execute(text("UPDATE goals SET category = 'retirement' WHERE category = 'RETIREMENT'"))
    conn.execute(text("UPDATE goals SET category = 'education' WHERE category = 'EDUCATION'"))
    conn.execute(text("UPDATE goals SET category = 'home' WHERE category = 'HOME'"))
    conn.execute(text("UPDATE goals SET category = 'vacation' WHERE category = 'VACATION'"))
    conn.execute(text("UPDATE goals SET category = 'emergency' WHERE category = 'EMERGENCY'"))
    conn.execute(text("UPDATE goals SET category = 'other' WHERE category = 'OTHER'"))
    
    print('Fixed enum values')
    
    result = conn.execute(text('SELECT id, email, risk_profile, kyc_status FROM users'))
    for row in result:
        print(f'User {row.id}: Risk={row.risk_profile}, KYC={row.kyc_status}')
