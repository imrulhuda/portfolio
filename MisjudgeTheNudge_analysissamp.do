********************************************************************************
** EITC DATASET - RESPONSES TO REFEREES
********************************************************************************
** This do file addresses the checks that referees requested (Misjudge the Nudge). 
** The dataset used for this code is unrestricted and has no identifiers; it
** is strictly used to reproduce the final tables.
** See MisjudgeTheNudge_FINAL.do for the restrcited data cleaning file.

** Last Modified: October 07, 2019
********************************************************************************

clear
clear matrix
set more off
set scheme s1color
estimates clear
graph drop _all
set matsize 2500
log close _all

********************************************************************************
** LOAD AND SET UP DATA
********************************************************************************
** SET DIRECTORY 
cd "C:\Users\ih2344\Dropbox\Reminders Creditscore\new results"
** No ID Dataset, Sheet 1
import excel "C:\Users\ih2344\Dropbox\Reminders Creditscore\new results\mainsamp_noid_July172019.xlsx", sheet("Sheet1") firstrow clear
** With ID Dataset
*use "G:\Deptdata\Research\Share\RE-AXB-A\EITC\Jimin\data\sampcut.dta", clear 

destring creditscore, replace
destring creditscore_diff, replace

********************************************************************************
** Label Variables for Table  
********************************************************************************
la var agi "Adjusted Gross Income" 
la var riskscale "Risk Preparedness"
la var num_dependents "Number of Dependents"
la var creditscore_diff "Credit Score Difference"
la var progress_dir "Achievement of Debt Goals"
la var cred_used_diff "Change in Percentage of Credit Used"
la var cred_used "Percentage of Credit Used"
la var total_pastdue_diff "Change in Past Due Balance"
la var av_max_late_2 "Maximum Delinquency Payment Patterns"
la var max_late_diff "Improvement in Maximum Delinquency Payment Patterns"
la var collections_diff "Change in the Number of Collection Accounts"
la var inquiries_diff "Change in the Number of Inquiries"
la var cs_diff_pct "Percent Change in Credit Score"
la var creditscore_up "Improving Credit Score"
la var progress_pct "Percent of Debt Goal Achieved"
la var key_max_late_diff "Improvement in High Credit Maximum Payment Pattern Delinquency"
la var weight_max_late_diff "Improvement in Weighted Maximum Payment Pattern Delinquency"
la var creditscore_2013 "Credit Score in 2013"
la var creditscore "Credit Score"
la var survey_balance "Initial Survey Debt Balance"
la var debt_total_new "Initial Survey Debt Balance"
la var survey_change "Target Change in Debt Balance"
la var cs_guess_under "Guessed Under Real (Surprised)"
la var condition "Texts"
la var info "APR Info"
la var race_White "White"
la var race_Black_African_American "Black or African American"
la var race_other_multi "Other or Multiple Race(s)"
la var edu_1 "Not High School Grad or GED"
la var edu_2 "High School Grad or GED" 
la var edu_3 "Some College" 
la var edu_4 "Bachelors Degree or More"
la var agi "Adjusted Gross Income" 
la var num_dependents "Number of Dependents"
la var age "Age"
la var female "Female"
la var present_bias "Present Bias"
la var search "Search Scale"
la var cs_error "Credit Score Error"
la var credit_improve "Improved Credit Score"

** Setting Up Locals for Controls 
local controls "agi female edu_2 edu_3 edu_4 riskscale calctip_scale num_dependents"
local control_int_list ""
foreach v in `controls' {
	capture drop cond_`v'
	capture drop info_`v'
	gen `v'_mid_fico =  `v' * mid_fico
	la var `v'_mid_fico  "`:var label `v'' * Mid-Fico"
	gen `v'_high_fico =  `v' * high_fico
	la var `v'_high_fico "`:var label `v'' * High-Fico"	
	local control_int_list "`control_int_list'`v'_mid_fico `v'_high_fico "
}

** Setting Up Locals for Table
local depvars "creditscore_diff progress_dir cred_used_diff total_pastdue_diff max_late_diff late_av_diff collections_diff inquiries_diff"
local credit "creditscore_2013 creditscore creditscore_diff progress_dir cred_used cred_used_diff total_pastdue total_pastdue_diff av_max_late_2 max_late_diff collections collections_diff inquiries inquiries_diff"
local tax "agi female age race_White race_Black_African_American race_other_multi edu_1 edu_2 edu_3 edu_4 num_dependents"
local surveys "riskscale calctip_scale survey_balance survey_change"
local sumvars "`credit' `tax' `surveys'"
local randos_p "creditscore_2013 debt_total_new female agi age edu_1 edu_2 edu_3 edu_4 race_White race_Black_African_American race_other_multi"
local randos "agi survey_balance age female edu_1 edu_2 edu_3 edu_4 race_White race_Black_African_American race_other_multi "

tempfile finalsamp_eitc
save `finalsamp_eitc'

