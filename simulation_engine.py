"""
Simulation Engine for UIP + PPP Exchange Rate Model
Backend logic for exchange rate simulations based on Uncovered Interest Parity and Purchasing Power Parity
"""

import numpy as np
import pandas as pd
from scipy.stats import skewnorm


class ExchangeRateSimulator:
    """Main simulation engine for UIP + PPP exchange rate modeling"""
    
    def __init__(self):
        self.results = None
        self.distributions = {}
        
    def simulate_exchange_rate_uip_ppp(self, S_t, theta, n_sim,
                                      i_dom_range, i_for_range,
                                      pi_dom_range, pi_for_range,
                                      sesgo_tasa_dom=False, skew_params=None):
        """
        Simulate exchange rate changes using UIP + PPP model
        
        Parameters:
        -----------
        S_t : float
            Current spot exchange rate
        theta : float
            Weight between UIP and PPP (0-1)
        n_sim : int
            Number of simulations
        i_dom_range : tuple
            Range for domestic interest rate (min, max)
        i_for_range : tuple
            Range for foreign interest rate (min, max)
        pi_dom_range : tuple
            Range for domestic inflation (min, max)
        pi_for_range : tuple
            Range for foreign inflation (min, max)
        sesgo_tasa_dom : bool
            Whether to use skewed distribution for domestic rate
        skew_params : dict
            Parameters for skewed normal distribution
            
        Returns:
        --------
        numpy.ndarray
            Simulated exchange rates
        """
        # Generate random variables
        i_for = np.random.uniform(*i_for_range, n_sim)
        pi_dom = np.random.uniform(*pi_dom_range, n_sim)
        pi_for = np.random.uniform(*pi_for_range, n_sim)

        # Generate domestic interest rate
        if sesgo_tasa_dom:
            if skew_params is None:
                skew_params = {'loc': np.mean(i_dom_range), 'scale': 0.01, 'skew': 5}
            i_dom = skewnorm.rvs(
                a=skew_params['skew'],
                loc=skew_params['loc'],
                scale=skew_params['scale'],
                size=n_sim
            )
        else:
            i_dom = np.random.uniform(*i_dom_range, n_sim)

        # Calculate exchange rate change using UIP + PPP
        delta_e = theta * (i_dom - i_for) + (1 - theta) * (pi_dom - pi_for)
        return S_t * (1 + delta_e)
    
    def simulate_news_impact(self, S_t, theta, n_sim,
                            i_dom_range, i_for_range,
                            pi_dom_range, pi_for_range,
                            sesgo_tasa_dom=False, skew_params=None):
        """
        Simulate impact of different news scenarios on exchange rate
        
        Parameters:
        -----------
        Same as simulate_exchange_rate_uip_ppp
        
        Returns:
        --------
        tuple
            (DataFrame with results, dict with distributions)
        """
        scenarios = {
            'Normal': {},
            'Subida tasas BanRep': {'i_dom_shift': 0.015},
            'Desanclaje inflacionario': {'pi_dom_shift': 0.02},
            'Choque externo': {'i_for_shift': -0.01, 'pi_for_shift': -0.005},
        }

        results = []
        distributions = {}
        
        for name, shifts in scenarios.items():
            # Adjust ranges based on scenario shifts
            i_dom_r = (i_dom_range[0] + shifts.get('i_dom_shift', 0),
                       i_dom_range[1] + shifts.get('i_dom_shift', 0))
            i_for_r = (i_for_range[0] + shifts.get('i_for_shift', 0),
                       i_for_range[1] + shifts.get('i_for_shift', 0))
            pi_dom_r = (pi_dom_range[0] + shifts.get('pi_dom_shift', 0),
                        pi_dom_range[1] + shifts.get('pi_dom_shift', 0))
            pi_for_r = (pi_for_range[0] + shifts.get('pi_for_shift', 0),
                        pi_for_range[1] + shifts.get('pi_for_shift', 0))

            # Run simulation for this scenario
            sims = self.simulate_exchange_rate_uip_ppp(
                S_t, theta, n_sim,
                i_dom_r, i_for_r,
                pi_dom_r, pi_for_r,
                sesgo_tasa_dom, skew_params
            )

            # Store results
            distributions[name] = sims
            results.append({
                'Escenario': name,
                'Media': np.mean(sims),
                'P5': np.percentile(sims, 5),
                'P95': np.percentile(sims, 95),
                'Std': np.std(sims),
                'Min': np.min(sims),
                'Max': np.max(sims)
            })

        self.results = pd.DataFrame(results)
        self.distributions = distributions
        
        return self.results, self.distributions
    
    def get_scenario_data(self, scenario_name):
        """Get distribution data for a specific scenario"""
        return self.distributions.get(scenario_name, [])
    
    def get_summary_stats(self):
        """Get summary statistics for all scenarios"""
        return self.results
    
    def calculate_confidence_intervals(self, confidence_level=0.95):
        """Calculate confidence intervals for all scenarios"""
        if self.results is None:
            return None
            
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        intervals = []
        for scenario in self.results['Escenario']:
            data = self.distributions[scenario]
            lower = np.percentile(data, lower_percentile)
            upper = np.percentile(data, upper_percentile)
            intervals.append({
                'Escenario': scenario,
                f'CI_{int(confidence_level*100)}_lower': lower,
                f'CI_{int(confidence_level*100)}_upper': upper
            })
        
        return pd.DataFrame(intervals)
    
    def get_scenario_summary(self, scenario_name, S_t, i_dom, i_for, plazo_dias=180, base_anual=360):
        """
        Get comprehensive summary for a specific scenario including forward rates and VaR
        
        Parameters:
        - scenario_name: Name of the scenario
        - S_t: Current spot exchange rate
        - i_dom: Domestic interest rate
        - i_for: Foreign interest rate
        - plazo_dias: Forward period in days
        - base_anual: Annual basis for calculations
        
        Returns:
        - Dictionary with comprehensive statistics
        """
        if scenario_name not in self.distributions:
            return None
            
        datos = self.distributions[scenario_name]
        return calcular_resumen_escenario(datos, S_t, i_dom, i_for, plazo_dias, base_anual)


