## ADDED Requirements

### Requirement: Futures Prices Database Schema
The system SHALL store normalized futures prices data in a PostgreSQL database with the following structure:
- A `commodities` table storing commodity metadata (BRENT, WTI, GASOIL, RBOB)
- A `contracts` table storing contract metadata (commodity, expiration year, expiration month)
  - Expiration month SHALL be stored as integer (1-12) derived from CME Group month codes
- A `prices` table storing daily settlement prices for each contract
- All tables SHALL be in a `futures_prices` schema

#### Scenario: Schema creation
- **WHEN** the database migration is run
- **THEN** the `futures_prices` schema is created with all required tables and indexes

### Requirement: Contract Naming Convention
The system SHALL parse contract names using CME Group month codes as defined at https://www.cmegroup.com/month-codes.html. Contract names in CSV files follow the pattern `COMMODITY_YYYYM` where:
- `COMMODITY` is the commodity code (BRENT, WTI, GO, RBOB)
- `YYYY` is the expiration year (e.g., 2011, 2012)
- `M` is the CME Group month code:
  - F = January
  - G = February
  - H = March
  - J = April
  - K = May
  - M = June
  - N = July
  - Q = August
  - U = September
  - V = October
  - X = November
  - Z = December

#### Scenario: Parse contract name
- **WHEN** processing a column header like "BRENT_2011F"
- **THEN** the system correctly identifies it as BRENT commodity, expiration year 2011, expiration month January

### Requirement: Data Loading
The system SHALL load historical futures prices from CSV files (BR_CUR.csv, WTI_CUR.csv, GO_CUR.csv, RB_CUR.csv) into the PostgreSQL database. Contract names in these files use CME Group month codes and MUST be parsed according to the contract naming convention.

#### Scenario: Successful data load
- **WHEN** the data loading script processes a CSV file
- **THEN** all contract prices are normalized and stored in the database with correct date parsing and month code interpretation

#### Scenario: Handle missing data
- **WHEN** a CSV row contains empty price values
- **THEN** those prices are stored as NULL in the database

### Requirement: Front Month Price Lookup
The system SHALL identify the front month (nearest expiring contract with a valid price) for a given commodity and date.

#### Scenario: Single date lookup
- **WHEN** querying front month price for BRENT on 2025-01-03
- **THEN** the system returns the price of the nearest expiring BRENT contract that has a price on that date

#### Scenario: Date range lookup
- **WHEN** querying front month prices for BRENT between 2025-01-03 and 2025-03-31
- **THEN** the system returns all front month prices for each date in the range

### Requirement: MCP Server for Futures Prices
The system SHALL provide an MCP server that exposes tools for querying futures prices data.

#### Scenario: Get front month price
- **WHEN** the AI agent calls `get_front_month_price` with commodity="BRENT" and date="2025-01-03"
- **THEN** the tool returns the front month settlement price with citation metadata

#### Scenario: Get front month prices for date range
- **WHEN** the AI agent calls `get_front_month_prices` with commodity="BRENT", start_date="2025-01-03", end_date="2025-03-31"
- **THEN** the tool returns all front month prices in the date range with citation metadata

#### Scenario: Calculate price change
- **WHEN** the AI agent calls `calculate_price_change` with commodity="BRENT", start_date="2025-01-03", end_date="2025-03-31"
- **THEN** the tool returns the price change (absolute and percentage) with citation metadata

#### Scenario: Get seasonal data
- **WHEN** the AI agent calls `get_seasonal_data` with commodity="GASOIL", contract_month_offset=2 (M2)
- **THEN** the tool returns historical prices for the second month contract across multiple years for seasonal analysis

### Requirement: Citation Metadata
All MCP tool responses SHALL include `_north_metadata` fields for proper citation display in the North UI.

#### Scenario: Citation format
- **WHEN** a tool returns price data
- **THEN** the response includes `_north_metadata` with title, source information, and timestamp

### Requirement: MCP Server Transport
The MCP server SHALL use StreamableHTTP transport as required by North MCP Python SDK.

#### Scenario: Server startup
- **WHEN** the MCP server starts
- **THEN** it uses StreamableHTTP transport and is accessible via HTTP endpoint

