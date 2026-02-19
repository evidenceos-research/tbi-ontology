#!/usr/bin/env python3
"""Ontology bundle validator for EvidenceOS TBI YAML modules."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency at runtime
    jsonschema = None


ONTOLOGY_DIR = Path(__file__).resolve().parent

YAML_FILES = {
    "cbim_framework": "cbim_framework.yaml",
    "clinical_entities": "clinical_entities.yaml",
    "imaging_cdes": "imaging_cdes.yaml",
    "temporal_phases": "temporal_phases.yaml",
    "provenance": "provenance.yaml",
    "implementation_science": "implementation_science.yaml",
    "methodology_extraction": "methodology_extraction.yaml",
}

EXPECTED_THRESHOLDS = {
    "gfap_pg_ml": 30.0,
    "uchl1_pg_ml": 360.0,
}

EXPECTED_KINETICS = {
    "gfap_clearance_half_life_hours": 24,
    "gfap_clearance_half_life_range_hours": [24, 36],
    "uchl1_clearance_half_life_hours": 8,
    "uchl1_clearance_half_life_range_hours": [7, 9],
}


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def nearly_equal(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.0)


def get_biomarker_threshold(cbim: dict[str, Any], analyte_id: str) -> float | None:
    variables = (
        cbim.get("channels", {})
        .get("biomarker", {})
        .get("variables", [])
    )
    for item in variables:
        if item.get("id") == analyte_id:
            return item.get("ct_threshold")
    return None


def validate_schema(module_name: str, data: dict[str, Any], schema: dict[str, Any], errors: list[str]) -> None:
    if jsonschema is None:
        return

    module_schema = {
        "$schema": schema.get("$schema"),
        "$ref": f"#/$defs/{module_name}",
        "$defs": schema.get("$defs", {}),
    }

    try:
        jsonschema.validate(instance=data, schema=module_schema)
    except jsonschema.ValidationError as exc:
        path = "/".join(str(p) for p in exc.absolute_path)
        prefix = f"{module_name} schema validation failed"
        if path:
            prefix += f" at '{path}'"
        errors.append(f"{prefix}: {exc.message}")


def validate_threshold_consistency(
    cbim: dict[str, Any],
    provenance: dict[str, Any],
    errors: list[str],
) -> None:
    cbim_gfap = get_biomarker_threshold(cbim, "gfap_pg_ml")
    cbim_uchl1 = get_biomarker_threshold(cbim, "uchl1_pg_ml")

    prov_gfap = (
        provenance.get("threshold_provenance", {})
        .get("gfap_ct_threshold", {})
        .get("value")
    )
    prov_uchl1 = (
        provenance.get("threshold_provenance", {})
        .get("uchl1_ct_threshold", {})
        .get("value")
    )

    if cbim_gfap is None:
        errors.append("cbim_framework.yaml missing biomarker variable 'gfap_pg_ml' ct_threshold")
    elif not nearly_equal(cbim_gfap, EXPECTED_THRESHOLDS["gfap_pg_ml"]):
        errors.append(
            f"GFAP threshold mismatch in cbim_framework.yaml: {cbim_gfap} != {EXPECTED_THRESHOLDS['gfap_pg_ml']}"
        )

    if cbim_uchl1 is None:
        errors.append("cbim_framework.yaml missing biomarker variable 'uchl1_pg_ml' ct_threshold")
    elif not nearly_equal(cbim_uchl1, EXPECTED_THRESHOLDS["uchl1_pg_ml"]):
        errors.append(
            f"UCH-L1 threshold mismatch in cbim_framework.yaml: {cbim_uchl1} != {EXPECTED_THRESHOLDS['uchl1_pg_ml']}"
        )

    if prov_gfap is None:
        errors.append("provenance.yaml missing threshold_provenance.gfap_ct_threshold.value")
    elif not nearly_equal(prov_gfap, EXPECTED_THRESHOLDS["gfap_pg_ml"]):
        errors.append(
            f"GFAP threshold mismatch in provenance.yaml: {prov_gfap} != {EXPECTED_THRESHOLDS['gfap_pg_ml']}"
        )

    if prov_uchl1 is None:
        errors.append("provenance.yaml missing threshold_provenance.uchl1_ct_threshold.value")
    elif not nearly_equal(prov_uchl1, EXPECTED_THRESHOLDS["uchl1_pg_ml"]):
        errors.append(
            f"UCH-L1 threshold mismatch in provenance.yaml: {prov_uchl1} != {EXPECTED_THRESHOLDS['uchl1_pg_ml']}"
        )


def validate_provenance_applicability(provenance: dict[str, Any], errors: list[str]) -> None:
    threshold_provenance = provenance.get("threshold_provenance", {})
    required_context = {"adult", "mild_tbi"}

    for field in ("gfap_ct_threshold", "uchl1_ct_threshold"):
        applies_to = threshold_provenance.get(field, {}).get("applies_to")
        if applies_to is None:
            errors.append(f"provenance.yaml missing threshold_provenance.{field}.applies_to")
            continue

        missing = sorted(required_context - set(applies_to))
        if missing:
            errors.append(
                f"provenance.yaml {field}.applies_to missing required contexts: {missing}"
            )


def validate_temporal_kinetics(temporal: dict[str, Any], errors: list[str]) -> None:
    subacute = temporal.get("phases", {}).get("subacute", {})
    windows = subacute.get("key_biomarker_windows", {})

    # Legacy v2 structure
    if windows:
        for key, expected in EXPECTED_KINETICS.items():
            actual = windows.get(key)
            if actual is None:
                errors.append(f"temporal_phases.yaml missing subacute.key_biomarker_windows.{key}")
                continue
            if actual != expected:
                errors.append(
                    f"Temporal kinetics mismatch for {key}: {actual!r} != {expected!r}"
                )
        return

    # v3 structure with analyte-specific clearance blocks
    clearance = subacute.get("biomarker_clearance_kinetics", {})
    gfap_range = clearance.get("gfap", {}).get("half_life_hours")
    uchl1_range = clearance.get("uchl1", {}).get("half_life_hours")

    if gfap_range is None:
        errors.append(
            "temporal_phases.yaml missing subacute.biomarker_clearance_kinetics.gfap.half_life_hours"
        )
    elif gfap_range != EXPECTED_KINETICS["gfap_clearance_half_life_range_hours"]:
        errors.append(
            "Temporal kinetics mismatch for gfap half-life range: "
            f"{gfap_range!r} != {EXPECTED_KINETICS['gfap_clearance_half_life_range_hours']!r}"
        )

    if uchl1_range is None:
        errors.append(
            "temporal_phases.yaml missing subacute.biomarker_clearance_kinetics.uchl1.half_life_hours"
        )
    elif uchl1_range != EXPECTED_KINETICS["uchl1_clearance_half_life_range_hours"]:
        errors.append(
            "Temporal kinetics mismatch for uchl1 half-life range: "
            f"{uchl1_range!r} != {EXPECTED_KINETICS['uchl1_clearance_half_life_range_hours']!r}"
        )


def validate_temporal_thresholds(temporal: dict[str, Any], errors: list[str]) -> None:
    kinetics = temporal.get("biomarker_kinetics", {})

    gfap_threshold = (
        kinetics.get("gfap", {})
        .get("ct_decision_threshold", {})
        .get("value")
    )
    uchl1_threshold = (
        kinetics.get("uchl1", {})
        .get("ct_decision_threshold", {})
        .get("value")
    )

    if gfap_threshold is None:
        errors.append("temporal_phases.yaml missing biomarker_kinetics.gfap.ct_decision_threshold.value")
    elif not nearly_equal(gfap_threshold, EXPECTED_THRESHOLDS["gfap_pg_ml"]):
        errors.append(
            "Temporal GFAP threshold mismatch: "
            f"{gfap_threshold} != {EXPECTED_THRESHOLDS['gfap_pg_ml']}"
        )

    if uchl1_threshold is None:
        errors.append("temporal_phases.yaml missing biomarker_kinetics.uchl1.ct_decision_threshold.value")
    elif not nearly_equal(uchl1_threshold, EXPECTED_THRESHOLDS["uchl1_pg_ml"]):
        errors.append(
            "Temporal UCH-L1 threshold mismatch: "
            f"{uchl1_threshold} != {EXPECTED_THRESHOLDS['uchl1_pg_ml']}"
        )


def validate_temporal_phase_ids(temporal: dict[str, Any], errors: list[str]) -> None:
    canonical = temporal.get("schema_contract", {}).get("canonical_phase_ids", [])
    phase_blocks = temporal.get("phases", {})
    actual_ids = [
        payload.get("id")
        for payload in phase_blocks.values()
        if isinstance(payload, dict) and payload.get("id")
    ]

    missing = sorted(set(canonical) - set(actual_ids))
    if missing:
        errors.append(f"temporal_phases.yaml missing phase IDs declared in schema_contract: {missing}")


def validate_phase_alignment(
    temporal: dict[str, Any],
    imaging: dict[str, Any],
    errors: list[str],
) -> None:
    temporal_ids = (
        temporal.get("schema_contract", {})
        .get("canonical_phase_ids", [])
    )
    imaging_ids = (
        imaging.get("schema_contract", {})
        .get("canonical_phase_ids", [])
    )

    if temporal_ids != imaging_ids:
        errors.append(
            "Canonical phase ID mismatch between temporal_phases.yaml and imaging_cdes.yaml"
        )

    valid_phase_ids = set(temporal_ids)
    used_phase_ids: set[str] = set()

    for section in ("core_cdes", "supplementary_cdes"):
        for cde in imaging.get(section, []):
            used_phase_ids.update(cde.get("temporal_phases", []))

    unknown = sorted(used_phase_ids - valid_phase_ids)
    if unknown:
        errors.append(f"imaging_cdes.yaml references unknown temporal phase IDs: {unknown}")


def validate_tapvi_and_counts(imaging: dict[str, Any], errors: list[str]) -> None:
    core = imaging.get("core_cdes", [])
    supplementary = imaging.get("supplementary_cdes", [])

    if len(core) != 9:
        errors.append(f"Expected 9 core CDEs, found {len(core)}")

    if len(supplementary) != 18:
        errors.append(f"Expected 18 supplementary CDEs, found {len(supplementary)}")

    ids = [cde.get("id") for cde in supplementary]
    if "tapvi" not in ids:
        errors.append("imaging_cdes.yaml missing supplementary CDE id 'tapvi'")
    if "tamvi" in ids:
        errors.append("imaging_cdes.yaml still contains deprecated id 'tamvi'")


def validate_mapping_hooks(files: dict[str, dict[str, Any]], errors: list[str]) -> None:
    modules_requiring_mappings = [
        "cbim_framework",
        "clinical_entities",
        "imaging_cdes",
        "provenance",
        "implementation_science",
    ]

    for name in modules_requiring_mappings:
        contract = files[name].get("schema_contract", {})
        if not contract.get("mapping_fields_optional"):
            errors.append(f"{name}.yaml missing schema_contract.mapping_fields_optional")

    hooks = files["imaging_cdes"].get("standards_mapping_hooks", {})
    template = hooks.get("default_mapping_template", {})
    required = {"radlex_id", "dicom_sr_code", "fhir_observation_code", "omop_concept_id"}
    missing = sorted(required - set(template.keys()))
    if missing:
        errors.append(
            f"imaging_cdes.yaml standards_mapping_hooks.default_mapping_template missing keys: {missing}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate EvidenceOS ontology bundle")
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Skip JSON Schema validation step",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    loaded: dict[str, dict[str, Any]] = {}
    for module_name, filename in YAML_FILES.items():
        path = ONTOLOGY_DIR / filename
        if not path.exists():
            errors.append(f"Missing required ontology file: {filename}")
            continue
        try:
            loaded[module_name] = load_yaml(path)
        except yaml.YAMLError as exc:
            errors.append(f"YAML parse error in {filename}: {exc}")

    if errors:
        for item in errors:
            print(f"[ERROR] {item}")
        return 1

    schema_path = ONTOLOGY_DIR / "schema.json"
    if not args.skip_schema:
        if jsonschema is None:
            warnings.append("jsonschema package not installed; skipping schema validation")
        elif not schema_path.exists():
            errors.append("schema.json not found")
        else:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            schema_defs = schema.get("$defs", {})
            for module_name, data in loaded.items():
                if module_name not in schema_defs:
                    warnings.append(
                        f"schema.json has no $defs entry for {module_name}; skipping schema validation for this module"
                    )
                    continue
                validate_schema(module_name, data, schema, errors)

    validate_threshold_consistency(loaded["cbim_framework"], loaded["provenance"], errors)
    validate_provenance_applicability(loaded["provenance"], errors)
    validate_temporal_kinetics(loaded["temporal_phases"], errors)
    validate_temporal_thresholds(loaded["temporal_phases"], errors)
    validate_temporal_phase_ids(loaded["temporal_phases"], errors)
    validate_phase_alignment(loaded["temporal_phases"], loaded["imaging_cdes"], errors)
    validate_tapvi_and_counts(loaded["imaging_cdes"], errors)
    validate_mapping_hooks(loaded, errors)

    if warnings:
        for item in warnings:
            print(f"[WARN] {item}")

    if errors:
        for item in errors:
            print(f"[ERROR] {item}")
        return 1

    print("[OK] Ontology validation passed")
    print("[OK] Threshold constants, kinetics, TAPVI terminology, and phase alignment are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
