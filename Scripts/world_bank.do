cd "C:\Users\Enkhsaikhan\Desktop\MA EDP\Fall-2024\Coding for economist\Assignment"

*Importing csv file 
import delimited "Data\Raw\worldbank-lifeexpectancy-raw.csv", varnames(1) clear

*--------------------------------Data cleaning----------------------------------
*Renaming 
	rename countryname country_name
	rename countrycode country_code
	rename gdppercapitapppconstant2011inter gdp_2011
	rename populationtotalsppoptotl pop
	rename lifeexpectancyatbirthtotalyearss life_exp 
	rename time year 

*Destringing, counting missing values	
	foreach i in gdp_2011 pop life_exp{
	    replace `i' = "." if `i' == ".."
		destring `i', replace 
		count if missing(`i') 
}
*Droping missing values 
	drop if missing(gdp_2011)

*Generating log of gdp, pop
	gen lgdp = log(gdp_2011)
	gen lpop = log(pop)
	
*Changing variable label 
    describe  
	label variable gdp_2011 "GDP per capita, PPP (constant 2011 international $)"
	label variable pop "Population, total"
	label variable life_exp "Life expectancy at birth, total (years)"

*Checking all country names, and codes uniquelly defined
    unique country_name country_code time
	
*Saving data set 
mkdir "Data\Cleaned"
save "Data\Cleaned\worldbank-lifeexpectancy-cleaned.dta", replace 



*-----------------------Income classification data cleanning--------------------
import excel using "Data\Raw\OGHIST.xlsx", sheet("Country Analytical History") ///
                    cellrange(A12:AM229) clear

*Renaming variables
	rename A country_code 
	rename B country_name

*Reshaping wide shaped data into long shaped one
	local year = 1987
	foreach var in C D E F G H I J K L M N O P Q R S T U V W X Y Z AA AB AC ///
	               AD AE AF AG AH AI AJ AK AL AM{
		rename `var' inccat_`year'
		local year = `year' + 1
}
	reshape long inccat_, i(country_code) j(year)

	rename inccat_ inc_cat 
	label variable inc_cat "World bank income classification" 
	replace inc_cat = "" if inc_cat == ".."
    count if missing(inc_cat)
	replace inc_cat = "LM" if inc_cat == "LM*"

*Saving data set 
save "Data\Cleaned\worldbank-incomeclassification-cleaned.dta", replace 

*Combining two data set 
use "Data\Cleaned\worldbank-lifeexpectancy-cleaned.dta", clear
sort country_code year 
merge 1:1 country_code year using ///
                   "Data\Cleaned\worldbank-incomeclassification-cleaned.dta"
drop if _merge == 2

save "Data\Cleaned\combined_data.dta", replace 



*-------------------Descriptive statistics, graph, analysis---------------------
use "Data\Cleaned\combined_data.dta", clear 

*Descriptive statistics of variables 
	sum gdp_2011 pop life_exp, detail
	tabstat gdp_2011 pop life_exp, s(mean median n sd max min) by(inc_cat)
	
*Scatter plot: gdp and life expectancy 
	set scheme white_tableau
	twoway (scatter life_exp lgdp if inc_cat == "H") /// 
	       (scatter life_exp lgdp if inc_cat == "UM") ///
		   (scatter life_exp lgdp if inc_cat == "LM") ///
		   (scatter life_exp lgdp if inc_cat == "L") ///
		   (lfit life_exp lgdp), ///
		   legend(order(1 "High income countries" 2 "Upper-middle countries" ///
                    3 "Lower-middle countries" 4 "Low income countries") ///
              ring(0) pos(2) col(2)) ///
		   xtitle("Log GDP per capita, PPP (constant 2011 international $)") ///
		   ytitle("Life expectancy at birth, total (years)") ///
		   title("Correlation between GDP per capita and Life expectancy")
		   
*Saving graph
mkdir graph
graph export "graph/Scatterplot.png", replace 

*Line graph: life expectancy and gdp by income categories
	gen weighted_life_exp = life_exp * pop
	gen weighted_gdp = gdp_2011 * pop
	 
	collapse (sum) pop weighted_life_exp weighted_gdp, by(year inc_cat)
	gen life_exp = weighted_life_exp / pop
	gen gdp = weighted_gdp / pop
	
	drop if inc_cat == "" | life_exp == 0 | gdp == 0 | gdp ==. | life_exp ==.
	
twoway (line life_exp year if inc_cat == "H") ///
       (line life_exp year if inc_cat == "UM") ///
       (line life_exp year if inc_cat == "LM") ///
       (line life_exp year if inc_cat == "L"), ///
       legend(order(1 "High income countries" 2 "Upper-middle countries" ///
                    3 "Lower-middle countries" 4 "Low income countries") ///
              position(2)) ///  
       xtitle("Year") ///
       ytitle("Life expectancy at birth, total (years)") ///
       title("Life expectancy by income category")

graph export "graph/life_exp.png", replace 
	
twoway (line gdp year if inc_cat == "H") ///
       (line gdp year if inc_cat == "UM") ///
       (line gdp year if inc_cat == "LM") ///
       (line gdp year if inc_cat == "L"), ///
       legend(order(1 "High income countries" 2 "Upper-middle countries" ///
                    3 "Lower-middle countries" 4 "Low income countries") ///
              position(2)) ///  
       xtitle("Year") ///
       ytitle("GDP per capita, PPP (constant 2011 international $)") ///
       title("GDP per capita by income category")
	
graph export "graph/gdp.png", replace
	
	
	
	
	
	
