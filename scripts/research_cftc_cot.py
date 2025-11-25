#!/usr/bin/env python3
"""
Research CFTC COT Data Format

This script helps research and understand the CFTC COT data format by:
1. Attempting to download sample reports
2. Analyzing file structure
3. Parsing sample data
4. Documenting findings

Focus: Disaggregated Futures and Options for:
- Petroleum and Products
- Natural Gas and Products
- Electricity
"""

import requests
import zipfile
import io
from pathlib import Path
from datetime import date, timedelta
import csv
import json
import os
import sys

# CFTC PRE base URL patterns (to be discovered)
CFTC_BASE_URL = "https://www.cftc.gov/files/dea/history/"

# Report types we're interested in
REPORT_TYPES = {
    "disaggregated_futures_options": "futures_disaggregated_combined"
}

# Target commodity groups
COMMODITY_GROUPS = [
    "Petroleum and Products",
    "Natural Gas and Products", 
    "Electricity"
]


def get_tuesday_date(target_date: date) -> date:
    """
    Get the Tuesday date for a given date (CFTC reports are as of Tuesday).
    CFTC reports are released Friday, but data is as of previous Tuesday.
    """
    # If target_date is Tuesday (weekday 1), return it
    # Otherwise, go back to the most recent Tuesday
    days_since_tuesday = (target_date.weekday() - 1) % 7
    if days_since_tuesday == 0:
        return target_date  # Already Tuesday
    tuesday = target_date - timedelta(days=days_since_tuesday)
    return tuesday


def construct_download_urls(report_date: date, report_type: str = "disaggregated_futures_options") -> list[str]:
    """
    Construct possible CFTC PRE download URLs.
    
    Based on research, CFTC uses patterns like:
    - deacotYYYY.zip (year-based, contains all reports for that year)
    - Individual report files may use different patterns
    
    Returns list of URL patterns to try.
    """
    date_str = report_date.strftime('%Y%m%d')
    year = report_date.year
    
    # Try different possible URL patterns based on CFTC website structure
    patterns = [
        # Pattern 1: Year-based archive (deacotYYYY.zip) - contains all reports for year
        f"{CFTC_BASE_URL}deacot{year}.zip",
        # Pattern 2: Individual report files - deacotYYYYMMDD.zip
        f"{CFTC_BASE_URL}deacot{date_str}.zip",
        # Pattern 3: futures_disaggregated_combined_YYYYMMDD.zip
        f"{CFTC_BASE_URL}futures_disaggregated_combined_{date_str}.zip",
        # Pattern 4: cot_YYYYMMDD.zip
        f"{CFTC_BASE_URL}cot_{date_str}.zip",
        # Pattern 5: cotYYYYMMDD.zip
        f"{CFTC_BASE_URL}cot{date_str}.zip",
        # Pattern 6: Short format
        f"{CFTC_BASE_URL}futures_disaggregated_short_{date_str}.zip",
        # Pattern 7: Long format
        f"{CFTC_BASE_URL}futures_disaggregated_long_{date_str}.zip",
    ]
    
    return patterns


