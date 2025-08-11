# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 09:31:50 2025

@author: stabith
"""

import csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
countries = pd.read_csv('Country_Codes.csv', encoding='latin1')

# Assuming the CSV loading and initial processing here are correct
country_code = list(countries.iloc[:76,0])
years = list(range(1995,2021))


dataframes = {}

# Loop through the years to read each CSV file
for years in years:
    filename = f'{years}_total.csv'
    dataframes[years] = pd.read_csv(filename)        
        
     
        
     
for key,value in dataframes.items():
    df = value
    length = len(df.iloc[:,0])
    new_y = np.repeat(int(key),length)
    df["Year"] = new_y


df_to_concat = []

for key,value in dataframes.items():
    df_to_concat.append(value)
    
    
df = pd.concat(df_to_concat, ignore_index = True)



grouped_df = df.groupby('Countries')["Private_Consumption"].mean()


Mean_Countries_1995_2020 = df.groupby(['Countries']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
)


bins = [1995, 2001, 2008, 2016, 2021]
labels = ['1995-2000', '2001-2007', '2008-2015', '2016-2020']

# Create a new column for year intervals
df['Interval'] = pd.cut(df['Year'], bins=bins, labels=labels, right=False)


EA = ['CYP',"AUT","BEL","DEU","ESP","EST","FIN","FRA","GRC","HRV","IRL","ITA","LTU","LUX","LVA","MLT","NLD","PRT","SVK","SVN"]
EU = ['ROU','CYP',"AUT","BEL","DEU","ESP","EST","FIN","FRA","GRC","HRV","IRL","ITA","LTU","LUX","LVA","MLT","NLD","PRT","SVK","SVN",'BGR','CZE','DNK','HUN','POL','SWE']

df['EA'] = df['Unnamed: 0'].apply(lambda x: 'EA' if x in EA else 'Non-EA')
df['EU'] = df['Unnamed: 0'].apply(lambda x: 'EU' if x in EU else 'Non-EU')



Mean_Countries_Interval = df.groupby(['Countries','Interval']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
)

Mean_Interval = df.groupby(['Interval']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
)

Mean_EA = df.groupby(['EA']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
)

Mean_EU = df.groupby(['EU']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
)

Mean_EA_Interval = df.groupby(['EA','Interval']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
).reset_index()

Mean_EU_Interval = df.groupby(['EU','Interval']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
).reset_index()



Mean_EA_Year = df.groupby(['EA','Year']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
).reset_index()


Mean_EU_Year = df.groupby(['EU','Year']).agg(
    Private =("Private_Consumption", 'mean'),
    Government =("Government_Consumption", 'mean'),
    Investment =("Investment_Consumption", 'mean'),
    Export =("Export", 'mean')
).reset_index()



Mean_EU_EA_Year_Concat = pd.concat([Mean_EA_Year,Mean_EU_Year])

# =============================================================================
# Bar Plots Mean_EA_Interval
# =============================================================================


# Separate the data into EA and Non-EA
EA_Data = Mean_EU_Interval[Mean_EU_Interval['EU'] == 'EU']
Non_EA_Data = Mean_EU_Interval[Mean_EU_Interval['EU'] != 'EU']

# Setting up the plot
fig, axes = plt.subplots(1, 2, figsize=(14, 8))

# Bar width
width = 0.2

# EA Bar Plot
x_values_ea = np.arange(len(EA_Data['Interval']))  # Numeric x positions for ea intervals
interval_labels_ea = EA_Data['Interval']  # Extract labels for the x-axis

axes[0].bar(x_values_ea, EA_Data['Private'], width, label='Private')
axes[0].bar(x_values_ea + width, EA_Data['Government'], width, label='Government')
axes[0].bar(x_values_ea + 2 * width, EA_Data['Investment'], width, label='Investment')
axes[0].bar(x_values_ea + 3 * width, EA_Data['Export'], width, label='Export')

axes[0].set_title('EU Import Content')
axes[0].set_xlabel('Interval')
axes[0].set_ylabel('Percentage')
axes[0].set_xticks(x_values_ea + 1.5 * width)  # Centralize tick marks
axes[0].set_xticklabels(interval_labels_ea)  # Set tick labels
axes[0].legend(loc='upper left')

# Non-EA Bar Plot
x_values_non_ea = np.arange(len(Non_EA_Data['Interval']))  # Numeric x positions for non-ea intervals
interval_labels_non_ea = Non_EA_Data['Interval']  # Extract labels for the x-axis

axes[1].bar(x_values_non_ea, Non_EA_Data['Private'], width, label='Private')
axes[1].bar(x_values_non_ea + width, Non_EA_Data['Government'], width, label='Government')
axes[1].bar(x_values_non_ea + 2 * width, Non_EA_Data['Investment'], width, label='Investment')
axes[1].bar(x_values_non_ea + 3 * width, Non_EA_Data['Export'], width, label='Export')

axes[1].set_title('Non-EU Import Content')
axes[1].set_xlabel('Interval')
axes[1].set_xticks(x_values_non_ea + 1.5 * width)  # Centralize tick marks
axes[1].set_xticklabels(interval_labels_non_ea)  # Set tick labels
axes[1].legend(loc='upper left')

# Adjust layout
plt.tight_layout()
plt.show()

# =============================================================================
# Bar Plots Mean_EU_Interval
# =============================================================================


# Separate the data into EA and Non-EA
EA_Data = Mean_EA_Interval[Mean_EA_Interval['EA'] == 'EA']
Non_EA_Data = Mean_EA_Interval[Mean_EA_Interval['EA'] != 'EA']

# Setting up the plot
fig, axes = plt.subplots(1, 2, figsize=(14, 8))

# Bar width
width = 0.2

# EA Bar Plot
x_values_ea = np.arange(len(EA_Data['Interval']))  # Numeric x positions for ea intervals
interval_labels_ea = EA_Data['Interval']  # Extract labels for the x-axis

axes[0].bar(x_values_ea, EA_Data['Private'], width, label='Private')
axes[0].bar(x_values_ea + width, EA_Data['Government'], width, label='Government')
axes[0].bar(x_values_ea + 2 * width, EA_Data['Investment'], width, label='Investment')
axes[0].bar(x_values_ea + 3 * width, EA_Data['Export'], width, label='Export')

axes[0].set_title('EA Import Content')
axes[0].set_xlabel('Interval')
axes[0].set_ylabel('Percentage')
axes[0].set_xticks(x_values_ea + 1.5 * width)  # Centralize tick marks
axes[0].set_xticklabels(interval_labels_ea)  # Set tick labels
axes[0].legend(loc='upper left')

# Non-EA Bar Plot
x_values_non_ea = np.arange(len(Non_EA_Data['Interval']))  # Numeric x positions for non-ea intervals
interval_labels_non_ea = Non_EA_Data['Interval']  # Extract labels for the x-axis

axes[1].bar(x_values_non_ea, Non_EA_Data['Private'], width, label='Private')
axes[1].bar(x_values_non_ea + width, Non_EA_Data['Government'], width, label='Government')
axes[1].bar(x_values_non_ea + 2 * width, Non_EA_Data['Investment'], width, label='Investment')
axes[1].bar(x_values_non_ea + 3 * width, Non_EA_Data['Export'], width, label='Export')

axes[1].set_title('Non-EA Import Content')
axes[1].set_xlabel('Interval')
axes[1].set_xticks(x_values_non_ea + 1.5 * width)  # Centralize tick marks
axes[1].set_xticklabels(interval_labels_non_ea)  # Set tick labels
axes[1].legend(loc='upper left')

# Adjust layout
plt.tight_layout()
plt.show()

# =============================================================================
# Plot EU & EA by Year
# =============================================================================
EU_Data = Mean_EU_EA_Year_Concat[Mean_EU_EA_Year_Concat['EU'] == 'EU']
EA_Data = Mean_EU_EA_Year_Concat[Mean_EU_EA_Year_Concat['EA'] == 'EA']
fig, ax = plt.subplots(figsize=(10, 6))

colors = ['b', 'g', 'r', 'y']
markers_eu = ['o', 'v', '^', '<']  # Different markers for EA
markers_ea = ['o', 'v', '^', '<']  # Different markers for Non-EA

# Dictionary to store handles and labels for custom legend
legend_handles = {}

# Plot each line and collect handles
for i, value_name in enumerate(['Private', 'Government', 'Investment', 'Export']):
    line_EU, = ax.plot(EU_Data['Year'], EU_Data[value_name], label=f'EU {value_name}', 
                       marker=markers_eu[i], linestyle='-', color=colors[i])
    line_EA, = ax.plot(EA_Data['Year'], EA_Data[value_name], label=f'EA {value_name}', 
                           marker=markers_ea[i], linestyle='--', color=colors[i])
    
    # Save handles for each plot
    legend_handles[f'EU {value_name}'] = line_EU
    legend_handles[f'EA {value_name}'] = line_EA

# Define custom legend order
custom_legend_order = [
    'EU Private', 'EA Private',
    'EU Government', 'EA Government',
    'EU Investment', 'EA Investment',  # Investment entries appear together
    'EU Export', 'EA Export',
]

# Create custom legend
handles = [legend_handles[label] for label in custom_legend_order]
labels = custom_legend_order
ax.legend(handles, labels, loc='best')

# Customize the plot
ax.set_title('Direct Import Content: EU vs EA by Year')
ax.set_xlabel('Year')
ax.set_ylabel('Measured Values')
plt.grid(True)
plt.show()




# =============================================================================
# Plot (Non)-EU by Year
# =============================================================================

eu_data = Mean_EU_Year[Mean_EU_Year['EU'] == 'EU']
non_eu_data = Mean_EU_Year[Mean_EU_Year['EU'] != 'EU']

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))

# Colors and markers for differentiation
colors = ['b', 'g', 'r', 'y']
markers_eu = ['o', 'v', '^', '<']  # Different markers for EA
markers_non_eu = ['o', 'v', '^', '<']  # Different markers for Non-EA

# Dictionary to store handles and labels for custom legend
legend_handles = {}

# Plot each line and collect handles
for i, value_name in enumerate(['Private', 'Government', 'Investment', 'Export']):
    line_EU, = ax.plot(eu_data['Year'], eu_data[value_name], label=f'EA {value_name}', 
                       marker=markers_eu[i], linestyle='-', color=colors[i])
    line_non_EU, = ax.plot(non_eu_data['Year'], non_eu_data[value_name], label=f'Non-EA {value_name}', 
                           marker=markers_non_eu[i], linestyle='--', color=colors[i])
    
    # Save handles for each plot
    legend_handles[f'EU {value_name}'] = line_EU
    legend_handles[f'Non-EU {value_name}'] = line_non_EU

# Define custom legend order
custom_legend_order = [
    'EU Private', 'Non-EU Private',
    'EU Government', 'Non-EU Government',
    'EU Investment', 'Non-EU Investment',  # Investment entries appear together
    'EU Export', 'Non-EU Export',
]

# Create custom legend
handles = [legend_handles[label] for label in custom_legend_order]
labels = custom_legend_order
ax.legend(handles, labels, loc='best')

# Customize the plot
ax.set_title('Direct Import Content: EU vs Non-EU by Year')
ax.set_xlabel('Year')
ax.set_ylabel('Measured Values')
plt.grid(True)
plt.show()


# =============================================================================
# Plot (Non)-EA by Year
# =============================================================================


# Separate the data into EA and Non-EA
ea_data = Mean_EA_Year[Mean_EA_Year['EA'] == 'EA']
non_ea_data = Mean_EA_Year[Mean_EA_Year['EA'] != 'EA']

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))

# Colors and markers for differentiation
colors = ['b', 'g', 'r', 'y']
markers_ea = ['o', 'v', '^', '<']  # Different markers for EA
markers_non_ea = ['o', 'v', '^', '<']  # Different markers for Non-EA

# Dictionary to store handles and labels for custom legend
legend_handles = {}

# Plot each line and collect handles
for i, value_name in enumerate(['Private', 'Government', 'Investment', 'Export']):
    line_ea, = ax.plot(ea_data['Year'], ea_data[value_name], label=f'EA {value_name}', 
                       marker=markers_ea[i], linestyle='-', color=colors[i])
    line_non_ea, = ax.plot(non_ea_data['Year'], non_ea_data[value_name], label=f'Non-EA {value_name}', 
                           marker=markers_non_ea[i], linestyle='--', color=colors[i])
    
    # Save handles for each plot
    legend_handles[f'EA {value_name}'] = line_ea
    legend_handles[f'Non-EA {value_name}'] = line_non_ea

# Define custom legend order
custom_legend_order = [
    'EA Private', 'Non-EA Private',
    'EA Government', 'Non-EA Government',
    'EA Investment', 'Non-EA Investment',  # Investment entries appear together
    'EA Export', 'Non-EA Export',
]

# Create custom legend
handles = [legend_handles[label] for label in custom_legend_order]
labels = custom_legend_order
ax.legend(handles, labels, loc='best')

# Customize the plot
ax.set_title('Direct Import Content: EA vs Non-EA by Year')
ax.set_xlabel('Year')
ax.set_ylabel('Measured Values')
plt.grid(True)
plt.show()

# =============================================================================
# Plot Each Country Seperately
# =============================================================================

coun = df['Countries'].unique()

for country in coun:
    df_country = df[df['Countries'] == country]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['b', 'g', 'r','y']

    for i, value_name in enumerate(['Private_Consumption', 'Government_Consumption', 'Investment_Consumption','Export']):
        ax.plot(df_country['Year'], df_country[value_name], label=value_name, marker='o', color=colors[i])

    ax.set_title(f'Direct Import Content of: {country}')
    ax.set_xlabel('Year')
    ax.set_ylabel('Measured Values')
    ax.legend()
    plt.show()

