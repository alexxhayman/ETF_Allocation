# ETF Allocation Project - Data Workflow Analysis

## 📊 **DATA FLOW OVERVIEW**

```
Raw Sources → Processing Scripts → Intermediate Files → Final Analysis → Output Reports
```

---

## 🗂️ **DATA SOURCES & LINEAGE**

### **1. Original Data Sources**

#### **ETF Performance Data:**
- **Source Files:** 9 individual iShares Excel files (.xlsx)
  - `iShares-Core-Dividend-Growth-ETF_fund.xlsx`
  - `iShares-MSCI-USA-Momentum-Factor-ETF_fund.xlsx`
  - `iShares-SP-500-Value-ETF_fund.xlsx`
  - `iShares-Asia-50-ETF_fund.xlsx`
  - `iShares-MSCI-USA-Quality-GARP-ETF_fund.xlsx`
  - `iShares-MSCI-EAFE-Min-Vol-Factor-ETF_fund.xlsx`
  - `iShares-Edge-MSCI-World-Momentum-Factor-UCITS-ETF-USD-Acc_fund.xlsx`
  - `iShares-MSCI-USA-Min-Vol-Factor-ETF_fund.xlsx`
  - `iShares-Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-EUR-Acc_fund.xlsx`

#### **Economic Data:**
- **Source File:** `Global Equity Fund (only economic data).xlsx`
  - Sheet: "Eco Data"
  - Columns: Date, US_GDP_QoQ_Ann (Column F), PCE_Prices (Column H)

#### **FX Data:**
- **Source:** External API (for EUR/USD conversion)
- **File:** `eurusd_historical_data.csv`

---

## 🔄 **PROCESSING PIPELINE**

### **Step 1: Economic Data Extraction**
```
Script: extract_economic_data.py
Input:  Global Equity Fund (only economic data).xlsx [Eco Data sheet]
Output: economic_data_extracted.csv
Process: Extracts Date, US_GDP_QoQ_Ann, PCE_Prices from columns A, F, H
```
**✅ Verification Point:** Check that dates align and economic indicators are properly extracted

### **Step 2: Economic Regime Classification**
```
Script: regime_modelling.py
Input:  economic_data_extracted.csv
Output: dates_and_regimes.csv, economic_regimes_classified.csv, economic_regimes_analysis.png
Process: Classifies each month into 4 economic regimes based on GDP/inflation trends
```
**✅ Verification Point:** Ensure regime logic is correct and dates are continuous

### **Step 3: ETF Data Consolidation**
```
Script: [ETF extraction process - appears to be in etf_extractor/]
Input:  9 individual iShares Excel files
Output: consolidated_etf_performance.csv
Process: Extracts monthly performance data from each ETF Excel file
```
**❌ Gap Identified:** ETF extraction script not clearly visible in main directory

### **Step 4: Currency Conversion** 
```
Script: eur_usd_converter.py, fx_converted_consolidated_etf_performance.py
Input:  consolidated_etf_performance.csv, eurusd_historical_data.csv
Output: consolidated_etf_performance_with_usd.csv
Process: Converts EUR-denominated ETF returns to USD
```
**✅ Verification Point:** EUR ETFs properly converted using historical FX rates

### **Step 5: Portfolio Optimization**
```
Script: optimal_allocation_refactored.py
Inputs: consolidated_etf_performance_with_usd.csv, dates_and_regimes.csv
Output: optimal_etf_allocations_constrained.csv
Process: Mean-variance optimization with 25% max allocation constraint
```
**✅ Verification Point:** All regime periods have sufficient data for optimization

### **Step 6: Report Generation**
```
Manual/Script: Summary report creation
Input:  optimal_etf_allocations_constrained.csv
Output: ETF_Allocation_Summary_Report.md, Quick_Reference_Allocation_Table.csv
Process: Format results for stakeholder consumption
```

---

## ⚠️ **DATA INTEGRITY ISSUES IDENTIFIED**

### **🔴 Critical Issues:**

