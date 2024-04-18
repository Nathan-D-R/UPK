/* Define the function */
%macro CleanOutput(input);

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
	length Model $6;
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
