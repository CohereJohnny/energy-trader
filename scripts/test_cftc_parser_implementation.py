#!/usr/bin/env python3
"""
Implementation Tests for CFTC Disaggregated COT Parser

These tests use real fixtures and validate parser functionality.
"""

import unittest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cftc_parser import CFTCDisaggregatedParser, CommodityData, CommodityPosition, ParsingError


class TestHTMLExtraction(unittest.TestCase):
    """Test HTML extraction."""
    
    def test_extract_pre_content_valid_html(self):
        """Test extracting <pre> content from valid HTML."""
        html = """
        <html>
        <body>
        <pre>
        Test content
        </pre>
        </body>
        </html>
        """
        parser = CFTCDisaggregatedParser()
        content = parser.extract_pre_content(html)
        self.assertEqual(content.strip(), "Test content")
    
    def test_extract_pre_content_missing_pre(self):
        """Test handling missing <pre> tag."""
        html = "<html><body>No pre tag</body></html>"
        parser = CFTCDisaggregatedParser(strict=False)
        content = parser.extract_pre_content(html)
        self.assertEqual(content, "")
        self.assertEqual(len(parser.errors), 1)
    
    def test_extract_pre_content_strict_mode(self):
        """Test strict mode raises error."""
        html = "<html><body>No pre tag</body></html>"
        parser = CFTCDisaggregatedParser(strict=True)
        with self.assertRaises(ParsingError):
            parser.extract_pre_content(html)


class TestPositionParsing(unittest.TestCase):
    """Test position row parsing."""
    
    def setUp(self):
        self.parser = CFTCDisaggregatedParser(strict=False)
    
    def test_parse_position_row_all(self):
        """Test parsing 'All' position row."""
        row = "All  :    29,051:    15,912     20,345      1,191        677      1,763         75          0         51      4,258        349      5,752:       49       114"
        position = self.parser.parse_position_row(row)
        
        self.assertIsNotNone(position)
        self.assertEqual(position.producer_long, 15912)
        self.assertEqual(position.producer_short, 20345)
        self.assertEqual(position.swap_long, 1191)
        self.assertEqual(position.swap_short, 677)
        self.assertEqual(position.swap_spreading, 1763)
        self.assertEqual(position.managed_money_long, 75)
        self.assertEqual(position.managed_money_short, 0)
        self.assertEqual(position.managed_money_spreading, 51)
        self.assertEqual(position.other_long, 4258)
        self.assertEqual(position.other_short, 349)
        self.assertEqual(position.other_spreading, 5752)
        self.assertEqual(position.nonreportable_long, 49)
        self.assertEqual(position.nonreportable_short, 114)
    
    def test_parse_position_row_with_missing_values(self):
        """Test parsing row with missing values (represented as '.')."""
        row = "All  :     1,000:       500        400        100          .         25          .          0          .         50          .         10:        5        10"
        position = self.parser.parse_position_row(row)
        
        self.assertIsNotNone(position)
        self.assertEqual(position.producer_long, 500)
        self.assertEqual(position.producer_short, 400)
        self.assertEqual(position.swap_long, 100)
        self.assertIsNone(position.swap_short)  # '.' should be None
        self.assertEqual(position.swap_spreading, 25)
    
    def test_parse_position_row_other(self):
        """Test parsing 'Other' row (Options only)."""
        row = "Other:         0:         0          0          0          0          0          0          0          0          0          0          0:        0         0"
        position = self.parser.parse_position_row(row)
        
        self.assertIsNotNone(position)
        self.assertEqual(position.producer_long, 0)
        self.assertEqual(position.producer_short, 0)
    
    def test_parse_position_row_invalid(self):
        """Test parsing invalid row."""
        row = "Invalid row format"
        position = self.parser.parse_position_row(row)
        self.assertIsNone(position)


class TestHeaderParsing(unittest.TestCase):
    """Test header parsing."""
    
    def setUp(self):
        self.parser = CFTCDisaggregatedParser(strict=False)
    
    def test_parse_header_valid(self):
        """Test parsing valid header."""
        header_line = "USGC HSFO (PLATTS) - ICE FUTURES ENERGY DIV                                                                                                      Code-02141B"
        date_line = "Disaggregated Commitments of Traders - Futures Only, October 07, 2025"
        
        header_info = self.parser.parse_header(header_line, date_line)
        
        self.assertEqual(header_info['market_name'], "USGC HSFO (PLATTS)")
        self.assertEqual(header_info['exchange'], "ICE FUTURES ENERGY DIV")
        self.assertEqual(header_info['cftc_code'], "02141B")
        from datetime import date
        self.assertEqual(header_info['report_date'], date(2025, 10, 7))
    
    def test_parse_header_missing_code(self):
        """Test parsing header without code."""
        header_line = "MARKET NAME - EXCHANGE"
        date_line = "Disaggregated Commitments of Traders - Futures Only, October 07, 2025"
        
        header_info = self.parser.parse_header(header_line, date_line)
        self.assertIsNone(header_info['cftc_code'])