def download_report(url: str, output_dir: Path = None) -> tuple[bool, bytes | None, str]:
    """
    Download a CFTC COT report.
    
    Returns:
        (success, content, error_message)
    """
    try:
        print(f"Attempting to download: {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"  ✓ Downloaded successfully ({len(response.content)} bytes)")
            return True, response.content, ""
        elif response.status_code == 404:
            return False, None, f"Report not found (404): {url}"
        else:
            return False, None, f"HTTP {response.status_code}: {url}"
            
    except requests.exceptions.RequestException as e:
        return False, None, f"Download error: {str(e)}"


def extract_zip(zip_content: bytes, output_dir: Path) -> list[Path]:
    """
    Extract ZIP file and return list of extracted file paths.
    """
    extracted_files = []
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            print(f"  ZIP contains {len(zip_file.namelist())} files:")
            for name in zip_file.namelist():
                print(f"    - {name}")
            
            zip_file.extractall(output_dir)
            extracted_files = [output_dir / name for name in zip_file.namelist()]
            
    except zipfile.BadZipFile:
        print(f"  ✗ Invalid ZIP file")
    except Exception as e:
        print(f"  ✗ Error extracting ZIP: {e}")
    
    return extracted_files


def analyze_text_file(file_path: Path) -> dict:
    """
    Analyze a text file (could be CSV, TSV, or fixed-width).
    """
    analysis = {
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "rows": 0,
        "columns": [],
        "sample_rows": [],
        "commodities_found": set(),
        "trader_categories": set(),
        "file_type": "unknown",
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Read first few lines to understand format
            first_lines = [f.readline() for _ in range(10)]
            f.seek(0)
            
            # Check if it's CSV-like (has commas or tabs)
            first_line = first_lines[0] if first_lines else ""
            if ',' in first_line:
                analysis["file_type"] = "csv"
                delimiter = ','
            elif '\t' in first_line:
                analysis["file_type"] = "tsv"
                delimiter = '\t'
            else:
                analysis["file_type"] = "fixed_width"
                delimiter = None
            
            if delimiter:
                reader = csv.reader(f, delimiter=delimiter)
                
                # Read header
                try:
                    header = next(reader)
                    analysis["columns"] = header
                    print(f"  Columns ({len(header)}): {header[:15]}...")  # Show first 15
                except StopIteration:
                    print(f"  ⚠ No header found")
                
                # Read sample rows
                for i, row in enumerate(reader):
                    if i < 10:  # First 10 rows
                        analysis["sample_rows"].append(row)
                    
                    # Try to identify commodity codes
                    for col_idx, value in enumerate(row):
                        if value and isinstance(value, str):
                            value_upper = value.strip().upper()
                            # Known commodity codes
                            if value_upper in ['CL', 'RB', 'HO', 'NG', 'BZ', 'G', 'PN']:
                                analysis["commodities_found"].add(value_upper)
                            # Check for commodity names
                            if any(term in value_upper for term in ['CRUDE', 'GASOLINE', 'HEATING', 'NATURAL GAS', 'PROPANE', 'ELECTRICITY']):
                                analysis["commodities_found"].add(value_upper[:20])  # Store first 20 chars
                    
                    analysis["rows"] += 1
                    
                    if i >= 100:  # Limit analysis to first 100 rows
                        break
            else:
                # Fixed-width format - just read as text
                lines = f.readlines()
                analysis["rows"] = len(lines)
                analysis["sample_rows"] = [line[:200] for line in lines[:10]]  # First 200 chars of first 10 lines
                print(f"  Fixed-width format, {len(lines)} lines")
                print(f"  Sample line: {lines[0][:200] if lines else 'N/A'}")
            
            analysis["commodities_found"] = list(analysis["commodities_found"])
            
    except Exception as e:
        print(f"  ✗ Error analyzing file: {e}")
        import traceback
        traceback.print_exc()
        analysis["error"] = str(e)
    
    return analysis


def analyze_csv_file(csv_path: Path) -> dict:
    """
    Analyze a CSV file to understand its structure.
    """
    analysis = {
        "file_path": str(csv_path),
        "rows": 0,
        "columns": [],
        "sample_rows": [],
        "commodities_found": set(),
        "trader_categories": set(),
    }
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.reader(f, delimiter=delimiter)
            
            # Read header
            header = next(reader)
            analysis["columns"] = header
            print(f"  Columns ({len(header)}): {header[:10]}...")  # Show first 10
            
            # Read sample rows
            for i, row in enumerate(reader):
                if i < 5:  # First 5 rows
                    analysis["sample_rows"].append(row)
                
                # Try to identify commodity and trader category columns
                # (This is a guess - need to see actual data)
                if len(row) > 0:
                    # Look for commodity names in various columns
                    for col_idx, value in enumerate(row):
                        if value and isinstance(value, str):
                            value_upper = value.upper()
                            # Check if it looks like a commodity code
                            if value_upper in ['CL', 'RB', 'HO', 'NG', 'BZ', 'G']:
                                analysis["commodities_found"].add(value_upper)
                
                analysis["rows"] += 1
                
                if i >= 100:  # Limit analysis to first 100 rows
                    break
            
            analysis["commodities_found"] = list(analysis["commodities_found"])
            
    except Exception as e:
        print(f"  ✗ Error analyzing CSV: {e}")
        analysis["error"] = str(e)
    
    return analysis


def main():
    """Main research function."""
    print("=" * 80)
    print("CFTC COT Data Format Research")
    print("=" * 80)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / "cftc_cot_samples"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Try recent dates (reports are released Fridays, data is as of Tuesday)
    # Use actual current date and go back to find recent Tuesdays
    today = date.today()
    
    # Also try year-based downloads (deacotYYYY.zip) for recent years
    # Try last 3 years
    test_years = [today.year, today.year - 1, today.year - 2]
    
    # Find recent Tuesdays (go back up to 20 weeks to find valid reports)
    test_dates = []
    current_date = today
    for _ in range(20):  # Try last 20 weeks
        tuesday = get_tuesday_date(current_date)
        if tuesday not in test_dates and tuesday <= today:
            test_dates.append(tuesday)
        current_date -= timedelta(days=7)
    
    # Sort dates (most recent first)
    test_dates.sort(reverse=True)
    
    # Initialize successful downloads list
    successful_downloads = []
    
    # Also try year-based downloads first (more likely to work)
    print(f"\nTrying year-based downloads for years: {test_years}")
    for year in test_years:
        year_url = f"{CFTC_BASE_URL}deacot{year}.zip"
        print(f"\n--- Testing year-based archive: {year} ---")
        success, content, error = download_report(year_url)
        
        if success and content:
            # Save ZIP file
            zip_path = output_dir / f"deacot{year}.zip"
            zip_path.write_bytes(content)
            print(f"  ✓ Saved to: {zip_path}")
            
            # Extract ZIP
            extract_dir = output_dir / f"extracted_year_{year}"
            extract_dir.mkdir(exist_ok=True)
            
            extracted_files = extract_zip(content, extract_dir)
            
            # Analyze extracted files
            for file_path in extracted_files:
                if file_path.suffix.lower() in ['.csv', '.txt']:
                    print(f"\n  Analyzing file: {file_path.name} ({file_path.stat().st_size} bytes)")
                    if file_path.suffix.lower() == '.csv':
                        analysis = analyze_csv_file(file_path)
                    else:
                        analysis = analyze_text_file(file_path)
                    
                    # Save analysis
                    analysis_path = output_dir / f"analysis_{file_path.stem}.json"
                    with open(analysis_path, 'w') as f:
                        json.dump(analysis, f, indent=2, default=str)
                    
                    print(f"  ✓ Analysis saved to: {analysis_path}")
                    
                    # Print summary
                    if "columns" in analysis and analysis["columns"]:
                        print(f"    Found {len(analysis['columns'])} columns")
                    if "commodities_found" in analysis and analysis["commodities_found"]:
                        print(f"    Commodities found: {analysis['commodities_found'][:10]}")
                    if "rows" in analysis:
                        print(f"    Total rows: {analysis['rows']}")
            
            successful_downloads.append({
                "type": "year_archive",
                "year": year,
                "url": year_url,
                "files": [str(f) for f in extracted_files]
            })
            break  # Found working pattern, can analyze this
    
    print(f"\nTesting {len(test_dates)} recent report dates...")
    print(f"Dates: {[d.strftime('%Y-%m-%d') for d in test_dates[:5]]}...")
    
    # Try to download reports
    successful_downloads = []
    
    for report_date in test_dates[:5]:  # Try first 5 dates
        print(f"\n--- Testing date: {report_date.strftime('%Y-%m-%d')} ---")
        
        # Try multiple URL patterns
        urls = construct_download_urls(report_date)
        success = False
        content = None
        successful_url = None
        
        for url in urls:
            success, content, error = download_report(url)
            if success and content:
                successful_url = url
                break
        
        if success and content:
            # Save ZIP file
            zip_path = output_dir / f"cot_{report_date.strftime('%Y%m%d')}.zip"
            zip_path.write_bytes(content)
            print(f"  Saved to: {zip_path}")
            
            # Extract ZIP
            extract_dir = output_dir / f"extracted_{report_date.strftime('%Y%m%d')}"
            extract_dir.mkdir(exist_ok=True)
            
            extracted_files = extract_zip(content, extract_dir)
            
            # Analyze extracted files
            for file_path in extracted_files:
                if file_path.suffix.lower() == '.csv':
                    print(f"\n  Analyzing CSV: {file_path.name}")
                    analysis = analyze_csv_file(file_path)
                    
                    # Save analysis
                    analysis_path = output_dir / f"analysis_{file_path.stem}.json"
                    with open(analysis_path, 'w') as f:
                        json.dump(analysis, f, indent=2, default=str)
                    
                    print(f"  ✓ Analysis saved to: {analysis_path}")
            
            successful_downloads.append({
                "date": report_date,
                "url": successful_url,
                "files": [str(f) for f in extracted_files]
            })
            break  # Found working URL pattern, move to next date
        else:
            print(f"  ✗ Failed: {error}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Research Summary")
    print("=" * 80)
    print(f"Successful downloads: {len(successful_downloads)}")
    
    if successful_downloads:
        print("\nNext steps:")
        print("1. Review extracted files in:", output_dir)
        print("2. Review analysis JSON files")
        print("3. Document actual URL patterns")
        print("4. Document CSV/XML structure")
    else:
        print("\n⚠ No successful downloads. Need to:")
        print("1. Verify CFTC PRE URL patterns")
        print("2. Check if reports are available for test dates")
        print("3. Consider alternative access methods")


if __name__ == "__main__":
    main()