********************************************************************************
** Robustness Check: Non Missing Debt Variables
********************************************************************************
local nonmiss 0
local allv "progress_dir cred_used_diff inquiries_diff total_pastdue_diff max_late_diff collections_diff"

if (`nonmiss'==1){

count if bigsamp==1 //247

foreach ii in `allv'{
	di "`ii'"
	count if `ii'==. & bigsamp==1
	replace bigsamp = . if `ii'==.
}
count if bigsamp==1 // 159
}

********************************************************************************
** Redefining Analysis Sample by 2013 Credit Score Group
********************************************************************************
** Identify Analysis Sample IDs
gen bigsamp2 = bigsamp
bysort id: replace bigsamp2 = 1 if bigsamp2[_n+1]==1

drop low_fico mid_fico high_fico fico_group

centile creditscore if pull==1 & bigsamp2==1 , centile(33 66)
*centile creditscore_2013 if bigsamp2==1, centile(33 66) // same thing

gen low_fico = (creditscore<588) if pull==1
gen mid_fico = (creditscore>=588 & creditscore<676) if pull==1
** used to be just ., not .a or .b ...    & creditscore!=.a & creditscore!=.b
gen high_fico = (creditscore>=676 & creditscore!=. & creditscore!=.a & creditscore!=.b) if pull==1
la var low_fico "Low Fico"
la var mid_fico "Middle Fico"
la var high_fico "High Fico"
*br id pull bigsamp bigsamp2 low_fico mid_fico

foreach ii in low_fico mid_fico high_fico{
	by id: replace `ii' = `ii'[_n-1] if `ii'==.
}

** Fico Groups
gen fico_group = 1 if low_fico==1
replace fico_group = 2 if mid_fico==1
replace fico_group = 3 if high_fico==1

********************************************************************************
** Summary Statistics Based on Condition 
********************************************************************************
eststo notext: estpost sum `randos_p' if bigsamp==1 & condition==0 
eststo text: estpost sum `randos_p' if bigsamp==1 & condition==1
eststo noinfo: estpost sum `randos_p' if bigsamp==1 & info==0 
eststo info: estpost sum `randos_p' if bigsamp==1 & info==1

** Export into rtf file: Table 1 
esttab text notext info noinfo using latex\alltables_cleanversion.rtf, replace ///
cells(mean(label(" ")fmt(%10.4gc)) sd(label(" ")fmt(%10.4gc)par)) ///
noobs nonumbers varwidth(30) title("Table 1: Summary Statistics By Condition") label compress nogaps ///
mtitle("Text" "No Text" "Info" "No Info") collabels(none) 

** Randomization Checks (T-Test Based on Analysis Sample)
foreach c in condition info   { // By Text Condition vs. Info 
	foreach v in `randos_p' { // For Each Variable in Sum Stats
		di "`v' `c'" 
		ttest `v' if bigsamp==1, by(`c') // T-Test 
	}
}

********************************************************************************
** Summary Statistics Based on Condition By Fico Group
********************************************************************************
local low_fico_t "Low Fico Group"
local mid_fico_t "Mid Fico Group"
local high_fico_t "High Fico Group"
local low_fico_n "Table A1: "
local mid_fico_n "Table A2: "
local high_fico_n "Table A3: "

