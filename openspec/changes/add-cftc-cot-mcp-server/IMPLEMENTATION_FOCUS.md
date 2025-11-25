# CFTC COT Implementation Focus

## Scope

**Focus Areas**:
1. **Report Type**: Disaggregated Futures and Options only
2. **Commodity Groups**:
   - Petroleum and Products
   - Natural Gas and Products
   - Electricity

**Out of Scope** (for now):
- Legacy reports
- Traders in Financial Futures (TFF) reports
- Other commodity groups (agricultural, metals, etc.)

## Target Commodities

### Petroleum and Products
- NYMEX Crude Oil (WTI) - CL
- ICE Brent Crude Oil - BZ
- NYMEX Gasoline (RBOB) - RB
- NYMEX Heating Oil - HO
- ICE Gas Oil - G

### Natural Gas and Products
- NYMEX Natural Gas - NG
- NYMEX Propane - PN

### Electricity
- NYMEX Electricity (various contracts) - Various codes

## Implementation Phases

### Phase 1: Research & Discovery (Current)
**Goal**: Understand exact data format and structure

**Tasks**:
1. Access CFTC PRE and locate Disaggregated Futures and Options reports
2. Download sample reports for target commodity groups
3. Analyze file structure (ZIP contents, CSV/XML format)
4. Document:
   - URL patterns for downloads
   - File naming conventions
   - CSV/XML structure
   - Field mappings
   - Commodity codes

**Deliverables**:
- Sample data files
- Format documentation
- URL pattern documentation

### Phase 2: Database Schema
**Goal**: Create schema optimized for target commodities

**Tasks**:
1. Design schema based on actual data structure
2. Create migration script
3. Add indexes for common queries
4. Create loading_log table

**Deliverables**:
- `002_create_cftc_cot_schema.sql`
- Schema documentation

### Phase 3: Data Loading Pipeline
**Goal**: Load sample data successfully

**Tasks**:
1. Implement downloader (construct URLs, download ZIPs)
2. Implement parser (extract ZIP, parse CSV/XML)
3. Implement validator (validate data integrity)
4. Implement loader (batch insert to database)
5. Test with sample reports

**Deliverables**:
- `scripts/ingest_cftc_cot.py`
- Test data loaded successfully

### Phase 4: Validation & Testing
**Goal**: Verify data quality and completeness

**Tasks**:
1. Validate data integrity (spot checks)
2. Verify all commodities loaded correctly
3. Check trader categories present
4. Validate date ranges
5. Performance testing

**Deliverables**:
- Validation report
- Data quality metrics

### Phase 5: MCP Server Integration
**Goal**: Expose data via MCP tools

**Tasks**:
1. Create MCP server structure
2. Implement database queries
3. Build MCP tools
4. Add citation metadata
5. Test with MCP client

**Deliverables**:
- Working MCP server
- MCP tools functional

### Phase 6: Agent Testing
**Goal**: Test with AI agent use cases

**Tasks**:
1. Test agent queries
2. Verify citation metadata
3. Test RAG JSON generation
4. Validate insights generation

**Deliverables**:
- Agent test results
- Use case validation

## Next Steps

1. **Start with Research**: Download and analyze sample reports
2. **Document Findings**: Create format specification
3. **Build Schema**: Based on actual data structure
4. **Implement Loader**: Focus on getting data in first
5. **Validate**: Ensure data quality
6. **Build MCP Server**: Expose via tools
7. **Test**: End-to-end validation

## Success Criteria

- [ ] Sample reports downloaded successfully
- [ ] Data parsed correctly (all fields extracted)
- [ ] Data loaded into database (all commodities, all trader categories)
- [ ] Data validated (integrity checks pass)
- [ ] MCP server queries return correct data
- [ ] Citation metadata present in responses
- [ ] Agent can query and analyze COT data successfully

