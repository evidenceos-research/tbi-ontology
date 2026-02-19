# LinkedIn Thread Draft: DAI -> TAPVI

1/ We need to stop treating terminology as cosmetic in TBI imaging.  
"DAI" is often too narrow for what we actually see and measure.

2/ Modern evidence shows punctate traumatic lesions are not always purely axonal.  
Many are cerebrovascular, and many are mixed phenotypes.

3/ That is why we adopted **TAPVI**:  
**Traumatic Axonal and/or Punctate Cerebrovascular Injury**.

4/ Why this matters: labels are not just words.  
They become dataset columns, model targets, risk features, and chart-facing explanations.

5/ If the label is wrong, the whole stack drifts:  
- data harmonization  
- model training  
- external validation  
- implementation comparability

6/ We updated our neuroimaging ontology to encode TAPVI with:  
- confidence levels  
- structured location matrices  
- temporal phase links  
- explicit deprecated terms  
- standards mapping hooks (RadLex / DICOM SR / FHIR / OMOP)

7/ We also aligned biomarker kinetics + thresholds across the stack:  
- GFAP >= 30 pg/mL  
- UCH-L1 >= 360 pg/mL  
- GFAP half-life 24-36h  
- UCH-L1 half-life 7-9h

8/ And we shipped validation tooling so this does not regress:  
YAML lint + schema checks + cross-file consistency checks.

9/ Bottom line: moving DAI -> TAPVI improves both scientific fidelity and production-grade interoperability.

10/ If you are building TBI registries, CDS, or imaging AI:  
migrate your ontology labels now.  
**CTA:** See `evidenceos-research/ontology` and run `python validate_ontology.py`.
