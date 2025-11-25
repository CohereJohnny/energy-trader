# CFTC COT Data Loading Plan

## Overview

This document outlines a comprehensive plan for batch loading CFTC Commitment of Traders (COT) data from the CFTC Public Reporting Environment (PRE) into our PostgreSQL database.

## Key Requirements

### Data Characteristics
- **Frequency**: Weekly reports (released Fridays at 3:30 PM ET)
- **Report Date**: Data as of previous Tuesday
- **Formats**: CSV, XML (within ZIP archives)
- **Report Types**: Disaggregated (short and long format)
- **Historical Range**: ~2006 to present (18+ years)
- **Data Volume**: 
  - ~52 reports per year
  - Multiple commodities per report (5+ petroleum commodities)
  - Multiple trader categories per commodity (4-5 categories)
  - Estimated: ~1,000+ reports × 5 commodities × 5 categories = ~25,000+ records

### Technical Requirements
- **Idempotency**: Re-running should not create duplicates
- **Resumability**: Should be able to resume from last successful load
- **Error Handling**: Handle network failures, parsing errors, invalid data
- **Performance**: Efficient batch processing for large historical backfills
- **Validation**: Data integrity checks before insertion
- **Progress Tracking**: Log progress and allow monitoring

## Architecture

### Components

1. **CFTC Data Downloader**: Downloads ZIP files from CFTC PRE
2. **Data Parser**: Extracts and parses CSV/XML files
3. **Data Validator**: Validates data integrity and completeness
4. **Database Loader**: Batch inserts into PostgreSQL with conflict handling
5. **Progress Tracker**: Tracks loading progress and state

### Database Schema

```sql
-- Schema: cftc_cot
-- Tables:
--   - reports: Report metadata
--   - markets: Commodity markets (WTI, RBOB, etc.)
--   - trader_categories: Trader categories
--   - positions: Position data
--   - concentration: Concentration data (long format)
--   - loading_log: Track loading progress and errors
```

## Data Loading Strategy

### Phase 1: Initial Historical Backfill

**Goal**: Load all available historical data efficiently

**Approach**:
1. **Determine Date Range**: Query CFTC PRE or use known start date (~2006)
2. **Generate Report Dates**: Calculate all Tuesday dates (report dates) from start to present
3. **Batch Processing**: Process reports in batches (e.g., monthly or quarterly)
4. **Parallel Downloads**: Download multiple reports concurrently (with rate limiting)
5. **Batch Inserts**: Use PostgreSQL COPY or batch INSERT with ON CONFLICT

**Batch Size**: 
- Downloads: 10-20 concurrent downloads (respect CFTC servers)
- Database inserts: 1000-5000 records per transaction

**Error Handling**:
- Retry failed downloads (exponential backoff)
- Log failed reports for manual review
- Continue processing other reports even if some fail

### Phase 2: Incremental Weekly Updates

**Goal**: Keep data current with weekly updates

**Approach**:
1. **Check for New Reports**: Query database for latest report date
2. **Calculate Next Report Date**: Next Tuesday after latest report
3. **Download and Process**: Single report processing
4. **Validate**: Check data completeness before insertion
5. **Notify**: Log completion or errors

**Schedule**: 
- Run weekly (e.g., Friday evening or Saturday morning)
- Can be automated via cron or scheduled task

## Implementation Plan

### Step 1: URL Construction and Download

**CFTC PRE URL Patterns**:

Research needed to identify exact URL patterns. Likely patterns:
- `https://www.cftc.gov/files/dea/history/futures_disaggregated_short_YYYYMMDD.zip`
- `https://www.cftc.gov/files/dea/history/futures_disaggregated_long_YYYYMMDD.zip`

**Implementation**:
```python
def construct_download_url(report_date: date, report_type: str, format: str) -> str:
    """
    Construct CFTC PRE download URL.
    
    Args:
        report_date: Report date (Tuesday)
        report_type: 'disaggregated' or 'legacy'
        format: 'short' or 'long'
    
    Returns:
        Download URL
    """
    date_str = report_date.strftime('%Y%m%d')
    filename = f"futures_{report_type}_{format}_{date_str}.zip"
    base_url = "https://www.cftc.gov/files/dea/history/"
    return f"{base_url}{filename}"

def download_report(url: str, output_dir: Path) -> Path:
    """
    Download report ZIP file.
    
    Returns:
        Path to downloaded file
    """
    # Implement with retry logic and error handling
    pass
```

### Step 2: File Extraction and Parsing

**ZIP Structure**:
- ZIP files contain CSV or XML files
- File naming may vary (need to research actual structure)

**Parsing Strategy**:
```python
def extract_and_parse(zip_path: Path) -> List[Dict]:
    """
    Extract ZIP and parse CSV/XML files.
    
    Returns:
        List of parsed records
    """
    # Extract ZIP
    # Identify file format (CSV vs XML)
    # Parse accordingly
    # Return structured data
    pass
```

**CSV Format** (example structure - needs verification):
```
Report Date,Market Code,Market Name,Category,Long,Short,Spread,Change Long,Change Short,...
2024-01-09,CL,Crude Oil,Managed Money,234567,45678,12345,5432,-1234,...
```

