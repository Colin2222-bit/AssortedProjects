. 

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
matplotlib.use('Agg')
import re
import statsmodels.api as sm
from statsmodels.formula.api import poisson
from scipy.stats import pearsonr, spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression


reader = pd.read_csv("orps.csv")
hq = reader["HQ Summary"]



#snowyvalues = reader.loc[reader.astype(str).apply(lambda row: row.str.contains("snow|cold", case=False, na=False).any(), axis=1)]
idavalues=reader.loc[(reader["Keywords"].str.contains("11D",flags=re.IGNORECASE,regex=True)) & 
(reader["HQ Summary"].str.contains("cold|snow|freez|rain|ice",flags=re.IGNORECASE,regex=True)) & 
(reader["Site"].isin(["Idaho National Laboratory"]))].copy()


idavalues.to_csv("ida.csv")


idavalues["Occurrence Date"] = pd.to_datetime(reader["Occurrence Date"], format='%m-%d-%Y')
idavalues['year'] = idavalues["Occurrence Date"].dt.year
idavalues = idavalues[idavalues['year'].between(2010, 2024) & (idavalues['year'] != 2013)]

years = [y for y in range(2010, 2025) if y != 2013]


yearly_counts = idavalues["year"].value_counts().reindex(years, fill_value=0).sort_index()





plt.figure(figsize=(12,6))
plt.plot(years, yearly_counts, marker="o", linestyle="-")
plt.xlabel("Year")
plt.ylabel("Number of Cold Weather Reports")
plt.title("Cold Weather Incidence Reports Per Year")
plt.grid(True)
plt.savefig("idaplot.png")


santafevalues=reader.loc[(reader["Keywords"].str.contains("11D",flags=re.IGNORECASE,regex=True)) & 
(reader["HQ Summary"].str.contains("cold|snow|freez|rain|ice",flags=re.IGNORECASE,regex=True)) & 
(reader["Site"].isin(["Los Alamos National Laboratory"]))].copy()
santafevalues.to_csv("santafe.csv")
santafevalues["Occurrence Date"] = pd.to_datetime(reader["Occurrence Date"], format='%m-%d-%Y')
santafevalues['year'] = santafevalues["Occurrence Date"].dt.year
santafevalues = santafevalues[santafevalues['year'].between(2010, 2024)]
nmyears = [y for y in range(2010, 2025)]
nmyc = santafevalues["year"].value_counts().reindex(nmyears, fill_value=0).sort_index()





plt.figure(figsize=(12,6))
plt.plot(nmyears, nmyc, marker="o", linestyle="-")

plt.xlabel("Year")
plt.ylabel("Number of Cold Weather Reports")
plt.title("Cold Weather Incidence Reports Per Year in Los Alamos Laboratory")
plt.grid(True)
plt.savefig("santafeplot.png")


vectorizer = TfidfVectorizer(stop_words='english')

hq = idavalues["HQ Summary"].astype(str)
tfidf_matrix = vectorizer.fit_transform(hq)
query = "slip ice snow freezing icy cold winter sidewalk"
query_vector = vectorizer.transform([query])
cos_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
top_n = 15
top_indices = cos_similarities.argsort()[-top_n:][::-1]
#print("Top descriptions similar to summary':\n")
#print(hq.iloc[top_indices])



nm = pd.read_csv('nmdata.csv')

nmavg = nm['TAVG']
nmmin = nm ['TMIN']
plt.figure(figsize=(12,6))
plt.plot(nm['DATE'], nm['TAVG'], label='Average Temperature (TAVG)', color='orange')
plt.plot(nm['DATE'], nm['TMIN'], label='Minimum Temperature (TMIN)', color='blue')

plt.xlabel('Year')
plt.ylabel('Temperature (°F)')
plt.title('Average and Minimum Temperatures Over Time in Los Alamos National Laboratory')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("SantaFe.png")

ida = pd.read_csv('idahodata.csv')

idavg = ida['TAVG']
idmin = ida ['TMIN']
idfreeze=ida['DX32']
plt.figure(figsize=(12,6))
plt.plot(ida['DATE'], ida['TAVG'], label='Average Temperature (TAVG)', color='orange')
plt.plot(ida['DATE'], ida['TMIN'], label='Minimum Temperature (TMIN)', color='blue')

plt.xlabel('Year')
plt.ylabel('Temperature (°F)')
plt.title('Average and Minimum Temperatures Over Time in Idaho')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("idaho.png")

mask = ~np.isnan(idavg)
minmask = ~np.isnan(idmin)
freezemask = ~np.isnan(idfreeze)
idavgmask = idavg[mask]
idminmask=idmin[mask]
idfreezemask = idfreeze[freezemask]

model = LinearRegression()
X = nmyc.values.reshape(-1, 1)
model.fit(X, nmmin)
slope = model.coef_[0]
intercept = model.intercept_
print(f"Slope: {slope}, Intercept: {intercept}")
r_sq = model.score(X, nmmin)
print(f"R-squared: {r_sq}")
list = [‘idavgmask’, ‘idminmask’, ‘idfreezemask’]
for temp in list:
pearsoncorrnm, pearsonpnm = pearsonr(yearly_counts, list)
print(f"pearson for avg: {pearsoncorrnm}, p-value avg: {pearsonpnm}")

spearmancorr, spearmanp = spearmanr(yearly_counts, idavgmask)
print(f"Spearman correlation: {spearmancorr:.3f}, p-value: {spearmanp:.3f}")

List2 = [‘nm[‘TAVG']’, ‘nm[‘TMIN']’, ‘nm[‘DX32']’]

For var in list2:
pearsoncorr, pearsonp = pearsonr(nmyc, var)
print(f"pearson for avg: {pearsoncorr}, p-value avg: {pearsonp}")

spearmancorr, spearmanp = spearmanr(nmyc, var)
print(f"Spearman correlation: {spearmancorr:.3f}, p-value: {spearmanp:.3f}")





data = pd.DataFrame({
    'incident_reports': nmyc,
    'avg_temp': nmavg,
    'min_temp': nmmin
})
print(data)