1. **ETF Extraction Process Unknown**
   - ETF consolidation script not clearly identified
   - Cannot verify how individual Excel files → consolidated CSV
   - **Risk:** Data extraction errors, missing data points

2. **Date Format Inconsistencies**
   - ETF data: DD-MM-YYYY format (end of month)
   - Economic data: YYYY-MM-DD format (start of month)  
   - **Fixed in:** optimal_allocation_refactored.py (uses year-month matching)

3. **Missing Data Handling**
   - Empty cells in ETF performance data
   - No clear documentation of how gaps are handled
   - **Risk:** Optimization based on incomplete data

### **🟡 Minor Issues:**

4. **FX Data Dependency**
   - External API dependency for EUR/USD rates
   - No fallback if API fails
   - **Risk:** Currency conversion accuracy

5. **File Naming Inconsistencies**
   - Mix of underscores and hyphens
   - Some generated files not clearly documented

---

## ✅ **DATA VERIFICATION CHECKLIST**

### **Source Data Verification:**
- [ ] **ETF Excel files contain expected performance data**
- [ ] **Economic Excel file has GDP and PCE data in correct columns**
- [ ] **Date ranges are consistent across all sources**
- [ ] **Performance data is monthly frequency**

### **Processing Verification:**
- [ ] **Economic regimes correctly classified (4 categories)**
- [ ] **ETF data properly consolidated (all 9 ETFs)**
- [ ] **EUR/USD conversion applied correctly**
- [ ] **Date alignment between ETF and regime data works**

### **Output Verification:**
- [ ] **All 8 regime allocations present in final output**
- [ ] **Allocation weights sum to 100% per regime**
- [ ] **No single ETF exceeds 25% allocation**
- [ ] **Sharpe ratios calculated correctly**

---

## 🔧 **RECOMMENDATIONS FOR IMPROVED TRACEABILITY**

### **1. Document ETF Extraction Process**
```python
# Create: etf_data_extractor.py
# Clearly document which Excel sheet/columns are used
# Add data validation checks
```

### **2. Add Data Validation Scripts**
```python
# Create: data_validation.py
# Verify date continuity
# Check for missing data patterns
# Validate calculation accuracy
```

### **3. Create Master Configuration File**
```yaml
# config.yaml
data_sources:
  etf_files: [list of Excel files]
  economic_file: "Global Equity Fund.xlsx"
  regime_periods:
    pre_garp: "2015-02-28 to 2020-01-31"
    post_garp: "2020-02-29 to 2025-06-30"
constraints:
  max_allocation_per_etf: 0.25
  min_observations: 5
```

### **4. Implement Data Lineage Tracking**
```python
# Add to each processing script:
# - Input file checksums
# - Processing timestamps  
# - Data quality metrics
# - Transformation logs
```

### **5. Create End-to-End Test**
```python
# test_full_pipeline.py
# Run complete pipeline with known test data
# Verify expected outputs
# Catch any breaking changes
```

---

## 🎯 **IMMEDIATE ACTION ITEMS**

1. **HIGH PRIORITY:** Document/locate ETF extraction process
2. **HIGH PRIORITY:** Add data validation at each step  
3. **MEDIUM PRIORITY:** Create configuration management
4. **MEDIUM PRIORITY:** Implement automated testing
5. **LOW PRIORITY:** Standardize file naming conventions

---

## 📈 **DATA QUALITY CONFIDENCE LEVELS**

- **Economic Regime Classification:** ✅ **HIGH** (clear logic, verifiable)
- **Currency Conversion:** ✅ **HIGH** (historical FX data, standard approach)  
- **Portfolio Optimization:** ✅ **HIGH** (established mean-variance method)
- **ETF Data Extraction:** ❓ **UNKNOWN** (process not documented)
- **Date Alignment:** ✅ **MEDIUM** (workaround implemented, but fragile)
- **Missing Data Handling:** ❓ **UNKNOWN** (no clear documentation)

**Overall Project Confidence:** **MEDIUM** - Core analysis is sound, but data pipeline has gaps that need addressing.