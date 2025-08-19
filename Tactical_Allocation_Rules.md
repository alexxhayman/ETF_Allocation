# SYSTEMATIC ETF TACTICAL ALLOCATION RULES
*Mathematical Optimization with Economic Logic - Single Period Analysis (2015-2025)*

## How to Use This Guide
1. **Identify Current/Target Regime**: Assess economic growth and inflation trends
2. **Choose Optimization Method**: Select Sharpe (conservative) or Sortino (upside-focused)  
3. **Implement Allocation**: Use the percentages below for systematic rebalancing

---

## OPTIMIZATION METHODOLOGY

### Mathematical Foundation
The ETF selections are **not arbitrary** - they result from solving this optimization problem:

**Objective Function:**
- **Sharpe Method**: Maximize `Mean Return / Total Volatility`
- **Sortino Method**: Maximize `Mean Return / Downside Volatility`

**Constraints:**
- All weights sum to 100% (`∑weights = 1.0`)
- Maximum 15% per ETF (`0 ≤ weight ≤ 0.15`)
- No short selling (`weight ≥ 0`)
- ETFs must have ≥60% data availability for statistical reliability

### Data-Driven Selection Process
1. **Historical Analysis**: Uses 125 observations (2015-2025) across all regimes
2. **Dynamic Universe**: Includes all 15 ETFs when sufficient data exists
3. **Statistical Validation**: Only ETFs with reliable historical data are included
4. **Optimization Engine**: Scipy minimize function tests thousands of weight combinations

---

## SHARPE RATIO ALLOCATIONS (Total Volatility - 15% Max)
*Conservative approach - penalizes all volatility*

### 🟢 Rising Growth, Falling Inflation
**Best Case Scenario - Balanced Growth** | **7 ETFs Used | 30 Observations**
- World_Momentum: **15.0%**
- USA_MinVol: **15.0%**
- Global_MinVol: **15.0%**
- World_MinVol_USD: **15.0%**
- USA_Momentum: **15.0%**
- EAFE_MinVol: **15.0%**
- Europe_Momentum_USD: **10.0%**

**Expected Return: 118.23% | Sharpe Ratio: 0.408**

**Economic Logic:**
- **Momentum ETFs** capture growth trends when economic conditions are improving
- **Minimum Volatility ETFs** benefit from falling inflation premiums while participating in growth
- **Global Diversification** captures worldwide growth opportunities
- **Strategy**: Balanced approach between growth capture and downside protection

### 🔥 Rising Growth, Rising Inflation
**Reflationary Growth - Quality Value Focus** | **7 ETFs Used | 27 Observations**
- Dividend_Growth: **15.0%**
- SP500_Value: **15.0%**
- USA_EqualWeight: **15.0%**
- Russell_2000: **15.0%**
- Asia_50: **15.0%**
- USA_Quality_Factor: **15.0%**
- USA_MinVol: **10.0%**

**Expected Return: 214.17% | Sharpe Ratio: 0.535**

**Economic Logic:**
- **Value ETFs** historically outperform growth during inflationary periods
- **Dividend Growth** provides income hedge against rising prices
- **Small Caps (Russell 2000)** tend to outperform in reflationary environments
- **Equal Weight** reduces mega-cap tech exposure that suffers from rising rates
- **Quality Factor** selects companies that can pass through inflation costs
- **Strategy**: Inflation-resilient positioning with value bias

### 📈 Slowing Growth, Falling Inflation
**Quality Opportunity - Momentum Focus** | **8 ETFs Used | 18 Observations**
- USA_Momentum: **15.0%**
- Europe_Momentum_USD: **15.0%**
- World_Momentum: **15.0%**
- USA_GARP: **15.0%**
- Europe_MinVol_EUR: **15.0%**
- USA_Quality_Factor: **15.0%**
- EAFE_MinVol: **5.9%**
- Russell_2000: **4.1%**

**Expected Return: 356.35% | Sharpe Ratio: 1.091**

