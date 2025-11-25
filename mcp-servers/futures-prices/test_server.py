#!/usr/bin/env python3
"""
Quick verification tests for Futures Prices MCP Server.
"""

import sys
import os
from datetime import date, datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from db import get_db, Database
from tools import (
    get_front_month_price,
    get_front_month_prices,
    calculate_price_change,
    get_seasonal_data
)


def test_database_connection():
    """Test database connection."""
    print("1. Testing database connection...")
    try:
        db = get_db()
        with db.conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"   ✓ Connected to PostgreSQL: {version[:50]}...")
        return True
    except Exception as e:
        print(f"   ✗ Database connection failed: {e}")
        return False


def test_get_front_month_price():
    """Test get_front_month_price tool."""
    print("\n2. Testing get_front_month_price...")
    try:
        # Test with valid data
        result = get_front_month_price('BRENT', '2010-01-04')
        
        # Check response structure
        assert 'text' in result, "Response missing 'text' field"
        assert '_north_metadata' in result, "Response missing '_north_metadata'"
        
        metadata = result['_north_metadata']
        assert 'title' in metadata, "Metadata missing 'title'"
        assert 'url' in metadata, "Metadata missing 'url'"
        assert 'author_name' in metadata, "Metadata missing 'author_name'"
        assert 'last_updated' in metadata, "Metadata missing 'last_updated'"
        
        print(f"   ✓ Valid response structure")
        print(f"   ✓ Response text: {result['text'][:80]}...")
        print(f"   ✓ Citation title: {metadata['title']}")
        
        # Test with invalid commodity
        result = get_front_month_price('INVALID', '2010-01-04')
        assert 'Error' in result['text'], "Should return error for invalid commodity"
        print(f"   ✓ Error handling works")
        
        return True
    except Exception as e:
        print(f"   ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_front_month_prices():
    """Test get_front_month_prices tool."""
    print("\n3. Testing get_front_month_prices...")
    try:
        # Test with valid date range
        result = get_front_month_prices('BRENT', '2025-01-01', '2025-01-10')
        
        assert 'text' in result, "Response missing 'text' field"
        assert '_north_metadata' in result, "Response missing '_north_metadata'"
        
        print(f"   ✓ Valid response structure")
        print(f"   ✓ Response contains {len(result['text'].split(chr(10)))} lines")
        
        # Test with invalid date range
        result = get_front_month_prices('BRENT', '2025-01-10', '2025-01-01')
        assert 'Error' in result['text'], "Should return error for invalid date range"
        print(f"   ✓ Error handling works")
        
        return True
    except Exception as e:
        print(f"   ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calculate_price_change():
    """Test calculate_price_change tool."""
    print("\n4. Testing calculate_price_change...")
    try:
        # Test with valid dates
        result = calculate_price_change('BRENT', '2010-01-04', '2010-01-05')
        
        assert 'text' in result, "Response missing 'text' field"
        assert '_north_metadata' in result, "Response missing '_north_metadata'"
        
        # Check that it includes price change info
        text = result['text']
        assert 'change' in text.lower() or 'price' in text.lower(), "Should include price change"
        
        print(f"   ✓ Valid response structure")
        print(f"   ✓ Response includes price change: {text[:100]}...")
        
        return True
    except Exception as e:
        print(f"   ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_seasonal_data():
    """Test get_seasonal_data tool."""
    print("\n5. Testing get_seasonal_data...")
    try:
        # Test with M2 (second month contract)
        result = get_seasonal_data('GO', 2)  # M2 GOBRs
        
        assert 'text' in result, "Response missing 'text' field"
        assert '_north_metadata' in result, "Response missing '_north_metadata'"
        
        # Check CSV-like format
        text = result['text']
        assert 'Date' in text or 'date' in text.lower(), "Should include date column"
        
        print(f"   ✓ Valid response structure")
        print(f"   ✓ Response formatted for charting: {len(text.split(chr(10)))} lines")
        
        # Test with invalid month offset
        result = get_seasonal_data('BRENT', 15)
        assert 'Error' in result['text'], "Should return error for invalid month offset"
        print(f"   ✓ Error handling works")
        
        return True
    except Exception as e:
        print(f"   ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_citation_metadata_format():
    """Test citation metadata format."""
    print("\n6. Testing citation metadata format...")
    try:
        result = get_front_month_price('WTI', '2010-01-04')
        metadata = result['_north_metadata']
        
        # Verify all required fields
        required_fields = ['title', 'url', 'author_name', 'last_updated']
        for field in required_fields:
            assert field in metadata, f"Missing required field: {field}"
            assert metadata[field], f"Field {field} is empty"
        
        # Verify timestamp format
        timestamp = metadata['last_updated']
        assert timestamp.endswith('Z'), "Timestamp should end with Z"
        
        print(f"   ✓ All required fields present")
        print(f"   ✓ Timestamp format correct: {timestamp}")
        
        return True
    except Exception as e:
        print(f"   ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_commodities():
    """Test all supported commodities."""
    print("\n7. Testing all commodities...")
    try:
        commodities = ['BRENT', 'WTI', 'GO', 'RBOB']
        test_date = '2010-01-04'
        
        for commodity in commodities:
            result = get_front_month_price(commodity, test_date)
            if 'Error' not in result['text']:
                print(f"   ✓ {commodity}: Price found")
            else:
                print(f"   ⚠ {commodity}: {result['text']}")
        
        return True
    except Exception as e:
        print(f"   ✗ Test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Futures Prices MCP Server - Verification Tests")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_get_front_month_price,
        test_get_front_month_prices,
        test_calculate_price_change,
        test_get_seasonal_data,
        test_citation_metadata_format,
        test_all_commodities,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

