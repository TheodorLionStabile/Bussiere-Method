import pandas as pd
import numpy as np
import time

years = list(range(2010,2024))
    
countries_figaro = pd.read_csv("Countries_FIGARO.csv", encoding='latin1')

def prepping_dataset_col(tupl):
    global df
    
    tupl_list = list(tupl)
    
    filtered_df = df[df['colIi'].isin(tupl_list)]

    summed_df = (
    filtered_df.groupby(['refArea', 'rowIi', 'counterpartArea'])
    .agg({'obsValue': 'sum'})
    .reset_index()
    )
    b=['_'.join(tupl_list)]
    summed_df['colIi'] = b[0]
    summed_df['icioiRow'] = summed_df.apply(lambda row: f"{row['refArea']}_{row['rowIi']}", axis=1)
    summed_df['icioiCol'] = summed_df.apply(lambda row: f"{row['counterpartArea']}_{row['colIi']}", axis=1)

    
    #Merging the rows
    remaining_df = df[~df['colIi'].isin(tupl_list)]

    df = pd.concat([remaining_df, summed_df], ignore_index=True)

def prepping_dataset_row(tupl):
    global df
    
    tupl_list = list(tupl)
    
    filtered_df = df[df['rowIi'].isin(tupl_list)]

    summed_df = (
    filtered_df.groupby(['refArea', 'colIi', 'counterpartArea'])
    .agg({'obsValue': 'sum'})
    .reset_index()
    )
    b=['_'.join(tupl_list)]
    summed_df['rowIi'] = b[0]
    summed_df['icioiRow'] = summed_df.apply(lambda row: f"{row['refArea']}_{row['rowIi']}", axis=1)
    summed_df['icioiCol'] = summed_df.apply(lambda row: f"{row['counterpartArea']}_{row['colIi']}", axis=1)

    
    #Merging the rows
    remaining_df = df[~df['rowIi'].isin(tupl_list)]

    df = pd.concat([remaining_df, summed_df], ignore_index=True)


def columns_dom(tupl):
    global df_dom#Call the df_dom we define in the final loop
    tupl_list = [tupl]#Takes the tupple (this case the country we loop over) and store it as a list the reason is we can use then the isin function integrated into python
    #The filtered_df takes the countries with which we are not working directly. That is, the "foreign" part of the Domestic Exports and Imports Table
    filtered_df = df_dom[~df_dom['counterpartArea'].isin(tupl_list)]
    #This renames all the counterpartArea in all production relations within the Figaro table in ROW.
    filtered_df["counterpartArea"] = "ROW"
    #With then merge again all relations between industries, allowing us to have correctly summed trade relations between our country and all other foreign industries
    summed_df = (
        filtered_df.groupby(['refArea', 'rowIi', 'colIi'])
        .agg({'obsValue': 'sum'})
        .reset_index()
        )
    #Once again reapply the term ROW inthe final setup.
    summed_df['counterpartArea'] = "ROW"
    #We sum up along rows to generate the newly corrected reference country and counterpart
    summed_df['icioiRow'] = summed_df.apply(lambda row: f"{row['refArea']}_{row['rowIi']}", axis=1)
    summed_df['icioiCol'] = summed_df.apply(lambda row: f"ROW_{row['colIi']}", axis=1)
    
    
    #Taking the Figaro tables we are interested in keeping (e.g the country whose domestic import and export table we are generating)
    remaining_df = df_dom[df_dom['counterpartArea'].isin(tupl_list)]
    #Finally, we simply concat by adding the newly generated rows.
    df_dom = pd.concat([remaining_df, summed_df], ignore_index=True)



def rows_dom(tupl):
    #Calling the previously defined datased
    global df_dom
    #Transforming the country tuple into a list, allowing us to use the isin integrated function.
    tupl_list = list(tupl)
    #Filter out the the reference country we are currently using
    filtered_df = df_dom[~df_dom['refArea'].isin(tupl_list)]
    #Setting all the countries to ROW
    filtered_df["refArea"] = "ROW"
    #Function to sum over the observed values
    summed_df = (
        filtered_df.groupby(['counterpartArea', 'rowIi', 'colIi'])
        .agg({'obsValue': 'sum'})
        .reset_index()
        )
    #Readjusting the reference area variable
    summed_df['refArea'] = "ROW"
                
    #Applying summing to icioRow and icioiCol
    summed_df['icioiRow'] = summed_df.apply(lambda row: f"{row['refArea']}_{row['rowIi']}", axis=1)
    summed_df['icioiCol'] = summed_df.apply(lambda row: f"{row['counterpartArea']}_{row['colIi']}", axis=1)
    
    
    #Storing the rows with our country of interest in a dataframe
    remaining_df = df_dom[df_dom['refArea'].isin(tupl_list)]
    #Concatenating the modified rows to the dataframe we are currently working with
    df_dom = pd.concat([remaining_df, summed_df], ignore_index=True)


