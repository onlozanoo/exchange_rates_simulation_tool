# 📊 UIP + PPP Exchange Rate Simulation Tool

A comprehensive Python application for simulating exchange rate movements using Uncovered Interest Parity (UIP) and Purchasing Power Parity (PPP) models. This tool provides both backend simulation capabilities and a user-friendly GUI for analyzing different economic scenarios and their impact on exchange rates.

## 🎯 Project Overview

This project implements a hybrid UIP + PPP model for exchange rate forecasting and risk analysis. It allows users to:

- **Simulate exchange rate movements** under different economic scenarios
- **Analyze tail risk** using Value at Risk (VaR) and Expected Shortfall
- **Calculate forward rates** using Covered Interest Parity (CIP)
- **Visualize results** through interactive charts and comprehensive statistics
- **Test different scenarios** including central bank rate changes, inflation shocks, and external shocks

## 🏗️ Architecture

The project follows a clean **backend/frontend separation**:

### Backend (`simulation_engine.py`)
- **`ExchangeRateSimulator`** class: Main simulation engine
- **Core simulation methods**: UIP + PPP calculations
- **Risk analysis functions**: VaR, Expected Shortfall, tail risk analysis
- **Forward rate calculations**: CIP-based forward rate computation
- **Utility functions**: Statistical analysis and data processing

### Frontend (`main.py`)
- **Tkinter GUI**: User-friendly interface
- **Interactive visualizations**: Impact curves, distribution histograms
- **Real-time parameter updates**: Automatic recalculation on parameter changes
- **Multiple view modes**: Impact analysis, dispersion analysis, comprehensive summaries

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Dependencies
```bash
pip install numpy pandas matplotlib scipy tkinter
```

### Quick Start
1. Clone or download the project files
2. Ensure both `main.py` and `simulation_engine.py` are in the same directory
3. Run the application:
```bash
python main.py
```

## 🚀 How to Use

### 1. Basic Operation

1. **Launch the application**: Run `python main.py`
2. **Set parameters**: Adjust the input fields as needed:
   - `S_t (spot)`: Current exchange rate (default: 4000 COP/USD)
   - `theta`: Weight between UIP and PPP (default: 0.6)
   - `n_sim`: Number of simulations (default: 100,000)
   - Interest rate ranges (domestic and foreign)
   - Inflation ranges (domestic and foreign)
3. **Choose scenario**: Select from dropdown menu
4. **View results**: Click any visualization button

### 2. Parameter Explanation

#### Core Parameters
- **S_t**: Current spot exchange rate (COP/USD)
- **theta**: Weight between UIP and PPP theories (0-1)
  - θ = 1: Pure UIP (interest rate differentials only)
  - θ = 0: Pure PPP (inflation differentials only)
  - 0 < θ < 1: Hybrid model

#### Rate Ranges
- **i_dom**: Domestic interest rate range (e.g., 8-11%)
- **i_for**: Foreign interest rate range (e.g., 4.5-5.5%)
- **pi_dom**: Domestic inflation range (e.g., 7-9%)
- **pi_for**: Foreign inflation range (e.g., 2.5-3.5%)

### 3. Available Scenarios

1. **Normal**: Baseline scenario with no shocks
2. **Subida tasas BanRep**: Central bank rate increase (+1.5%)
3. **Desanclaje inflacionario**: Domestic inflation shock (+2%)
4. **Choque externo**: External shock (foreign rate -1%, inflation -0.5%)

### 4. Visualization Options

#### 📈 Impact Curve (`Ver curva impacto`)
- Shows mean exchange rate for each scenario
- Displays 5th and 95th percentile confidence intervals
- Compares relative impact of different shocks

#### 📊 Distribution Histogram (`Ver dispersión`)
- Histogram of simulated exchange rates for selected scenario
- Shows key percentiles (P1, P5, P50, P95, P99)
- Includes mean line for reference

#### 🎯 Comprehensive Summary (`Ver resumen completo`)
- Complete statistics for selected scenario
- Includes VaR calculations in COP
- Shows implied forward rate using CIP
- Formatted display with thousands separators

