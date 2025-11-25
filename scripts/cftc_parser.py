#!/usr/bin/env python3
"""
CFTC Disaggregated COT Parser

Parses CFTC Disaggregated Commitment of Traders reports from HTML pages.
Handles fixed-width format data embedded in <pre> tags.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from pathlib import Path
import re
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class CommodityPosition:
    """Represents positions for a commodity."""
    # Producer/Merchant/Processor/User
    producer_long: Optional[int] = None
    producer_short: Optional[int] = None
    
    # Swap Dealers
    swap_long: Optional[int] = None
    swap_short: Optional[int] = None
    swap_spreading: Optional[int] = None
    
    # Managed Money
    managed_money_long: Optional[int] = None
    managed_money_short: Optional[int] = None
    managed_money_spreading: Optional[int] = None
    
    # Other Reportables
    other_long: Optional[int] = None
    other_short: Optional[int] = None
    other_spreading: Optional[int] = None
    
    # Nonreportable
    nonreportable_long: Optional[int] = None
    nonreportable_short: Optional[int] = None


@dataclass
class CommodityData:
    """Represents complete data for a commodity."""
    market_name: str
    exchange: str
    cftc_code: Optional[str] = None
    report_date: Optional[date] = None
    open_interest: Optional[int] = None
    
    # Positions (All = Futures + Options, Old = Futures only, Other = Options only)
    positions_all: Optional[CommodityPosition] = None
    positions_old: Optional[CommodityPosition] = None
    positions_other: Optional[CommodityPosition] = None
    
    # Changes from previous week
    changes: Optional[CommodityPosition] = None
    
    # Percentages
    percentages_all: Optional[CommodityPosition] = None
    
    # Trader counts
    trader_counts_all: Optional[CommodityPosition] = None
    
    # Concentration
    concentration_gross_4_long: Optional[float] = None
    concentration_gross_4_short: Optional[float] = None
    concentration_gross_8_long: Optional[float] = None
    concentration_gross_8_short: Optional[float] = None
    concentration_net_4_long: Optional[float] = None
    concentration_net_4_short: Optional[float] = None
    concentration_net_8_long: Optional[float] = None
    concentration_net_8_short: Optional[float] = None


class ParsingError(Exception):
    """Exception raised during parsing."""
    pass


class CFTCDisaggregatedParser:
    """Parser for CFTC Disaggregated COT reports."""
    
    def __init__(self, strict: bool = False):
        """
        Initialize parser.
        
        Args:
            strict: If True, raise errors on parsing failures. If False, log and continue.
        """
        self.strict = strict
        self.errors: List[str] = []
    
    def extract_pre_content(self, html: str) -> str:
        """
        Extract content from <pre> tag in HTML.
        
        Args:
            html: HTML content
            
        Returns:
            Text content from <pre> tag
            
        Raises:
            ParsingError: If <pre> tag not found and strict=True
        """
        soup = BeautifulSoup(html, 'html.parser')
        pre_tag = soup.find('pre')
        
        if pre_tag is None:
            if self.strict:
                raise ParsingError("No <pre> tag found in HTML")
            self.errors.append("No <pre> tag found in HTML")
            return ""
        
        return pre_tag.get_text()
    
    def identify_commodity_blocks(self, text: str) -> List[Tuple[int, int]]:
        """
        Identify commodity blocks in text.
        
        Args:
            text: Text content from <pre> tag
            
        Returns:
            List of (start_line, end_line) tuples for each commodity block
        """
        lines = text.split('\n')
        blocks = []
        current_block_start = None
        
        for i, line in enumerate(lines):
            # Look for commodity header (contains "Code-" and "Disaggregated")
            if 'Code-' in line and 'Disaggregated' in lines[i+1] if i+1 < len(lines) else False:
                if current_block_start is not None:
                    # End previous block
                    blocks.append((current_block_start, i))
                current_block_start = i
        
        # End last block
        if current_block_start is not None:
            blocks.append((current_block_start, len(lines)))
        
        return blocks
    
    def parse_header(self, header_line: str, date_line: str) -> Dict[str, Optional[str]]:
        """
        Parse commodity header.
        
        Args:
            header_line: Line containing market name and code
            date_line: Line containing report date
            
        Returns:
            Dictionary with market_name, exchange, cftc_code, report_date
        """
        result = {
            'market_name': None,
            'exchange': None,
            'cftc_code': None,
            'report_date': None
        }
        
        # Extract CFTC code
        code_match = re.search(r'Code-(\w+)', header_line)
        if code_match:
            result['cftc_code'] = code_match.group(1)
        
        # Extract market name and exchange
        # Format: "MARKET NAME - EXCHANGE"
        if ' - ' in header_line:
            parts = header_line.split(' - ')
            if len(parts) >= 2:
                result['market_name'] = parts[0].strip()
                # Remove code from exchange name
                exchange = parts[1].split('Code-')[0].strip()
                result['exchange'] = exchange
        
        # Extract date
        # Format: "Disaggregated Commitments of Traders - Futures Only, October 07, 2025"
        date_match = re.search(r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', date_line)
        if date_match:
            month_str, day_str, year_str = date_match.groups()
            try:
                month = datetime.strptime(month_str, '%B').month
                day = int(day_str)
                year = int(year_str)
                result['report_date'] = date(year, month, day)
            except (ValueError, KeyError):
                if self.strict:
                    raise ParsingError(f"Invalid date format: {date_line}")
                self.errors.append(f"Invalid date format: {date_line}")
        
        return result
    
    def parse_position_row(self, row: str) -> Optional[CommodityPosition]:
        """
        Parse a position row (All, Old, or Other).
        
        Format: "All  : [Open Interest]: [Producer Long] [Producer Short] [Swap Long] [Swap Short] [Swap Spread] [MM Long] [MM Short] [MM Spread] [Other Long] [Other Short] [Other Spread]: [Nonrep Long] [Nonrep Short]"
        
        Args:
            row: Position row string
            
        Returns:
            CommodityPosition object or None if parsing fails
        """
        # Skip if row doesn't start with All, Old, Other, or spaces followed by colon (for changes row)
        stripped = row.strip()
        # Allow changes rows that start with colon (after spaces)
        if not (stripped.startswith('All') or stripped.startswith('Old') or stripped.startswith('Other') or stripped.startswith(':')):
            return None
        
        # Split by colons to get fields
        parts = [p.strip() for p in row.split(':')]
        
        if len(parts) < 4:
            if self.strict:
                raise ParsingError(f"Invalid position row format (need 4 parts): {row[:100]}")
            self.errors.append(f"Invalid position row format (need 4 parts): {row[:100]}")
            return None
        
        try:
            position = CommodityPosition()
            
            # Part 0: Row type (All/Old/Other) - ignore
            # Part 1: Open Interest - extract separately, not part of position
            # Part 2: Positions section (11 values separated by whitespace)
            positions_section = parts[2].strip()
            position_values = positions_section.split()
            
            if len(position_values) < 11:
                if self.strict:
                    raise ParsingError(f"Not enough position values (need 11, got {len(position_values)}): {row[:100]}")
                self.errors.append(f"Not enough position values (need 11, got {len(position_values)})")
                return None
            
            # Map position values (11 values total)
            position.producer_long = self._parse_int(position_values[0])
            position.producer_short = self._parse_int(position_values[1])
            position.swap_long = self._parse_int(position_values[2])
            position.swap_short = self._parse_int(position_values[3])
            position.swap_spreading = self._parse_int(position_values[4])
            position.managed_money_long = self._parse_int(position_values[5])
            position.managed_money_short = self._parse_int(position_values[6])
            position.managed_money_spreading = self._parse_int(position_values[7])
            position.other_long = self._parse_int(position_values[8])
            position.other_short = self._parse_int(position_values[9])
            position.other_spreading = self._parse_int(position_values[10])
            
            # Part 3: Nonreportable positions (2 values)
            nonreportable_section = parts[3].strip()
            nonreportable_values = nonreportable_section.split()
            
            if len(nonreportable_values) >= 2:
                position.nonreportable_long = self._parse_int(nonreportable_values[0])
                position.nonreportable_short = self._parse_int(nonreportable_values[1])
            
            return position
            
        except (ValueError, IndexError) as e:
            if self.strict:
                raise ParsingError(f"Error parsing position row: {e}")
            self.errors.append(f"Error parsing position row: {e}")
            return None
    
    def _parse_int(self, value: str) -> Optional[int]:
        """
        Parse integer value, handling missing values and commas.
        
        Args:
            value: String value to parse
            
        Returns:
            Integer value or None if missing/invalid
        """
        if not value or value.strip() == '' or value.strip() == '.':
            return None
        
        # Remove commas and whitespace
        cleaned = value.replace(',', '').strip()
        
        try:
            return int(cleaned)
        except ValueError:
            return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """
        Parse float value, handling missing values.
        
        Args:
            value: String value to parse
            
        Returns:
            Float value or None if missing/invalid
        """
        if not value or value.strip() == '' or value.strip() == '.':
            return None
        
        # Remove commas and whitespace
        cleaned = value.replace(',', '').strip()
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def parse_commodity_block(self, lines: List[str]) -> Optional[CommodityData]:
        """
        Parse a complete commodity block.
        
        Args:
            lines: List of lines for the commodity block
            
        Returns:
            CommodityData object or None if parsing fails
        """
        if len(lines) < 3:
            return None
        
        # Parse header
        header_info = self.parse_header(lines[0], lines[1])
        
        commodity = CommodityData(
            market_name=header_info.get('market_name', 'Unknown'),
            exchange=header_info.get('exchange', 'Unknown'),
            cftc_code=header_info.get('cftc_code'),
            report_date=header_info.get('report_date')
        )
        
        # Find and parse different sections
        # Look for "All  :" followed by different value types to identify sections
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped.startswith(('All', 'Old', 'Other')):
                continue
            
            parts = line.split(':')
            if len(parts) < 2:
                continue
            
            first_value = parts[1].strip()
            
            # Position rows: Large integer (Open Interest > 100)
            oi_value = self._parse_int(first_value)
            if oi_value and oi_value > 100:
                if stripped.startswith('All  :'):
                    commodity.positions_all = self.parse_position_row(line)
                    commodity.open_interest = oi_value
                elif stripped.startswith('Old  :'):
                    commodity.positions_old = self.parse_position_row(line)
                elif stripped.startswith('Other:'):
                    commodity.positions_other = self.parse_position_row(line)
            
            # Percentage rows: Value is ~100.0 (floats) - check if previous line mentions "Percent"
            if i > 0 and 'Percent of Open Interest' in lines[i-1]:
                if stripped.startswith('All  :'):
                    commodity.percentages_all = self.parse_position_row(line)  # Same structure, but values are floats
                    # Re-parse as floats
                    if commodity.percentages_all:
                        p = commodity.percentages_all
                        # Re-parse all values as floats
                        parts = line.split(':')
                        if len(parts) >= 2:
                            position_values = parts[2].strip().split()
                            if len(position_values) >= 11:
                                p.producer_long = self._parse_float(position_values[0])
                                p.producer_short = self._parse_float(position_values[1])
                                p.swap_long = self._parse_float(position_values[2])
                                p.swap_short = self._parse_float(position_values[3])
                                p.swap_spreading = self._parse_float(position_values[4])
                                p.managed_money_long = self._parse_float(position_values[5])
                                p.managed_money_short = self._parse_float(position_values[6])
                                p.managed_money_spreading = self._parse_float(position_values[7])
                                p.other_long = self._parse_float(position_values[8])
                                p.other_short = self._parse_float(position_values[9])
                                p.other_spreading = self._parse_float(position_values[10])
                            if len(parts) >= 4:
                                nonreportable_values = parts[3].strip().split()
                                if len(nonreportable_values) >= 2:
                                    p.nonreportable_long = self._parse_float(nonreportable_values[0])
                                    p.nonreportable_short = self._parse_float(nonreportable_values[1])
            
            # Trader count rows: Small integer (< 1000 typically)
            elif oi_value and oi_value < 1000 and not '.' in first_value:
                # Check if this looks like a trader count row (small numbers)
                if stripped.startswith('All  :'):
                    commodity.trader_counts_all = self.parse_position_row(line)
            
            # Changes row: Line before contains "Changes in Commitments from"
            if i > 0 and 'Changes in Commitments from' in lines[i-1]:
                # This is the changes row - starts with spaces and colon
                if stripped.startswith(':'):
                    commodity.changes = self.parse_position_row(line)
        
        # Parse concentration data (appears after trader counts section)
        # Look for concentration section header
        for i, line in enumerate(lines):
            if 'Percent of Open Interest Held' in line or 'Largest Traders' in line:
                # Look for the "All  :" row in concentration section (appears 3-4 lines after header)
                for j in range(i+1, min(i+8, len(lines))):
                    conc_line = lines[j]
                    conc_stripped = conc_line.strip()
                    if conc_stripped.startswith('All  :'):
                        # Parse concentration row
                        # Format: "All  : [Gross 4 Long] [Gross 4 Short] [Gross 8 Long] [Gross 8 Short] [Net 4 Long] [Net 4 Short] [Net 8 Long] [Net 8 Short]"
                        parts = conc_line.split(':')
                        if len(parts) >= 2:
                            values = parts[1].strip().split()
                            if len(values) >= 8:
                                commodity.concentration_gross_4_long = self._parse_float(values[0])
                                commodity.concentration_gross_4_short = self._parse_float(values[1])
                                commodity.concentration_gross_8_long = self._parse_float(values[2])
                                commodity.concentration_gross_8_short = self._parse_float(values[3])
                                commodity.concentration_net_4_long = self._parse_float(values[4])
                                commodity.concentration_net_4_short = self._parse_float(values[5])
                                commodity.concentration_net_8_long = self._parse_float(values[6])
                                commodity.concentration_net_8_short = self._parse_float(values[7])
                                break
                break
        
        return commodity
    
    def parse(self, html: str) -> List[CommodityData]:
        """
        Parse CFTC disaggregated COT report from HTML.
        
        Args:
            html: HTML content containing the report
            
        Returns:
            List of CommodityData objects
        """
        # Extract text from <pre> tag
        text = self.extract_pre_content(html)
        
        if not text:
            return []
        
        # Identify commodity blocks
        lines = text.split('\n')
        blocks = self.identify_commodity_blocks(text)
        
        commodities = []
        for start, end in blocks:
            block_lines = lines[start:end]
            commodity = self.parse_commodity_block(block_lines)
            if commodity:
                commodities.append(commodity)
        
        return commodities


if __name__ == '__main__':
    # Test with real data
    html_path = Path(__file__).parent.parent / "data" / "cftc_cot_samples" / "petroleum_lf_page.html"
    
    if html_path.exists():
        with open(html_path, 'r', encoding='iso-8859-1') as f:
            html = f.read()
        
        parser = CFTCDisaggregatedParser(strict=False)
        commodities = parser.parse(html)
        
        print(f"Parsed {len(commodities)} commodities")
        print(f"Errors: {len(parser.errors)}")
        
        if commodities:
            print(f"\nFirst commodity: {commodities[0].market_name}")
            print(f"  Exchange: {commodities[0].exchange}")
            print(f"  Code: {commodities[0].cftc_code}")
            print(f"  Date: {commodities[0].report_date}")
            print(f"  Open Interest: {commodities[0].open_interest}")
    else:
        print(f"Test file not found: {html_path}")

