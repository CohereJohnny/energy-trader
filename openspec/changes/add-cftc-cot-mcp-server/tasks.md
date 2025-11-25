## 1. Research & Design
- [ ] 1.1 Research CFTC PRE web interface and data download methods
- [ ] 1.2 Identify download URL patterns for COT reports (CSV/XML formats)
- [ ] 1.2 Analyze sample COT report structure (petroleum_lf.htm)
- [ ] 1.3 Design database schema for COT data storage
- [ ] 1.4 Design JSON structure for RAG applications
- [ ] 1.5 Identify required MCP tools and their parameters

## 2. Database Schema
- [ ] 2.1 Create `cftc_cot` schema in PostgreSQL
- [ ] 2.2 Create `reports` table (report_date, report_type, format)
- [ ] 2.3 Create `markets` table (market_code, market_name, exchange, commodity_type)
- [ ] 2.4 Create `trader_categories` table (category_code, category_name, category_type)
- [ ] 2.5 Create `positions` table (report_id, market_id, category_id, positions data)
- [ ] 2.6 Create `concentration` table (report_id, market_id, category_id, concentration data)
- [ ] 2.7 Create indexes for common queries (report_date, market_code, category)
- [ ] 2.8 Create migration script `002_create_cftc_cot_schema.sql`

## 3. Data Ingestion Pipeline
- [ ] 3.1 Create `scripts/ingest_cftc_cot.py` script
- [ ] 3.2 Research CFTC PRE download URL patterns and construct programmatic download URLs
- [ ] 3.3 Implement CFTC data download client (download CSV/XML files from PRE)
- [ ] 3.4 Implement CSV/XML parser for disaggregated reports
- [ ] 3.4 Implement data validation and error handling
- [ ] 3.5 Implement database insertion with conflict handling
- [ ] 3.6 Add command-line arguments (date range, commodity filter)
- [ ] 3.7 Test with sample reports (petroleum commodities)

## 4. MCP Server Implementation
- [ ] 4.1 Create `mcp-servers/cftc-cot/` directory structure
- [ ] 4.2 Set up Python project with `pyproject.toml` and `requirements.txt`
- [ ] 4.3 Create `db.py` for database queries
- [ ] 4.4 Create `citations.py` for citation metadata helpers
- [ ] 4.5 Create `tools.py` with MCP tool implementations:
  - [ ] 4.5.1 `get_cot_data` - Query COT data by commodity and date range
  - [ ] 4.5.2 `analyze_positioning_trends` - Analyze trends over time
  - [ ] 4.5.3 `compare_positioning` - Compare across commodities/dates
  - [ ] 4.5.4 `get_positioning_extremes` - Identify extreme positioning
- [ ] 4.6 Create `server.py` with MCP server setup and tool registration
- [ ] 4.7 Add `.env.example` with database connection config
- [ ] 4.8 Add `setup.sh` script for environment setup

## 5. RAG JSON Generation
- [ ] 5.1 Implement function to generate structured JSON from database records
- [ ] 5.2 Format JSON with hierarchical structure (report -> markets -> categories)
- [ ] 5.3 Include all relevant fields (positions, changes, concentration)
- [ ] 5.4 Add metadata (report_date, report_type, data_source)
- [ ] 5.5 Test JSON generation with sample data

## 6. Testing
- [ ] 6.1 Create test data ingestion script with sample COT report
- [ ] 6.2 Test database queries for all MCP tools
- [ ] 6.3 Create MCP client test suite (`mcp-clients/cftc-cot-tester/`)
- [ ] 6.4 Test all MCP tools with various parameters
- [ ] 6.5 Test citation metadata generation
- [ ] 6.6 Test JSON generation for RAG
- [ ] 6.7 Performance testing with historical data

## 7. Documentation
- [ ] 7.1 Create `mcp-servers/cftc-cot/README.md` with setup instructions
- [ ] 7.2 Document MCP tool parameters and usage
- [ ] 7.3 Document database schema in `database/schema.md`
- [ ] 7.4 Create example queries and use cases
- [ ] 7.5 Update `openspec/project.md` with CFTC COT capability

