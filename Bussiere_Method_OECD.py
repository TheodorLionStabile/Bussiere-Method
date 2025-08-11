
import csv
import pandas as pd
import numpy as np

#Imports all available countries in OECD data
countries = pd.read_csv('Country_Codes.csv', encoding='latin1')

#We take the Country Codes for Country_Codes CSV
country_code = list(countries.iloc[:76,0])
#The number in this list (e.g. 1995,2021) should only be changed when the OECD data is expanded beyond the currenty timeframe.
#That means once the Supply Use and Demand Use Table by the OECD are updated you can change this once the files are included. 
years = list(range(2018,2019))


#This variable should be edited by hand. You can add more methods through simply adding them to the list:

methods = ["indirect","direct","total"] 
for method in methods:#Goes through methods
    for years in years:#For loop to estimates each available year
        dataframes = {}#Storin dataframes that are being studied
    
    # Loop through the years to read each CSV file that we have stored in the same working directory
        for country in country_code:#Looping overa available countries
            filename = f'{country}{years}dom.csv'#Flexible naming convention to allow unqiue combinations.
            dataframes[country] = pd.read_csv(filename)#Story the dataframes we will use for estimating in a dictionary for easier handling.

        #The following GDP components are possible.
        #1. PC is Private Consumption - All the consumption from households
        #2. GC is Government Consumption - All the consumption that arises from Government Expenditure 
        #3. Inv is Investment - This is the classical investment component
        #4. EXPO is Exports - This is the demand that is derived externally
        
        pc_dict = {}#Dictionary that stores Private Consumption for the ongoing estimate
        gc_dict = {}#Dictionary that stores Government Consumption for the ongoing estimate
        inv_dict = {} #Dictionary that stores Investment for the ongoing estimate
        expo_dict = {} #Dictionary that stores Exports for the ongoing estimate
                
        ##----------------------------------------------------------------------------------------------------------------------------------
        # Modify by hand
        ##----------------------------------------------------------------------------------------------------------------------------------
        # Demand Type is the expnditure component of which you estimate the Import Content share. 
        #This is a simply list and can be simply modified like any other python list. 
        
        demand_type = ["PC","GC","Inv","EXPO"]
        ##----------------------------------------------------------------------------------------------------------------------------------
        
        #Here we start looping over each demand component. Therefore, at this stage the script is performing the following:
            #For the country x in year x and then enter into eeach demand source you are interested in estimating.
        for d in demand_type:
            
            #This is where we initialize and estimate the Leontief Matrix
            for key,value in dataframes.items():#This loops over the dataframes we have loaded above (e.g. countryyearsdom.csv)
                Matrix_A_dom = np.empty((45,45))#This create an empty 45 x 45 Matrix. This is hte cause because the Supply Use tables come in this form. Should be adjusted appropriately if more industries added or product level supply use table used.
                Matrix_A_dom[:] = np.nan 
                Matrix_A_dom = pd.DataFrame(Matrix_A_dom) #This turn the Matrix into a Pandas dataframe making the modifications later easier. 

                df = value#This reads the dataframes in
                
                #Here we loop over the pandas dataframe to derive th productivity coefficients needed for the Leontief Matrix
                for i in range(45):
                    for j in range(45):
                        x_ij = df.iloc[i, j + 1]
                        row = df[df['Unnamed: 0'] == "OUTPUT"].index[0]
                        x_j = df.iloc[row, j + 1]
                        
                        if x_j == 0:
                            a_ij = 0
                        else:    
                            a_ij = x_ij / x_j
                            
                        Matrix_A_dom.at[i,j] = a_ij
            
                #Here the same thing as above occurrs however, we take the Foreign component of the matrix, or the 
                Matrix_A_Foreign = np.empty((45,45))
                Matrix_A_Foreign[:] = np.nan
                Matrix_A_Foreign = pd.DataFrame(Matrix_A_Foreign)
                df_import = df.iloc[45:,:]
                df_import = df_import.reset_index(drop=True)
            
                for i in range(45):
                    for j in range(45):
                        x_ij = df_import.iloc[i, j + 1]
                        row = df_import[df_import['Unnamed: 0'] == "OUTPUT"].index[0]
                        x_j = df_import.iloc[row, j + 1]
                        
                        if x_j == 0:
                            a_ij = 0
                        else:    
                            a_ij = x_ij / x_j
                            
                        Matrix_A_Foreign.at[i,j] = a_ij
            
                #Create identity matrix required for Leontief
                I = np.identity(45)
                #Transforming the pandas to a numpy to allow for matrix operations
                A_Domestic = Matrix_A_dom.to_numpy()
                B = I - A_Domestic #Creating inversable matrix
                B_inv = np.linalg.inv(B) #Inversing matrix for Leontief Matrix
                
                if d == "PC":
                    #Private consumption is made out of Household consumption and Non-Profit consumption. This could theoretically be split if needed. 
                    F_d = np.array(df.loc[:44,"HFCE"]+df.loc[:44,"NPISH"])
                elif d == "GC":
                    F_d = np.array(df.loc[:44,"GGFC"])
                elif d == "Inv":
                    F_d = np.array(df.loc[:44,"GFCF"])
                elif d == "EXPO":
                    F_d = np.array(df.loc[:44,"EXPO"])
                else:
                    #This is an error in case the naming convention above was not ensured. 
                    print("Wrong Demand Type")
            
                #Generating X matrix by multiplying inverse B matrix and final demand source.
                X = B_inv @ F_d
                
                #Foreign input coefficient
                A_Foreign = Matrix_A_Foreign.to_numpy()
                
                #Indirect Import Demand
                M_ind = A_Foreign @ X
                        
                if d == "PC":
                    F_m = np.array(df.loc[45:89,"HFCE"]+df.loc[45:89,"NPISH"])
                elif d == "GC":
                    F_m = np.array(df.loc[45:89,"GGFC"])
                elif d == "Inv":
                    F_m = np.array(df.loc[45:89,"GFCF"])
                elif d == "EXPO":
                    F_m = np.array(df.loc[45:89,"EXPO"])        
                else:
                    print("Wrong Demand Type")
                
                #Direct Imports on the Left 
                M_dir = F_m
                
                #This is a vector of ones and is part of the Bussiere Methodology
                u = np.ones((1,45))
                
                uM_ind = u @ M_ind
                uM_dir = u @ M_dir
                uF_m = u @ F_m
                uF_d = u @ F_d
                
                #Total Import
                Total_Import_Component = uM_ind+uM_dir
                
                #This is total demand
                Total_demand = uF_m+uF_d
                
                
                #Calculating the direct and indirect import content share
                if method == "direct":
                    share = (uM_dir/Total_demand)*100
                elif method == "indirect":
                    share = (uM_ind/Total_demand)*100
                elif method == "total":
                    share = (Total_Import_Component/Total_demand)*100
                
                #Based on the demand we are currently interested in
                if d == "PC":
                    pc_dict[key] = share
                elif d == "GC":
                    gc_dict[key] = share
                elif d == "Inv":
                    inv_dict[key] = share
                elif d == "EXPO":
                    expo_dict[key] = share
                else:
                    print("Missing Dictionary")#If the dictionary is missing. 
               
        #Creating an empty dataframe
        df_final = pd.DataFrame()
        #Creating a column for Private Consumption
        df_final["Private_Consumption"] = np.nan
        #Creating a column for Government Consumption
        df_final["Government_Consumption"] = np.nan
        #Column for Investment Consumption
        df_final["Investment_Consumption"] = np.nan
        #Column for Export
        df_final["Export"] = np.nan
        
            
        ##----------------------------------------------------------------------------------------------------------------------------------
        # Modify by hand
        ##----------------------------------------------------------------------------------------------------------------------------------
        #Here we store a list of import content share components. 
        #We need the list to be able to populate the final excel with the values we are interested in.
        dictionaries = [pc_dict,gc_dict,inv_dict,expo_dict]
        
        ##----------------------------------------------------------------------------------------------------------------------------------

        
        #stores countries for final export of data so not only code is available
        s = countries.set_index("Code")
        
        #Loops over the values we have stored to create tables with import contents
        for p in dictionaries:#Here we mannually set which demand components we would like to store
            for key,value in p.items():
                test = value[0]
                if p == pc_dict:
                    df_final.at[key,"Private_Consumption"] = test
                elif p == gc_dict:
                    df_final.at[key,"Government_Consumption"] = test
                elif p == inv_dict:
                    df_final.at[key,"Investment_Consumption"] = test
                elif p == expo_dict:
                    df_final.at[key,"Export"] = test
         
        #Creates merged pandas to exports
        df_final = pd.merge(df_final, s, right_index=True, left_index=True)
        
        #Stores dictionaries and data
        share_csv_data = df_final.to_csv(f'{years}_{method}.csv', index = True) 
