# Stop Calling It DAI: Why TAPVI Is the More Accurate Language for Traumatic Brain Injury Imaging

## The short version

"Diffuse Axonal Injury (DAI)" has been used for decades, but modern imaging-pathology evidence shows it is often too narrow. Many punctate lesions on MRI are cerebrovascular, not purely axonal.

That is why our ontology now adopts **TAPVI**: **Traumatic Axonal and/or Punctate Cerebrovascular Injury**.

This is not a branding change. It is a data quality correction.

---

## Why DAI became insufficient

Three evidence-backed issues have become hard to ignore:

1. **Mixed lesion biology**  
   Punctate susceptibility lesions can represent vascular injury, axonal injury, or both.
2. **Phenotype conflation**  
   Labeling all punctate lesions as "axonal" collapses distinct mechanisms.
3. **Poor downstream interoperability**  
   Ambiguous labels make it harder to build robust, harmonized imaging data products.

In practice, this means DAI can overstate confidence in mechanism and reduce clarity for prognostic modeling.

---

## What TAPVI fixes

TAPVI explicitly encodes that punctate traumatic lesions may be:

- axonal,
- punctate cerebrovascular,
- or mixed.

This improves both **clinical communication** and **machine-readable structure**.

In our imaging ontology, TAPVI is represented with:

- explicit confidence fields,
- standardized location matrices,
- temporal phase links,
- deprecated-term traceability,
- and mapping hooks for RadLex / DICOM SR / FHIR / OMOP.

---

## Why this matters for open clinical AI

If you want reproducible neuroimaging AI, terminology precision is not optional.

When terminology is wrong, every downstream layer inherits the error:

- cohort definitions,
- labels for training/evaluation,
- model explanations,
- clinical audit trails,
- and implementation science comparisons across settings.

Moving from DAI to TAPVI tightens that entire chain.

---

## What we released

We packaged a six-module TBI ontology bundle with:

- CBI-M channel framework
- Clinical entities (including pediatric GCS/PTA metadata)
- WG2 imaging CDEs with TAPVI
- Temporal phase framework with corrected biomarker kinetics
- Provenance metadata for threshold/regulatory traceability
- Implementation science contexts (HIC/LMIC/military)

Plus:

- `schema.json`
- `context.jsonld`
- CI validation workflow
- deterministic consistency checks (thresholds, kinetics, terminology, phase IDs)

---

## Call to action

If your pipeline still uses DAI as a top-level label, now is the right time to migrate.

Use TAPVI terminology in:

- annotation schemas,
- model outputs,
- explainability narratives,
- and cross-site data exchange.

**Repository CTA:** Review and adapt the ontology bundle in `evidenceos-research/ontology` and run `python validate_ontology.py` before integration.
