import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ETFSortinoOptimizer:
    """
    ETF Portfolio Optimizer using Sortino Ratio with rolling windows
    """
    
    def __init__(self, data_file, max_weight=0.25, window_months=24, rebalance_freq=3):
        """
        Initialize the optimizer
        
        Parameters:
        - data_file: path to CSV file with ETF returns
        - max_weight: maximum allocation per ETF (default 25%)
        - window_months: rolling window size in months (default 24)
        - rebalance_freq: rebalancing frequency in months (default 3)
        """
        self.max_weight = max_weight
        self.window_months = window_months
        self.rebalance_freq = rebalance_freq
        self.data = None
        self.etf_names = None
        self.results = {}
        
        # Load and clean data
        self._load_data(data_file)
        self._prepare_data()
        
    def _load_data(self, data_file):
        """Load ETF data from CSV and prepare USD-only dataset"""
        print("Loading ETF data...")
        raw_data = pd.read_csv(data_file)
        
        # Clean column names by stripping spaces
        raw_data.columns = raw_data.columns.str.strip()
        
        # Convert date column
        raw_data['Date'] = pd.to_datetime(raw_data['Date'], format='%d-%m-%Y')
        raw_data.set_index('Date', inplace=True)
        
        # Define EUR and USD versions of the European ETF
        eur_etf_column = 'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-EUR-Acc'
        usd_etf_column = 'Edge-MSCI-Europe-Momentum-Factor-UCITS-ETF-USD-Converted'
        
        # Get all ETF columns except the EUR version
        all_etf_columns = [col for col in raw_data.columns if col != 'Date']
        etf_columns_usd = [col for col in all_etf_columns if col != eur_etf_column]
        
        # Select only the USD columns
        self.data = raw_data[etf_columns_usd].copy()
        
        # Convert all columns to numeric, handling any non-numeric values
        for col in self.data.columns:
            self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
        
        # Get ETF names (all columns)
        self.etf_names = list(self.data.columns)
        
        print(f"Loaded {len(self.etf_names)} ETFs (USD terms):")
        for etf in self.etf_names:
            if 'USD-Converted' in etf:
                print(f"  ✓ {etf} (EUR ETF converted to USD)")
            else:
                print(f"  • {etf}")
        
    def _prepare_data(self):
        """Clean data and filter from Feb 2020 onwards"""
        print("\nPreparing data...")
        
        # Filter from Feb 2020 where all ETFs have data
        start_date = '2020-02-29'
        self.data = self.data[self.data.index >= start_date]
        
        # Remove rows where any ETF has missing data
        initial_rows = len(self.data)
        self.data = self.data.dropna()
        final_rows = len(self.data)
        
        if initial_rows != final_rows:
            print(f"Removed {initial_rows - final_rows} rows with missing data")
        
        print(f"Clean dataset: {len(self.data)} months from {self.data.index[0].strftime('%Y-%m-%d')} to {self.data.index[-1].strftime('%Y-%m-%d')}")
        print(f"ETFs included: {len(self.etf_names)}")
        
        # Show data availability summary
        print(f"\nData availability per ETF:")
        for etf in self.etf_names:
            non_null_count = self.data[etf].notna().sum()
            print(f"  {etf}: {non_null_count}/{len(self.data)} months ({non_null_count/len(self.data)*100:.1f}%)")
        
    def calculate_sortino_ratio(self, returns, target_return=0):
        """
        Calculate Sortino ratio for a return series
        
        Parameters:
        - returns: pandas Series of returns
        - target_return: target return (default 0)
        
        Returns:
        - sortino_ratio: float
        """
        excess_returns = returns - target_return
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return np.inf  # No downside risk
        
        downside_deviation = np.sqrt(np.mean(downside_returns ** 2))
        
        if downside_deviation == 0:
            return np.inf
        
        return np.mean(excess_returns) / downside_deviation
    
    def calculate_portfolio_sortino(self, weights, returns_matrix):
        """
        Calculate portfolio Sortino ratio given weights and returns
        
        Parameters:
        - weights: array of portfolio weights
        - returns_matrix: DataFrame of ETF returns
        
        Returns:
        - portfolio_sortino: float
        """
        portfolio_returns = np.dot(returns_matrix, weights)
        return self.calculate_sortino_ratio(pd.Series(portfolio_returns))
    
    def optimize_portfolio(self, returns_window):
        """
        Optimize portfolio weights to maximize Sortino ratio
        
        Parameters:
        - returns_window: DataFrame with ETF returns for the optimization window
        
        Returns:
        - optimal_weights: array of optimized weights
        - sortino_ratio: achieved Sortino ratio
        """
        n_assets = len(self.etf_names)
        
        # Objective function: minimize negative Sortino ratio
        def objective(weights):
            return -self.calculate_portfolio_sortino(weights, returns_window.values)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # weights sum to 1
        ]
        
        # Bounds: 0% to max_weight for each ETF
        bounds = [(0, self.max_weight) for _ in range(n_assets)]
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if result.success:
            optimal_weights = result.x
            portfolio_sortino = -result.fun
            return optimal_weights, portfolio_sortino
        else:
            print(f"Optimization failed: {result.message}")
            return initial_weights, self.calculate_portfolio_sortino(initial_weights, returns_window.values)
    
    def run_backtest(self):
        """
        Run the complete rolling window backtest
        """
        print(f"\nRunning backtest with {self.window_months}-month windows, rebalancing every {self.rebalance_freq} months...")
        
        # Initialize results storage
        self.results = {
            'rebalance_dates': [],
            'weights': [],
            'sortino_ratios': [],
            'portfolio_returns': [],
            'individual_returns': []
        }
        
        # Calculate rebalancing points
        total_months = len(self.data)
        rebalance_points = range(self.window_months, total_months, self.rebalance_freq)
        
        portfolio_value = 100  # Start with 100
        portfolio_series = [portfolio_value]
        
        current_weights = None
        
        for i, rebalance_idx in enumerate(rebalance_points):
            # Define the optimization window
            window_start = rebalance_idx - self.window_months
            window_end = rebalance_idx
            
            returns_window = self.data.iloc[window_start:window_end]
            rebalance_date = self.data.index[rebalance_idx]
            
            # Optimize portfolio
            optimal_weights, portfolio_sortino = self.optimize_portfolio(returns_window)
            
            # Store results
            self.results['rebalance_dates'].append(rebalance_date)
            self.results['weights'].append(optimal_weights.copy())
            self.results['sortino_ratios'].append(portfolio_sortino)
            
            # Calculate portfolio performance until next rebalance
            if i < len(rebalance_points) - 1:
                next_rebalance_idx = rebalance_points[i + 1]
                performance_period = self.data.iloc[rebalance_idx:next_rebalance_idx]
            else:
                # Last period: until end of data
                performance_period = self.data.iloc[rebalance_idx:]
            
            # Calculate portfolio returns for this period
            period_portfolio_returns = np.dot(performance_period.values, optimal_weights)
            self.results['portfolio_returns'].extend(period_portfolio_returns.tolist())
            self.results['individual_returns'].extend(performance_period.values.tolist())
            
            # Update portfolio value
            for monthly_return in period_portfolio_returns:
                portfolio_value *= (1 + monthly_return / 100)
                portfolio_series.append(portfolio_value)
            
            current_weights = optimal_weights
            
            # Show top allocation with ETF name
            top_etf_idx = np.argmax(optimal_weights)
            top_etf_name = self.etf_names[top_etf_idx]
            top_allocation = optimal_weights[top_etf_idx] * 100
            
            print(f"Rebalance {i+1}: {rebalance_date.strftime('%Y-%m-%d')} | Sortino: {portfolio_sortino:.3f} | Top: {top_etf_name.split('-')[0]} ({top_allocation:.1f}%)")
        
        # Create portfolio performance series
        performance_dates = self.data.index[self.window_months:]
        self.portfolio_performance = pd.Series(
            portfolio_series[1:len(performance_dates)+1], 
            index=performance_dates
        )
        
        print(f"\nBacktest completed! {len(self.results['rebalance_dates'])} rebalancing periods")
        
    def analyze_results(self):
        """
        Analyze and display backtest results
        """
        if not self.results:
            print("No results to analyze. Run backtest first.")
            return
        
        print("\n" + "="*60)
        print("USD PORTFOLIO PERFORMANCE ANALYSIS")
        print("="*60)
        
        # Overall performance metrics
        total_return = (self.portfolio_performance.iloc[-1] / self.portfolio_performance.iloc[0] - 1) * 100
        annualized_return = ((self.portfolio_performance.iloc[-1] / self.portfolio_performance.iloc[0]) ** (12 / len(self.portfolio_performance)) - 1) * 100
        
        # Calculate portfolio statistics
        portfolio_returns_series = pd.Series(self.results['portfolio_returns'])
        portfolio_volatility = portfolio_returns_series.std() * np.sqrt(12)  # Annualized
        portfolio_sortino = self.calculate_sortino_ratio(portfolio_returns_series) * np.sqrt(12)  # Annualized
        
        max_drawdown = self._calculate_max_drawdown(self.portfolio_performance)
        
        print(f"Total Return: {total_return:.2f}%")
        print(f"Annualized Return: {annualized_return:.2f}%")
        print(f"Annualized Volatility: {portfolio_volatility:.2f}%")
        print(f"Annualized Sortino Ratio: {portfolio_sortino:.3f}")
        print(f"Maximum Drawdown: {max_drawdown:.2f}%")
        
        # Average allocations
        print(f"\nAverage Allocations (USD Terms):")
        avg_weights = np.mean(self.results['weights'], axis=0)
        allocation_summary = []
        for i, etf in enumerate(self.etf_names):
            allocation_summary.append((etf, avg_weights[i]*100))
        
        # Sort by allocation descending
        allocation_summary.sort(key=lambda x: x[1], reverse=True)
        
        for etf, allocation in allocation_summary:
            if 'USD-Converted' in etf:
                print(f"  {etf}: {allocation:.1f}% ⭐ (EUR ETF in USD terms)")
            else:
                print(f"  {etf}: {allocation:.1f}%")
        
        # Best and worst periods
        best_period_idx = np.argmax(self.results['sortino_ratios'])
        worst_period_idx = np.argmin(self.results['sortino_ratios'])
        
        print(f"\nBest Sortino Period: {self.results['rebalance_dates'][best_period_idx].strftime('%Y-%m-%d')} (Sortino: {self.results['sortino_ratios'][best_period_idx]:.3f})")
        print(f"Worst Sortino Period: {self.results['rebalance_dates'][worst_period_idx].strftime('%Y-%m-%d')} (Sortino: {self.results['sortino_ratios'][worst_period_idx]:.3f})")
        
    def _calculate_max_drawdown(self, price_series):
        """Calculate maximum drawdown"""
        peak = price_series.expanding().max()
        drawdown = (price_series - peak) / peak * 100
        return drawdown.min()
    
    def plot_results(self, save_plots=False):
        """
        Create visualization plots
        """
        if not self.results:
            print("No results to plot. Run backtest first.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('USD ETF Portfolio Optimization Results', fontsize=16, fontweight='bold')
        
        # 1. Portfolio Performance
        axes[0, 0].plot(self.portfolio_performance.index, self.portfolio_performance.values, linewidth=2, color='blue')
        axes[0, 0].set_title('Portfolio Value Over Time (USD)')
        axes[0, 0].set_ylabel('Portfolio Value')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Rolling Sortino Ratios
        axes[0, 1].plot(self.results['rebalance_dates'], self.results['sortino_ratios'], 
                       marker='o', linewidth=2, markersize=6, color='green')
        axes[0, 1].set_title('Rolling Sortino Ratios')
        axes[0, 1].set_ylabel('Sortino Ratio')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Average Allocations
        avg_weights = np.mean(self.results['weights'], axis=0) * 100
        
        # Create shorter labels for plotting
        short_labels = []
        colors = []
        for name in self.etf_names:
            if 'USD-Converted' in name:
                short_labels.append('Europe-USD*')
                colors.append('gold')  # Highlight the converted ETF
            else:
                short_labels.append(name.split('-')[0] + '-' + name.split('-')[1] if len(name.split('-')) > 1 else name)
                colors.append('steelblue')
        
        bars = axes[1, 0].bar(range(len(self.etf_names)), avg_weights, color=colors)
        axes[1, 0].set_title('Average ETF Allocations (USD Terms)')
        axes[1, 0].set_ylabel('Allocation (%)')
        axes[1, 0].set_xticks(range(len(self.etf_names)))
        axes[1, 0].set_xticklabels(short_labels, rotation=45, ha='right')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, avg_weights):
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 4. Allocation Heatmap
        weights_matrix = np.array(self.results['weights']).T * 100
        im = axes[1, 1].imshow(weights_matrix, cmap='RdYlBu_r', aspect='auto')
        axes[1, 1].set_title('Allocation Heatmap Over Time')
        axes[1, 1].set_ylabel('ETFs')
        axes[1, 1].set_xlabel('Rebalancing Periods')
        axes[1, 1].set_yticks(range(len(self.etf_names)))
        axes[1, 1].set_yticklabels(short_labels)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=axes[1, 1])
        cbar.set_label('Allocation (%)', rotation=270, labelpad=15)
        
        plt.tight_layout()
        
        if save_plots:
            plt.savefig('usd_etf_optimization_results.png', dpi=300, bbox_inches='tight')
            print("Plots saved as 'usd_etf_optimization_results.png'")
        
        plt.show()

# Example usage
if __name__ == "__main__":
    # Initialize optimizer with USD-converted data
    optimizer = ETFSortinoOptimizer(
        data_file='consolidated_etf_performance_with_usd.csv',  # Updated filename
        max_weight=0.25,  # 25% maximum allocation
        window_months=24,  # 24-month rolling window
        rebalance_freq=3   # Quarterly rebalancing
    )
    
    # Run backtest
    optimizer.run_backtest()
    
    # Analyze results
    optimizer.analyze_results()
    
    # Create plots
    optimizer.plot_results(save_plots=True)
    
    # Access detailed results
    print(f"\nDetailed results available in optimizer.results dictionary")
    print(f"Portfolio performance series available in optimizer.portfolio_performance")
    print(f"\nNote: European ETF is now included in USD terms for proper currency comparison!")