** By Fico Group
foreach ii in low_fico mid_fico high_fico{
	eststo clear 
	eststo notext: estpost sum `randos_p' if bigsamp==1 & condition==0 & `ii'==1
	eststo text: estpost sum `randos_p' if bigsamp==1 & condition==1 & `ii'==1
	eststo noinfo: estpost sum `randos_p' if bigsamp==1 & info==0 & `ii'==1 
	eststo info: estpost sum `randos_p' if bigsamp==1 & info==1 & `ii'==1
	
	** Export into rtf file: Appendix Tables A1, A2, A3
	esttab text notext info noinfo using latex\alltables_cleanversion.rtf, append ///
	cells(mean(label(" ")fmt(%10.4gc)) sd(label(" ")fmt(%10.4gc)par)) ///
	noobs nonumbers varwidth(30) title("``ii'_n'Summary Statistics By Treatment, Regression Sample for ``ii'_t'") label compress nogaps ///
	mtitle("Text" "No Text" "Info" "No Info") collabels(none) 

}
** Randomization Checks (T-Test Based on Analysis Sample)
foreach c in condition info { // By Text Condition vs. Info 
	foreach v in `randos_p' { // For Each Variable in Sum Stats
		di "`v' `c'" 
		ttest `v' if bigsamp==1 & high_fico==1, by(`c') // T-Test 
	}
}
*

********************************************************************************
** DEBT BALANCES AMONG THOSE IN ANALYSIS SAMPLE AND/OR WITH AGI
** Share of average debt graph out of total average debt
********************************************************************************
** Share of debt among analaysis sample
mean debt_credit debt_auto debt_student debt_mortgage debt_medical debt_collection debt_other if bigsamp==1 
matrix stats = r(table)
matrix A = stats[1,1...]' , stats[5,1...]' , stats[6,1...]'
su debt_total_new if bigsamp==1 
local mean_s = r(mean)
di `mean_s'
matrix B = (A / `mean_s')*100 // Average Initial Debt Balance Scalar 
matlist B

********************************************************************************
** VARIABLES AND LOCAL SET UP FOR REGRESSIONS
********************************************************************************
la var edu "Education Level"
la def edu 1 "Less than HS" 2 "HS Grad or Equiv" 3 "Some College" 4 "Bachelors or More"
la val edu edu

** Locals: These locals are for table formatting in latex. Each table is assigned
** a certain opt level, based on the number of variable and stats needed.
local opt1_p `" modelwidth(6) nonotes label star(* 0.10 ** 0.05 *** 0.01) b(%5.3fc) se(%5.3fc) stats(r2_p N, labels("Pseudo-R\super 2\super0" Observations) fmt(%5.3f %5.0g)) varlabels(_cons Constant) msign("\endash ")"'
local opt1 `" modelwidth(6) nonotes label star(* 0.10 ** 0.05 *** 0.01) b(%5.3fc) se(%5.3fc) stats(r2 r2_a N, labels("R\super 2\super0" "Adjusted-R\super 2\super0" Observations) fmt(%5.3f %5.3f %5.0g)) varlabels(_cons Constant) msign("\endash ")"'
local opt4 `" nonumbers modelwidth(7) eqlabels("" "Cut 1" "Cut 2") label nonotes star(* 0.10 ** 0.05 *** 0.01) b(%5.3fc) se(%5.3fc) stats(r2 r2_a r2_p N, labels("R\super 2\super0" "Adjusted-R\super 2\super0" "Pseudo-R\super 2\super0" Observations) fmt(%5.3f %5.3f %5.3f %5.0g))  varlabels(_cons Constant) msign("\endash ")"'
local opt5 `" numbers modelwidth(7) label nonotes star(* 0.10 ** 0.05 *** 0.01) b(%5.3fc) se(%5.3fc) stats(r2_p N, labels("Pseudo-R\super 2\super0" Observations) fmt(%5.3f %5.0g))  varlabels(_cons Constant) msign("\endash ")"'

** Add extended education variable 
la def edu_all 1 "Less than HS" 2 "HS, No Diploma" 3 "HS or GED" 4 "Some College" 5 "Associate's Degree" 6 "Bachelor's Degree" 7 "Some Grad School" 8 "Graduate Degree"
la val educational_background edu_all

