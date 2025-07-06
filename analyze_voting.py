import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np

def read_voting_data(filename):
    """
    Read the voting data from the text file and convert to DataFrame
    """
    data = []
    
    def categorize_result(result):
        """
        Categorize voting results into 4 clear categories
        """
        result = result.strip().upper()
        if result in ['SI', 'SI +++']:
            return 'yes'
        elif result in ['NO', 'NO ---']:
            return 'no'
        elif result in ['ABST', 'ABSTENCIÓN']:
            return 'abs'
        else:
            return 'others'
    
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and line.startswith('[') and line.endswith(']'):
                # Remove brackets and split by comma
                content = line[1:-1]
                parts = [part.strip() for part in content.split(',')]
                
                if len(parts) >= 3:
                    team = parts[0]
                    # Name might contain commas, so join all middle parts
                    name = ', '.join(parts[1:-1])
                    raw_result = parts[-1]
                    result = categorize_result(raw_result)
                    
                    data.append({
                        'team': team,
                        'name': name,
                        'result': result
                    })
    
    return pd.DataFrame(data)

def create_charts(df):
    """
    Create two charts to visualize the voting data: pie chart and bar chart by teams with table
    """
    # Set up the plotting style
    plt.style.use('default')
    
    # Define consistent colors for each voting result
    result_colors = {
        'yes': '#2ecc71',    # green
        'no': '#e74c3c',     # red
        'abs': '#f39c12',    # orange
        'others': '#95a5a6'  # gray
    }
    
    # Create a figure with 3 subplots: pie chart, bar chart, and table
    fig = plt.figure(figsize=(20, 18))  # Even more height for maximum spacing
    gs = fig.add_gridspec(3, 2, height_ratios=[2, 2, 4], hspace=0.6, wspace=0.3)  # Much more space for table and maximum vertical spacing
    
    # Create subplots
    ax1 = fig.add_subplot(gs[:2, 0])  # Pie chart (spans 2 rows for bigger size)
    ax2 = fig.add_subplot(gs[:2, 1])  # Bar chart (spans 2 rows)
    ax3 = fig.add_subplot(gs[2, :])   # Table (spans full width)
    
    fig.suptitle('Congressional Voting Analysis', fontsize=18, fontweight='bold', y=0.97)
    
    # Chart 1: Pie chart for overall vote results
    result_counts = df['result'].value_counts()
    # Create color list in the same order as result_counts
    pie_colors = [result_colors[result] for result in result_counts.index]
    
    wedges, texts, autotexts = ax1.pie(result_counts.values, 
                                      labels=result_counts.index, 
                                      autopct='%1.1f%%', 
                                      startangle=90,
                                      colors=pie_colors)
    ax1.set_title('Overall Vote Results Distribution', fontsize=14, pad=20)
    
    # Make percentage text bold and larger
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    # Chart 2: Bar chart showing results by teams
    # Get top 10 teams by total representatives
    top_teams = df['team'].value_counts().head(10).index
    df_top_teams = df[df['team'].isin(top_teams)]
    
    # Create crosstab for top teams
    vote_by_team = pd.crosstab(df_top_teams['team'], df_top_teams['result'])
    
    # Ensure all result categories are present and in consistent order
    result_categories = ['yes', 'no', 'abs', 'others']
    for category in result_categories:
        if category not in vote_by_team.columns:
            vote_by_team[category] = 0
    
    # Reorder columns to match our consistent order
    vote_by_team = vote_by_team[result_categories]
    
    # Create color list for bar chart in the same order
    bar_colors = [result_colors[category] for category in result_categories]
    
    # Create stacked bar chart
    vote_by_team.plot(kind='bar', 
                     stacked=True, 
                     ax=ax2,
                     color=bar_colors,
                     width=0.8)
    
    ax2.set_title('Voting Results by Political Party (Top 10)', fontsize=14, pad=20)
    ax2.set_xlabel('Political Party', fontsize=12)
    ax2.set_ylabel('Number of Votes', fontsize=12)
    ax2.legend(title='Vote Result', 
              bbox_to_anchor=(1.05, 1), 
              loc='upper left',
              fontsize=10)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3)
    
    # Chart 3: Table showing the data
    # Sort by total representatives for consistency with bar chart
    vote_by_team_with_total = vote_by_team.copy()
    vote_by_team_with_total['Total'] = vote_by_team_with_total.sum(axis=1)
    vote_by_team_with_total = vote_by_team_with_total.sort_values('Total', ascending=False)
    
    # Create table data with better formatting
    table_data = []
    columns = ['Political Party', 'Yes', 'No', 'Abstentions', 'Others', 'Total']
    
    for party in vote_by_team_with_total.index:
        # Better party name handling - keep more characters but format nicely
        party_display = party
        if len(party) > 20:
            party_display = party[:17] + '...'
        
        row = [
            party_display,
            str(vote_by_team_with_total.loc[party, 'yes']),
            str(vote_by_team_with_total.loc[party, 'no']),
            str(vote_by_team_with_total.loc[party, 'abs']),
            str(vote_by_team_with_total.loc[party, 'others']),
            str(vote_by_team_with_total.loc[party, 'Total'])
        ]
        table_data.append(row)
    
    # Add totals row
    total_yes = vote_by_team_with_total['yes'].sum()
    total_no = vote_by_team_with_total['no'].sum()
    total_abs = vote_by_team_with_total['abs'].sum()
    total_others = vote_by_team_with_total['others'].sum()
    grand_total = vote_by_team_with_total['Total'].sum()
    
    totals_row = [
        'TOTAL',
        str(total_yes),
        str(total_no),
        str(total_abs),
        str(total_others),
        str(grand_total)
    ]
    table_data.append(totals_row)
    
    # Create the table with better styling
    ax3.axis('tight')
    ax3.axis('off')
    
    # Header colors that match the chart colors
    header_colors = ['#34495e', '#2ecc71', '#e74c3c', '#f39c12', '#95a5a6', '#2c3e50']
    
    table = ax3.table(cellText=table_data,
                     colLabels=columns,
                     cellLoc='center',
                     loc='center',
                     colColours=header_colors,
                     bbox=[0, 0, 1, 1])  # Full width and height
    
    # Enhanced table styling
    table.auto_set_font_size(False)
    table.set_fontsize(14)  # Even larger font size
    table.scale(1, 8)  # Make rows extremely tall for maximum readability
    
    # Style header row
    for i in range(len(columns)):
        cell = table[(0, i)]
        cell.set_text_props(weight='bold', color='white')
        cell.set_height(0.5)  # Very tall header
    
    # Style data cells with alternating row colors and column-specific colors
    for i in range(len(table_data)):
        # Check if this is the totals row (last row)
        is_totals_row = (i == len(table_data) - 1)
        
        if is_totals_row:
            row_color = '#2c3e50'  # Dark color for totals row
        else:
            row_color = '#f8f9fa' if i % 2 == 0 else '#ffffff'  # Alternating row colors
        
        for j in range(len(columns)):
            cell = table[(i+1, j)]
            cell.set_height(0.45)  # Extremely tall data cells
            
            if is_totals_row:
                # Special styling for totals row
                cell.set_facecolor('#2c3e50')
                cell.set_text_props(weight='bold', color='white', size=15)  # Larger font for totals
            elif j == 0:  # Party name column
                cell.set_facecolor(row_color)
                cell.set_text_props(weight='bold', ha='left')
            elif j == 1:  # Yes column
                cell.set_facecolor('#d5f4e6')  # Light green
                cell.set_text_props(weight='bold', color='#27ae60')
            elif j == 2:  # No column
                cell.set_facecolor('#f8d7da')  # Light red
                cell.set_text_props(weight='bold', color='#c0392b')
            elif j == 3:  # Abstentions column
                cell.set_facecolor('#fff3cd')  # Light yellow
                cell.set_text_props(weight='bold', color='#d68910')
            elif j == 4:  # Others column
                cell.set_facecolor('#e9ecef')  # Light gray
                cell.set_text_props(color='#6c757d')
            elif j == 5:  # Total column
                cell.set_facecolor('#e8f4f8')  # Light blue
                cell.set_text_props(weight='bold', color='#2c3e50')
    
    # Add borders to all cells
    for key, cell in table.get_celld().items():
        cell.set_linewidth(1.5)
        cell.set_edgecolor('#bdc3c7')
    
    ax3.set_title('Detailed Voting Results by Political Party', fontsize=14, fontweight='bold', pad=25)
    
    plt.tight_layout()
    plt.show()

