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
    data['Program_3yo'] = data['Percentage of 3-year-olds Enrolled in State Pre-K'].apply(lambda x: 0 if x == 0 else 1)
    
    data['Program_4yo'] = data['Percentage of 4-year-olds Enrolled in State Pre-K'].apply(lambda x: 0 if x == 0 else 1)
    
    # Sort by 'State Name' and 'Year'
    data = data.sort_values(by=['State Name', 'Year']).reset_index(drop=True)

    return data

def rename_columns(data):
    data = data.rename(columns={'State Name': 'State'})
    data = data.rename(columns={'Poverty Rate': 'Poverty'})
    data.columns = data.columns.str.replace(' ', '_')
    data.columns = data.columns.str.replace('_\(2022_Dollars\)', '')
    data.columns = data.columns.str.replace('All-Reported', 'All')
    data.columns = data.columns.str.replace('Total_', '')
    data.columns = data.columns.str.replace('_in_State_Pre-K', '')
    data.columns = data.columns.str.replace('_Benchmark', '_B')
    data.columns = data.columns.str.replace('3-year-olds', '3yo')
    data.columns = data.columns.str.replace('4-year-olds', '4yo')
    data.columns = data.columns.str.replace('Percentage_of', 'P')
    data.columns = data.columns.str.replace('Number_of', 'N')
    data.columns = data.columns.str.replace('&', 'and')


    return data

def fill_missing(data):
    # List of columns to apply the filling logic
    numeric_cols = [
        'All_Spending_per_Child', 'State_Spending_per_Child', 
        'All_Spending', 'State_Pre-K_Spending', 'N_3yo_Enrolled', 
        'N_4yo_Enrolled', 'P_3yo_Enrolled', 'P_4yo_Enrolled', 
        'State_Pre-K_Enrollment'
    ]
    
    # Replace "NOT REPORTED" with NaN (null) in the specified columns
    data[numeric_cols] = data[numeric_cols].replace("NOT REPORTED", pd.NA)
    
    # Convert columns with potential textual representations of numbers to numeric, forcing errors to NA
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # Group by state to ensure that the filling logic is applied within each state
    grouped = data.groupby('State')

    # Function to apply the specified filling logic to a column within each group
    def fill_na_within_group(series):
        # Forward fill then backward fill for ends
        series = series.fillna(method='ffill').fillna(method='bfill')
        # Interpolate for mid values
        return series.interpolate()

    # Apply the filling logic to each group for the specified numeric columns
    for col in numeric_cols:
        data[col] = grouped[col].transform(fill_na_within_group)

    return data

def main():
    # Import and clean data
    poverty = clean_poverty('./Data/state_poverty.xlsx')
    quality = clean_quality('./Data/state_preschool_quality.xlsx')
    spending = clean_general('./Data/state_preschool_spending.xlsx')
    enrollment = clean_general('./Data/state_preschool_enrollment.xlsx')
    
    # Merge data on 'State Name' and 'Year'
    data = merge_data(poverty, spending, enrollment, quality)
    
    data = rename_columns(data)
    
    data = fill_missing(data)

    # Remove States "National" and "Guam"
    data = data[data['State'] != 'National']
    data = data[data['State'] != 'Guam']

    # Export to data.xlsx
    data.to_excel('./data.xlsx', index=False)

# Entry Point
if __name__ == '__main__':
    main()
