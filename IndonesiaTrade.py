
#PROJECT 4 - Center for Global Sustainability Indonesia trade visualization

#IndoNickel is a pivoted Excel sheet showing Indonesia’s top trade partner imports for several nickel harmonized system codes, per year. The code loops through the top 3 partners per HS code and plots them on a stacked bar chart. 

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

vals = pd.read_excel("IndoNickel.xlsx", header=1, engine='openpyxl')
vals = vals.drop(columns='Grand Total', errors='ignore')



hscodes = vals.iloc[:, 0].dropna().unique()
hscodes = [code for code in hscodes if code != 'Grand Total']

vals.iloc[:, 0] = vals.iloc[:, 0].ffill()

titles = {
    "7503": 'Nickel Waste',
    "260400": 'Nickel Ore/Concentrate',
    "282540": 'Nickel Oxide and Hydroxide',
    "283324": "Nickel Sulphate",
    "750110": "Nickel Matte",
    "750120": "Nickel Oxide Sinter",
    "750210": "Nickel - Not Alloyed",
    "720260": "Ferronickel",
    "381511": "Nickel Catalyst",
    "282735": "Nickel Chloride",
    "750400": "Nickel Powder and Flake"
}



for hscode in hscodes:
    hs = vals[vals.iloc[:, 0] == hscode].copy()
    hs = hs.set_index(hs.columns[1])
    hs = hs.drop(columns=hs.columns[0])
    hs.index = hs.index.str.replace("Other Asia, nes", "Taiwan")
    hs=hs.drop(index = "Indonesia", errors = 'ignore')
    country = hs.index
    colors = [] 
  
   
   

    
    vals_no_world = hs.drop(index='World', errors='ignore')
    countrytotals = vals_no_world.sum(axis=1)
    topcountries = countrytotals.sort_values(ascending=False).head(3).index.tolist()

    
    
    
    
    world = hs.loc['World']
    top3 = hs.loc[topcountries].sum()
    rest_of_world = world - top3
    rest_of_world[rest_of_world <=0] = np.nan


    plt.figure(figsize=(12, 6))

    countrycolors = {

    # Individually colored countries
    
    "Japan": "#ff7f0e",         # medium orange
    "Rep. of Korea": "#8c564b", # warm brown
    "Taiwan": "#e377c2",        # pink/magenta
    "China": "#1f77b4",          # muted blue
    "Germany": "black",        # black
    "India": "#17becf",          # cyan
    "Colombia": "#bcbd22",       # olive/yellow-green
    "Thailand": "#ffbb78",       # light orange
    "Singapore": "#d62728",      # red
    "Canada": "#2ca02c",         # bright green
    "Rest of World": "#9467bd",  # purple
    "Other": "#7f7f7f"           # neutral gray fallback
}

     
    maxvalue = vals_no_world.max().max()
   
    if maxvalue >= 1e9:
        scale = 1e9
        ylabel = "Import Quantity (Billion kg)"
    elif maxvalue >= 1e6:
        scale = 1e6
        ylabel = "Import Quantity (Million kg)"
    elif maxvalue >= 1e3:
        scale = 1e3
        ylabel = "Import Quantity (Thousand kg)"
    else: 
        scale = 1
        ylabel = "Import Quantity (kg)"

    
      
    ydata = hs.loc[topcountries]
        #Gets export data for top countires
    ydata.loc["Rest of World"] = rest_of_world
     #Adds rest of world to the stacked bar
    ydata=ydata.T
     #Transposes data (flips rows and columns)
    ydata=ydata / scale 
 
    colorlist = [countrycolors.get(c, "#e377c2") if c != "Other" else "#e377c2" for c in ydata.columns]

    
    
    ax = ydata.plot(
    kind='bar',
    stacked=True,
    
    width = 0.8,
    figsize=(12, 6),
    color = colorlist
    
)
    ax.grid(False)
        #Uses .plot to make bar graphs with stacking and no gridlines
    
    plt.xticks(rotation=45)
    plt.xlabel("Year")
    plt.ylabel(ylabel)
  

    plt.legend()
    plt.title("Indonesia " + f"{titles[str(int(float(hscode)))]} Imports Per Year (HS {int(hscode)})")
 
     
   
    plt.tight_layout()
    plt.savefig(f"IndoImportsBar{int(hscode)}.png")
    plt.close()
