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
from scipy.signal import find_peaks as fp

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

#SET REDUNDANT MACHINES TO ZERO
for stat_gen in stat_machines:
    if "Battery" in stat_gen.loc_name:
        stat_gen.pgini = 0 #set reactive and active power for BATT = 0
        stat_gen.qgini = 0
        
    if "Marine" in stat_machines:
        stat_gen.pgini = 0 #set reactive and active power for MAR = 0
        stat_gen.qgini = 0
#ADD COLUMNS TO DF 
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

stability_results = []

#Create a new index
df_fitted = df_fitted.reset_index(drop=True)
#GET 1ST TEST VALUES 0 - 204
genTest_df = df_fitted.iloc[:]
#GENERATOR SETS
# RESET ALL GENERATOR OUTPUTS to make active power 0


#GET FIRST ROW OF GENTEST_DF, set
for index, row in genTest_df.iterrows():
    for gen in syn_machines:
        gen.pgini = 0
    for gen in stat_machines:
        gen.pgini = 0
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
            
            
    total_gen = sum(gen.pgini for gen in syn_machines) + sum(gen.pgini for gen in stat_machines)#total generation
    app.PrintPlain("TOTAL GENERATION= " + str(total_gen))

#PART 2, RUN SIMULATION

#RUN LOAD FLOW
    
    #CALC METHOD:
    ldf.iopt_net = 0 #SET AC LOAD FLOW BALANCED POSITIVE SEQUENCE
    #Active power regulation:
    ldf.iPST_at = 0 #automatic adjustment of phase shifters
    ldf.iopt_plim = 1 #consider active power limits
    #Voltage and reactive power regulation
    ldf.iopt_at = 1 #consider automatic tap adjustment of transformers
    ldf.iopt_asht = 1 #consider automatic tap adjustment of shunt capacitor
    ldf.iopt_lim = 1 #consider reactive power limits
    #Temperature dependency of lines and cables
    ldf.iopt_tem = 0 #lines and cables at 20 degrees
    #load options
    ldf.iopt_pq = 1 #consider voltage dependency of loads
    
    ldf.iPbalancing = 4
    
    #execute load flow
    ldf.Execute()
    
    #RUN INITIAL CONDITIONS
    #RUN INITIAL CONDITIONS
    initCond.tstop = 15 #set time to 15 seconds
    test = initCond.Execute()
    #Test to see if initial conditions ran
    if test == 0:
        app.PrintPlain("Initial Conditions: SUCCESS")
    else:
        app.PrintPlain("Initial Conditions didn't work")
    
    #RUN SIMULATION
    run.tstop = 15.0 # set stop time to 15 seconds
    run.iopt_store = 1  #ensure the full storage
    run.Execute() #execute run
    
    #GET RESULTS
    
    #GET RID OF DIVERGENT RUNS HERE
    if (run.Execute()) != 0:
        app.PrintPlain("ERROR! RMS SIMULATION DID NOT CONVERGE!")
    else:
        app.PrintPlain("SUCESS! RMS SIMULATION CONVERGED!")
    
    #Export results
    export.Execute()
    result_df = pd.read_csv("results_file.csv")
    result_df = result_df.rename(columns=result_df.iloc[0]).iloc[1:].reset_index(drop=True)
    app.PrintPlain(result_df)
    #Next read data from dataframe to ensure convergence
    #convert data into values
    time = pd.to_numeric(result_df["Time in s"].values)
    freq = pd.to_numeric(result_df["Electrical Frequency in Hz"].values)
    peaks, _ = fp(freq) #find peaks in frequency response
    #If the peaks grow, the frequency response is unstable.
    peak_freq = freq[peaks] #Returns the frequency values
    peak_time = time[peaks]
    app.PrintPlain("Peaks are: " + str(peak_freq)) #RETURNS INDICIES OF PEAKS
    peak_freq = peak_freq[1:] #Remove first peak
    peak_time = peak_time[1:] #Remove first peak
    # fit linear trend for a lot of peaks
    if len(peak_freq) > 2:
        slope = np.polyfit(peak_time, peak_freq, 1)[0]
    else:
        slope = 0
    
    
    if slope > 0.0005:
        stability = 0
    else:
        stability = 1
    
    app.PrintPlain("Peak slope:" + str(slope) +"Stability is: " +str(stability))
    stability_results.append(stability)

app.PrintPlain(stability_results)
df_fitted["Stability"] = stability_results
df_fitted_stable = df_fitted.copy()
for index, row in df_fitted_stable.iterrows():
    if row["Stability"] == 0:
        df_fitted_stable.drop(row, axis=0, inplace=True)















