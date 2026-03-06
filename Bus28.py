# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 15:22:10 2026

@author: chari
"""
#IMPORTS
import powerfactory as pf
import pandas as pd
import numpy as np
import matplotlib as plt

#ASSIGN A STUDY CASE
app = pf.GetApplication()

#Get PowerFactory commands
ldf = app.GetFromStudyCase("ComLdf") #Load flow
initCond = app.GetFromStudyCase("ComInc") #initial conditions
run = app.GetFromStudyCase("ComSim") #Run simualtion
results = app.GetFromStudyCase("ElmRes") #Results variable
export = app.GetFromStudyCase("ComRes") #Export results

#Get data objects
syn_machines = app.GetCalcRelevantObjects("*.ElmSym") #Sync generators
stat_machines = app.GetCalcRelevantObjects("*.ElmGenstat") #stat generators
transformer = app.GetCalcRelevantObjects("*.ElmTr2") #Transformer
mac_type = app.GetCalcRelevantObjects("*.TypSym") #sync machine type
trans_type = app.GetCalcRelevantObjects("*.TypTr2") #transformer type
loads = app.GetCalcRelevantObjects("*.ElmLod") #get general loads

#EMPTY SETS
syncSet = []
imports =[]
machine_types = []
wind_mac = []
solar_mac = []
genSet = []
#EMPTY DF
df_cap = pd.DataFrame()

#DISCONNECT REDUNDANT MACHINES
for stat_gen in stat_machines:
    if "Battery" in stat_gen.loc_name:
        stat_gen.pgini = 0
        stat_gen.outserv = 1
for trans in transformer:
    if "Battery" in trans.loc_name:
        trans.outserv =1
# ADD COLUMNS TO DF 
for gen in syn_machines: #iterate thriugh sync machines
    if gen.outserv == 0: #if connected
        # Resolve energy type
        if "Sync Condenser" in gen.loc_name:
            energyName = "Sync Condenser" #get Sync condenser name
        else:
            energyName = gen.loc_name.split()[-1]  # get last word
        # Add empty column if not present in df
        if energyName not in df_cap.columns:
            df_cap[energyName] = None #add energy name column to df
        # Reset syncSet for this iteration
        syncSet.clear()
        # Find matching machines
        for item in mac_type:
            if "Storage" in energyName:
                energyName = "PS" #connect storage to PS (pump storage) 
            if energyName.lower() in item.loc_name.lower():
                syncSet.append(item)
        # Skip if no matching units found
        if not syncSet:
            continue
        # Total capacity
        if "PS" in str(energyName): #change energy name back to storage
            energyName = "Storage"
        total_cap = sum(item.sgn for item in syncSet)
        total_ac_cap = sum((item.sgn * item.cosn) for item in syncSet)
        # Store capacity in first row
        df_cap.loc[0, energyName] = total_cap #total apparent power for each energy type
        df_cap.loc[1, energyName] = total_ac_cap #total active power rating
        
for gen in stat_machines:  #iterate through static machines
    if gen.outserv == 0: #if machine is connected   
        # Resolve energy type
        if "HVDC" in gen.loc_name:
            energyName = "HVDC" #make energy name HDVC
        else:
            energyName = gen.loc_name.split()[-1]  #get last word
        # Add empty column if not present
        if energyName not in df_cap.columns:
            df_cap[energyName] = None #add energy name to dfcolumns
        # Reset syncSet for this iteration
        syncSet.clear()
        # Find matching machines
        for item in stat_machines:
            if energyName.lower() in item.loc_name.lower():
                syncSet.append(item) #add items of same energy name to list
        # Skip if no matching units found
        if not syncSet:
            continue
        # Total capacity
        total_cap = sum(item.sgn for item in syncSet) #total apparent capacity
        total_ac_cap = sum((item.sgn * item.cosn) for item in syncSet) #total active capacity
        # Store capacity in first row
        df_cap.loc[0, energyName] = total_cap #append capacity to first and sec row
        df_cap.loc[1, energyName] = total_ac_cap
#Calculate total load
total_load = 0        
for load in loads: #iterate through loads
    if load.outserv == 0: #if connected
        total_load += load.plini #sum loads
app.PrintPlain(total_load)
#Find maximum active power energy share for each energy type
df_cap.loc[2] = (df_cap.loc[1]*100/total_load) 

# Print results
app.PrintPlain(df_cap)
app.PrintPlain(df_cap.loc[0])
app.PrintPlain(df_cap.loc[1])
app.PrintPlain(df_cap.loc[2])

#Read generator values
gen_df = pd.read_csv("Historic GB data.csv")
#gen_df.drop(gen_df.index[280512:], inplace=True) #drop years 2025

app.PrintPlain("Total generation rows = " + str(len(gen_df)))
#247675

#CRITERIA OF MAXIMUM ENERGY PERCENTAGE
limits = {
    "HYDRO_perc": 2.584773,
    "STORAGE_perc": 1.432173,
    "GAS_perc": 71.064955,
    "NUCLEAR_perc": 11.074902,
    "BIOMASS_perc": 5.497144,
    "OTHER_perc": 4.161784,
    "WIND_perc": 70.581048,
    "IMPORTS_perc": 33.321613,   # HVDC treated as imports
    "SOLAR_perc": 4.736517,
    }
df_fitted = gen_df.copy() #Create copies of a dataframes
mask = pd.Series(True, index=df_fitted.index) #create a bit mask of 1s

for col, limit in limits.items(): #iterate through limits
    if col in df_fitted.columns: #look for column in dataframe
        mask &= df_fitted[col] <= limit #AND mask with values under the limit
        #new mask made
df_fitted = df_fitted[mask] #save df_fitted with mask
df_fitted = df_fitted[df_fitted["COAL"] == 0] #remove rows with coal!=0

#create new files with filtered results
df_fitted.to_csv("Fitted Gen DF.csv") 
df_fitted.to_excel("Fitted Gen DF.xlsx")

#check number of possible samples
app.PrintPlain(str(len(df_fitted)))

#Create a new index
df_fitted = df_fitted.reset_index(drop=True)



#GET 1ST TWO TEST VALUES 0 - 204
genTest_df = df_fitted.iloc[50:51]

#GENERATOR SETS
# RESET ALL GENERATOR OUTPUTS
for gen in syn_machines:
    gen.pgini = 0


for gen in stat_machines:
    gen.pgini = 0

#GET FIRST ROW OF GENTEST_DF, set
for index, row in genTest_df.iterrows():
    genSet.clear()
    gen_row = genTest_df.loc[index] #The generation row
    for col in genTest_df.columns:
        if (col.endswith("_perc")):
            energyName = col.replace("_perc","").capitalize()
            if energyName in ["Generation"]: #skip wind and solar
                continue
            perc_value = gen_row[col] #get percentage value
            genSet.append(perc_value) #add to check perc sum
            tot_gen = (perc_value/100) * abs(total_load) #find total generated in MW
            app.PrintPlain("Total power injection" + str(tot_gen)) #This works
            
            #HANDLE IMPORTS
            imports.clear()
            if energyName == ("Imports"):
                for gen in stat_machines:
                    if "DC Link" in gen.loc_name or "HVDC" in gen.loc_name:
                        if gen.outserv == 0: #check out of service
                            imports.append(gen) #make a list of imports machines
                if len(imports) == 0:
                    continue
                total_rating = sum(gen.Pnom for gen in imports) #find total import rating
                app.PrintPlain("Total Import rating =" + str(total_rating))
                if (total_rating < tot_gen):
                    app.PrintPlain("OH NO Too much Injected Power!")
                    break
                for gen in imports:
                    actPow = (gen.Pnom/total_rating)*tot_gen
                    gen.pgini = actPow
                import_act_pow = sum(gen.pgini for gen in imports)
                app.PrintPlain("The total active power for imports is" + str(import_act_pow))
                continue
            
            #HANDLE WIND AND SOLAR
            machine_types.clear()
            if energyName in ["Wind", "Solar"]:
                for gen in stat_machines:
                    if energyName.lower() in gen.loc_name.lower():
                        if gen.outserv == 0:
                            machine_types.append(gen)

                if len(machine_types) == 0:
                    continue
                total_rating = sum((gen.Pnom) for gen in machine_types) 
                app.PrintPlain("Total synch rating for wind or solar is" + str(total_rating))#Sum machine rating
                
                #check total ratings added correctly
                if total_rating == 0:
                    continue
                for gen in machine_types:
                    actPow = (gen.Pnom/total_rating) * tot_gen
                    app.PrintPlain("Active wind/solar loop is" + str(actPow))
                    gen.pgini = actPow #update active power
                mac_act_pow = sum(gen.pgini for gen in machine_types)
                app.PrintPlain("The total active power for machines is" + str(mac_act_pow))
                total_generation = sum(genSet)
                app.PrintPlain("The generation percentage is" +str(total_generation))
                continue
            #SYNCHRONOUS MACHINES    
            machine_types.clear()
            for gen in syn_machines:
                if energyName.lower() in gen.loc_name.lower():
                    if gen.outserv == 0:
                        machine_types.append(gen)

            if len(machine_types) == 0:
                continue
            total_rating = sum((gen.Pnom) for gen in machine_types) 
            app.PrintPlain("Total synch rating is" + str(total_rating))#Sum machine rating
            
            #check total ratings added correctly
            if total_rating == 0:
                continue
            for gen in machine_types:
                actPow = (gen.Pnom/total_rating) * tot_gen
                app.PrintPlain("Active loop is" + str(actPow))
                gen.pgini = actPow #update active power
            mac_act_pow = sum(gen.pgini for gen in machine_types)
            app.PrintPlain("The total active power for machines is" + str(mac_act_pow))
            total_generation = sum(genSet)
            app.PrintPlain("The generation percentage is" +str(total_generation))
            
#Loading DF:
# =============================================================================
# 
#      
#         if (col == "Wind_perc"):
#             wind_value = gen_row[col] #get value of onshore wind
#             wind_inj = (wind_value/100) * abs(total_load) #get percentage of wind injected
#             #create set with wind machines
#             wind_mac.clear()
#             for stat_gen in stat_machines:
#                 if "Wind" in stat_gen.loc_name:
#                     if stat_gen.outserv == 0:
#                         wind_mac.append(stat_gen) #add wind generator to the list
#             wind_rating = sum(stat_gen.Pnom for stat_gen in wind_mac)
#             app.PrintPlain("Wind rating is" + str(wind_rating))
#             for stat_gen in wind_mac:
#                 act_pow = (stat_gen.Pnom / wind_rating) * wind_inj
#                 app.PrintPlain("Active wind loop is" + str(act_pow))
#                 stat_gen.pgini = act_pow
#             wind_act_pow = sum(stat_gen.pgini for stat_gen in wind_mac)
#             app.PrintPlain("The total active power for wind is" + str(wind_act_pow))
#             
#         if (col=="Solar_perc"):
#             solar_value = gen_row[col] #get value of onshore wind
#             solar_inj = (solar_value/100) * abs(total_load)
#             #create set with wind machines
#             solar_mac.clear()
#             for stat_gen in stat_machines:
#                 if "Solar" in stat_gen.loc_name:
#                     if stat_gen.outserv == 0:
#                         solar_mac.append(stat_gen) #add wind generator to the list
#             solar_rating = sum(stat_gen.Pnom for stat_gen in solar_mac)
#             app.PrintPlain("Solar rating is" + str(solar_rating))
#             for stat_gen in solar_mac:
#                 act_pow = (stat_gen.Pnom / solar_rating) * solar_inj
#                 app.PrintPlain("Active solar loop is" + str(act_pow))
#                 stat_gen.pgini = act_pow
#             solar_act_pow = sum(stat_gen.pgini for stat_gen in solar_mac)
#             app.PrintPlain("The total active power for solar is" + str(solar_act_pow))
# =============================================================================
             
total_gen = sum(gen.pgini for gen in syn_machines) + sum(gen.pgini for gen in stat_machines)#total generation
app.PrintPlain("TOTAL GENERATION= " + str(total_gen))
