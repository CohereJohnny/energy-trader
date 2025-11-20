# Sprint 1 Test Plan

Test cases for Sprint 1 deliverables.

## Database Schema Tests
- [ ] Schema creation succeeds
- [ ] All tables created with correct structure
- [ ] Indexes created and functional
- [ ] Foreign key constraints work correctly

## Data Loading Tests
- [ ] BRENT CSV loads successfully
- [ ] WTI CSV loads successfully
- [ ] GASOIL CSV loads successfully
- [ ] RBOB CSV loads successfully
- [ ] Month codes parsed correctly (all 12 codes)
- [ ] Contract names parsed correctly
- [ ] Dates parsed correctly
- [ ] NULL prices handled correctly
- [ ] Duplicate data handled correctly

## Front Month Logic Tests
- [ ] Front month detection works for single date
- [ ] Front month detection works for date range
- [ ] Contract expiration logic correct
- [ ] Rollover logic correct

## Data Integrity Tests
- [ ] Row counts match CSV files
- [ ] Price values match CSV values
- [ ] Date ranges correct
- [ ] No data corruption

## Performance Tests
- [ ] Front month query completes in < 100ms
- [ ] Date range query completes in < 500ms
- [ ] Bulk data loading completes in reasonable time

