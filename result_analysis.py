# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 17:23:14 2026

@author: chari


1) ADD ZONAL STABILITY FILES IN THE SECTION LISTED AS """"""""""""""""""

2) SAVED PLOTS CAN BE FOUND UNDER THESE NAMES:
    
    "Stable_RoCoF_Subplots.png"
    "Unstable_RoCoF_Subplots.png"
    "Binned_RoCoF_Subplots.png"
    "Stability_Ratio_Subplots.png"
    "Standard_dev_subplots.png"
    "Zonal_dev_subplots.png"

3) SAVED REGRESSION ANALYSIS CAN BE FOUND UNDER THE NAME:
    
    "RoCoF_Model_Metrics.csv"

"""




#Imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

#Read Results file
df1 = pd.read_csv("Zonal stability Results - Zone 1 20%.csv")
df2 = pd.read_csv("Zonal stability Results - Zone 4 20%.csv")
df3 = pd.read_csv("Zonal stability Results - Zone 8 20%.csv")
df4 = pd.read_csv("Zonal stability Results - Zone 17 20%.csv")
df5 = pd.read_csv("Zonal stability Results - Zone 28 20%.csv")
df_COI = pd.read_csv("Zonal stability Results - Zone 1 COI.csv")

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

#Create dictionary for dataframes
df_frame = {
            'Zone 01': df1,
            'Zone 04': df2,
            'Zone 08': df3,
            'Zone 17': df4,
            'Zone 28': df5,
            'COI': df_COI}
metrics_container = []
fig_stable, axes_stable = plt.subplots(2, 3, figsize=(18, 10))
axes_stable = axes_stable.flatten()

fig_unstable, axes_unstable = plt.subplots(2, 3, figsize=(18, 10))
axes_unstable = axes_unstable.flatten()

fig_binned, axes_binned = plt.subplots(2, 3, figsize=(18, 10))
axes_binned = axes_binned.flatten()

fig_ratio, axes_ratio = plt.subplots(2, 3, figsize=(18, 10))
axes_ratio = axes_ratio.flatten()

fig_sensitivity, axes_sens = plt.subplots(2, 3, figsize=(18, 10))
axes_sens = axes_sens.flatten()

fig_std, axes_std = plt.subplots(2, 3, figsize=(18, 10))
axes_std = axes_std.flatten()

fig_zonal_spread, axes_zonal_spread = plt.subplots(2, 3, figsize=(18, 10))
axes_zonal_spread = axes_zonal_spread.flatten()

plot_idx_rocof = 0
plot_idx_bins = 0 
plot_idx_ratio = 0
plot_idx_unstable = 0
plot_idx_sens = 0
plot_idx_std = 0
plot_idx_zonal_spread = 0
for zoneKey, df in df_frame.items():
    #Renewable energy is Solar, Wind, Hydro and Biomass
    df["Total RENEWABLE_perc"] = pd.to_numeric(df["WIND_perc"]) + pd.to_numeric(df["HYDRO_perc"]) + pd.to_numeric(df["BIOMASS_perc"]) + pd.to_numeric(df["SOLAR_perc"])
    df["INVERTER-BASED RENEWABLE_perc"] = pd.to_numeric(df["WIND_perc"]) + pd.to_numeric(df["SOLAR_perc"])
    max_renew_perc = np.max(df["Total RENEWABLE_perc"])
    min_renew_perc = np.min(df["Total RENEWABLE_perc"])
    max_IBR_perc = np.max(df["INVERTER-BASED RENEWABLE_perc"])
    min_IBR_perc = np.min(df["INVERTER-BASED RENEWABLE_perc"])
    print(str(max_renew_perc) +"   "+ str(min_renew_perc))
    print(str(max_IBR_perc) + "     " + str(min_IBR_perc))
    
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
    df_fitted = df.copy() #Create copies of a dataframes
    mask = pd.Series(True, index=df_fitted.index) #create a bit mask of 1s
    
    for col, limit in limits.items(): #iterate through limits
        if col in df_fitted.columns: #look for column in dataframe
            mask &= df_fitted[col] <= limit #AND mask with values under the limit
            #new mask made
    df_fitted = df_fitted[mask] #save df_fitted with mask
    df_fitted = df_fitted[df_fitted["COAL"] == 0] #remove rows with coal!=0
        
    df = df_fitted #after filtering is applied to 2026 to reduce data concentration
    
    #Max renewable perc: 71.68% and Min renewable percentage: 10.81%
    # 10-20, 20-30, 30-40, 40-50, 50-60, 60-70 and 70-80, 7 bins
    if zoneKey == 'COI':
        #COI stability criteria
        df1 = df.copy()
        df1 = df1[(df1["COI Nadir"] > 49.5) & (abs(df1["COI RoCoF"]) < 0.5)]
        print(len(df))
        #INERTIA VS RENEWABLES
        plt.figure(figsize=(9,6)) #The figure size
        plt.scatter(
            df1["INVERTER-BASED RENEWABLE_perc"],
            df1[" Effective Inertia "],
            color= 'red',
            s=18,
            alpha=0.65,
            edgecolors='black',
            linewidths=0.2
        )
        
        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.xlabel("Inverter-Based Renewable Penetration (%)", fontdict=label_fontdict)
        plt.ylabel("Effective Inertia (s)", fontdict = label_fontdict)
        plt.title(
            "System Effective Inertia vs Inverter-Based Renewable Penetration", 
        fontdict={'family': 'Calibri', 'weight': 'bold', 'size': 16})
        plt.grid()
        tick_values = np.arange(0, 70, 5)
        plt.xticks(tick_values)
        plt.tight_layout()
        plt.savefig('Effective Inertia vs Renewable.png', dpi=300)

        #ROCOF VS INERTIA
        plt.figure(figsize=(9,6))
        plt.scatter(
            df1[" Effective Inertia "],
            df1["COI RoCoF"],
            color= 'red',
            s=18,
            alpha=0.65,
            edgecolors='black',
            linewidths=0.2  
            )
        
        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.xlabel("Effective Inertia", fontdict=label_fontdict)
        plt.ylabel("COI RoCoF (Hz/s)", fontdict = label_fontdict)
        plt.title(
            "COI RoCoF vs System Effective Inertia", 
        fontdict={'family': 'Calibri', 'weight': 'bold', 'size': 16})
        plt.grid()
        tick_values = np.arange(0, 5)
        plt.xticks(tick_values, fontname="Calibri")
        plt.tight_layout()
        plt.savefig('COI ROCOF vs Inertia.png', dpi=300)

        #ROCOF VS RENEWABLES
        plt.figure(figsize=(9,6))
        plt.scatter(
            df1["INVERTER-BASED RENEWABLE_perc"],
            df1["COI RoCoF"],
            color= 'red',
            s=18,
            alpha=0.65,
            edgecolors='black',
            linewidths=0.2  
            )
        
        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.xlabel("Inverter-Based Renewable Penetration (%)", fontdict=label_fontdict)
        plt.ylabel("COI RoCoF (Hz/s)", fontdict = label_fontdict)
        plt.title(
            "COI RoCoF vs Inverter-Based Renewable Penetration (%)", 
        fontdict={'family': 'Calibri', 'weight': 'bold', 'size': 16})
        plt.grid()
        tick_values = np.arange(0, 70, 5)
        plt.xticks(tick_values, fontname="Calibri")
        plt.tight_layout()
        plt.savefig('COI ROCOF vs RES.png', dpi=300)
        
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))  # wider figure for side-by-side

        label_fontdict = {'family': "Calibri", 'size': 14}
        title_fontdict = {'family': 'Calibri', 'weight': 'bold', 'size': 16}
        
        # COI RoCoF vs Inertia

        axes[0].scatter(
            df1[" Effective Inertia "],
            df1["COI RoCoF"],
            color='red',
            s=18,
            alpha=0.65,
            edgecolors='black',
            linewidths=0.2
        )
        
        axes[0].set_xlabel("Effective Inertia", fontdict=label_fontdict)
        axes[0].set_ylabel("COI RoCoF (Hz/s)", fontdict=label_fontdict)
        axes[0].set_title(
            "COI RoCoF vs System Effective Inertia",
            fontdict=title_fontdict
        )
        axes[0].grid()
        axes[0].set_xticks(np.arange(0, 5))

        
     
        # COI RoCoF vs RES
        axes[1].scatter(
            df1["INVERTER-BASED RENEWABLE_perc"],
            df1["COI RoCoF"],
            color='red',
            s=18,
            alpha=0.65,
            edgecolors='black',
            linewidths=0.2
        )
        
        axes[1].set_xlabel(
            "Inverter-Based Renewable Penetration (%)",
            fontdict=label_fontdict
        )
        axes[1].set_ylabel("COI RoCoF (Hz/s)", fontdict=label_fontdict)
        axes[1].set_title(
            "COI RoCoF vs Inverter-Based Renewable Penetration (%)",
            fontdict=title_fontdict
        )
        axes[1].grid()
        axes[1].set_xticks(np.arange(0, 70, 5))
        
        
        plt.tight_layout()
        plt.savefig("COI_RoCoF_Comparison.png", dpi=300)
     
        
        #NADIR VS INERTIA
        plt.figure(figsize=(9,6))
        plt.scatter(
            df1[" Effective Inertia "],
            df1["COI Nadir"],
            color= 'red',
            s=18,
            alpha=0.65,
            edgecolors='black',
            linewidths=0.2  
            )
        
        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.xlabel("Effective Inertia", fontdict=label_fontdict)
        plt.ylabel("COI Nadir (Hz)", fontdict = label_fontdict)
        plt.title(
            "COI Nadir vs System Effective Inertia", 
        fontdict={'family': 'Calibri', 'weight': 'bold', 'size': 16})
        plt.grid()
        tick_values = np.arange(0, 5)
        plt.xticks(tick_values, fontname="Calibri")
        plt.tight_layout()
        plt.savefig('COI NADIR vs Inertia.png', dpi=300)

    
    else:
        #ZONAL CASE
        
        zones = ["Zone 01", "Zone 04", "Zone 08", "Zone 17", "Zone 28"]
        #Count the number of cases in each region.
        plt.figure(figsize =(9,6))
        colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
        df_new = df.copy()
        
    
        #Mark the turning point for an increase in RoCoF
        #Mark the turning point for an increase in RoCoF
        turning_point1 = 20
        turning_point2 = 40 #The percentage of IBR that cause RoCoF to increase
        #Make a mask to create a 
        mask0 = (df_new["INVERTER-BASED RENEWABLE_perc"] < turning_point1)
        mask1 = (df_new["INVERTER-BASED RENEWABLE_perc"] > turning_point1) & \
                (df_new["INVERTER-BASED RENEWABLE_perc"] < turning_point2)
        mask2 = (df_new["INVERTER-BASED RENEWABLE_perc"] >= turning_point2)
        color_map = {
        "Zone 01": "tab:blue",
        "Zone 04": "tab:orange", 
        "Zone 08": "tab:green",
        "Zone 17": "tab:red",
        "Zone 28": "tab:purple"}
        
        #STABILITY CRITERIA HERE
        
        #condition 1, all results must be stable in all zones
        stability_cols = [f"Stability {z}" for z in zones]
        all_stable = df[stability_cols].eq(1).all(axis=1)
        # Condition 2: all nadirs higher than 49.5 Hz
        nadir_cols = [f"Nadir {z}" for z in zones]
        nadir_ok = (df[nadir_cols] >= 49.5).all(axis=1)
        stability_mask = all_stable & nadir_ok
        df_stable = df[stability_mask].copy()
        df_unstable = df[~stability_mask].copy()
        
        #RAW ROCOF INDIVIDUAL
        plt.figure(figsize=(9,6))
        
        for zone in zones:
            #PLT DATA
            plt.scatter(
                df_stable["INVERTER-BASED RENEWABLE_perc"],
                df_stable[f"Min RoCoF {zone}"],
                label=zone,
                color=color_map[zone],
                s=18,
                alpha=0.65,
                edgecolors='black',
                linewidths=0.2)

            #Sort data first (IMPORTANT for gradients)
            df_stable = df_stable.sort_values("INVERTER-BASED RENEWABLE_perc")
            #Create the mask to seperate data
            x2, y2 = df_stable.loc[mask2,"INVERTER-BASED RENEWABLE_perc"], df_stable.loc[mask2, f"Min RoCoF {zone}"]
            valid2 = x2.notna() & y2.notna() #remove nans
            x2, y2 = x2[valid2], y2[valid2]
            #calculate linear fit in data
            grad2, inter2 = np.polyfit(x2, y2, 1)
            # quadratic fit in data
            coeffs_quad = np.polyfit(x2, y2, 2)
            poly_quad = np.poly1d(coeffs_quad) #gets coefficients
            
            # Generate smooth fit and evenly spaced lines
            x2_fit = np.linspace(x2.min(), x2.max(), 200) #200 evenly spaced variables
            y2_fit_quad = poly_quad(x2_fit) #find y values from x
            
            # This is the R2 calculation for coefficient of determination
            y_pred = poly_quad(x2)
            ss_res = np.sum((y2 - y_pred)**2)
            ss_tot = np.sum((y2 - np.mean(y2))**2)
            r2 = 1 - (ss_res / ss_tot) #coefficient of determination
            #Print this
            print(f"{zoneKey} | {zone} | R^2 = {r2:.3f}")
            # plot trend lines on the graphs
            plt.plot(x2_fit, y2_fit_quad, linestyle='--', linewidth=1.5, color=color_map[zone])
            #calculate correlation, the sqrt of coeff of determination
            corr = np.corrcoef(x2, y2)[0,1]
            print(f"{zoneKey} | {zone} | Correlation = {corr:.3f}")
            
            #CERTAINTY CALCULATION
            residuals = y2 - y_pred #predicted vs actual y value
            std_err = np.std(residuals) #standard deviation of the predicted gap
            
            upper = y2_fit_quad + std_err #Plus and minus the standard deviation gap
            lower = y2_fit_quad - std_err
            #Show where the values could fall on the plot
            plt.fill_between(x2_fit, lower, upper, alpha=0.15)
            #Append these values to the set
            metrics_container.append({
            "Disturbance Zone": zoneKey,
            "Zone": zone,
            "Gradient": grad2,
            "Correlation (r)": corr,
            "R^2": r2,
            "Standard Deviation": std_err
        })
        
        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.xlabel("Inverter-Based Resource (IBR) Penetration (%)", fontdict=label_fontdict)
        plt.ylabel("Minimum RoCoF (Hz/s)", fontdict = label_fontdict)
        plt.title(
            f"{zoneKey} Disturbance: RoCoF vs Inverter-Based Resource (IBR) Penetration (%)", 
            fontdict={'family': 'Calibri', 'weight': 'bold', 'size': 16})
        plt.legend(title="Zones", frameon=True)
        plt.grid(True, color='black', linestyle='--', linewidth=0.6, alpha=0.5)
        tick_values = np.arange(0, 70, 5)
        plt.xticks(tick_values, fontname="Calibri")
        plt.tight_layout()
        plt.savefig(f'ROCOF {zoneKey} - No lines.png', dpi=300)

        
        #Create the 5 subplots for RoCoF
        ax = axes_stable[plot_idx_rocof]
        plot_idx_rocof += 1 #Add the index
        
        for zone in zones:
            
            ax.scatter(
                df_stable["INVERTER-BASED RENEWABLE_perc"],
                df_stable[f"Min RoCoF {zone}"],
                color=color_map[zone],
                s=18,
                alpha=0.65,
                edgecolors='black',
                linewidths=0.2
            )
            ax.set_xlabel("IBR Penetration (%)", fontsize=10)
            ax.set_ylabel("Minimum RoCoF (Hz/s)", fontsize=10)
            ax.grid()
            ax.set_title(f"Disturbance: {zoneKey}", fontsize=12, fontweight='bold')
            x2, y2 = df_stable.loc[mask2,"INVERTER-BASED RENEWABLE_perc"], df_stable.loc[mask2, f"Min RoCoF {zone}"]
            
            # Remove NaNs
            valid2 = x2.notna() & y2.notna()
            x2 = x2[valid2]
            y2 = y2[valid2]
            
            # linear fit in data
            grad2, inter2 = np.polyfit(x2, y2, 1)
            
            # quadratic fit in data
            coeffs_quad = np.polyfit(x2, y2, 2)
            poly_quad = np.poly1d(coeffs_quad)
            
            # Generate smooth fit
            x2_fit = np.linspace(x2.min(), x2.max(), 200)
            y2_fit_quad = poly_quad(x2_fit)
            
            # This is the R2 calculation for coefficient of determination
            y_pred = poly_quad(x2)
            ss_res = np.sum((y2 - y_pred)**2)
            ss_tot = np.sum((y2 - np.mean(y2))**2)
            r2 = 1 - (ss_res / ss_tot)
            
            # plot lines on the graphs
            ax.plot(x2_fit, y2_fit_quad, linestyle='--', linewidth=1.5, color=color_map[zone])
            #CERTAINTY CALCULATION
            residuals = y2 - y_pred #predicted vs actual y value
            std_err = np.std(residuals) #standard deviation of the predicted gap
            
            upper = y2_fit_quad + std_err #Plus and minus the standard deviation gap
            lower = y2_fit_quad - std_err
            #Show where the values could fall on the plot
            ax.fill_between(x2_fit, lower, upper, alpha=0.15)
        
        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.legend(title="Zones", frameon=True)

        tick_values = np.arange(0, 70, 5)
        plt.xticks(tick_values, fontname="Calibri")
        plt.tight_layout()

        #Unstable result - PLOT RAW UNSTABLE RESULTS
        plt.figure(figsize=(9,6))
        for zone in zones:
            plt.scatter(
            df_unstable["INVERTER-BASED RENEWABLE_perc"],
            df_unstable[f"Min RoCoF {zone}"],
            label=zone,
            color=color_map[zone],
            s=18,
            alpha=0.65,
            edgecolors='black',
            linewidths=0.2)
           
       
        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.xlabel("Inverter-Based Resource (IBR) Penetration (%)", fontdict=label_fontdict)
        plt.ylabel("Min RoCoF (Hz/s)", fontdict = label_fontdict)
        plt.title(
            f"{zoneKey} Disturbance: RoCoF vs Inverter-Based Resource (IBR) Penetration (%) for Unstable Cases", 
            fontdict={'family': 'Calibri', 'weight': 'bold', 'size': 16})
        plt.legend(title="Zones", frameon=True)
        plt.grid()
        tick_values = np.arange(0, 70, 5)
        plt.xticks(tick_values, fontname="Calibri")
        plt.tight_layout()
        plt.savefig(f'ROCOF {zoneKey} - Unstable.png', dpi=300)
        
        #PLOT GROUPED UNSTABLE RESULT
        ax = axes_unstable[plot_idx_unstable]
        plot_idx_unstable += 1
        
        for zone in zones:
                
            ax.scatter(
                df_unstable["INVERTER-BASED RENEWABLE_perc"],
                df_unstable[f"Min RoCoF {zone}"],
                color=color_map[zone],
                s=18,
                alpha=0.65,
                edgecolors='black',
                linewidths=0.2
            )
        
        ax.set_title(f"Disturbance: {zoneKey}", fontsize=12, fontweight='bold')
        ax.set_xlabel("IBR Penetration (%)", fontsize=10)
        ax.set_ylabel("Minimum RoCoF (Hz/s)", fontsize=10)
        ax.grid()
        tick_values = np.arange(0, 70, 5)
        ax.set_xticks(tick_values)
        
        
        #Stnadard deviation ROCOF plot INDIVIDUAL
        plt.figure(figsize=(9,6))
        bins = np.arange(0, 75, 5) #Create frequency bins
        
        for zone in zones:
            
            if len(df_stable) < 10:
                continue
        
            df_stable["RES_bin"] = pd.cut(
                df_stable["INVERTER-BASED RENEWABLE_perc"],
                bins=bins
            ) #split stable data into bins
            #Find grouped standard deviation
            grouped = df_stable.groupby("RES_bin")[f"Min RoCoF {zone}"].std()
            #Calculate the median  value for each bin
            bin_centres = np.array([b.mid for b in grouped.index])
            spread = grouped.values #the spread are the values in each bin
            #Plot the line graph
            plt.plot(
                bin_centres,
                spread,
                marker='o',
                label=zone,
                color=color_map[zone]
            )
        
        plt.xlabel("IBR Penetration (%)")
        plt.ylabel("RoCoF Standard Deviation")
        plt.title(f"{zoneKey} Disturbance: Increase in RoCoF Variability with Renewable Penetration")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig("RoCoF_Spread_vs_RES.png", dpi=300)
        
        #Grouped standard deviation plots
        ax = axes_std[plot_idx_std]
        plot_idx_std += 1
        for zone in zones:
            if len(df_stable) < 10:
                continue
        
            df_stable["RES_bin"] = pd.cut(
                df_stable["INVERTER-BASED RENEWABLE_perc"],
                bins=bins
            ) #split stable data into bins
            #Find grouped standard deviation
            grouped = df_stable.groupby("RES_bin")[f"Min RoCoF {zone}"].std()
            #Calculate the median  value for each bin
            bin_centres = np.array([b.mid for b in grouped.index])
            spread = grouped.values #the spread are the values in each bin
        
            ax.plot(
                bin_centres,
                spread,
                marker='o',
                label=zone,
                color=color_map[zone]
            )
        
        ax.set_title(f"Disturbance: {zoneKey}", fontsize=12, fontweight='bold')
        ax.set_xlabel("IBR Penetration (%)", fontsize=10)
        ax.set_ylabel("Standard Deviation of Minimum RoCoF (Hz/s)", fontsize=10)
        ax.grid()
        tick_values = np.arange(0, 70, 5)
        ax.set_xticks(tick_values)
    
        #MEAN ROCOF
        plt.figure(figsize=(9,6))

        for zone in zones:
                    
            # Skip if not enough data
            if len(df_stable) < 10:
                print(f"{zone} skipped (not enough data)")
                continue
        
            # Create RES bins
            df_stable["RES_bin"] = pd.cut(
                df_stable["INVERTER-BASED RENEWABLE_perc"],
                bins=10)
            # Group by bin and compute mean RoCoF, aggregated data
            df_grouped = df_stable.groupby("RES_bin")[f"Min RoCoF {zone}"].agg(['mean','std'])
            #find middle data
            bin_centre = df_grouped.index.map(lambda x: x.mid)
            #Plot errorbars
            plt.errorbar(
                bin_centre,
                df_grouped['mean'],
                yerr=df_grouped['std'],
                marker='o',
                capsize=3,
                label=zone,
                color=color_map[zone]
            )
        

        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.xlabel("Inverter-Based Resource (IBR) Penetration (%)", fontdict=label_fontdict)
        plt.ylabel("Mean Minimum RoCoF (Hz/s)", fontdict=label_fontdict)
        plt.title(
            f"{zoneKey} Disturbance: Mean RoCoF vs Renewable Penetration (Binned)", 
            fontdict={'family': 'Calibri', 'weight': 'bold', 'size': 16})
        plt.legend(title="Zones")
        plt.grid()
        plt.tight_layout()
        plt.savefig(f'Binned_RoCoF_{zoneKey}.png', dpi=300)
 
        #PLOT GROUPED trend of MEAN ROCOF
        ax = axes_binned[plot_idx_bins]
        plot_idx_bins+=1
        for zone in zones:
            df_stable = df[(df[f"Stability {zoneKey}"] == 1) & 
                           (df[f"Nadir {zone}"] >= 49.5)].copy()
        
            if len(df_stable) < 10:
                continue
        
            df_stable["RES_bin"] = pd.cut(
                df_stable["INVERTER-BASED RENEWABLE_perc"], bins=10
            )
        
            # Group by bin and compute mean RoCoF
            df_grouped = df_stable.groupby("RES_bin")[f"Min RoCoF {zone}"].agg(['mean','std'])

            bin_centres = df_grouped.index.map(lambda x: x.mid)
            #PLOT ERRORBARS
            ax.errorbar(
                bin_centres,
                df_grouped['mean'],
                yerr=df_grouped['std'],
                marker='o',
                capsize=3,
                label=zone,
                color=color_map[zone]
            )
        
        ax.set_title(f"{zoneKey}", fontsize=12, fontweight='bold')
        ax.set_xlabel("IBR Penetration (%)", fontsize=10)
        ax.set_ylabel("Mean Minimum RoCoF (Hz/s)", fontsize=10)
        ax.grid()
        
        
        #ZONAL SPEAD! tHIS IS IMPORTNAT
        plt.figure(figsize=(9,6))
        
        rocof_cols = [f"Min RoCoF {z}" for z in zones] #group rocof column
        df_stable["RoCoF_mean"] = df_stable[rocof_cols].mean(axis=1)
        #Calculate the rolling mean
        
        for zone in zones: #calculate the difference in each column from the mean
            df_stable[f"Dev {zone}"] = abs(
                df_stable[f"Min RoCoF {zone}"] -df_stable["RoCoF_mean"]
            )
        
        #Create data bins and plot
        bins = np.arange(0, 75, 5)
        df_stable["RES_bin"] = pd.cut(df_stable["INVERTER-BASED RENEWABLE_perc"], bins)
        
        for zone in zones:
            #For each bin find the mean deviation from the frequency mean
            dev_mean = df_stable.groupby("RES_bin")[f"Dev {zone}"].mean()
            bin_centres = np.array([b.mid for b in dev_mean.index])
            #Plot deviation from the mean
            plt.plot(
                bin_centres,
                dev_mean.values,
                marker='o',
                label=zone,
                color=color_map[zone]
            )
        
        plt.xlabel("IBR Penetration (%)")
        plt.ylabel("Mean Absolute Deviation from System RoCoF")
        plt.title(f" {zoneKey} Disturbance: Zonal Divergence in RoCoF with Increasing Renewable Penetration")
        plt.legend(title="Zones")
        plt.grid()
        plt.tight_layout()
        plt.savefig("Zonal_Divergence_vs_RES.png", dpi=300)
        
        #ADD grouped ZONAL SPREAD RESULT
        ax_spread = axes_zonal_spread[plot_idx_zonal_spread]
        plot_idx_zonal_spread+=1
        rocof_cols = [f"Min RoCoF {z}" for z in zones] #group rocof column
        df_stable["RoCoF_mean"] = df_stable[rocof_cols].mean(axis=1)
        #Calculate the rolling mean
        
        for zone in zones: #calculate the difference in each column from the mean
            df_stable[f"Dev {zone}"] = abs(
                df_stable[f"Min RoCoF {zone}"] -df_stable["RoCoF_mean"]
            )
        
        #Create data bins and plot
        bins = np.arange(0, 75, 5)
        df_stable["RES_bin"] = pd.cut(df_stable["INVERTER-BASED RENEWABLE_perc"], bins)
        for zone in zones:
            #For each bin find the mean deviation from the frequency mean
            dev_mean = df_stable.groupby("RES_bin")[f"Dev {zone}"].mean()
            bin_centres = np.array([b.mid for b in dev_mean.index])
            #Plot deviation from the mean
            ax_spread.plot(
                bin_centres,
                dev_mean.values,
                marker='o',
                label=zone,
                color=color_map[zone]
            )
        
        ax_spread.set_xlabel("IBR Penetration (%)")
        ax_spread.set_ylabel("Mean Absolute Deviation from System RoCoF (Hz/s)")
        ax_spread.set_title(f"Disturbance: {zoneKey}", fontsize=12, fontweight='bold')
        ax_spread.grid()
        
        plt.figure(figsize=(9,6))
        # Create bins
        bins = np.arange(0, 75, 5)
        df["RES_bin"] = pd.cut(df["INVERTER-BASED RENEWABLE_perc"], bins=bins)
        
        zones = ["Zone 01", "Zone 04", "Zone 08", "Zone 17", "Zone 28"]
        # Condition 1: all zones stable
        stability_cols = [f"Stability {z}" for z in zones]
        all_stable = df[stability_cols].eq(1).all(axis=1)
        
        # Condition 2: all nadirs higher than 49.5 Hz
        nadir_cols = [f"Nadir {z}" for z in zones]
        nadir_ok = (df[nadir_cols] >= 49.5).all(axis=1)
        
        df["System_Stable"] = all_stable & nadir_ok
        
        #THIS IS IMPORTANT
        total_counts = df.groupby("RES_bin").size()
        stable_counts = df[df["System_Stable"]].groupby("RES_bin").size()
        # Align bins
        stable_counts = stable_counts.reindex(total_counts.index, fill_value=0)
        # Stability ratio
        stability_ratio = stable_counts / total_counts
        # Bin centres
        bin_centres = total_counts.index.map(lambda x: x.mid)
        
        #plot graphs
        plt.bar(
            bin_centres,
            stability_ratio,
            width=4,   # matches 5% bins nicely
            color='black',
            alpha=0.7
        )
        ax.set_xlabel("Inverter_based Renewable percentage (%)", fontdict=label_fontdict)
        ax.set_ylabel("Mean Minimum RoCoF (Hz/s)", fontdict=label_fontdict)
        ax.set_title(f"Disturbance: {zoneKey}", fontsize=12, fontweight='bold')
        # Formatting
        label_fontdict = {'family':"Calibri", 'size': 14}
        plt.xlabel("Inverter-Based Renewable Penetration (%)", fontdict=label_fontdict)
        plt.ylabel("Fraction of Stable Cases", fontdict=label_fontdict)
        plt.title(
            f"System-Wide Stability {zoneKey} vs Renewable Penetration", 
            fontdict={'family': 'Calibri', 'weight': 'bold', 'size': 16}
        )
        
        plt.ylim(0, 1)
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig(f'System_Stability_Ratio {zoneKey}.png', dpi=300)

        #Plot stability ratio for 5 plot
        ax = axes_ratio[plot_idx_ratio]
        plot_idx_ratio+=1
        for zone in zones:
            bins = np.arange(0, 75, 5)
            df["RES_bin"] = pd.cut(df["INVERTER-BASED RENEWABLE_perc"], bins=bins)
            
            stability_cols = [f"Stability {z}" for z in zones]
            nadir_cols = [f"Nadir {z}" for z in zones]
            
            all_stable = df[stability_cols].eq(1).all(axis=1)
            nadir_ok = (df[nadir_cols] >= 49.5).all(axis=1)
            
            df["System_Stable"] = all_stable & nadir_ok
            
            total_counts = df.groupby("RES_bin").size()
            stable_counts = df[df["System_Stable"]].groupby("RES_bin").size()
            
            stable_counts = stable_counts.reindex(total_counts.index, fill_value=0)
            
            ratio = stable_counts / total_counts
            bin_centres = total_counts.index.map(lambda x: x.mid)
            
            ax.bar(bin_centres, ratio, width=4)
        ax.set_xlabel("Inverter-Based Renewable Penetration (%)", fontdict=label_fontdict)
        ax.set_ylabel("Fraction of Stable Cases", fontdict=label_fontdict)
        ax.set_title(f"Disturbance: {zoneKey}", fontsize=12, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.grid(axis='y')
        
   
legend_ax = axes_stable[5]
legend_ax.axis('off')

legend_ax.set_title("Zones", fontsize=12, fontweight='bold')

y_pos = np.linspace(0.8, 0.2, len(zones))

for i, zone in enumerate(zones):
    legend_ax.scatter(0.2, y_pos[i],
                      color=color_map[zone],
                      s=60,
                      edgecolors='black')
    
    legend_ax.text(0.35, y_pos[i],
                   zone,
                   fontsize=10,
                   va='center')

legend_ax.set_xlim(0, 1)
legend_ax.set_ylim(0, 1)

legend_ax = axes_unstable[5]
legend_ax.axis('off')

legend_ax.set_title("Zones", fontsize=12, fontweight='bold')

y_pos = np.linspace(0.8, 0.2, len(zones))

for i, zone in enumerate(zones):
    legend_ax.scatter(0.2, y_pos[i],
                      color=color_map[zone],
                      s=60,
                      edgecolors='black')
    
    legend_ax.text(0.35, y_pos[i],
                   zone,
                   fontsize=10,
                   va='center')

legend_ax.set_xlim(0, 1)
legend_ax.set_ylim(0, 1)


legend_ax = axes_binned[5]
legend_ax.axis('off')

legend_ax.set_title("Zones", fontsize=12, fontweight='bold')

y_pos = np.linspace(0.8, 0.2, len(zones))

for i, zone in enumerate(zones):
    legend_ax.scatter(0.2, y_pos[i],
                      color=color_map[zone],
                      s=60,
                      edgecolors='black')
    
    legend_ax.text(0.35, y_pos[i],
                   zone,
                   fontsize=10,
                   va='center')

legend_ax.set_xlim(0, 1)
legend_ax.set_ylim(0, 1)


axes_ratio[5].axis('off')

legend_ax = axes_sens[5]
legend_ax.axis('off')

legend_ax.set_title("Zones", fontsize=12, fontweight='bold')

y_pos = np.linspace(0.8, 0.2, len(zones))

for i, zone in enumerate(zones):
    legend_ax.scatter(0.2, y_pos[i],
                      color=color_map[zone],
                      s=60,
                      edgecolors='black')
    
    legend_ax.text(0.35, y_pos[i],
                   zone,
                   fontsize=10,
                   va='center')

legend_ax.set_xlim(0, 1)
legend_ax.set_ylim(0, 1)

legend_ax = axes_std[5]
legend_ax.axis('off')

legend_ax.set_title("Zones", fontsize=12, fontweight='bold')

y_pos = np.linspace(0.8, 0.2, len(zones))

for i, zone in enumerate(zones):
    legend_ax.scatter(0.2, y_pos[i],
                      color=color_map[zone],
                      s=60,
                      edgecolors='black')
    
    legend_ax.text(0.35, y_pos[i],
                   zone,
                   fontsize=10,
                   va='center')

legend_ax.set_xlim(0, 1)
legend_ax.set_ylim(0, 1)

legend_ax = axes_zonal_spread[5]
legend_ax.axis('off')

legend_ax.set_title("Zones", fontsize=12, fontweight='bold')

y_pos = np.linspace(0.8, 0.2, len(zones))

for i, zone in enumerate(zones):
    legend_ax.scatter(0.2, y_pos[i],
                      color=color_map[zone],
                      s=60,
                      edgecolors='black')
    
    legend_ax.text(0.35, y_pos[i],
                   zone,
                   fontsize=10,
                   va='center')

legend_ax.set_xlim(0, 1)
legend_ax.set_ylim(0, 1)

#Add figure titles for all subplots
fig_stable.suptitle(
    "Minimum RoCoF vs VRE Penetration for Stable Frequency Responses",
    fontsize=20,
    fontweight='bold'
)

fig_binned.suptitle(
    "Binned Mean Minimum RoCoF per zone vs Inverter-Based Resource Penetration (%)",
    fontsize=20,
    fontweight='bold'
)

fig_unstable.suptitle("Unstable Minimum RoCoF per zone vs Inverter-Based Resource  Penetration (%)",
    fontsize=20,
    fontweight='bold'
)
fig_unstable.tight_layout(rect=[0,0,1,0.95])


fig_ratio.suptitle(
    "System Stability Ratio vs Inverter-Based Resource Penetration (%)",
    fontsize=20,
    fontweight='bold'
)
fig_std.suptitle(
    "RoCoF Variability vs VRE Penetration",
    fontsize=20,
    fontweight='bold'
)

fig_zonal_spread.suptitle(
    "Zonal RoCoF Deviation from System Mean vs VRE Penetration",
    fontsize=20,
    fontweight='bold'
)
#Save figures
fig_stable.savefig("Stable_RoCoF_Subplots.png", dpi=300)
fig_unstable.savefig("Unstable_RoCoF_Subplots.png", dpi=300)
fig_binned.savefig("Binned_RoCoF_Subplots.png", dpi=300)
fig_ratio.savefig("Stability_Ratio_Subplots.png", dpi=300)
fig_std.savefig("Standard_dev_subplots.png", dpi=300)
fig_zonal_spread.savefig("Zonal_dev_subplots.png", dpi=300)
plt.show()

#Upload Regression data to data container
metrics_df = pd.DataFrame(metrics_container)
metrics_df.to_csv("RoCoF_Model_Metrics.csv", index=False)



