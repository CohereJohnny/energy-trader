# CFTC COT Data Research Findings

## Date: 2025-01-20

## Summary

Successfully downloaded and analyzed CFTC COT data from the Public Reporting Environment (PRE).

## Download Method

**URL Pattern**: `https://www.cftc.gov/files/dea/history/deacot{YYYY}.zip`

- **Year-based archives**: CFTC provides annual ZIP files containing all reports for a given year
- **File naming**: `deacot2025.zip` for year 2025
- **Contents**: Each ZIP contains a single `annual.txt` file with all COT data for that year

## Data File Structure

### File Format
- **File**: `annual.txt` (within ZIP archive)
- **Format**: CSV (comma-delimited)
- **Size**: ~15 MB for 2025 data (compressed: ~1.8 MB)
- **Rows**: 101 rows (including header)
- **Columns**: 129 columns

### Column Structure

The file contains 129 columns. Key columns include:

1. **Market and Exchange Names** - Full name of the market/exchange
2. **As of Date in Form YYMMDD** - Report date (YYMMDD format)
3. **As of Date in Form YYYY-MM-DD** - Report date (ISO format)
4. **CFTC Contract Market Code** - Contract code
5. **CFTC Market Code in Initials** - Market code initials
6. **CFTC Region Code** - Region code
7. **CFTC Commodity Code** - Commodity code
8. **Open Interest (All)** - Total open interest
9. **Noncommercial Positions-Long (All)** - Non-commercial long positions
10. **Noncommercial Positions-Short (All)** - Non-commercial short positions
11. **Noncommercial Positions-Spreading (All)** - Non-commercial spread positions
12. **Commercial Positions-Long (All)** - Commercial long positions
13. **Commercial Positions-Short (All)** - Commercial short positions
14. **Total Reportable Positions-Long (All)** - Total reportable long positions
15. **Total Reportable Positions-Short (All)** - Total reportable short positions

**Note**: The file appears to contain both "All" (futures + options combined) and separate futures/options breakdowns, plus disaggregated trader categories.

### Disaggregated Data Columns

Based on the column count (129 columns), the file likely includes:
- Disaggregated trader categories (Producer/Merchant, Swap Dealers, Managed Money, etc.)
- Separate futures and options breakdowns
- Concentration data (for long format reports)

## Target Commodities

Need to filter for:
- **Petroleum and Products**: Crude Oil (WTI, Brent), Gasoline (RBOB), Heating Oil, Gas Oil
- **Natural Gas and Products**: Natural Gas, Propane
- **Electricity**: Electricity futures

## Next Steps

1. **Examine Sample Data**: Look at actual rows for target commodities
2. **Identify Column Mappings**: Map columns to our database schema
3. **Parse Disaggregated Categories**: Identify which columns represent disaggregated trader categories
4. **Design Schema**: Create database schema based on actual data structure
5. **Build Parser**: Implement parser for `annual.txt` format

## Files Generated

- `data/cftc_cot_samples/deacot2025.zip` - Downloaded ZIP file
- `data/cftc_cot_samples/extracted_year_2025/annual.txt` - Extracted data file
- `data/cftc_cot_samples/analysis_annual.json` - Analysis results

## Key Findings

### Data Structure
- **File Format**: CSV with 129 columns
- **Report Frequency**: Weekly reports (each row is a Tuesday report date)
- **Data Coverage**: Contains all commodities for the entire year
- **Format Type**: This appears to be **LEGACY format** (Noncommercial/Commercial), not Disaggregated

### Column Categories
1. **Basic Info** (columns 1-7): Market name, dates, codes
2. **Legacy Positions - All** (columns 8-17): Futures + Options combined
   - Noncommercial (Long, Short, Spreading)
   - Commercial (Long, Short)
   - Total Reportable
   - Nonreportable
3. **Legacy Positions - Old** (columns 18-27): Futures only
4. **Legacy Positions - Other** (columns 28-37): Options only
5. **Changes** (columns 38-47): Week-over-week changes
6. **Percentages** (columns 48-77): % of Open Interest
7. **Trader Counts** (columns 78-101): Number of traders
8. **Concentration** (columns 102-125): Largest trader positions
9. **Metadata** (columns 126-129): Contract units, codes

### Target Commodities Found
- **1,143 entries** found matching our target terms (CRUDE, GASOLINE, HEATING, NATURAL GAS, PROPANE, ELECTRICITY, RBOB, WTI, BRENT, GAS OIL)
- Examples found: Brent-related contracts, various petroleum products

### Important Note: Disaggregated Format
⚠️ **This file appears to be LEGACY format, not DISAGGREGATED format.**

The user specifically requested **Disaggregated Futures and Options** which should include:
- Producer/Merchant/Processor/User
- Swap Dealers
- Managed Money
- Other Reportables

**Next Steps**: Need to locate the disaggregated format file. It may be:
- A separate file in the ZIP archive
- A different URL pattern (e.g., `deacot_disaggregated_YYYY.zip`)
- Available through CFTC PRE web interface with different download options

## Questions to Resolve

1. ✅ Does `annual.txt` contain all reports for the year? **YES** - Contains weekly reports
2. ✅ How are individual weekly reports represented? **Each row is a weekly report**
3. ❓ What are the exact column names for disaggregated trader categories? **Need to find disaggregated file**
4. ❓ Are there separate files for short vs. long format reports? **Unknown - need to check**
5. ✅ How to identify and filter for our target commodity groups? **Filter by market name or commodity code**