# Utility functions for data analysis
def calculate_var(data, confidence_level=0.95):
    """Calculate Value at Risk"""
    return np.percentile(data, (1 - confidence_level) * 100)

def calculate_expected_shortfall(data, confidence_level=0.95):
    """Calculate Expected Shortfall (Conditional VaR)"""
    var = calculate_var(data, confidence_level)
    return np.mean(data[data <= var])

def analyze_tail_risk(distributions, confidence_level=0.95):
    """Analyze tail risk across all scenarios"""
    tail_analysis = []
    
    for scenario, data in distributions.items():
        var = calculate_var(data, confidence_level)
        es = calculate_expected_shortfall(data, confidence_level)
        
        tail_analysis.append({
            'Escenario': scenario,
            'VaR': var,
            'Expected_Shortfall': es,
            'Tail_Probability': (1 - confidence_level)
        })
    
    return pd.DataFrame(tail_analysis)

def calcular_forward_cip(S_t, i_dom, i_for, plazo_dias, base_anual=360):
    """
    Calcula el tipo de cambio forward implícito usando paridad cubierta de tasas de interés (CIP).

    Parámetros:
    - S_t: Tipo de cambio spot actual (ej. COP/USD).
    - i_dom: Tasa de interés doméstica nominal anual (ej. 0.095 para 9.5%).
    - i_for: Tasa de interés extranjera nominal anual.
    - plazo_dias: Plazo del forward en días (ej. 180 para 6 meses).
    - base_anual: Base de cálculo (360 o 365 según convención).

    Retorna:
    - Tipo de cambio forward implícito.
    """
    n = plazo_dias / base_anual  # fracción del año
    F_tT = S_t * ((1 + i_dom) / (1 + i_for))**n
    return F_tT

def calcular_resumen_escenario(datos, S_t, i_dom, i_for, plazo_dias=180, base_anual=360):
    """
    Calcula un resumen completo de estadísticas para un escenario.
    
    Parámetros:
    - datos: Array con los datos simulados del tipo de cambio
    - S_t: Tipo de cambio spot actual
    - i_dom: Tasa de interés doméstica
    - i_for: Tasa de interés extranjera
    - plazo_dias: Plazo para forward (días)
    - base_anual: Base de cálculo para forward
    
    Retorna:
    - Diccionario con todas las estadísticas
    """
    # Estadísticas básicas
    media = np.mean(datos)
    p1 = np.percentile(datos, 1)
    p5 = np.percentile(datos, 5)
    p50 = np.percentile(datos, 50)
    p95 = np.percentile(datos, 95)
    p99 = np.percentile(datos, 99)
    
    # VaR en COP (asumiendo 1 USD de exposición)
    var_5pct_cop = p5  # P5 ya está en COP/USD
    var_1pct_cop = p1  # P1 ya está en COP/USD
    
    # Forward implícito
    forward_implicito = calcular_forward_cip(S_t, i_dom, i_for, plazo_dias, base_anual)
    
    return {
        'Media': media,
        'P1': p1,
        'P5': p5,
        'P50': p50,
        'P95': p95,
        'P99': p99,
        'VaR_5pct_COP': var_5pct_cop,
        'VaR_1pct_COP': var_1pct_cop,
        'Forward_implicito': forward_implicito
    } 