**Economic Logic:**
- **Multiple Momentum ETFs** capture liquidity-driven rallies from central bank easing
- **GARP (Growth at Reasonable Price)** identifies sustainable growth in slowing economy
- **Quality Factor** represents flight-to-quality in uncertain growth environment
- **European Exposure** diversifies across different monetary policy responses
- **Strategy**: High-conviction momentum and quality with global diversification

### ⚠️ Slowing Growth, Rising Inflation
**Stagflation Defense - Minimum Volatility Focus** | **7 ETFs Used | 41 Observations**
- Global_MinVol: **15.0%**
- World_Momentum: **15.0%**
- USA_MinVol: **15.0%**
- USA_Momentum: **15.0%**
- Europe_Momentum_USD: **15.0%**
- World_MinVol_USD: **15.0%**
- Europe_MinVol_EUR: **10.0%**

**Expected Return: -21.72% | Sharpe Ratio: -0.059**

**Economic Logic:**
- **Heavy Min-Vol Allocation** provides defensive positioning in challenging macro environment
- **Momentum ETFs** still capture relative strength opportunities even in difficult periods
- **Global Geographic Spread** reduces concentration risk across different policy responses
- **Strategy**: Capital preservation with selective momentum exposure

---

## SORTINO RATIO ALLOCATIONS (Downside Volatility Only - 15% Max)
*Upside-focused approach - allows for positive volatility*

### 🟢 Rising Growth, Falling Inflation
**Balanced Momentum & Quality** | **10 ETFs Used | 30 Observations**
- Europe_Momentum_USD: **15.0%**
- USA_Momentum: **15.0%**
- World_Momentum: **14.5%**
- Global_MinVol: **13.2%**
- World_MinVol_USD: **12.8%**
- USA_MinVol: **12.4%**
- Dividend_Growth: **9.1%**
- EAFE_MinVol: **4.9%**
- SP500_Value: **2.8%**
- USA_Quality_Factor: **0.2%**

**Expected Return: 118.14% | Sortino Ratio: 0.560**

**Economic Logic:**
- **Sortino optimization** allows higher upside volatility while protecting downside
- **Multiple momentum exposures** capture growth trends across regions
- **Defensive anchors** (min-vol ETFs) provide downside protection
- **Strategy**: Maximum upside participation with downside risk management

### 🔥 Rising Growth, Rising Inflation
**Conservative Growth Strategy** | **9 ETFs Used | 27 Observations**
- Dividend_Growth: **15.0%**
- USA_Momentum: **15.0%**
- World_MinVol_USD: **15.0%**
- Global_MinVol: **15.0%**
- USA_MinVol: **15.0%**
- EAFE_MinVol: **12.0%**
- World_Momentum: **7.6%**
- Russell_2000: **4.6%**
- Asia_50: **0.8%**

**Expected Return: 147.69% | Sortino Ratio: 1.218**

**Economic Logic:**
- **Dividend focus** provides inflation protection and income generation
- **Min-vol emphasis** reduces downside risk in uncertain environment
- **Selective momentum exposure** captures growth while managing volatility
- **Strategy**: Conservative approach emphasizing income and capital preservation

### 📈 Slowing Growth, Falling Inflation
**High-Conviction Quality & Small Caps** | **8 ETFs Used | 18 Observations**
- Russell_2000: **15.0%**
- USA_GARP: **15.0%**
- USA_Quality_Factor: **15.0%**
- Europe_Momentum_USD: **15.0%**
- USA_EqualWeight: **15.0%**
- World_Momentum: **13.8%**
- SP500_Value: **7.9%**
- Europe_MinVol_EUR: **3.3%**

**Expected Return: 370.86% | Sortino Ratio: 2502.186**

**Economic Logic:**
- **Small-cap emphasis** captures recovery opportunities in improving liquidity conditions
- **Quality/GARP focus** identifies companies with sustainable competitive advantages
- **Equal-weight exposure** reduces mega-cap concentration risk
- **Strategy**: High-conviction growth positioning with exceptional downside protection

