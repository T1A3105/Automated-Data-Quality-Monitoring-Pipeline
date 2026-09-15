# Data Quality Report — day2

**Generated:** 2026-09-15T06:27:14.851061

**Status:** FAIL

**Rows checked:** 126

**Issues found:** 6 (3 critical, 3 warning)

| Severity | Check | Detail |
|---|---|---|
| warning | null_rate | Column 'customer_id' has 7.1% null values (threshold: 5%) |
| warning | null_rate | Column 'amount' has 10.3% null values (threshold: 5%) |
| warning | duplicates | Found 6 duplicate row(s) (excluding order_id/created_at) |
| critical | out_of_range | Column 'amount' has 5 value(s) outside expected range [0, 100000] (e.g. -250.0) |
| critical | out_of_range | Column 'quantity' has 4 value(s) outside expected range [1, 500] (e.g. 9999) |
| critical | row_count_drop | Row count dropped 37.0% vs previous day (200 -> 126) |
