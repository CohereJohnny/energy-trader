# Sprint 4 Tasks

## Goals
Integrate MCP server with AI agent and test end-to-end queries. This sprint focuses on configuring the AI agent to use the futures prices MCP server and validating natural language query handling.

**OpenSpec Change**: AI Agent Integration for `add-futures-price-mcp-server`

## Tasks

### 1. Agent Instructions Development
- [x] 1.1 Review North agent best practices and sample instructions
- [x] 1.2 Populate agent-instructions.md with role, mission, and behavior rules
- [x] 1.3 Define tool usage guidelines for futures prices MCP server
- [x] 1.4 Specify output format and citation requirements
- [x] 1.5 Add domain-specific guidance for energy trading context

**Progress Notes**:
- ✅ Completed comprehensive agent instructions in `specs/agent-instructions.md`
- ✅ Includes role, mission, core behavior rules, tool usage guidelines, conditional logic, output format, quality checks, and domain context
- ✅ Follows North best practices with clear structure and examples

### 2. AI Agent Configuration
- [ ] 2.1 Configure AI agent to connect to futures prices MCP server
- [ ] 2.2 Set up MCP server endpoint and authentication
- [ ] 2.3 Verify agent can discover available tools
- [ ] 2.4 Test basic tool invocation from agent

### 3. End-to-End Query Testing
- [ ] 3.1 Test: "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?"
- [ ] 3.2 Test: "What was the front month Brent Settlement yesterday?"
- [ ] 3.3 Test: "Display a seasonal chart of M2 GOBRs"
- [ ] 3.4 Test additional natural language query variations
- [ ] 3.5 Validate agent selects correct tools for queries
- [ ] 3.6 Validate agent formats responses appropriately

### 4. Citation Metadata Validation
- [ ] 4.1 Verify citations appear in agent responses
- [ ] 4.2 Validate citation format matches North MCP metadata structure
- [ ] 4.3 Test citation display in UI
- [ ] 4.4 Ensure all tool responses include proper citations

### 5. Error Handling & Edge Cases
- [ ] 5.1 Test agent behavior with invalid commodity codes
- [ ] 5.2 Test agent behavior with invalid dates
- [ ] 5.3 Test agent behavior with missing data scenarios
- [ ] 5.4 Validate error messages are user-friendly
- [ ] 5.5 Test agent handling of ambiguous queries

### 6. Performance Optimization
- [ ] 6.1 Measure end-to-end query response times
- [ ] 6.2 Optimize tool selection logic if needed
- [ ] 6.3 Validate performance meets requirements (< 5s for simple queries)

### 7. User Acceptance Testing
- [ ] 7.1 Create UAT test scenarios
- [ ] 7.2 Execute UAT with sample queries
- [ ] 7.3 Document feedback and issues
- [ ] 7.4 Address any UAT findings

### 8. Documentation
- [ ] 8.1 Document agent configuration
- [ ] 8.2 Update project documentation with agent setup
- [ ] 8.3 Create user guide for querying the agent
- [ ] 8.4 Document known limitations and future enhancements

## Sprint Review

### Demo Readiness
- TBD

### Gaps/Issues
- TBD

### Next Steps
- TBD