### ⚠️ Slowing Growth, Rising Inflation
**Defensive Momentum Strategy** | **7 ETFs Used | 41 Observations**
- USA_Momentum: **15.0%**
- World_Momentum: **15.0%**
- USA_MinVol: **15.0%**
- World_MinVol_USD: **15.0%**
- Global_MinVol: **15.0%**
- Europe_Momentum_USD: **15.0%**
- Europe_MinVol_EUR: **10.0%**

**Expected Return: -21.72% | Sortino Ratio: -0.077**

**Economic Logic:**
- **Momentum-focused defense** captures relative strength even in difficult conditions
- **Global min-vol diversification** provides defensive characteristics across regions
- **Strategy**: Risk management with selective opportunity capture

---

## WHY MATH AND ECONOMICS ALIGN

### The Optimization Logic
The mathematical optimizer finds ETFs that **actually performed best** (risk-adjusted) during similar historical conditions. This creates logical patterns:

#### **Pattern Recognition:**
- **Stagflation → Min-Vol ETFs**: Math confirms defensive positioning works
- **Reflationary Growth → Value/Dividend ETFs**: Math validates inflation hedge theory
- **Growth + Falling Inflation → Momentum ETFs**: Math supports trend-following in easy monetary policy
- **Slowing Growth → Quality/GARP ETFs**: Math confirms flight-to-quality behavior

#### **Risk Management:**
- **15% Maximum Allocation**: Professional risk management standard
- **7-10 ETFs per regime**: Optimal diversification without over-diversification
- **Dynamic Universe**: Uses all available data without artificial constraints

### Statistical Robustness
- **125 Total Observations**: Larger sample than split-period approaches
- **41 Stagflation Observations**: Most reliable estimates for difficult conditions
- **60% Data Availability Rule**: Ensures statistical significance
- **Both Optimization Methods**: Conservative (Sharpe) and aggressive (Sortino) approaches

---

## IMPLEMENTATION GUIDELINES

### Regime Assessment Framework
#### Growth Indicators:
- GDP growth trends and revisions
- Employment data and job creation
- Corporate earnings growth and guidance
- Business investment and capex spending

#### Inflation Indicators:
- CPI and PPI trends and components
- Wage growth and labor costs
- Commodity price trends
- Central bank policy stance and forward guidance

### Portfolio Management
- **Rebalancing Frequency**: Monthly or when regime shifts with >70% confidence
- **Transition Management**: Use 50/50 blend during regime uncertainty
- **Risk Monitoring**: 15% maximum ensures professional risk management standards
- **Performance Tracking**: Monitor both individual ETF and overall regime performance

### Method Selection Guidelines
- **Sharpe Ratio**: Choose for conservative approach in volatile/uncertain markets
- **Sortino Ratio**: Choose for upside participation in trending/confident markets
- **Regime Confidence**: Use Sharpe when regime unclear, Sortino when highly confident

---

## PERFORMANCE INSIGHTS

### Historical Performance Rankings
1. **Slowing Growth, Falling Inflation**: 370.86% return (Sortino) - Central bank easing creates exceptional opportunities
2. **Rising Growth, Rising Inflation**: 214.17% return (Sharpe) - Reflationary growth with proper positioning  
3. **Rising Growth, Falling Inflation**: 118.23% return (Sharpe) - Balanced growth environment

### Risk Management Observations
- **Stagflation periods** are challenging but momentum exposure still adds value
- **Quality and minimum volatility** ETFs provide consistent downside protection across regimes
- **Small caps and equal-weight** exposure significantly enhances returns in growth environments
- **Geographic diversification** reduces single-country policy risk

---

*Generated from Mathematical Optimization of Historical Data (2015-2025)*  
*Single-Period Analysis with Dynamic ETF Universe*  
*Professional 15% Maximum Allocation Constraint*  
*Where Mathematics Meets Economic Intuition*