/* Define the function */
%macro GenerateModel(input);

data Results;
	set PE;
	where SUBSTR(Parameter, 1, 5) ne "State" and SUBSTR(Parameter, 1, 4) ne "Year";
run;

data Results;
	length Model $5;
	length Parameter $30;
	set Results;
	Model = "Model";
	if Probt le 0.01 then Star="***";
		else if Probt le 0.05 then Star="**";
		else if Probt le 0.1 then Star="*";
		
		/* Handle stars */
	EditedResults=cats(Put(Estimate,comma16.2),star);
	output;
	
	/* Handle robust standard errors */
	EditedResults=cats("(",put(StdErr,comma16.2),")");
	output;
run;

data Results;
	set Results;
	if mod(_n_,2)=0 then Parameter = trim(Parameter) || "-delete";
run;

data Results;
	set Results;
	Regressor = Parameter;
	Result = EditedResults;
	keep Regressor Result;
run;

data NumofObs;
	set OBS(rename=() drop=CValue1);
	where Label1="Number of Observations";
	Model=put(nValue1,comma16.);
	drop nValue1;
run;

data AdjRsq;
	set AdjRsq(rename=(cvalue1=Model) drop=nvalue1);
	Where Label1 = "Adjusted R-Square";
run;

data OSM;
	set OverallSig;
	where Effect="Model";
	if ProbF le 0.01 then Star="***";
		else if ProbF le 0.05 then Star="**";
		else if ProbF le 0.1 then Star="*";

	Label1="Overall Significance";
	EditedValue=cats(put(FValue,comma16.2),Star);
	Model = EditedValue;
	
	keep Label1 Model;
run;

/* Combine rows for the other statistics */
data OtherStat;
	*length Model $10;
	set NumofObs AdjRsq OSM;
	rename Label1=Regressor Model=Result;
run;

data Model&input.;
	set Results OtherStat;
run;

data Model&input.;
	set Model&input.(rename=(Result=Model&input.));
	retain Index&input. 0; 
	Index&input. + 1;
run;

proc sort data=Model&input.;
	by Regressor;
run;

%mend;

proc import datafile="/home/u62949701/MySAS/Data/Data.xlsx"
	out=work.Data
	dbms=xlsx
	replace;
sheet="Data";
getnames=yes;
run;

data Data;
	set Data;
	Poverty = Poverty;
	Enrollment = Enrollment;
run;

/* Main */
ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
proc surveyreg Data=Data;
	Class State Year;
	Model Poverty=Program Spending Enrollment QualityMet TeacherDegree DevelopmentStandards ClassSize SpecializedTraining TeacherRatio AssistantTeacher ProfessionalDevelopment ScreeningReferral QualityImprovement State Year /Solution AdjRsq;
run;

%GenerateModel(1);

/* Program */
ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
Proc SurveyReg Data=Data;
	Class State Year;
	Model Poverty=Program State Year /Solution AdjRsq;
Run;

%GenerateModel(2);

/* Funding */
ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
Proc SurveyReg Data=Data;
	Class State Year;
	Model Poverty=Program Spending State Year /Solution AdjRsq;
Run;

%GenerateModel(3);

/* Quality */
ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
Proc SurveyReg Data=Data;
	Class State Year;
	Model Poverty=Program QualityMet State Year /Solution AdjRsq;
Run;

%GenerateModel(4);

/* Enrollment */

ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
Proc SurveyReg Data=Data;
	Class State Year;
	Model Poverty=Program Enrollment State Year /Solution AdjRsq;
Run;

%GenerateModel(5);

/* Individual Quality */
ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
Proc SurveyReg Data=Data;
	Class State Year;
	Model Poverty=Program TeacherDegree DevelopmentStandards ClassSize SpecializedTraining TeacherRatio AssistantTeacher ProfessionalDevelopment ScreeningReferral QualityImprovement State Year /Solution AdjRsq;
Run;

%GenerateModel(6);

/* No FE */
ods output ParameterEstimates=PE DataSummary=Obs 
			FitStatistics=AdjRsq Effects=OverallSig;
Proc SurveyReg Data=Data;
	Model Poverty=Program Spending Enrollment QualityMet /Solution AdjRsq;
Run;

%GenerateModel(7);

data Final;
	merge Model1-Model6;
	by Regressor;
run;

proc sort data=Final;
	by Index1;
run;

data Final;
	set Final;
	if mod(_n_,2)=0 then Regressor = "";
	keep Regressor Model1-Model6;
run;

ods excel file="/home/u62949701/MySAS/Exports/SeniorProject.xlsx" options(Embedded_Titles="ON" Embedded_Footnotes="ON");
proc print data=Final noobs; 
	var Regressor;
	*format Regressor $Regressor.; 
	var Model1-Model6 / style(header)={Just=Center} style(data)={Just=Center tagattr="type:string"};
	title "Table: Differences-in-Differences Models";
	footnote "Source: Outcome Data by US Census, Pre-K Data by NIEER.";
	footnote2 "Notes: *, **, and *** signify 10%, 5%, and 1% significance levels, respectively.";
	footnote3 "Robust Standard Errors in parenthesis.";
run;
ods excel close;