** Adding continuous credit score instead?
gen creditscore2 = creditscore^2
la var creditscore2 "Credit Score Squared"

*sort id pull
gen creditscore_pull1 = creditscore if pull==1
gen startcreditscore = creditscore_pull1[_n-1]
drop creditscore_pull1
la var startcreditscore "Initial Credit Score"
gen startcreditscore2 = startcreditscore^2
la var startcreditscore2 "Initial Credit Score Squared"

******************************************************************************** 
** REGRESSION: CREDIT SCORE DIFFERENCE
******************************************************************************** 
** Create interaction variable
gen info_text = info*condition
la var info_text "Text * APR Info"
gen text_credscore = condition*startcreditscore
la var text_credscore "Text * Credit Score"

** Interactions and Labels
local condition "Texts"
local info "Info" 
local low_fico "Low Score"
local mid_fico "Mid Score"
local high_fico "High Score"

local fico "low_fico mid_fico high_fico"

foreach var of local fico{
	gen cond_`var' = condition * `var'
	la var cond_`var' "`condition' * ``var''"
	gen info_`var' = info * `var'
	la var info_`var' "`info' * ``var''"
}

** RESULT: Regression by Fico Group level
eststo csall: reg creditscore_diff condition if bigsamp==1 // original regression, no controls
forval g = 1/3 {
	eststo cs`g': reg creditscore_diff condition if bigsamp==1 & fico_group==`g'
	eststo cs`g'_per: reg cs_diff_pct condition if bigsamp==1 & fico_group==`g'
}
esttab csall cs1 cs2 cs3 using latex\tables_ref1.rtf, replace `opt1' ///
title("Table 2: Credit Score Difference") nonumbers mtitles("Overall" "Low" "Middle" "High")

eststo linear: reg creditscore_diff startcreditscore condition text_credscore if bigsamp==1
esttab linear using latex\tables_ref1.rtf, append `opt1' ///
title("Table 3: Credit Score Difference, Linear Effect") nonumbers mtitles("Overall")

/** RESULT: Regression Using Credit Score Different, Percent (APPENDIX)
esttab cs1_per cs2_per cs3_per using latex\tables_ref1.rtf, append `opt1' ///
title("Table A4: Percent Change in Credit Score") nonumbers mtitles("Low-Score" "Middle-Score" "High-Score")
*/
********************************************************************************
** REGRESSIONS: PAYMENT PATTERN AND DEBT MANAGEMENT
********************************************************************************
** Combine Group Levels to Single Variable and Get Sample Size by Fico Group
reg creditscore_diff condition if bigsamp==1 & fico_group==1 
gen sampgroup = e(sample)
reg creditscore_diff condition if bigsamp==1 & fico_group==2
replace sampgroup = 2 if e(sample)==1
reg creditscore_diff condition if bigsamp==1 & fico_group==3
replace sampgroup = 3 if e(sample)==1
la def sampgroup 1 "Low" 2 "Mid" 3 "High"
la val sampgroup sampgroup

