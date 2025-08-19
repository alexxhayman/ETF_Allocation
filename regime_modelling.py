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
        print("Economic Regime Distribution:")
        print("=" * 40)
        for regime, count in regime_summary.items():
            pct = (count / len(df)) * 100
            print(f"{regime:<15}: {count:3d} periods ({pct:5.1f}%)")
        
        # Recent regime analysis
        recent_data = df.tail(6)  # Last 6 periods
        print(f"\nRecent Regime History (Last 6 periods):")
        print("=" * 50)
        for _, row in recent_data.iterrows():
            date_str = row['Date'].strftime('%Y-%m')
            print(f"{date_str}: {row['Regime']:<12} (GDP: {row['US_GDP_QoQ_Ann']:5.2f}%, PCE: {row['PCE_Prices']:5.2f}%)")
        
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def visualize_regimes(df, save_plot=True):
    """
    Create visualizations of the economic regimes with timeline bands and pie chart.
    """
    
    # Define colors for each regime
    regime_colors = {
        'Rising Growth, Falling Inflation': '#2E8B57',   # Sea Green (Best scenario)
        'Rising Growth, Rising Inflation': '#FF6B35',    # Orange Red (Reflationary)
        'Slowing Growth, Rising Inflation': '#8B0000',   # Dark Red (Stagflationary)  
        'Slowing Growth, Falling Inflation': '#4169E1',  # Royal Blue (Deflationary)
        'Insufficient Data': '#D3D3D3'  # Light Gray
    }
    
    # Create subplot layout - one large timeline and one pie chart
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[3, 1], width_ratios=[2, 2, 1])
    
    # Main timeline plot spanning top row
    ax_main = fig.add_subplot(gs[0, :])
    
    # Create regime timeline with bands
    df_clean = df[df['Regime'] != 'Insufficient Data'].copy()
    
    # Create a numeric mapping for regimes for plotting bands
    regime_mapping = {
        'Rising Growth, Falling Inflation': 3,
        'Rising Growth, Rising Inflation': 2, 
        'Slowing Growth, Rising Inflation': 1,
        'Slowing Growth, Falling Inflation': 0
    }
    
    df_clean['Regime_Numeric'] = df_clean['Regime'].map(regime_mapping)
    
    # Plot the regime bands
    for i, (date, regime) in enumerate(zip(df_clean['Date'], df_clean['Regime'])):
        if i < len(df_clean) - 1:
            next_date = df_clean.iloc[i + 1]['Date']
            y_pos = regime_mapping[regime]
            ax_main.barh(y_pos, (next_date - date).days, left=date, height=0.8, 
                        color=regime_colors[regime], alpha=0.7, edgecolor='white', linewidth=0.5)
    
    # Format the main timeline
    ax_main.set_ylim(-0.5, 3.5)
    ax_main.set_yticks([0, 1, 2, 3])
    ax_main.set_yticklabels([
        'Slowing Growth,\nFalling Inflation',
        'Slowing Growth,\nRising Inflation', 
        'Rising Growth,\nRising Inflation',
        'Rising Growth,\nFalling Inflation'
    ], fontsize=10)
    
    ax_main.set_xlabel('Year', fontsize=12)
    ax_main.set_title('Economic Regimes Timeline', fontsize=16, fontweight='bold', pad=20)
    ax_main.grid(True, axis='x', alpha=0.3)
    
    # Add regime color legend
    handles = [plt.Rectangle((0,0),1,1, color=regime_colors[regime], alpha=0.7) 
              for regime in ['Rising Growth, Falling Inflation', 'Rising Growth, Rising Inflation',
                           'Slowing Growth, Rising Inflation', 'Slowing Growth, Falling Inflation']]
    labels = ['Rising Growth, Falling Inflation', 'Rising Growth, Rising Inflation',
              'Slowing Growth, Rising Inflation', 'Slowing Growth, Falling Inflation']
    ax_main.legend(handles, labels, loc='upper right', bbox_to_anchor=(1, 1))
    
    # Economic indicators subplot
    ax_indicators = fig.add_subplot(gs[1, :2])
    
    # Plot GDP and PCE on same chart with dual y-axis
    ax_gdp = ax_indicators
    ax_pce = ax_indicators.twinx()
    
    # GDP line
    line1 = ax_gdp.plot(df_clean['Date'], df_clean['US_GDP_QoQ_Ann'], 
                       color='steelblue', linewidth=2, label='GDP Growth (QoQ Ann.)')
    ax_gdp.set_ylabel('GDP Growth (%)', color='steelblue', fontsize=10)
    ax_gdp.tick_params(axis='y', labelcolor='steelblue')
    
    # PCE line  
    line2 = ax_pce.plot(df_clean['Date'], df_clean['PCE_Prices'], 
                       color='orangered', linewidth=2, label='PCE Inflation')
    ax_pce.set_ylabel('PCE Inflation (%)', color='orangered', fontsize=10)
    ax_pce.tick_params(axis='y', labelcolor='orangered')
    
    ax_indicators.set_xlabel('Year', fontsize=10)
    ax_indicators.set_title('Economic Indicators', fontsize=12, fontweight='bold')
    ax_indicators.grid(True, alpha=0.3)
    
    # Combined legend for indicators
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax_indicators.legend(lines, labels, loc='upper left')
    
    # Pie chart for regime distribution
    ax_pie = fig.add_subplot(gs[1, 2])
    
    regime_counts = df_clean['Regime'].value_counts()
    colors = [regime_colors[regime] for regime in regime_counts.index]
    
    wedges, texts, autotexts = ax_pie.pie(regime_counts.values, labels=None, autopct='%1.1f%%',
                                         colors=colors, startangle=90)
    
    # Make percentage text smaller and white
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(8)
        autotext.set_fontweight('bold')
    
    ax_pie.set_title('Regime\nDistribution', fontsize=11, fontweight='bold')
    
    # Add pie chart legend with short names
    short_labels = ['Rise/Fall', 'Rise/Rise', 'Slow/Rise', 'Slow/Fall']
    ax_pie.legend(wedges, short_labels, title="Regimes", loc="center left", 
                 bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
    
    plt.tight_layout()
    
    if save_plot:
        plt.savefig('economic_regimes_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\nChart saved as 'economic_regimes_analysis.png'")
    
    # plt.show()  # Comment out for non-interactive execution

def export_regime_data(df, output_file='economic_regimes_classified.csv'):
    """
    Export the classified data to CSV for further analysis.
    """
    # Select relevant columns for export
    export_df = df[['Date', 'US_GDP_QoQ_Ann', 'PCE_Prices', 'GDP_Trend', 'PCE_Trend', 'Regime']].copy()
    export_df.to_csv(output_file, index=False)
    print(f"Classified data exported to: {output_file}")

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
    print(f"Dates and regimes exported to: {output_file}")
    
    # Show preview
    print(f"\nPreview of {output_file}:")
    print(simple_df.tail(10).to_string(index=False))

# Main execution
if __name__ == "__main__":
    # File paths
    input_csv = "economic_data_extracted.csv"  # From previous script
    
    print("Economic Regime Classification Model")
    print("=" * 50)
    
    # Classify regimes
    classified_data = classify_economic_regimes(input_csv, lookback_periods=3)
    
    if classified_data is not None:
        # Create visualizations
        visualize_regimes(classified_data)
        
        # Export results
        export_regime_data(classified_data)
        export_dates_regimes_only(classified_data)
        
        print(f"\nAnalysis complete! Use the classified data for:")
        print("   • Tactical asset allocation")
        print("   • Sector rotation strategies") 
        print("   • Risk management frameworks")
        print("   • Market timing models")