#### 💼 Forward Contract Evaluation (`Evaluar Forward`)
- **CIP Analysis**: Compares offered forward with Covered Interest Parity
- **UIP+PPP Analysis**: Evaluates against expected spot rate from simulation
- **Protection Assessment**: Determines if forward provides downside protection
- **Uncertainty Analysis**: Checks if forward reduces risk reasonably
- **Final Recommendation**: Clear accept/negotiate/reject decision
- **Comprehensive Report**: Detailed analysis with reasoning

### 5. Forward Evaluation Logic

The forward evaluation uses a sophisticated two-tier analysis:

#### **Tier 1: CIP (Covered Interest Parity)**
- Compares offered forward with theoretical CIP forward
- **✅ Favorable**: Forward ≤ CIP (fair or advantageous)
- **❌ Unfavorable**: Forward > CIP (potential overpricing)

#### **Tier 2: UIP+PPP Model (Expected Spot)**
- Uses simulation mean as expected future spot rate
- **Protection Analysis**:
  - ✅ Forward < expected spot = Provides protection
  - ❌ Forward ≥ expected spot = No protection
- **Uncertainty Analysis**:
  - ✅ Within P5-P95 = Reasonable uncertainty reduction
  - ⚠️ Above P95 = Likely overpaying
  - ✅ Below P5 = Very conservative

#### **Final Decision Logic**
**✅ ACCEPT** if at least one condition is met:
- Forward ≤ CIP (covered interest parity)
- Forward < expected spot (protection)

**⚠️ NEGOTIATE/REJECT** if:
- Forward > CIP AND Forward > expected spot

## 🔬 Technical Details

### Model Formula

The core simulation uses this hybrid UIP + PPP formula:

```
Δe = θ(i_dom - i_for) + (1-θ)(π_dom - π_for)
S_t+1 = S_t * (1 + Δe)
```

Where:
- `Δe`: Expected exchange rate change
- `θ`: Weight parameter (0-1)
- `i_dom, i_for`: Domestic and foreign interest rates
- `π_dom, π_for`: Domestic and foreign inflation rates
- `S_t`: Current spot rate

### Forward Rate Calculation

Forward rates are calculated using Covered Interest Parity:

```
F_tT = S_t * ((1 + i_dom) / (1 + i_for))^n
```

Where `n` is the time fraction (days/360 or days/365).

### Risk Metrics

- **VaR (Value at Risk)**: 1st and 5th percentiles
- **Expected Shortfall**: Average loss beyond VaR
- **Tail Risk Analysis**: Comprehensive risk assessment

## 📈 Example Output

### Comprehensive Summary Example
```
RESUMEN COMPLETO - NORMAL

Media: 4,248.51
P1: 4,201.00
P5: 4,212.54
P50: 4,246.93
P95: 4,289.92
P99: 4,309.93
VaR_5pct_COP: 4,212.54
VaR_1pct_COP: 4,201.00
Forward implícito: 4,171.10
```

### Forward Evaluation Example
```
EVALUACIÓN DE CONTRATO FORWARD
==================================================
ESCENARIO: Normal
Spot actual: 4,000.00 COP/USD
Forward ofrecido: 4,100.00 COP/USD

📊 ANÁLISIS CIP (PARIDAD CUBIERTA)
----------------------------------------
Forward CIP implícito: 4,171.10 COP/USD
❌ Forward > CIP: POSIBLE SOBREPRECIO
Diferencia: -71.10 COP/USD

📈 ANÁLISIS UIP + PPP (SPOT ESPERADO)
==================================================
Spot esperado (media): 4,248.51 COP/USD
P5: 4,212.54 COP/USD
P95: 4,289.92 COP/USD

✅ Forward < spot esperado: TE PROTEGE
✅ Dentro P5-P95: REDUCE INCERTIDUMBRE RAZONABLEMENTE
Diferencia vs spot esperado: -148.51 COP/USD

🎯 RECOMENDACIÓN FINAL
==============================

✅ ACEPTA EL CONTRATO

Razones:
• Forward < spot esperado (protección)
```

## 🛠️ Advanced Usage

### Using the Backend Directly