** Local for Regression Loop
foreach v in `depvars' {
	local est`v' "reg"
	local k`v' = 1
}
foreach v in creditscore_up {
	local est`v' "probit"
	local k`v' = 2
}
foreach v in progress_dir  {
	local est`v' "oprobit"
	local k`v' = 2
}
** Locals for Labels
local T1 "Low Fico"
local t1 "low"
local T2 "Middle Fico"
local t2 "mid"
local T3 "High Fico"
local t3 "high"

********************************************************************************
** REGRESSIONS: CHANGE IN CREDIT SCORE WITH PAYMENT PATTERN & DEBT MANAGEMENT
********************************************************************************
** Local for Variables in Regression for Paper Regressions
local debt "progress_dir cred_used_diff inquiries_diff"
local pay "total_pastdue_diff max_late_diff collections_diff"
local vars1 "progress_dir cred_used_diff" // Debt Management Variables
local vars2 "total_pastdue_diff collections_diff " // Payment Pattern Variables 
local vars3 "inquiries_diff max_late_diff"

* Loop for each fico group
forvalue g = 1/3 {
	** Regression for debt manage and payment patterns
	foreach v in creditscore_diff `vars1' `vars2' `vars3' `debt' `pay'{
		di "`v'_old`g'"
		eststo `v'_old`g': `est`v'' `v' condition if fico_group==`g' & sampgroup==`g'
		di "`v'`g'"
		eststo `v'`g': `est`v'' `v' condition info if fico_group==`g' & sampgroup==`g'
		di "`v'`g'_int"
		eststo `v'`g'_int: `est`v'' `v' condition info info_text if fico_group==`g' & sampgroup==`g'
	}
	
	** Probit regression for improving credit score
	eststo imp_f`g': probit credit_improve condition info if fico_group==`g' & sampgroup==`g'
	eststo imp_f`g'_int: probit credit_improve condition info info_text if fico_group==`g' & sampgroup==`g'
	test condition + info_text = 0
	
	** OLS: Percent of debt goal achieved
	eststo progpct`g': reg progress_pct condition info if fico_group==`g' & sampgroup==`g'
	eststo progpct`g'_int: reg progress_pct condition info info_text if fico_group==`g' & sampgroup==`g'
	test condition + info_text = 0
	
	** OLS: Improvement in high credit maximum payment pattern delinquency
	eststo maxlate`g': reg key_max_late_diff condition info if fico_group==`g' & sampgroup==`g'
	eststo maxlate`g'_int: reg key_max_late_diff condition info info_text if fico_group==`g' & sampgroup==`g'
	test condition + info_text = 0
	
	** OLS: Improvement in weighted maximum payment pattern delinquency
	eststo wtmaxlate`g': reg weight_max_late_diff condition info if fico_group==`g' & sampgroup==`g'
	eststo wtmaxlate`g'_int: reg weight_max_late_diff condition info info_text if fico_group==`g' & sampgroup==`g'
	test condition + info_text = 0
}
********************************************************************************
** EXPORT RESULTS
********************************************************************************
** Table 7: Credit Score Difference 
esttab creditscore_diff1 creditscore_diff1_int ///
creditscore_diff2 creditscore_diff2_int ///
creditscore_diff3 creditscore_diff3_int ///
using latex\tables_ref1.rtf, append `opt4' title("Table 7: Credit Score Difference") varwidth(14) compress nogaps ///
nomtitles mgroups("Low-Score" "Mid-Score" "High-Score", pattern(1 0 1 0 1 0))

** COMBINE RESULTS FOR DEBT MANAGEMENT
** Table 4: Debt Management
esttab progress_dir_old1 progress_dir_old2 progress_dir_old3 ///
cred_used_diff_old1 cred_used_diff_old2 cred_used_diff_old3 ///
inquiries_diff_old1 inquiries_diff_old2 inquiries_diff_old3 ///
using latex\tables_ref1.rtf, append `opt4' title("Table 4: Debt Management") varwidth(14) compress nogaps ///
mtitle("Low" "Mid" "High" "Low" "Mid" "High" "Low" "Mid" "High") ///
mgroups("Achievement of Debt Goals" "Change in Percentage of Credit Used" "Change in Number of Inquiries", pattern(1 0 0 1 0 0 1 0 0))

** Table A8: Debt Management: Achieving Debt Goal and Percent of Credit Use
esttab progress_dir1 progress_dir1_int progress_dir2 progress_dir2_int progress_dir3 progress_dir3_int ///
cred_used_diff1 cred_used_diff1_int cred_used_diff2 cred_used_diff2_int cred_used_diff3 cred_used_diff3_int  ///
using latex\tables_ref1.rtf, append `opt4' title("Table A8: Debt Management: Achieving Debt Goal and Percent of Credit Use") varwidth(14) compress nogaps ///
mtitle("Low" "" "Mid" "" "High" "" "Low" "" "Mid" "" "High" "") mgroups("Debt Goal" "Pct Credit", pattern(1 0 0 0 0 0 1 0 0 0 0 0))
*
** COMBINE RESULTS FOR PAYMENT PATTERN
** Table 5: Payment Patterns
esttab total_pastdue_diff_old1 total_pastdue_diff_old2 total_pastdue_diff_old3 ///
max_late_diff_old1 max_late_diff_old2 max_late_diff_old3 ///
collections_diff_old1 collections_diff_old2 collections_diff_old3 ///
using latex\tables_ref1.rtf, append `opt4' title("Table 5: Payment Patterns") varwidth(14) compress nogaps ///
mtitle("Low" "Mid" "High" "Low" "Mid" "High" "Low" "Mid" "High") ///
mgroups("Change in Past Due Balance" "Improvement in Maximum Delinquency Payment Patterns" "Change in the Number of Collection Accounts", pattern(1 0 0 1 0 0 1 0 0))

