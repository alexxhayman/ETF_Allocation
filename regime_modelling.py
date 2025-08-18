import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def classify_economic_regimes(csv_file_path, lookback_periods=3):
    """
    Classify economic data into 4 regimes based on growth and inflation trends.
    
    Regimes:
    1. Rising Growth, Falling Inflation (Best for risk assets)
    2. Rising Growth, Rising Inflation (Reflationary environment) 
    3. Slowing Growth, Rising Inflation (Stagflationary pressures)
    4. Slowing Growth, Falling Inflation (Deflationary environment)
    
    Parameters:
    csv_file_path (str): Path to the CSV file with economic data
    lookback_periods (int): Number of periods to use for trend calculation
    """
    
    try:
        # Read the CSV data
        df = pd.read_csv(csv_file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        
        # Calculate rolling averages to smooth the data
        df['GDP_MA'] = df['US_GDP_QoQ_Ann'].rolling(window=lookback_periods, min_periods=1).mean()
        df['PCE_MA'] = df['PCE_Prices'].rolling(window=lookback_periods, min_periods=1).mean()
        
        # Calculate trends (change over lookback periods)
        df['GDP_Trend'] = df['GDP_MA'].diff(lookback_periods)
        df['PCE_Trend'] = df['PCE_MA'].diff(lookback_periods)
        
        # Classify regimes
        def classify_regime(gdp_trend, pce_trend):
            if pd.isna(gdp_trend) or pd.isna(pce_trend):
                return 'Insufficient Data'
            
            if gdp_trend >= 0 and pce_trend < 0:
                return 'Rising Growth, Falling Inflation'
            elif gdp_trend >= 0 and pce_trend >= 0:
                return 'Rising Growth, Rising Inflation'
            elif gdp_trend < 0 and pce_trend >= 0:
                return 'Slowing Growth, Rising Inflation'
            else:
                return 'Slowing Growth, Falling Inflation'
        
        df['Regime'] = df.apply(lambda row: classify_regime(row['GDP_Trend'], row['PCE_Trend']), axis=1)
        
        # Create regime summary
        regime_summary = df['Regime'].value_counts()
        print("📊 Economic Regime Distribution:")
        print("=" * 40)
        for regime, count in regime_summary.items():
            pct = (count / len(df)) * 100
            print(f"{regime:<15}: {count:3d} periods ({pct:5.1f}%)")
        
        # Recent regime analysis
        recent_data = df.tail(6)  # Last 6 periods
        print(f"\n🔍 Recent Regime History (Last 6 periods):")
        print("=" * 50)
        for _, row in recent_data.iterrows():
            date_str = row['Date'].strftime('%Y-%m')
            print(f"{date_str}: {row['Regime']:<12} (GDP: {row['US_GDP_QoQ_Ann']:5.2f}%, PCE: {row['PCE_Prices']:5.2f}%)")
        
        return df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def visualize_regimes(df, save_plot=True):
    """
    Create visualizations of the economic regimes.
    """
    
    # Define colors for each regime
    regime_colors = {
        'Rising Growth, Falling Inflation': '#2E8B57',   # Sea Green (Best scenario)
        'Rising Growth, Rising Inflation': '#FF6B35',    # Orange Red (Reflationary)
        'Slowing Growth, Rising Inflation': '#8B0000',   # Dark Red (Stagflationary)  
        'Slowing Growth, Falling Inflation': '#4169E1',  # Royal Blue (Deflationary)
        'Insufficient Data': '#D3D3D3'  # Light Gray
    }
    
    # Create subplot layout
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Economic Regime Analysis', fontsize=16, fontweight='bold')
    
    # 1. Time series with regime coloring
    for regime in df['Regime'].unique():
        if regime != 'Insufficient Data':
            regime_data = df[df['Regime'] == regime]
            ax1.scatter(regime_data['Date'], regime_data['US_GDP_QoQ_Ann'], 
                       c=regime_colors[regime], label=regime, alpha=0.7, s=50)
    
    ax1.set_title('GDP Growth by Regime Over Time')
    ax1.set_ylabel('GDP QoQ Annualized (%)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Inflation by regime
    for regime in df['Regime'].unique():
        if regime != 'Insufficient Data':
            regime_data = df[df['Regime'] == regime]
            ax2.scatter(regime_data['Date'], regime_data['PCE_Prices'], 
                       c=regime_colors[regime], label=regime, alpha=0.7, s=50)
    
    ax2.set_title('Inflation by Regime Over Time')
    ax2.set_ylabel('PCE Prices (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Regime scatter plot
    for regime in df['Regime'].unique():
        if regime != 'Insufficient Data':
            regime_data = df[df['Regime'] == regime]
            ax3.scatter(regime_data['US_GDP_QoQ_Ann'], regime_data['PCE_Prices'],
                       c=regime_colors[regime], label=regime, alpha=0.7, s=60)
    
    ax3.axhline(y=df['PCE_Prices'].median(), color='gray', linestyle='--', alpha=0.5)
    ax3.axvline(x=df['US_GDP_QoQ_Ann'].median(), color='gray', linestyle='--', alpha=0.5)
    ax3.set_xlabel('GDP QoQ Annualized (%)')
    ax3.set_ylabel('PCE Prices (%)')
    ax3.set_title('Growth vs Inflation Regime Map')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Regime duration analysis
    regime_counts = df['Regime'].value_counts()
    valid_regimes = regime_counts[regime_counts.index != 'Insufficient Data']
    colors = [regime_colors[regime] for regime in valid_regimes.index]
    
    ax4.pie(valid_regimes.values, labels=valid_regimes.index, autopct='%1.1f%%',
           colors=colors, startangle=90)
    ax4.set_title('Regime Distribution')
    
    plt.tight_layout()
    
    if save_plot:
        plt.savefig('economic_regimes_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\n📈 Chart saved as 'economic_regimes_analysis.png'")
    
    plt.show()

def export_regime_data(df, output_file='economic_regimes_classified.csv'):
    """
    Export the classified data to CSV for further analysis.
    """
    # Select relevant columns for export
    export_df = df[['Date', 'US_GDP_QoQ_Ann', 'PCE_Prices', 'GDP_Trend', 'PCE_Trend', 'Regime']].copy()
    export_df.to_csv(output_file, index=False)
    print(f"💾 Classified data exported to: {output_file}")

def export_dates_regimes_only(df, output_file='dates_and_regimes.csv'):
    """
    Export a simplified CSV with just dates and regimes.
    """
    # Create simplified dataframe with just dates and regimes
    simple_df = df[['Date', 'Regime']].copy()
    
    # Format date for readability
    simple_df['Date'] = simple_df['Date'].dt.strftime('%Y-%m-%d')
    
    # Remove rows with insufficient data
    simple_df = simple_df[simple_df['Regime'] != 'Insufficient Data']
    
    simple_df.to_csv(output_file, index=False)
    print(f"📅 Dates and regimes exported to: {output_file}")
    
    # Show preview
    print(f"\n📋 Preview of {output_file}:")
    print(simple_df.tail(10).to_string(index=False))

# Main execution
if __name__ == "__main__":
    # File paths
    input_csv = "economic_data_extracted.csv"  # From previous script
    
    print("🏛️  Economic Regime Classification Model")
    print("=" * 50)
    
    # Classify regimes
    classified_data = classify_economic_regimes(input_csv, lookback_periods=3)
    
    if classified_data is not None:
        # Create visualizations
        visualize_regimes(classified_data)
        
        # Export results
        export_regime_data(classified_data)
        export_dates_regimes_only(classified_data)
        
        print(f"\n✅ Analysis complete! Use the classified data for:")
        print("   • Tactical asset allocation")
        print("   • Sector rotation strategies") 
        print("   • Risk management frameworks")
        print("   • Market timing models")