class TestBlockIdentification(unittest.TestCase):
    """Test commodity block identification."""
    
    def setUp(self):
        self.parser = CFTCDisaggregatedParser()
    
    def test_identify_blocks(self):
        """Test identifying commodity blocks."""
        text = """
MARKET 1 - EXCHANGE                                                                                                      Code-00001A
Disaggregated Commitments of Traders - Futures Only, January 01, 2025
--------------------------------------------------------------------
...

MARKET 2 - EXCHANGE                                                                                                      Code-00002B
Disaggregated Commitments of Traders - Futures Only, January 01, 2025
--------------------------------------------------------------------
...
"""
        blocks = self.parser.identify_commodity_blocks(text)
        self.assertGreaterEqual(len(blocks), 2)


class TestFullParsing(unittest.TestCase):
    """Test full parsing pipeline."""
    
    def setUp(self):
        self.parser = CFTCDisaggregatedParser(strict=False)
        self.fixture_path = Path(__file__).parent / "test_fixtures" / "cftc_minimal_block.txt"
    
    def test_parse_minimal_block(self):
        """Test parsing minimal valid block."""
        if not self.fixture_path.exists():
            self.skipTest("Fixture not found")
        
        with open(self.fixture_path, 'r') as f:
            text = f.read()
        
        # Wrap in HTML
        html = f"<html><body><pre>{text}</pre></body></html>"
        
        commodities = self.parser.parse(html)
        
        self.assertEqual(len(commodities), 1)
        commodity = commodities[0]
        self.assertEqual(commodity.market_name, "MINIMAL MARKET")
        self.assertEqual(commodity.exchange, "TEST EXCHANGE")
        self.assertEqual(commodity.cftc_code, "00001A")
        self.assertIsNotNone(commodity.open_interest)
        self.assertIsNotNone(commodity.positions_all)
    
    def test_parse_real_data(self):
        """Test parsing real CFTC data."""
        html_path = Path(__file__).parent.parent / "data" / "cftc_cot_samples" / "petroleum_lf_page.html"
        
        if not html_path.exists():
            self.skipTest("Real data fixture not found")
        
        with open(html_path, 'r', encoding='iso-8859-1') as f:
            html = f.read()
        
        commodities = self.parser.parse(html)
        
        # Should parse multiple commodities
        self.assertGreater(len(commodities), 0)
        
        # Check first commodity
        c = commodities[0]
        self.assertIsNotNone(c.market_name)
        self.assertIsNotNone(c.exchange)
        self.assertIsNotNone(c.cftc_code)
        self.assertIsNotNone(c.report_date)
        self.assertIsNotNone(c.open_interest)
        self.assertIsNotNone(c.positions_all)
        
        # Validate positions
        p = c.positions_all
        self.assertIsNotNone(p.producer_long)
        self.assertIsNotNone(p.producer_short)
        self.assertIsNotNone(p.swap_long)
        self.assertIsNotNone(p.swap_short)
        self.assertIsNotNone(p.swap_spreading)
        
        # Check that errors are minimal
        self.assertLess(len(self.parser.errors), 10, "Too many parsing errors")


class TestDataValidation(unittest.TestCase):
    """Test data validation."""
    
    def setUp(self):
        self.parser = CFTCDisaggregatedParser(strict=False)
    
    def test_validate_open_interest_positive(self):
        """Test that Open Interest is positive."""
        # This would be tested in integration with database
        pass
    
    def test_validate_positions_non_negative(self):
        """Test that positions are non-negative."""
        row = "All  :    29,051:    15,912     20,345      1,191        677      1,763         75          0         51      4,258        349      5,752:       49       114"
        position = self.parser.parse_position_row(row)
        
        # All values should be non-negative
        self.assertGreaterEqual(position.producer_long, 0)
        self.assertGreaterEqual(position.producer_short, 0)
        self.assertGreaterEqual(position.swap_long, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