** Table A9: Payment Pattern: Past Due Balances and Accounts in Collection
esttab total_pastdue_diff1 total_pastdue_diff1_int total_pastdue_diff2 total_pastdue_diff2_int ///
total_pastdue_diff3 total_pastdue_diff3_int collections_diff1 collections_diff1_int ///
collections_diff2 collections_diff2_int collections_diff3 collections_diff3_int ///
using latex\tables_ref1.rtf, append `opt4' title("Table A9: Payment Pattern: Past Due Balances and Accounts in Collection") varwidth(14) compress nogaps ///
mtitle("Low" "" "Mid" "" "High" "" "Low" "" "Mid" "" "High" "") ///
mgroups("Change in Past Due Balance" "Change in the Number of Collection Accounts", pattern(1 0 0 0 0 0 1 0 0 0 0 0))

********************************************************************************
** OTHER REGRESSIONS FOR APPENDIX
********************************************************************************
** Table A11: Number of Inquiries and Improvement in Maximum Delinquency
esttab inquiries_diff1 inquiries_diff1_int inquiries_diff2 inquiries_diff2_int inquiries_diff3 inquiries_diff3_int ///
max_late_diff1 max_late_diff1_int max_late_diff2 max_late_diff2_int max_late_diff3 max_late_diff3_int ///
using latex\tables_ref1.rtf,  append `opt4' title("Table A11: Number of Inquiries and Improvement in Maximum Delinquency") varwidth(14) compress nogaps ///
mtitle("Low" "" "Mid" "" "High" "" "Low" "" "Mid" "" "High" "") mgroups("Inquiries" "Delinquency", pattern(1 0 0 0 0 0 1 0 0 0 0 0))

** Table A5: Improving Credit Score
esttab imp_f1 imp_f1_int imp_f2 imp_f2_int imp_f3 imp_f3_int ///
using latex\tables_ref1.rtf,  append `opt5' title("Table A5: Improving Credit Score") varwidth(14) compress nogaps ///
nomtitles mgroups("Low-Score" "Mid-Score" "High-Score", pattern(1 0 1 0 1 0))

** Table A6: Percent of Debt Goal Achieved
esttab progpct1 progpct1_int progpct2 progpct2_int progpct3 progpct3_int ///
using latex\tables_ref1.rtf, append `opt1' title("Table A6: Percent of Debt Goal Achieved") varwidth(14) compress nogaps ///
numbers nomtitles mgroups("Low-Score" "Mid-Score" "High-Score", pattern(1 0 1 0 1 0))

** Table A7: Improvement in High Credit Maximum Payment Pattern Delinquency
esttab maxlate1 maxlate1_int maxlate2 maxlate2_int maxlate3 maxlate3_int ///
using latex\tables_ref1.rtf, append `opt1' title("Table A7: Improvement in High Credit Maximum Payment Pattern Delinquency") varwidth(14) compress nogaps ///
numbers nomtitles mgroups("Low-Score" "Mid-Score" "High-Score", pattern(1 0 1 0 1 0))
*

********************************************************************************
** FULL PAYMENT PATTERN REGRESSIONS 
********************************************************************************
** This section is the panel dataset and all identifiers are included.
** See MisjudgeTheNudge_FINAL.do for the compilation of the dataset.

use `finalsamp_eitc', clear

********************************************************************************
** Redefining Analysis Sample by 2013 Credit Score Group
********************************************************************************