def pop_df(dataframe_empty):
    #taking in the empty dataframe generated in create_dom_matrix
    df = dataframe_empty
    #This for loop goes along all our panel data and populates based on the combinations of icioiCol and icioiRow (which are respecively our row indices and column indices in our empty df)
    for j in range(0,len(df_dom["icioiRow"])):
        #For each element j store the column name to call
        column_nam = df_dom.loc[j,"icioiCol"]
        #For each element j store the row name to call
        row_nam = df_dom.loc[j,"icioiRow"]
        #Store the observed value in pre-prepped df_dom
        observed_value = df_dom.loc[j,"obsValue"]
        #Identifying the right index in the empty dataframe
        row_ind = df[df["row_series"]==row_nam].index[0]
        #Populating the respective cell we call in our empty dataframe
        df.loc[row_ind,column_nam] = observed_value
    #We return our populated dataframe
    return df


def myFunc(e, country):
    prefix = e[:3]
    rest = e[3:]  # Everything after the prefix
    return (0, rest) if not prefix == "ROW"  else (1, rest)


def create_dom_matrix(country):
    #This calls the function columns dom.
    columns_dom(country)
    #This call in the function rows_dom
    rows_dom((country,"W2"))
    #Excluding the columns that start with P (these are the demand components)
    column_names = df_dom["icioiCol"][~df_dom["colIi"].str.startswith("P")].unique()
    #Selecting the columns that start with P (these are the demand components)
    column_names_p = df_dom["icioiCol"][df_dom["colIi"].str.startswith("P")].unique()
    #Transforming the pandas series to a list
    column_names_unsorted = list(column_names)
    #Sorting the non-valueadded data alphabetically
    column_names_unsorted.sort(key=lambda e: myFunc(e, country=country))
    #Transforming the value added variables into list from pandas series
    column_names_p = list(column_names_p)
    #Sorting only the value added data alphabetically
    column_names_p.sort(key=lambda e: myFunc(e, country=country))
    #Transformingthe sorted lists into series again (to be used to fill up empty dataframe)
    sorted_column_names_p = pd.Series(column_names_p).reset_index(drop=True)
    #Generating the properly arranged column name
    column_names = pd.concat([pd.Series(["row_series"]), pd.Series(column_names_unsorted), sorted_column_names_p]).reset_index(drop=True)
    #We apply the same logic as before but to generate the rows
    row_names = df_dom["icioiRow"][~df_dom["icioiRow"].str.startswith("W2")].unique()
    row_names_w = df_dom["icioiRow"][df_dom["icioiRow"].str.startswith("W2")].unique()
    sorted_row_names = list(row_names)
    sorted_row_names.sort(key=lambda e: myFunc(e, country=country))
    row_series = pd.Series(["row_series"])
    sorted_row_names_w = pd.Series(row_names_w).sort_values().reset_index(drop=True)
    row_names = pd.concat([pd.Series(sorted_row_names), sorted_row_names_w]).reset_index(drop=True)
    #Generating the empty dataframe
    dataframe_empty = pd.DataFrame(columns=column_names)
    #Placing into the row_series column all the pre-generated row names
    dataframe_empty["row_series"] = row_names
    #Calling pop_df a function required to populate the empty dataframe with the cleaned up data (e.g. the merged industries)
    final_outcome=pop_df(dataframe_empty)
    #Ensure that the values we populated the dataframe with are a float
    final_outcome.iloc[:, 1:] = final_outcome.iloc[:, 1:].apply(lambda col: col.astype(float))
    #We store the columns we have generated
    my_list = list(final_outcome.columns)
    #We store all the columns that start with ROW
    ROW_col = [my_list.index(item) for item in my_list if item.startswith("ROW")]
    ROW_col_names = [item for item in my_list if item.startswith("ROW")]
    #We index for all the columns that should become an export in the domestic import and export table
    Export_ind = pd.Index(ROW_col)
    #Generating the export column in the domestic import and export table by summing up all Export_index columns
    final_outcome['EXPO'] = final_outcome.iloc[:, Export_ind].sum(axis=1)
    #We drop the previously identified columns of Row_col_names out of the datframe we are generating.
    final_outcome = final_outcome.drop(columns=ROW_col_names)
    #Calling the empty dataframe and storing the rows starting with ROW
    short_store = final_outcome["row_series"].str.startswith("ROW")
    #Creating an index of the ROW rows
    index_start = short_store[short_store == True].index[0]
    #Storing the rows that are for the national value added factors
    short_store2 = final_outcome["row_series"].str.startswith("W2")
    #Index the value added elements
    index_end =short_store2[short_store2 == True].index[0]
    #The rows representing ROW product need to equal 0 in the export columns for the domestic import and export tables
    final_outcome.loc[index_start:index_end, "EXPO"] = 0
    #Generating the Import columns in the matrix to 0 allowing us to populate it selectively. 
    final_outcome["IMPO"] = 0
    #Populationg the Import column through pandas integrated sum function
    final_outcome.loc[index_start:index_end,"IMPO"] = final_outcome.iloc[index_start:index_end,1:-2].sum(axis=1)
    print(f"The list is the following: {my_list}")
    #Renaming demand components to adjust them to OECD structure
    name_change_dictionary = {"P3_S13":"GGFC","P3_S14":"HFCE","P3_S15":"NPISH","P51G":"GFCF","P5M":"INVNT"}
    #Looping over the naming dictionary to rename the columns correctly
    for key,value in name_change_dictionary.items():
        item_to_change = [item for item in my_list if item.endswith(key)]
        final_outcome = final_outcome.rename(columns = {item_to_change[0]:value})
    #Generating a row for value added
    final_outcome.loc[102,"row_series"] = "VALU"
    #Summing up the value added rows which are located between index 96 and 98
    summed_values = final_outcome.iloc[96:98, 1:].sum(axis=0)
    #Populating the VALUE row with the sum of the different value added subcomponents
    final_outcome.iloc[102, 1:] = summed_values.values
    #Dropping the individual value added rows into a single value added
    final_outcome = final_outcome.drop(index=[96,97])
    #Sum along rows
    column_sums = final_outcome.sum(axis=0)
    #
    final_outcome.loc[len(final_outcome)+2] = column_sums
    #Populating our import and export table with a total output row
    final_outcome.loc[103,"row_series"] = "OUTPUT"
    #columns that need a zero value in value added and output
    columns_to_zero = ["HFCE","NPISH","GGFC","GFCF","INVNT","EXPO","IMPO"]
    #Looping over columns that require 0 in value added at output tables
    for i in columns_to_zero:
        valu_ind = final_outcome[final_outcome["row_series"]=="VALU"].index
        output_ind = final_outcome[final_outcome["row_series"]=="OUTPUT"].index
        final_outcome.loc[valu_ind,i] = 0
        final_outcome.loc[output_ind,i] = 0
        
    names_col = list(final_outcome.columns)
    names_col_new = ['_'.join(item.split("_")[1:]) if item.startswith(country) else item for item in names_col]
    rename_dictionary = dict(zip(names_col, names_col_new))
    final_outcome = final_outcome.rename(columns=rename_dictionary)
    final_outcome = final_outcome.reindex(columns=["row_series","A01_A02","A03","B","C10T12","C13T15","C16","C17_C18","C19","C20","C21","C22","C23","C24","C25","C26","C27","C28","C29","C30","C31_32_C33","D35","E35_E37T39","E36","F","G45_G46_G47","H49","H50","H51","H52","H53","I","J58","J59_60","J61","J62_63","K64","K65","K66","L","M69_70_M71_M72_M73_M74_75","N77_N78_N79_N80T82","O84","P85","Q86_Q87_88","R90T92_R93","S94_S95_S96","T","U","HFCE","NPISH","GGFC","GFCF","INVNT","EXPO","IMPO"])
    final_outcome['Total'] = final_outcome.iloc[:,1:].sum(axis=1)
    short_store = final_outcome["row_series"].str.startswith("ROW")
    index_start = short_store[short_store == True].index[0]
    short_store2 = final_outcome["row_series"].str.startswith("W2")
    index_end =short_store2[short_store2 == True].index[0]
    final_outcome.loc[index_start:index_end, "Total"] = 0
    return final_outcome


for i in years:#Function loops over the years available to us (e.g. multiregional IO tables in years x to y)
    df = pd.read_csv(f"flatfile_eu-ic-io_ind-by-ind_25ed_{i}.csv")#Stores the years' multiregional df
    #This for loop loops over the different industry combinations to adjust to the OECD structure.
    for k in [("A01","A02"),("C17","C18"),("C31_32","C33"),("E35","E37T39"),("G45","G46","G47"),("M69_70","M71","M72","M73","M74_75"),("N77","N78","N79","N80T82"),("Q86","Q87_88"),("R90T92","R93"),("S94","S95","S96")]:
        prepping_dataset_col(k)#This function merges the industry columns
        prepping_dataset_row(k)#This function merge the industry rows
        

    for j in countries_figaro["Country_Code"].unique():
        print(f"We started the domestic matrix for country {j}")
        df_dom = df
        df_final = create_dom_matrix(j)
        globals()[f"df_{j}_{i}"] = df_final
        df_final.to_csv(f"df_{j}_{i}.csv", index=False)
    

    


















