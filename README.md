# EvidenceOS TBI Ontology Bundle

This directory contains a standalone ontology bundle for traumatic brain injury (TBI) decision support, synthetic data generation, and translational implementation.

## Scope

The bundle currently includes seven ontology modules:

1. `cbim_framework.yaml` - Clinical-Biomarker-Imaging-Modifier (CBI-M) channel framework
2. `clinical_entities.yaml` - GCS components, pediatric variants, PTA tools, confounders
3. `imaging_cdes.yaml` - WG2 neuroimaging CDEs (core + supplementary) and TAPVI terminology
4. `temporal_phases.yaml` - NINDS-aligned temporal phase definitions and biomarker windows
5. `provenance.yaml` - Threshold/rule provenance and audit metadata
6. `implementation_science.yaml` - Deployment contexts, equity, RE-AIM/CFIR framing
7. `methodology_extraction.yaml` - Systematic extraction schema for NINDS WG citation methodology analysis

## Canonical Clinical Constants

- **GFAP CT threshold**: `>= 30 pg/mL`
- **UCH-L1 CT threshold**: `>= 360 pg/mL`
- **GFAP half-life**: `24-36 hours`
- **UCH-L1 half-life**: `7-9 hours`
- **Terminology update**: DAI is deprecated for ontology naming; use **TAPVI** (Traumatic Axonal and/or Punctate Cerebrovascular Injury)

## Interoperability

Mapping hooks are included as optional fields for downstream standards alignment:

- RadLex IDs
- DICOM SR codes
- FHIR observation/location codes
- OMOP concept IDs

These are intentionally nullable in the open-source release and can be populated by implementers.

## Validation and CI

### Local validation

```bash
pip install -r requirements-dev.txt
yamllint .
python validate_ontology.py
```

### CI workflow

A GitHub Actions workflow is provided at:

- `.github/workflows/ontology-validation.yml`

It runs YAML linting and ontology consistency checks on pull requests and pushes.

## Package Metadata

- `schema.json` - Bundle-level JSON Schema used by validation tooling
- `context.jsonld` - JSON-LD context for semantic and linked-data interoperability
- `LICENSE` - Apache License 2.0

## Intended Use

This ontology bundle is designed for:

- CDS/triage model specification (BRIDGE-TBI style stacks)
- Synthetic cohort generation and benchmarking
- Cross-site implementation profiling (HIC, LMIC, military/austere)
- Reproducible research with explicit provenance and auditability