**XML Format**: Parse using XML parser (lxml or xml.etree)

### Step 3: Data Validation

**Validation Rules**:
1. **Required Fields**: Report date, market code, category, positions
2. **Data Types**: Validate numeric fields are valid numbers
3. **Business Rules**: 
   - Long + Short + Spread ≤ Open Interest (approximately)
   - Positions ≥ 0
   - Changes can be negative
4. **Completeness**: Check for missing trader categories or markets

**Implementation**:
```python
def validate_record(record: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a single record.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    # Validate data types
    # Check business rules
    
    return len(errors) == 0, errors
```

### Step 4: Database Loading

**Loading Strategy**:

1. **Transaction Management**: Use transactions for batch inserts
2. **Conflict Handling**: Use `ON CONFLICT DO NOTHING` or `ON CONFLICT DO UPDATE`
3. **Batch Size**: Insert in batches (1000-5000 records per transaction)
4. **Progress Tracking**: Update loading_log table

**Implementation**:
```python
def load_to_database(records: List[Dict], batch_size: int = 1000):
    """
    Load records to database in batches.
    """
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        with db.transaction():
            # Insert batch with ON CONFLICT handling
            # Update loading_log
            pass
```

### Step 5: Progress Tracking

**Loading Log Table**:
```sql
CREATE TABLE cftc_cot.loading_log (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    report_type VARCHAR(20) NOT NULL,
    format VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pending', 'downloading', 'parsing', 'loading', 'completed', 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    records_loaded INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_date, report_type, format)
);
```

**Usage**:
- Track which reports have been processed
- Resume from last successful load
- Identify failed reports for retry
- Monitor progress

## Detailed Implementation Steps

### 1. Research and Discovery

**Tasks**:
- [ ] Access CFTC PRE and identify exact URL patterns
- [ ] Download sample reports and analyze file structure
- [ ] Document CSV/XML format specifications
- [ ] Identify all petroleum commodities and their codes
- [ ] Identify all trader categories in disaggregated reports
- [ ] Test download URLs for various dates

**Deliverables**:
- URL pattern documentation
- Sample data files
- Format specification document

### 2. Database Schema Creation

**Tasks**:
- [ ] Create `cftc_cot` schema
- [ ] Create all tables (reports, markets, trader_categories, positions, concentration)
- [ ] Create `loading_log` table
- [ ] Create indexes for performance
- [ ] Create unique constraints for idempotency
- [ ] Create migration script

**Deliverables**:
- Migration script: `002_create_cftc_cot_schema.sql`
- Schema documentation

### 3. Data Downloader Implementation

**Tasks**:
- [ ] Implement URL construction function
- [ ] Implement download function with retry logic
- [ ] Add rate limiting (respect CFTC servers)
- [ ] Handle HTTP errors (404, 500, etc.)
- [ ] Implement exponential backoff for retries
- [ ] Add progress callbacks
- [ ] Cache downloaded files (optional, for debugging)

**Deliverables**:
- `scripts/cftc_downloader.py`
- Unit tests for download logic

### 4. Data Parser Implementation

**Tasks**:
- [ ] Implement ZIP extraction
- [ ] Implement CSV parser
- [ ] Implement XML parser (if needed)
- [ ] Handle different file naming conventions
- [ ] Parse all trader categories
- [ ] Parse concentration data (long format)
- [ ] Handle edge cases (missing data, malformed files)

**Deliverables**:
- `scripts/cftc_parser.py`
- Unit tests with sample data

### 5. Data Validator Implementation

**Tasks**:
- [ ] Implement field validation
- [ ] Implement data type validation
- [ ] Implement business rule validation
- [ ] Generate validation error reports
- [ ] Handle partial data (some categories missing)

**Deliverables**:
- `scripts/cftc_validator.py`
- Validation test cases

### 6. Database Loader Implementation

**Tasks**:
- [ ] Implement batch insert with transactions
- [ ] Implement ON CONFLICT handling
- [ ] Update loading_log table
- [ ] Handle foreign key constraints
- [ ] Optimize insert performance
- [ ] Add progress reporting

**Deliverables**:
- `scripts/cftc_loader.py`
- Database loading tests

### 7. Main Ingestion Script

**Tasks**:
- [ ] Combine all components into main script
- [ ] Add command-line interface (CLI)
- [ ] Support date range specification
- [ ] Support single report processing
- [ ] Support batch processing
- [ ] Add dry-run mode
- [ ] Add verbose logging
- [ ] Generate summary reports

**Deliverables**:
- `scripts/ingest_cftc_cot.py`
- CLI documentation
- Usage examples

### 8. Testing and Validation

**Tasks**:
- [ ] Test with sample reports
- [ ] Test historical backfill (small date range)
- [ ] Test incremental updates
- [ ] Test error handling (network failures, invalid data)
- [ ] Test idempotency (re-running script)
- [ ] Validate data integrity (spot checks)
- [ ] Performance testing (large batches)