keep if bigsamp==1 // Keep regression (analysis) sample only
drop low_fico mid_fico high_fico fico_group 
centile creditscore_2013, centile(33 66) // same thing
gen low_fico = (creditscore_2013<588) 
gen mid_fico = (creditscore_2013>=588 & creditscore_2013<676) 
** used to be just ., not .a or .b ...    & creditscore!=.a & creditscore!=.b
gen high_fico = (creditscore_2013>=676 & creditscore_2013!=. & creditscore_2013!=.a & creditscore_2013!=.b) 
la var low_fico "Low Fico"
la var mid_fico "Middle Fico"
la var high_fico "High Fico"
*br id pull bigsamp bigsamp2 low_fico mid_fico

foreach ii in low_fico mid_fico high_fico{
	bysort id: replace `ii' = `ii'[_n-1] if `ii'==.
}

** Fico Groups
gen fico_group = 1 if low_fico==1
replace fico_group = 2 if mid_fico==1
replace fico_group = 3 if high_fico==1

** Combine Group Levels to Single Variable and Get Sample Size by Fico Group
reg creditscore_diff condition if bigsamp==1 & fico_group==1 
gen sampgroup = e(sample)
reg creditscore_diff condition if bigsamp==1 & fico_group==2
replace sampgroup = 2 if e(sample)==1
reg creditscore_diff condition if bigsamp==1 & fico_group==3
replace sampgroup = 3 if e(sample)==1
la def sampgroup 1 "Low" 2 "Mid" 3 "High", replace
la val sampgroup sampgroup

********************************************************************************

** NOTE: The regressions are based on full monthly payment pattern data, but
** specifically only for analysis sample. 
** See earlier in the code for subset of payment pattern data that was created
** for this purposes.
*keep if bigsamp==1 // Keep regression (analysis) sample only
keep id info fico_group sampgroup creditscore_2013 // Keep only needed variables 
merge 1:m id using "delinquency.dta" // Merge with delinquency file (see original for construction) 
drop if _merge==2
drop _merge

** REGRESSION 
** Looking at one year back from pull 1 
gen month2 = .
gen x = 11
forvalue ii = 1/12 {
	replace month2 = `ii' + x if month==`ii'
	replace x = x-2
}
drop x

** Second ID: for account and ID identifier
egen id2 = group(id acct)
order acct id2, after(id)
order month2, after(month)

** Label vars for table
la var id "Individual ID"
la var condition "Text Condition"
la var pattern "Payment Pattern"
la var month2 "Time Since First Pull"
la var acctgroup "Account Type"
la var acct "Accounts"
la var id2 "ID and ACCT"
la var fico_group "Fico Group"
la var sampgroup "Regression Group"
la var info "APR Info"

** ENTIRE ANALYSIS SAMPLE WITHOUT ID CONTROLS
local i0 ""
local i1 "i.acctgroup"
local i2 "i.id"
local i3 "i.id i.acctgroup"

local t0 ""
local t1 ""
local t2 "drop(*id*)"
local t3 "drop(*id*)"

local title1 "Low Fico"
local title2 "Mid Fico"
local title3 "High Fico"

** XTREGS
xtset, clear
xtset id2 month2

** Table 6: Payment Pattern for All Accounts by Fico Group 
forvalue x = 0/0{
	eststo clear 
	forvalue y = 1/3{
		eststo r`x'_f`y': xtreg pattern i.condition `i`x'' c.month2 if month<13 & fico_group==`y' & sampgroup==`y', vce(cluster id)
		eststo rr`x'_f`y': xtreg pattern i.condition `i`x'' c.month2 c.month2#i.condition if month<13 & fico_group==`y' & sampgroup==`y', vce(cluster id)
	}
}


esttab r0_f1 rr0_f1 r0_f2 rr0_f2 r0_f3 rr0_f3 using latex\tables_ref1.rtf, append  ///
nonotes label star(* 0.10 ** 0.05 *** 0.01) b(%5.3fc) se(%5.3fc) ///
stats(chi2 p N, labels("Chi\super 2\super0" "P Value" "Observations") ///
fmt(%5.3f %5.3f %12.0g)) varlabels(_cons Constant) msign("\endash ") `t`x'' nobaselevels ///
title("Table 6: Payment Pattern for All Accounts by Fico Group") numbers mtitle("Low Fico" "" "Mid Fico" "" "High Fico" "") 

