# CFTC Disaggregated COT Data Findings

## Date: 2025-01-20

## Data Source

**URL**: `https://www.cftc.gov/dea/futures/petroleum_lf.htm`

**Format**: HTML page with embedded fixed-width text data in `<pre>` tags

**Source File**: The HTML references `petroleumlf.txt` but direct access returns 404. Data is embedded in HTML.

## Data Format

### Structure
- **Fixed-width text format** (not CSV)
- **Report Type**: Disaggregated Commitments of Traders - Futures Only
- **Report Frequency**: Weekly (latest report date shown: October 07, 2025)
- **Commodities**: ~23 petroleum-related contracts

### Trader Categories (Disaggregated)

The disaggregated format includes:

1. **Producer/Merchant/Processor/User**
   - Long positions
   - Short positions

2. **Swap Dealers**
   - Long positions
   - Short positions
   - Spreading positions

3. **Managed Money**
   - Long positions
   - Short positions
   - Spreading positions

4. **Other Reportables**
   - Long positions
   - Short positions
   - Spreading positions

5. **Nonreportable Positions**
   - Long positions
   - Short positions

### Data Sections Per Commodity

Each commodity entry includes:

1. **Header**: Market name, exchange, code, report date
2. **Positions Section**:
   - All (Futures + Options combined)
   - Old (Futures only)
   - Other (Options only)
3. **Changes Section**: Week-over-week changes
4. **Percentages Section**: % of Open Interest
5. **Trader Counts Section**: Number of traders in each category
6. **Concentration Section**: % held by largest traders (4 or less, 8 or less)

### Example Data Structure

```
USGC HSFO (PLATTS) - ICE FUTURES ENERGY DIV                                                                                                      Code-02141B
Disaggregated Commitments of Traders - Futures Only, October 07, 2025                                                                                        
-------------------------------------------------------------------------------------------------------------------------------------------------------------
     :          :                                              Reportable Positions                                                      :   Nonreportable
     :          :  Producer/Merchant/ :                                :                                :                                :     Positions
     :   Open   :   Processor/User    :          Swap Dealers          :         Managed Money          :       Other Reportables        :
     : Interest :   Long   :  Short   :   Long   :  Short   :Spreading :   Long   :  Short   :Spreading :   Long   :  Short   :Spreading :   Long  :  Short
-------------------------------------------------------------------------------------------------------------------------------------------------------------
     :          :(1000 barrels)                                                                                                          :
     :          :    Positions                                                                                                           :
All  :    29,051:    15,912     20,345      1,191        677      1,763         75          0         51      4,258        349      5,752:       49       114
Old  :    29,051:    15,912     20,345      1,191        677      1,763         75          0         51      4,258        349      5,752:       49       114
Other:         0:         0          0          0          0          0          0          0          0          0          0          0:        0         0
```

### Field Positions (Fixed-Width)

Based on the structure, approximate column positions:

- **Open Interest**: Column ~15-25
- **Producer/Merchant Long**: Column ~30-40
- **Producer/Merchant Short**: Column ~45-55
- **Swap Dealers Long**: Column ~60-70
- **Swap Dealers Short**: Column ~75-85
- **Swap Dealers Spreading**: Column ~90-100
- **Managed Money Long**: Column ~105-115
- **Managed Money Short**: Column ~120-130
- **Managed Money Spreading**: Column ~135-145
- **Other Reportables Long**: Column ~150-160
- **Other Reportables Short**: Column ~165-175
- **Other Reportables Spreading**: Column ~180-190
- **Nonreportable Long**: Column ~195-205
- **Nonreportable Short**: Column ~210-220

## Commodities Found

The report includes petroleum-related contracts such as:
- USGC HSFO (PLATTS)
- FUEL OIL-3% USGC/3.5% FOB RDAM
- USGC HSFO-PLATTS/BRENT 1ST LN
- And ~20 more petroleum contracts

## Data Access Method

### Current Method
1. Download HTML page: `https://www.cftc.gov/dea/futures/petroleum_lf.htm`
2. Extract `<pre>` tag content
3. Parse fixed-width format

### Alternative Methods to Explore
- Check CFTC PRE for disaggregated download options
- Look for historical disaggregated files
- Check if there's a programmatic API or data feed

## Parsing Strategy

### Fixed-Width Parsing
1. **Identify Commodity Blocks**: Look for lines containing "Code-" and "Disaggregated"
2. **Extract Header Info**: Market name, exchange, code, date
3. **Parse Position Rows**: 
   - "All" row (Futures + Options)
   - "Old" row (Futures only)
   - "Other" row (Options only)
4. **Parse Changes Row**: Week-over-week changes
5. **Parse Percentages**: % of Open Interest
6. **Parse Trader Counts**: Number of traders
7. **Parse Concentration**: Largest trader percentages

### Data Normalization
- Convert fixed-width to structured format
- Handle missing values (represented as "." or "0")
- Parse numeric values (remove commas, handle negative signs)
- Extract dates from header

## Database Schema Implications

Based on this structure, we need:

1. **Markets Table**: Store market/exchange information
2. **Reports Table**: Store report metadata (date, type)
3. **Positions Table**: Store positions with columns for:
   - Producer/Merchant (Long, Short)
   - Swap Dealers (Long, Short, Spreading)
   - Managed Money (Long, Short, Spreading)
   - Other Reportables (Long, Short, Spreading)
   - Nonreportable (Long, Short)
4. **Changes Table**: Store week-over-week changes
5. **Concentration Table**: Store concentration data

## Next Steps

1. ✅ Extract data from HTML page
2. ⏳ Build parser for fixed-width format
3. ⏳ Test parser with sample data
4. ⏳ Design database schema based on actual structure
5. ⏳ Implement data loading pipeline
6. ⏳ Test with multiple reports

## Files Generated

- `data/cftc_cot_samples/petroleum_lf_page.html` - Downloaded HTML page
- `data/cftc_cot_samples/petroleumlf_disaggregated_from_html.txt` - Extracted text data (111 KB)

