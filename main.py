## Libraries
import pandas as pd

## Data Cleaning Functions

def clean_poverty(file):
    # Read in data
    poverty = pd.read_excel(file)

    # Unpivot all columns on 'State'
    poverty = poverty.melt(id_vars=['State'], var_name='Year', value_name='Poverty Rate')

    # Filter where 'Year' >= 2002
    poverty = poverty[poverty['Year'] >= 2002]

    # Rename 'State' to 'State Name'
    poverty = poverty.rename(columns={'State': 'State Name'})

    return poverty

def clean_quality(file):
    # Read in data
    quality = pd.read_excel(file)

    # Filter where 'Program Name' = null
    quality = quality[quality['Program Name'].isnull()]

    # Drop 'Program Name' column
    quality = quality.drop(columns=['Program Name'])

    # Replace values in 'Variable Name' column
    quality['Variable Name'] = quality['Variable Name'].replace({
        'Family Support Service Requirements Benchmark': 'Continuous Quality Improvement System Benchmark',
        'Monitoring Benchmark': 'Continuous Quality Improvement System Benchmark',
        'Early Learning Standards Benchmark': 'Early Learning & Development Standards Benchmark',
        'Teacher In-Service Benchmark': 'Staff Professional Development Benchmark'
    })

    # Pivot 'Variable Name' column
    quality = quality.pivot_table(index=['State Name', 'Year'], columns=['Variable Name'], values='Value', aggfunc='first').reset_index()

    # Add new column to count number of "Yes" (not 'State Name' or 'Year'')
    quality['Quality Standards Met'] = quality.drop(columns = ['State Name', 'Year']).apply(lambda x: x.str.contains('yes', case=False).sum(), axis=1)

    return quality

def clean_general(file):
    # Read in data
    data = pd.read_excel(file)

    # Filter where 'Program Name' = null
    data = data[data['Program Name'].isnull()]

    # Drop 'Program Name' column
    data = data.drop(columns=['Program Name'])

    # Pivot on 'Variable Name'
    data = data.pivot_table(index=['State Name', 'Year'], columns=['Variable Name'], values='Value', aggfunc='first').reset_index()

    return data

# Merge Data by 'State Name' and 'Year'
def merge_data(poverty, spending, enrollment, quality):
    # Merge poverty and spending
    data = pd.merge(poverty, spending, on=['State Name', 'Year'], how='outer')
    # Merge data and enrollment
    data = pd.merge(data, enrollment, on=['State Name', 'Year'], how='outer')
    # Merge data and quality
    data = pd.merge(data, quality, on=['State Name', 'Year'], how='outer')
    
    # Replace values in all columns
    data = data.replace({'Yes': 1, 'No': 0, 'No program': 0, 'NA - Program level only': 1, '': 'NOT COLLECTED', 'Not reported': 'NOT REPORTED'})

    # Program Indicators
    data['3 Year Old Program'] = data['Percentage of 3-year-olds Enrolled in State Pre-K'].apply(lambda x: '0' if x == 0 else '1')
    
    data['4 Year Old Program'] = data['Percentage of 4-year-olds Enrolled in State Pre-K'].apply(lambda x: '0' if x == 0 else '1')
    
    # Sort by 'State Name' and 'Year'
    data = data.sort_values(by=['State Name', 'Year']).reset_index(drop=True)

    return data

def main():
    # Import and clean data
    poverty = clean_poverty('./Data/state_poverty.xlsx')
    quality = clean_quality('./Data/state_preschool_quality.xlsx')
    spending = clean_general('./Data/state_preschool_spending.xlsx')
    enrollment = clean_general('./Data/state_preschool_enrollment.xlsx')
    
    # Merge data on 'State Name' and 'Year'
    data = merge_data(poverty, spending, enrollment, quality)
    
    # Export to data.csv
    pd.DataFrame(data).to_csv('data.csv', index=False)

# Entry Point
if __name__ == '__main__':
    main()
