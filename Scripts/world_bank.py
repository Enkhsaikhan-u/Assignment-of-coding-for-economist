import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings


#--------------------Importing raw data-----------------------
life_expect = pd.read_csv(r"C:\Users\Enkhsaikhan\Desktop\MA EDP\Fall-2024\Coding for economist\Assignment\Data\Raw\worldbank-lifeexpectancy-raw.csv")
income_cat = pd.read_excel(r"C:\Users\Enkhsaikhan\Desktop\MA EDP\Fall-2024\Coding for economist\Assignment\Data\Raw\OGHIST.xlsx",
                            sheet_name = "Country Analytical History", usecols="A:AM", skiprows= 10, nrows = 217, header = None)
print(life_expect)


#--------------------Importing raw data-----------------------
#####Cleaning life expectancy data
#Renaming columns
life_expect = life_expect.rename(columns={"Time":"year", 
                                          "Time Code": "year_code", 
                                          "Country Name": "country_name",
                                          "Country Code": "country_code",
                                          "GDP per capita, PPP (constant 2011 international $) [NY.GDP.PCAP.PP.KD]":"gdp_2011", 	
                                          "Population, total [SP.POP.TOTL]":"pop",
                                          "Life expectancy at birth, total (years) [SP.DYN.LE00.IN]":"life_exp"})

#Droping missing values
life_expect[["gdp_2011", "pop", "life_exp"]] =  life_expect[["gdp_2011", "pop", "life_exp"]].apply(pd.to_numeric, errors="coerce")
missing_value = life_expect.isnull().sum()
missing_value

life_expect = life_expect.dropna()
life_expect = life_expect.reset_index(drop=True)
life_expect["year"].dtype

#Log transformation 
life_expect["lgdp_2011"] = np.log(life_expect["gdp_2011"])
life_expect["lpop"] = np.log(life_expect["pop"])

print(life_expect)

####Cleaning income category data
#Renaming columns to reshaping wide to long
year = [str(year) for year in range(1987, 2024)]
income_cat.columns = ['country_code', 'country_name'] + year
income_cat = income_cat.reset_index(drop=True)

#Reshaping wide to long
income_cat_long = pd.melt(income_cat, id_vars=['country_code', 'country_name'], var_name='year', value_name='inc_cat')
income_cat_long

#Droping missing values
income_cat_long["inc_cat"] = income_cat_long["inc_cat"].replace({"LM*":"LM", "..": None})
income_cat_long["inc_cat"] = income_cat_long["inc_cat"].replace({"H":"High income", 
                                                                 "UM":"Upper-middle income",
                                                                 "LM":"Lower-middle income",
                                                                 "L":"Low income"})
income_cat = income_cat.dropna()
income_cat_long.value_counts("inc_cat")
income_cat_long["year"] = income_cat_long["year"].astype(int)

#Mergin two data sets 
combined_data = pd.merge(life_expect, income_cat_long, on=["country_code", "year"], how="inner")
combined_data.isna().sum()

combined_data['country_name'] = combined_data['country_name_x']
combined_data = combined_data.drop(columns=['country_name_x', 'country_name_y'])
combined_data = combined_data.dropna()
print(combined_data["inc_cat"].value_counts())


#--------------------Saving cleaned data set-----------------------
save_path = r"C:\Users\Enkhsaikhan\Desktop\MA EDP\Fall-2024\Coding for economist\Assignment\Data\Cleaned"

# Save a text or CSV file to this path
combined_data.to_csv(os.path.join(save_path, "combined_data.csv"), index=False)


#--------------------Summary statistics-----------------------
#Summary statistics
print(combined_data.filter(["gdp_2011", "lgdp_2011", "pop", "life_exp"]).describe().transpose())

#Grouped summary statistics
print(combined_data.groupby("inc_cat")[["gdp_2011", "lgdp_2011", "pop", "life_exp"]].agg([np.mean, np.median, np.std, min, max]))

#Using loops for summary statistics 
inc_categories = combined_data['inc_cat'].unique()
for inc_cat in inc_categories:
    inc_data = combined_data[combined_data['inc_cat'] == inc_cat]
    avg_life_exp = inc_data['life_exp'].mean()
    print(f"{inc_cat}: Avg Life Expectancy = {avg_life_exp:.3} in the last 30 years")


#---------------------Creating graphs------------------------
#Scatter plot 
legend_order = ["High income", "Upper-middle income", "Lower-middle income", "Low income"]
sns.scatterplot(x="lgdp_2011", y="life_exp", data=combined_data, hue="inc_cat", hue_order = legend_order)
plt.xlabel("Log of GDP per capita, PPP (constant 2011 international $)")
plt.ylabel("Life expectancy at birth, total (years)")
plt.legend(title="Income categories")
plt.show()


#Creating graph using lists
country = list(combined_data[combined_data["year"] == 2017]["country_code"])
lgdp = list(combined_data[combined_data["year"] == 2017]["lgdp_2011"])
life_exp = list(combined_data[combined_data["year"] == 2017]["life_exp"])
pop = list(combined_data[combined_data["year"] == 2017]["pop"])
inc_cat = list(combined_data[combined_data["year"] == 2017]["inc_cat"])
pop = np.array(pop)/1000000

income_mapping = {
    'Low income': 1,
    'Lower-middle income': 2,
    'Upper-middle income': 3,
    'High income': 4
}
colors = [income_mapping[level] for level in inc_cat]


plt.scatter(x=lgdp, y=life_exp, s = np.array(pop), c=colors)
plt.xlabel("Log of GDP per capita, PPP (constant 2011 international $)")
plt.ylabel("Life expectancy at birth, total (years)")
plt.title("World Bank 2017")

plt.text(9.4, 79, "China")
plt.text(8.6, 72, "India")
plt.text(10.74, 80, "USA")
plt.text(8.3, 55.5, "Nigeria")
plt.show()