```python
from simulation_engine import ExchangeRateSimulator

# Create simulator instance
simulator = ExchangeRateSimulator()

# Run simulation
results, distributions = simulator.simulate_news_impact(
    S_t=4000, theta=0.6, n_sim=10000,
    i_dom_range=(0.08, 0.11),
    i_for_range=(0.045, 0.055),
    pi_dom_range=(0.07, 0.09),
    pi_for_range=(0.025, 0.035)
)

# Get specific scenario data
normal_data = simulator.get_scenario_data("Normal")

# Get comprehensive summary
summary = simulator.get_scenario_summary("Normal", 4000, 0.095, 0.05)
```

### Custom Scenarios

You can modify the scenarios in `simulation_engine.py`:

```python
scenarios = {
    'Custom Scenario': {
        'i_dom_shift': 0.02,    # +2% domestic rate
        'pi_for_shift': -0.01   # -1% foreign inflation
    }
}
```

## 🗺️ Project Roadmap

### ✅ Completed Features

#### Core Functionality
- [x] UIP + PPP hybrid model implementation
- [x] Monte Carlo simulation engine
- [x] Multiple economic scenarios
- [x] Skewed distribution support for domestic rates
- [x] Real-time parameter updates

#### Visualization
- [x] Impact curve charts with confidence intervals
- [x] Distribution histograms with percentiles
- [x] Comprehensive summary reports
- [x] Forward contract evaluation system

#### Risk Analysis
- [x] Value at Risk (VaR) calculations
- [x] Expected Shortfall analysis
- [x] Tail risk assessment
- [x] Forward rate calculations using CIP
- [x] Forward contract evaluation against CIP and UIP+PPP models

#### User Interface
- [x] Tkinter GUI with intuitive controls
- [x] Parameter change detection
- [x] View persistence (stays on current visualization)
- [x] Proper window closing handling
- [x] Forward price input with validation
- [x] Comprehensive evaluation reports

#### Code Quality
- [x] Backend/frontend separation
- [x] Comprehensive documentation
- [x] Error handling and validation
- [x] Clean code architecture

### 🚧 Future Enhancements

#### Advanced Modeling
- [ ] **GARCH models** for volatility clustering
- [ ] **Regime switching models** for different economic states
- [ ] **Machine learning integration** for parameter estimation
- [ ] **Stochastic volatility models** for more realistic dynamics

#### Enhanced Scenarios
- [ ] **Custom scenario builder** in GUI
- [ ] **Historical scenario analysis** using real data
- [ ] **Stress testing framework** for extreme scenarios
- [ ] **Correlation analysis** between variables

#### Risk Management
- [ ] **Portfolio VaR** calculations
- [ ] **Expected Shortfall** visualization
- [ ] **Risk decomposition** by factor
- [ ] **Backtesting framework** for model validation

#### Data Integration
- [ ] **Real-time data feeds** (Bloomberg, Reuters)
- [ ] **Historical data import** from CSV/Excel
- [ ] **Database integration** for storing results
- [ ] **API endpoints** for external access

#### User Interface Improvements
- [ ] **Web-based interface** (Flask/Django)
- [ ] **Interactive dashboards** (Plotly/Dash)
- [ ] **Export functionality** (PDF reports, Excel)
- [ ] **Multi-language support**

#### Performance & Scalability
- [ ] **Parallel processing** for large simulations
- [ ] **GPU acceleration** using CUDA
- [ ] **Cloud deployment** options
- [ ] **Caching mechanisms** for repeated calculations

#### Documentation & Training
- [ ] **Video tutorials** for new users
- [ ] **Advanced usage examples**
- [ ] **API documentation** for developers
- [ ] **Academic paper** on methodology

## 🤝 Contributing

We welcome contributions! Please feel free to:

1. **Report bugs** or suggest improvements
2. **Submit pull requests** with new features
3. **Improve documentation** or add examples
4. **Share use cases** and success stories

## 📚 References

### Academic Background
- **Uncovered Interest Parity (UIP)**: Theory of exchange rate determination based on interest rate differentials
- **Purchasing Power Parity (PPP)**: Theory linking exchange rates to inflation differentials
- **Covered Interest Parity (CIP)**: Risk-free arbitrage condition for forward rates

### Technical References
- **Monte Carlo Simulation**: Numerical method for risk analysis
- **Value at Risk (VaR)**: Standard risk metric in finance
- **Expected Shortfall**: Coherent risk measure beyond VaR

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the project repository
- Contact the development team
- Check the documentation for common solutions

---

**Built with ❤️ for financial analysis and risk management** 