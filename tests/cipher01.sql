--  1.1	Get all instances of 2 hour glucose tests
;WITH CTE AS
(
    SELECT 
	    PatientSID
            ,LabChemResultNumericValue
	    ,LabChemCompleteDateTime
    FROM
	    CDWWork.Chem.patientLabChem AS Lab
    INNER JOIN 
       (
	    SELECT
		    *     
	    FROM
		    CDWWork.Dim.LabChemTest l
	    WHERE 
	 	   (
			 LabChemTestName LIKE ('%glucose tolerance test%') OR 
			 LabChemTestName LIKE ('%2HR GTT%') OR LabChemTestName LIKE ('%2 HOUR GLUCOSE%')
		    ) 
		    AND 
                   (
			 LabChemTestName NOT LIKE ('1/2HR GTT%') 
		     AND LabChemTestName NOT LIKE ('%1%') 
		     AND LabChemTestName NOT LIKE ('%1/2 HOUR GLUCOSE%') 
		     AND LabChemTestName NOT LIKE ('%3%')  
		     AND LabChemTestName NOT LIKE ('%4%') 
		     AND LabChemTestName NOT LIKE ('%5%') 
		     AND LabChemTestName NOT LIKE ('%6%')
		    )
        ) AS DIMLAB
	    ON 
		Lab.Labchemtestsid = DIMLAB.LabChemtestSID
    INNER JOIN
	(
	    SELECT
		    *
	    FROM
		    CDWWork.Dim.Topography AS Topg	
	    WHERE
			(Topography LIKE '%blood%' OR
			 Topography LIKE '%plasma%' OR 
			 Topography LIKE '%serum%' OR 
			 Topography LIKE '%ser/pla%')
	    ) AS Topg
		ON 
		    Lab.topographysid = Topg.topographysid 
    UNION			   
    SELECT 
	    PatientSID
    	    ,LabChemResultNumericValue
	    ,LabChemCompleteDateTime
     FROM 
 	    CDWWork.Chem.PatientLabChem Lab
     INNER JOIN 
	   (
		SELECT
			*
		FROM
			CDWWork.Dim.LabChemTest l
	   ) AS DIMLAB
		ON 
			Lab.Labchemtestsid = DIMLAB.LabChemtestSID
     INNER JOIN 
			CDWWork.Dim.NationalVALabCode AS NatLab 
		ON
			DIMLAB.NationalVALabCodeSID = NatLab.NationalVALabCodeSID
     INNER JOIN 
	(
		 SELECT 
			* 
		 FROM 
			CDWWork.Dim.Loinc
		 WHERE 
			LOINC = '72171-2' OR
			LOINC = '6751-2' OR
			LOINC = '26547-0'  
	) AS LOI
		ON
		    LOI.LoincSID = NatLab.DefaultLoincSID
      INNER JOIN
	(
		 SELECT
			*
		 FROM
			CDWWork.Dim.Topography
		 WHERE
			(Topography LIKE '%blood%' OR
			 Topography LIKE '%plasma%' OR 
			 Topography LIKE '%serum%' OR 
			 Topography LIKE '%ser/pla%')	
	) AS Topg
		ON 
		    Lab.topographysid = Topg.topographysid 
	UNION
	SELECT 
		PatientSID
		,LabChemResultNumericValue
		,LabChemCompleteDateTime
	FROM 
		CDWWork.Chem.PatientLabChem Lab
	INNER JOIN 
	  (
		SELECT 
			* 
		FROM 
			CDWWork.Dim.Loinc
		WHERE 
			LOINC = '72171-2' OR
			LOINC = '6751-2' OR
			LOINC = '26547-0' 
	   ) AS LOI
		ON
		    Lab.LoincSID = LOI.LoincSID
	   INNER JOIN
		(
		    SELECT
			*
		    FROM
			CDWWork.Dim.Topography
		    WHERE
			(Topography LIKE '%blood%' OR
			 Topography LIKE '%plasma%' OR 
			 Topography LIKE '%serum%' OR 
			 Topography LIKE '%ser/pla%')	
			) AS Topg
		ON 
		    Lab.topographysid = Topg.topographysid 
	   INNER JOIN 
		   (
		    SELECT
			*
		    FROM
			CDWWork.Dim.LabChemTest l
		   ) AS DIMLAB
		ON 
		    Lab.Labchemtestsid = DIMLAB.LabChemtestSID
)
SELECT DISTINCT
	PatientSID
        ,LabChemResultNumericValue
	,LabChemCompleteDateTime 
INTO 
	#2hrGlucLabs
FROM 
	CTE;
 
-- xxx Rows;		:28s
 
 
 
--  1.2	Index table 
 
CREATE CLUSTERED COLUMNSTORE INDEX 
CCI
ON 
#2hrGlucLabs;
 
-- :00s;
 
 
 
--  1.3	Filter for those with a glucose tolerance test >= 140 AND < 200
 
SELECT DISTINCT 
	PAT.PatientICN
INTO 
	#2hrGlucLabs_140to200
FROM  
	#2hrGlucLabs AS LAB
INNER JOIN
	CDWWork.Patient.Patient AS PAT
    ON
	LAB.PatientSID = PAT.PatientSID
WHERE 
	(LabChemResultNumericValue >= 140 AND LabChemResultNumericValue < 200);
 
-- xxx Rows;		:01s
 
 
 
--	3.22	Index table 
 
CREATE CLUSTERED COLUMNSTORE INDEX 
CCI
ON 
#2hrGlucLabs_140to200;
 

-- :00s