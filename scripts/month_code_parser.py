#!/usr/bin/env python3
"""
CME Group Month Code Parser

Parses CME Group month codes used in futures contract naming.
Reference: https://www.cmegroup.com/month-codes.html
"""

# CME Group month code mapping
CME_MONTH_CODES = {
    'F': 1,   # January
    'G': 2,   # February
    'H': 3,   # March
    'J': 4,   # April
    'K': 5,   # May
    'M': 6,   # June
    'N': 7,   # July
    'Q': 8,   # August
    'U': 9,   # September
    'V': 10,  # October
    'X': 11,  # November
    'Z': 12,  # December
}

# Reverse mapping: month number to CME code
MONTH_TO_CME_CODE = {v: k for k, v in CME_MONTH_CODES.items()}


def parse_contract_name(contract_name: str) -> dict:
    """
    Parse a contract name like 'BRENT_2011F' into components.
    
    Args:
        contract_name: Contract name in format COMMODITY_YYYYM
        
    Returns:
        dict with keys: commodity, year, month, cme_code
        
    Raises:
        ValueError: If contract name format is invalid
    """
    if not contract_name or '_' not in contract_name:
        raise ValueError(f"Invalid contract name format: {contract_name}")
    
    parts = contract_name.split('_')
    if len(parts) != 2:
        raise ValueError(f"Invalid contract name format: {contract_name}")
    
    commodity = parts[0]
    year_month = parts[1]
    
    if len(year_month) < 5:
        raise ValueError(f"Invalid year/month format: {year_month}")
    
    year_str = year_month[:4]
    cme_code = year_month[4].upper()
    
    try:
        year = int(year_str)
    except ValueError:
        raise ValueError(f"Invalid year: {year_str}")
    
    if cme_code not in CME_MONTH_CODES:
        raise ValueError(f"Invalid CME month code: {cme_code}")
    
    month = CME_MONTH_CODES[cme_code]
    
    return {
        'commodity': commodity,
        'year': year,
        'month': month,
        'cme_code': cme_code
    }


def get_cme_code(month: int) -> str:
    """
    Get CME month code for a given month number (1-12).
    
    Args:
        month: Month number (1-12)
        
    Returns:
        CME month code (F, G, H, J, K, M, N, Q, U, V, X, Z)
        
    Raises:
        ValueError: If month is not 1-12
    """
    if month < 1 or month > 12:
        raise ValueError(f"Month must be between 1 and 12, got: {month}")
    
    return MONTH_TO_CME_CODE[month]


def get_month_number(cme_code: str) -> int:
    """
    Get month number (1-12) for a CME month code.
    
    Args:
        cme_code: CME month code (F, G, H, J, K, M, N, Q, U, V, X, Z)
        
    Returns:
        Month number (1-12)
        
    Raises:
        ValueError: If CME code is invalid
    """
    cme_code = cme_code.upper()
    if cme_code not in CME_MONTH_CODES:
        raise ValueError(f"Invalid CME month code: {cme_code}")
    
    return CME_MONTH_CODES[cme_code]


if __name__ == '__main__':
    # Test the parser
    test_cases = [
        'BRENT_2011F',
        'WTI_2025M',
        'GO_2023Z',
        'RBOB_2024J',
    ]
    
    print("Testing CME Month Code Parser\n")
    for contract_name in test_cases:
        try:
            result = parse_contract_name(contract_name)
            print(f"Contract: {contract_name}")
            print(f"  Commodity: {result['commodity']}")
            print(f"  Year: {result['year']}")
            print(f"  Month: {result['month']} ({result['cme_code']})")
            print()
        except ValueError as e:
            print(f"Error parsing {contract_name}: {e}\n")