def print_summary_statistics(df):
    """
    Print summary statistics about the voting data
    """
    print("="*60)
    print("CONGRESSIONAL VOTING ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nTotal number of representatives: {len(df)}")
    print(f"Number of political parties/teams: {df['team'].nunique()}")
    
    print("\n--- Vote Results Summary ---")
    result_summary = df['result'].value_counts()
    for result, count in result_summary.items():
        percentage = (count / len(df)) * 100
        print(f"{result}: {count} votes ({percentage:.1f}%)")
    
    print("\n--- Political Parties Summary ---")
    team_summary = df['team'].value_counts().head(10)
    print("Top 10 parties by number of representatives:")
    for i, (team, count) in enumerate(team_summary.items(), 1):
        print(f"{i:2d}. {team}: {count} representatives")
    
    print("\n--- Voting Patterns by Party ---")
    vote_patterns = pd.crosstab(df['team'], df['result'], normalize='index') * 100
    print("Percentage of 'yes' votes by party (parties with 3+ representatives):")
    
    parties_with_enough_reps = df['team'].value_counts()
    parties_3_plus = parties_with_enough_reps[parties_with_enough_reps >= 3].index
    
    if 'yes' in vote_patterns.columns:
        yes_percentages = vote_patterns.loc[parties_3_plus, 'yes'].sort_values(ascending=False)
        for party, percentage in yes_percentages.items():
            rep_count = parties_with_enough_reps[party]
            print(f"{party}: {percentage:.1f}% ({rep_count} reps)")

def main():
    """
    Main function to execute the analysis
    """
    filename = "resultado_votes.txt"
    
    try:
        # Read and process the data
        print("Reading voting data...")
        df = read_voting_data(filename)
        
        if df.empty:
            print("No data found in the file.")
            return
        
        print(f"Successfully loaded {len(df)} voting records.")
        
        # Display first few rows
        print("\nFirst 5 records:")
        print(df.head())
        
        # Print summary statistics
        print_summary_statistics(df)
        
        # Create and display charts
        print("\nGenerating charts...")
        create_charts(df)
        
        # Save the DataFrame to CSV for future use
        df.to_csv("voting_analysis.csv", index=False, encoding='utf-8')
        print(f"\nData saved to 'voting_analysis.csv'")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
