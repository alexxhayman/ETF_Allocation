# ETF Regime-Based Allocation Strategy
**Tactical Asset Allocation for Economic Regimes**

---

## Executive Summary

This report presents optimized ETF allocations for different economic regimes, designed to maximize risk-adjusted returns while limiting individual ETF exposure to 25% maximum. The analysis covers two periods: Pre-GARP (2015-2020) and Post-GARP (2020-2025), providing 8 distinct tactical allocation strategies.

---

## Key Constraints Applied
- **Maximum allocation per ETF: 25%**
- **Minimum required observations: 5 months per regime**
- **Optimization target: Maximize Sharpe ratio**

---

## 🎯 **TACTICAL ALLOCATION GUIDE**

### **PRE-GARP PERIOD (2015-2020)**

#### **1. Rising Growth, Falling Inflation** ⭐ *Strong Performance*
**Expected Return:** 122.7% | **Sharpe Ratio:** 0.79

| ETF | Allocation | Strategy |
|-----|-----------|----------|
| EAFE Min Vol | 25.0% | International defensive |
| USA Min Vol | 25.0% | US defensive |
| Europe Momentum EUR | 23.6% | European growth |
| USA Momentum | 13.4% | US growth |
| Europe Momentum USD | 13.0% | European growth (USD) |

**Portfolio Style:** Balanced momentum + defensive

---

#### **2. Slowing Growth, Rising Inflation** 
**Expected Return:** 85.0% | **Sharpe Ratio:** 0.36

| ETF | Allocation | Strategy |
|-----|-----------|----------|
| USA Momentum | 25.0% | US growth |
| World Momentum | 25.0% | Global growth |
| USA Min Vol | 25.0% | US defensive |
| EAFE Min Vol | 25.0% | International defensive |

**Portfolio Style:** Equal-weight momentum + defensive

---

#### **3. Slowing Growth, Falling Inflation** ⚠️ *Challenging Environment*
**Expected Return:** 57.5% | **Sharpe Ratio:** 0.12

| ETF | Allocation | Strategy |
|-----|-----------|----------|
| SP500 Value | 25.0% | US value |
| USA Min Vol | 25.0% | US defensive |
| Europe Momentum EUR | 25.0% | European growth |
| Dividend Growth | 25.0% | Income focus |

**Portfolio Style:** Defensive with value tilt

---

#### **4. Rising Growth, Rising Inflation** ⭐ *Excellent Performance*
**Expected Return:** 257.8% | **Sharpe Ratio:** 0.88

| ETF | Allocation | Strategy |
|-----|-----------|----------|
| Dividend Growth | 25.0% | Income focus |
| USA Momentum | 25.0% | US growth |
| SP500 Value | 25.0% | US value |
| Asia 50 | 25.0% | Asian markets |

**Portfolio Style:** Growth + value with inflation protection

---

### **POST-GARP PERIOD (2020-2025)**

#### **5. Rising Growth, Falling Inflation**
**Expected Return:** 126.7% | **Sharpe Ratio:** 0.28

| ETF | Allocation | Strategy |
|-----|-----------|----------|
| USA Momentum | 25.0% | US growth |
| USA Min Vol | 25.0% | US defensive |
| EAFE Min Vol | 19.6% | International defensive |
| SP500 Value | 16.8% | US value |
| Asia 50 | 11.3% | Asian markets |
| World Momentum | 2.3% | Global growth |

**Portfolio Style:** Diversified with US tilt

---

#### **6. Slowing Growth, Rising Inflation** ❌ *Avoid This Regime*
**Expected Return:** -89.3% | **Sharpe Ratio:** -0.21

| ETF | Allocation | Strategy |
|-----|-----------|----------|
| Asia 50 | 25.0% | Asian markets |
| Europe Momentum EUR | 25.0% | European growth |
| Europe Momentum USD | 25.0% | European growth (USD) |
| Dividend Growth | 25.0% | Income focus |

**Portfolio Style:** International focus (negative returns expected)

---

#### **7. Slowing Growth, Falling Inflation** 🏆 *BEST PERFORMER*
**Expected Return:** 400.6% | **Sharpe Ratio:** 1.17

| ETF | Allocation | Strategy |
|-----|-----------|----------|
| Europe Momentum EUR | 25.0% | European growth |
| USA GARP | 25.0% | Quality growth |
| USA Momentum | 21.5% | US growth |
| Europe Momentum USD | 20.6% | European growth (USD) |
| World Momentum | 7.8% | Global growth |

**Portfolio Style:** Growth-focused with quality tilt

---

#### **8. Rising Growth, Rising Inflation**
**Expected Return:** 187.1% | **Sharpe Ratio:** 0.41

| ETF | Allocation | Strategy |
|-----|-----------|----------|
| Europe Momentum EUR | 25.0% | European growth |
| USA GARP | 25.0% | Quality growth |
| USA Min Vol | 25.0% | US defensive |
| Dividend Growth | 25.0% | Income focus |

**Portfolio Style:** Balanced growth + defensive

---

## 📊 **PERFORMANCE RANKING**

### **By Sharpe Ratio (Best to Worst):**
1. **Post-GARP Slowing Growth, Falling Inflation** - 1.17 🏆
2. **Pre-GARP Rising Growth, Rising Inflation** - 0.88
3. **Pre-GARP Rising Growth, Falling Inflation** - 0.79
4. **Post-GARP Rising Growth, Rising Inflation** - 0.41
5. **Pre-GARP Slowing Growth, Rising Inflation** - 0.36
6. **Post-GARP Rising Growth, Falling Inflation** - 0.28
7. **Pre-GARP Slowing Growth, Falling Inflation** - 0.12
8. **Post-GARP Slowing Growth, Rising Inflation** - (-0.21) ❌

---

## 🎯 **IMPLEMENTATION RECOMMENDATIONS**

### **High Priority Regimes (Sharpe > 0.5):**
- **Slowing Growth, Falling Inflation (Post-GARP)** - Aggressive allocation
- **Rising Growth, Rising Inflation (Pre-GARP)** - Strong momentum strategy
- **Rising Growth, Falling Inflation (Pre-GARP)** - Balanced approach

### **Moderate Priority Regimes (Sharpe 0.2-0.5):**
- **Rising Growth, Rising Inflation (Post-GARP)** - Defensive growth
- **Slowing Growth, Rising Inflation (Pre-GARP)** - Cautious momentum
- **Rising Growth, Falling Inflation (Post-GARP)** - Diversified approach

### **Low Priority/Avoid (Sharpe < 0.2):**
- **Slowing Growth, Falling Inflation (Pre-GARP)** - Minimal allocation
- **Slowing Growth, Rising Inflation (Post-GARP)** - Consider cash/bonds

---

## 🔧 **OPERATIONAL NOTES**

### **Key ETFs by Usage:**
- **USA Min Vol**: Appears in 6/8 allocations - Core defensive holding
- **USA Momentum**: Appears in 6/8 allocations - Core growth holding  
- **Europe Momentum EUR**: Appears in 6/8 allocations - Key international exposure
- **USA GARP**: Only available post-2020, but dominant when applicable

### **Rebalancing Triggers:**
- Monitor economic regime changes monthly
- Rebalance when regime shifts are confirmed
- Maintain 25% maximum allocation discipline
- Review allocations quarterly for drift

---

**Report Generated:** Based on historical data analysis (2000-2025)  
**Methodology:** Mean-variance optimization with Sharpe ratio maximization  
**Constraints:** Maximum 25% per ETF allocation