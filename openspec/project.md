# Project Context

## Purpose
Energy Trader is an AI Agent application for international oil trading and supply optimization. The system leverages MCP (Model Context Protocol) servers to provide an AI agent that helps traders analyze fundamental data, global price sets, and market positioning to inform forward outlook on oil markets and make data-driven trading decisions.

Key capabilities include:
- AI Agent that queries and analyzes futures prices for ICE BRENT, NYMEX WTI, ICE GASOIL, and NYMEX RBOB
- MCP servers that provide tools for accessing fundamental data from DOE/EIA (weekly and monthly) and IEA
- MCP tools for analyzing Commitment of Traders (COT) reports for market positioning insights
- Tools for generating seasonal charts and price change analyses
- Market sentiment analysis through curated datasets
- Retrieving commodity prices, futures contracts, and open positions via MCP tools

## Tech Stack
- **Frontend Framework**: Next.js 14 (App Router)
- **Frontend Language**: TypeScript
- **MCP Servers**: Python (using North MCP Python SDK)
- **MCP SDK**: [North MCP Python SDK](https://github.com/cohere-ai/north-mcp-python-sdk)
- **Database**: Containerized PostgreSQL (multiple schemas)
- **Styling**: TailwindCSS
- **Development**: OpenSpec for spec-driven development
- **Package Managers**: 
  - pnpm (for Next.js frontend)
  - uv (for Python MCP servers)

## Project Conventions

### Code Style
- **Component naming**: Use kebab-case for component files (e.g., `price-chart.tsx`, `futures-table.tsx`)
- **TypeScript**: Strict mode enabled, prefer explicit types over `any`
- **Formatting**: Follow standard Next.js/React conventions
- **Imports**: Organize imports (external, internal, relative) with clear separation
- **Comments**: Use clear, concise comments for complex business logic, especially domain-specific calculations

### Architecture Patterns

#### Frontend Architecture
- **Server Components First**: Prefer React Server Components and Next.js SSR features. Minimize client components (`'use client'`) to small, isolated interactive pieces
- **Data Fetching**: Use Server Components for data fetching with proper loading and error states
- **Component Structure**: 
  - Keep components focused and single-purpose
  - Extract reusable logic into utilities or hooks
  - Use semantic HTML elements where possible
- **Error Handling**: Always implement error handling and error logging for data fetching operations
- **State Management**: Use React state for UI state; prefer server-side data fetching over client-side state for data

#### MCP Architecture
- **MCP Servers**: Build dedicated MCP servers using the [North MCP Python SDK](https://github.com/cohere-ai/north-mcp-python-sdk)
- **Transport**: Use StreamableHTTP transport (SSE transport is deprecated)
- **Citations Pattern**: Follow the [citations example](https://github.com/cohere-ai/north-mcp-python-sdk/blob/main/examples/server_with_citations.py) to include `_north_metadata` fields in tool responses for proper citation display in the North UI
- **MCP Tools**: Each MCP server exposes tools for specific data domains:
  - Commodity prices retrieval
  - Futures contracts data
  - Open positions tracking
  - EIA data access
  - IEA data access
  - CFTC data access
- **MCP Clients**: Build MCP clients to test and interact with MCP servers during development
- **Tool Response Format**: Include citation metadata in tool responses:
  ```python
  {
      "text": "Result content",
      "_north_metadata": {
          "title": "Source Title",
          "url": "https://source.url",
          "author_name": "Author Name",
          "last_updated": "timestamp",
          "page_number": "page_number"
      }
  }
  ```

#### Backend Architecture
- **Database**: Containerized PostgreSQL instance
- **Schema Organization**: Use multiple schemas to organize different datasets:
  - Separate schemas for futures prices, fundamental data, positioning data, etc.
  - Schema-per-dataset pattern for better organization and access control

### Testing Strategy
- **MCP Server Testing**: Build MCP clients to test MCP servers and tools
- **Unit Tests**: Write tests for critical business logic and data transformations
- **Data Validation**: Test data parsing and validation for futures price data
- **API Testing**: Test API endpoints and data fetching logic
- **Integration Tests**: Test MCP server integration with the AI agent
- **Frontend Tests**: Focus on testing user-facing functionality and edge cases

### Git Workflow
- **Sprint-Based Development**: Project uses sprint-based approach (see `sprints/sprintplan.md`)
- **Branching**: Create sprint branches (e.g., `sprint-1`, `sprint-2`) for each sprint
- **Commit Messages**: Use conventional commits (feat:, fix:, refactor:, etc.)
- **Spec-Driven Development**: Follow OpenSpec workflow - create proposals before implementing features
- **Code Review**: Ensure all changes align with project specs before merging
- **Sprint Completion**: Merge sprint branch to main, tag release, archive sprint directory

## Domain Context

### Core Data Sets
1. **Futures Prices**:
   - ICE BRENT (Brent crude oil futures)
   - NYMEX WTI (West Texas Intermediate crude oil futures)
   - ICE GASOIL (Gas oil futures)
   - NYMEX RBOB (Reformulated Blendstock for Oxygenate Blending gasoline futures)

2. **Fundamental Data Sources**:
   - DOE/EIA Weekly Petroleum Status Report: https://www.eia.gov/petroleum/supply/weekly/
   - DOE/EIA Monthly Petroleum Supply: https://www.eia.gov/petroleum/supply/monthly/
   - IEA Data and Statistics: https://www.iea.org/data-and-statistics/data-sets

3. **Market Positioning**:
   - CFTC Commitment of Traders Report: https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm

### Key Concepts
- **Front Month**: The nearest expiring futures contract
- **Settlement Price**: The official closing price of a futures contract
- **M2 GOBRs**: Month 2 Gas Oil Brent Ratio (example of spread analysis)
- **Seasonal Analysis**: Historical price patterns by time of year
- **Market Sentiment**: Analysis of trader positioning and market outlook

### Common Queries
- Price changes between dates (e.g., "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?")
- Current settlement prices (e.g., "What was the front month Brent Settlement yesterday?")
- Seasonal charts (e.g., "Display a seasonal chart of M2 GOBRs")
- Spread analysis and positioning insights

## Important Constraints
- **Data Accuracy**: Financial data must be precise - no rounding errors in price calculations
- **Performance**: Large historical datasets (4000+ rows per commodity) require efficient querying and caching
- **Regulatory**: Trading data may be subject to financial regulations - ensure proper data handling and audit trails
- **Real-time Requirements**: Settlement prices and current market data need to be up-to-date
- **Data Privacy**: Trading strategies and positions are sensitive - ensure proper access controls

## External Dependencies
- **North MCP Python SDK**: [cohere-ai/north-mcp-python-sdk](https://github.com/cohere-ai/north-mcp-python-sdk) - For building MCP servers with authentication and citations support
- **PostgreSQL**: Containerized database instance (not Supabase)
- **EIA API**: For accessing DOE/EIA petroleum supply data (may require API keys)
- **IEA API**: For accessing IEA data sets (may require API keys)
- **CFTC**: Commitment of Traders data (may require web scraping or API access)
- **Futures Exchanges**: ICE and NYMEX data feeds (may require data provider subscriptions)
- **Python Dependencies**: Managed via `uv` package manager