**Deliverables**:
- Test suite
- Test data
- Performance benchmarks

## Error Handling Strategy

### Download Errors
- **404 Not Found**: Report doesn't exist (skip, log warning)
- **500 Server Error**: Retry with exponential backoff (max 3 retries)
- **Network Timeout**: Retry with exponential backoff
- **Rate Limiting**: Implement delays between requests

### Parsing Errors
- **Invalid Format**: Log error, skip record, continue processing
- **Missing Fields**: Log warning, use defaults or NULL where appropriate
- **Malformed Data**: Log error, skip record, continue processing

### Database Errors
- **Constraint Violations**: Log error, skip record (shouldn't happen with validation)
- **Connection Errors**: Retry with exponential backoff
- **Transaction Failures**: Rollback, log error, continue with next batch

### Recovery Strategy
- **Failed Downloads**: Retry in next run (tracked in loading_log)
- **Failed Parsing**: Manual review of problematic files
- **Failed Database Inserts**: Review error logs, fix data, re-run

## Performance Optimization

### Download Optimization
- **Concurrent Downloads**: 10-20 concurrent downloads (with rate limiting)
- **Connection Pooling**: Reuse HTTP connections
- **Caching**: Cache downloaded ZIP files (optional, for debugging)

### Parsing Optimization
- **Streaming Parsing**: Parse large files in chunks
- **Parallel Parsing**: Parse multiple files concurrently (if multiple commodities)

### Database Optimization
- **Batch Inserts**: Insert 1000-5000 records per transaction
- **COPY Command**: Consider PostgreSQL COPY for very large batches
- **Index Management**: Disable indexes during bulk load, rebuild after
- **Connection Pooling**: Use connection pool for database connections

## Monitoring and Logging

### Logging Levels
- **INFO**: Progress updates, successful operations
- **WARNING**: Skipped records, missing data
- **ERROR**: Failed downloads, parsing errors, database errors
- **DEBUG**: Detailed operation logs (verbose mode)

### Metrics to Track
- **Reports Processed**: Total, successful, failed
- **Records Loaded**: Total records inserted
- **Processing Time**: Time per report, total time
- **Error Rate**: Percentage of failed operations
- **Data Quality**: Validation error counts

### Progress Reporting
- **Console Output**: Real-time progress updates
- **Log Files**: Detailed logs for debugging
- **Database Log**: Track in loading_log table
- **Summary Report**: Generate at end of run

## CLI Interface Design

```bash
# Historical backfill (date range)
python scripts/ingest_cftc_cot.py \
    --start-date 2020-01-01 \
    --end-date 2024-01-01 \
    --report-type disaggregated \
    --format long

# Single report
python scripts/ingest_cftc_cot.py \
    --report-date 2024-01-09 \
    --report-type disaggregated \
    --format long

# Incremental update (latest)
python scripts/ingest_cftc_cot.py \
    --incremental \
    --report-type disaggregated \
    --format long

# Dry run (no database writes)
python scripts/ingest_cftc_cot.py \
    --start-date 2024-01-01 \
    --end-date 2024-01-31 \
    --dry-run

# Verbose logging
python scripts/ingest_cftc_cot.py \
    --start-date 2024-01-01 \
    --end-date 2024-01-31 \
    --verbose
```

## Data Quality Checks

### Pre-Load Validation
- Check report date is valid Tuesday
- Check all required fields present
- Validate data types
- Check business rules

### Post-Load Validation
- Compare record counts (expected vs. loaded)
- Spot check sample records
- Verify no duplicates
- Check data consistency (e.g., positions sum correctly)

### Ongoing Monitoring
- Track data completeness over time
- Monitor for missing reports
- Alert on unusual patterns

## Rollback Strategy

### If Data Load Fails
- **Transaction Rollback**: Each batch is in a transaction
- **Partial Loads**: Can identify and remove failed batches
- **Re-run**: Script is idempotent, can re-run safely

### If Wrong Data Loaded
- **Delete by Date Range**: Remove specific date range
- **Re-load**: Re-run script for date range

## Future Enhancements

1. **Automated Scheduling**: Cron job for weekly updates
2. **Email Notifications**: Alert on failures or completion
3. **Data Quality Dashboard**: Monitor data completeness
4. **Incremental Validation**: Continuous data quality checks
5. **API Endpoint**: Expose loading status via API
6. **Data Archival**: Archive old reports to reduce database size

## Dependencies

- **Python Libraries**:
  - `requests`: HTTP downloads
  - `pandas`: CSV parsing and data manipulation
  - `lxml` or `xml.etree`: XML parsing (if needed)
  - `psycopg2`: PostgreSQL database access
  - `python-dotenv`: Environment variable management
  - `click` or `argparse`: CLI interface

## Timeline Estimate

- **Research and Discovery**: 2-3 days
- **Database Schema**: 1 day
- **Downloader**: 2-3 days
- **Parser**: 3-4 days
- **Validator**: 2 days
- **Database Loader**: 2-3 days
- **Main Script**: 2 days
- **Testing**: 3-4 days
- **Total**: ~3-4 weeks

