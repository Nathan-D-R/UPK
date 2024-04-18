%include "/home/u62949701/MySAS/CleanOutput.sas";

%macro GenerateModels();
%let n = 1;

proc import datafile="/home/u62949701/MySAS/Data/data.xlsx"
	out=work.Data
	dbms=xlsx
	replace;
run;

data Data;
	set Data;
run;

/* Main */
ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
proc surveyreg Data=Data;
	Class State Year;
	Model Poverty =
	Program_3yo
	Program_4yo
	All_Spending_per_Child
	State_Spending_per_Child
	P_3yo_Enrolled
	P_4yo_Enrolled
	Quality_Standards_Met
	State Year /Solution AdjRsq;
run;

%CleanOutput(&n); %let n = %eval(&n + 1);

/* Main */
ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
proc surveyreg Data=Data;
	Class State Year;
	Model Poverty =
	Program_3yo
	Program_4yo
	All_Spending_per_Child
	State_Spending_per_Child
	P_3yo_Enrolled
	P_4yo_Enrolled
	Quality_Standards_Met
	State Year /Solution AdjRsq;
run;

%CleanOutput(&n);

%mend;
%GenerateModels();

data Final;
	merge Model1-Model2;
	by Regressor;
run;

proc sort data=Final;
	by Index1;
run;

data Final;
	set Final;
	if mod(_n_,2)=0 then Regressor = "";
	keep Regressor Model1-Model2;
run;

ods excel file="/home/u62949701/MySAS/Exports/SeniorProject.xlsx" options(Embedded_Titles="ON" Embedded_Footnotes="ON");
proc print data=Final noobs; 
	var Regressor Model1-Model2;
	*format Regressor $Regressor.; 
	var Model1 / style(header)={Just=Center} style(data)={Just=Center tagattr="type:string"};
	title "Table: Differences-in-Differences Models";
	footnote "Source: Outcome Data by US Census, Pre-K Data by NIEER.";
	footnote2 "Notes: *, **, and *** signify 10%, 5%, and 1% significance levels, respectively.";
	footnote3 "Robust Standard Errors in parenthesis.";
run;
ods excel close;
