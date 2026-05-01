
This code repository displays all programs used to complete this Dissertation.

The PowerFactory Grid Stability Automation Suite is a toolset designed to evaluate power system resilience under high Inverter-Based Resource (IBR) penetration. It bridges the gap between historical generation data and dynamic simulation by automating the process of mapping real-world generation profiles onto a PowerFactory network model.

The software performs large-scale "what-if" scenarios, executing 624 of Root Mean Square (RMS) simulations to calculate critical stability metrics such as Rate of Change of Frequency (RoCoF), frequency nadir, and damping ratios. Its primary role is to provide a statistical foundation for understanding how displaced synchronous inertia impacts zonal and system-wide stability.

The suite operates as an external automation layer that controls the PowerFactory engine via its Python API. The workflow follows a linear data pipeline:
-Data Processing: Cleans and scales historical GB grid data (e.g., wind/solar percentages).
-Simulation Engine: Iteratively updates PowerFactory generator objects, runs load flows, and executes RMS simulations for specified disturbances.
-Stability Assessment: Extracts results to calculate specific metrics (Nadir, RoCoF) and classifies the response as stable, decaying, or growing.

Required Software:
DIgSILENT PowerFactory (Tested on version 2026).
Python 3.x (Must match the version compatible with your PowerFactory installation).

Dependencies:
Install the following Python libraries via pip:
pip install pandas numpy matplotlib scipy

Installation instructions:
Ensure the PowerFactory python folder is in your system environment variables (PATH).
Place the provided .py files into your PowerFactory script directory or a dedicated workspace.
Ensure the following input files are in the working directory:
df_fuel_ckan.csv (Raw historical data)
PowerFactory Project .pfd must be active and contain busbars named BB1.1.ElmTerm within designated Zones.

How to run the project:
1) Prepare Data: Run the pre-processing script (source 4) to generate Historic GB data.csv.
2) Activate Project: Open PowerFactory and activate the relevant study case and project.
3) Execute Simulation: Run the main simulation script (source 2 or source 3).
      The script will automatically detect synchronous and static generators.
      It will iterate through the filtered generation rows and print progress to the PowerFactory output window.
4) Analyse Results: Run the plotting script (source 5) to generate subplots of RoCoF and stability ratios.

Algorythms and Equations:
1) COI Centre-of-Inertia calculation to calculate COI frequency: $\frac{\sum H_i S_i f_i}{\sum H_i S_i}$
2) Active power Initialisation: $P_{total}^{inj} = S_{k}^{pu} \times P_{Load}$ then $P_i^{inj} = \frac{P_i^{lim}}{{P_{total}^{lim}}} \times  P_{total}^{inj}$ 
3) The calculation of RoCoF = $\frac{\Delta f}{dt}$

Known limits and improvements:
1) The spatial study code is known to have extremely long run time of completion. This code can take anywhere from 3 to 8 hours to run. Future improvements include narrowing run-time through a parallel completion of simulations.
2) The results and discussion code cannot save previous results files, and no version control exists. 

   
