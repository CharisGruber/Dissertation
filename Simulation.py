#IMPORTS
#Import powerfactory, pandas and numpy
import powerfactory as pf
import pandas as pd
import numpy as np
import matplotlib as plt

#DIgSILENT PowerFactory Python COM API
#connect to powerfactory app
app = pf.GetApplication()

#print line to check it is connected
app.PrintPlain("Hello Manchester! The script is running.")
#project has already been activated.

#CREATE COMMANDS from study case
ldf = app.GetFromStudyCase("ComLdf")
initCond = app.GetFromStudyCase("ComInc")
run = app.GetFromStudyCase("ComSim")
export = app.GetFromStudyCase("ASCII Result Export.ComRes")

#GET TEST GENERATOR OBJECT
 #set active power of wind generator to 600 MW
gen = app.GetCalcRelevantObjects("Z01 Wind.ElmGenstat")[0] #Name of gen
gen.pgini = 600.0 #set the active power to 600 MW

# RUN THE LOAD FLOW
ldf.Execute()

#RUN INITIAL CONDITIONS
initCond.tstop = 15 #set time to 15 seconds
test = initCond.Execute()
#Test to see if initial conditions ran
if test == 0:
    app.PrintPlain("Initial Conditions: SUCCESS")
else:
    app.PrintPlain("Initial Conditions didn't work")
    
#SET GENERATOR TRIP EVENT MANUALLY IN POWERFACTORY

#RUN SIMULATION
run.tstop = 15.0 # set stop time to 15 seconds
run.iopt_store = 1  #ensure the full storage
run.Execute() #execute run

#EXPORT RESULTS
export.Execute()
df = pd.read_csv("results_file.csv")
app.PrintPlain(df)

