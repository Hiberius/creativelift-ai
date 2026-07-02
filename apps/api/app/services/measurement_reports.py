from __future__ import annotations

import csv
import io
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.schemas.common import (
    MeasurementAnalyzeRequest,
    MeasurementCsvImportError,
    MeasurementCsvImportRead,
    MeasurementCsvImportRequest,
    MeasurementReportCreate,
    MeasurementReportRead,
    MeasurementReportSummaryRead,
    MeasurementVariantInput,
)
from app.services.measurement import analyze_observed_variants

_MAX_REPORTS = 100
_MAX_IMPORT_ROWS = 200
_DEFAULT_STORAGE_PATH = "tmp/measurement_reports.json"
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
REQUIRED_CSV_COLUMNS = [
    "name",
    "control_visitors",
    "control_conversions",
    "treatment_visitors",
    "treatment_conversions",
]


def _storage_path() -> Path:
    path = Path(os.getenv("CREATIVELIFT_REPORT_STORE", _DEFAULT_STORAGE_PATH))
    return path if path.is_absolute() else _PROJECT_ROOT / path


def _load_reports() -> list[MeasurementReportRead]:
    path = _storage_path()
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [MeasurementReportRead.model_validate(item) for item in raw[:_MAX_REPORTS]]
    except Exception:
        return []


def _persist_reports() -> None:
    path = _storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.tmp")
    payload = [report.model_dump(mode="json") for report in _reports[:_MAX_REPORTS]]
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temp_path, path)


_reports: list[MeasurementReportRead] = _load_reports()


def _new_measurement_report(payload: MeasurementReportCreate) -> MeasurementReportRead:
    analysis = analyze_observed_variants(payload.request)
    return MeasurementReportRead(
        id=uuid4(),
        created_at=datetime.now(UTC),
        source=payload.source,
        notes=payload.notes,
        request=payload.request,
        analysis=analysis,
    )


def create_measurement_report(payload: MeasurementReportCreate) -> MeasurementReportRead:
    report = _new_measurement_report(payload)
    _reports.insert(0, report)
    del _reports[_MAX_REPORTS:]
    _persist_reports()
    return report


def list_measurement_reports(limit: int = 20) -> list[MeasurementReportRead]:
    return _reports[:limit]


def clear_measurement_reports() -> None:
    _reports.clear()
    path = _storage_path()
    if path.exists():
        path.unlink()


def _variant(report: MeasurementReportRead, key: str) -> dict:
    variant = report.analysis.variants.get(key)
    if variant:
        return variant
    return next(iter(report.analysis.variants.values()), {})


def _report_row(report: MeasurementReportRead) -> dict[str, object]:
    control = _variant(report, "control")
    treatment = _variant(report, "treatment")
    comparison = report.analysis.comparison
    srm = report.analysis.srm
    return {
        "id": str(report.id),
        "created_at": report.created_at.isoformat(),
        "name": report.analysis.name,
        "source": report.source,
        "recommendation": report.analysis.recommendation,
        "control_label": control.get("label", "Control"),
        "control_visitors": control.get("visitors", 0),
        "control_conversions": control.get("conversions", 0),
        "control_conversion_rate": control.get("conversion_rate", 0),
        "treatment_label": treatment.get("label", "Treatment"),
        "treatment_visitors": treatment.get("visitors", 0),
        "treatment_conversions": treatment.get("conversions", 0),
        "treatment_conversion_rate": treatment.get("conversion_rate", 0),
        "absolute_lift": comparison.get("absolute_lift", ""),
        "relative_lift": comparison.get("relative_lift", ""),
        "p_value": comparison.get("p_value", ""),
        "srm_p_value": srm.get("p_value", ""),
        "decision_summary": report.analysis.decision_summary,
        "recommended_action": report.analysis.recommended_action,
        "notes": report.notes,
    }


def export_measurement_reports(format_name: str = "csv", limit: int = 100) -> tuple[str, str, str]:
    reports = list_measurement_reports(limit)
    if format_name == "json":
        content = json.dumps([report.model_dump(mode="json") for report in reports], indent=2)
        return content, "application/json", "creativelift-measurement-reports.json"
    if format_name == "markdown":
        parts = ["# CreativeLift AI Measurement Reports", ""]
        for report in reports:
            row = _report_row(report)
            parts.extend(
                [
                    f"## {row['name']}",
                    "",
                    f"- Recommendation: {row['recommendation']}",
                    f"- Control CVR: {float(row['control_conversion_rate']):.4f}",
                    f"- Treatment CVR: {float(row['treatment_conversion_rate']):.4f}",
                    f"- Relative lift: {float(row['relative_lift'] or 0):.4f}",
                    f"- P-value: {row['p_value']}",
                    f"- Decision: {row['decision_summary']}",
                    f"- Action: {row['recommended_action']}",
                    "",
                ]
            )
        return "\n".join(parts), "text/markdown", "creativelift-measurement-reports.md"

    rows = [_report_row(report) for report in reports]
    output = io.StringIO()
    fieldnames = list(_report_row(reports[0]).keys()) if reports else list(_report_row(_new_empty_report()).keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue(), "text/csv", "creativelift-measurement-reports.csv"


def summarize_measurement_reports(limit: int = 100) -> MeasurementReportSummaryRead:
    reports = list_measurement_reports(limit)
    counts = {
        "winner": 0,
        "loser": 0,
        "inconclusive": 0,
        "invalid_srm": 0,
        "needs_more_data": 0,
    }
    lifts: list[float] = []
    best_report: MeasurementReportRead | None = None
    best_lift: float | None = None
    for report in reports:
        recommendation = report.analysis.recommendation
        if recommendation in counts:
            counts[recommendation] += 1
        relative_lift = report.analysis.comparison.get("relative_lift")
        if isinstance(relative_lift, (int, float)):
            lift = float(relative_lift)
            lifts.append(lift)
            if best_lift is None or lift > best_lift:
                best_lift = lift
                best_report = report
    return MeasurementReportSummaryRead(
        total=len(reports),
        winners=counts["winner"],
        losers=counts["loser"],
        inconclusive=counts["inconclusive"],
        invalid_srm=counts["invalid_srm"],
        needs_more_data=counts["needs_more_data"],
        average_relative_lift=sum(lifts) / len(lifts) if lifts else None,
        best_report_id=best_report.id if best_report else None,
        best_report_name=best_report.analysis.name if best_report else None,
        best_relative_lift=best_lift,
    )


def _new_empty_report() -> MeasurementReportRead:
    payload = MeasurementReportCreate(
        request=MeasurementAnalyzeRequest(
            name="empty",
            control=MeasurementVariantInput(key="control", visitors=0, conversions=0),
            treatment=MeasurementVariantInput(key="treatment", visitors=0, conversions=0),
        )
    )
    return _new_measurement_report(payload)


def _field_map(headers: list[str] | None) -> dict[str, str]:
    return {header.strip().lower(): header for header in headers or [] if header}


def _row_value(row: dict[str, str | None], fields: dict[str, str], key: str, default: str = "") -> str:
    header = fields.get(key)
    if not header:
        return default
    return str(row.get(header) or default).strip()


def _number(raw: str, field_name: str) -> float:
    cleaned = raw.strip().rstrip("%").replace("_", "").replace(" ", "").replace(",", "")
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be numeric") from exc


def _integer(raw: str, field_name: str) -> int:
    value = _number(raw, field_name)
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")
    if int(value) != value:
        raise ValueError(f"{field_name} must be a whole number")
    return int(value)


def _ratio_from_csv(raw: str, default: float | None, field_name: str) -> float | None:
    if not raw.strip():
        return default
    value = _number(raw, field_name)
    return value / 100 if value > 1 else value


def _csv_row_to_report(
    row: dict[str, str | None],
    fields: dict[str, str],
    payload: MeasurementCsvImportRequest,
) -> MeasurementReportCreate:
    name = _row_value(row, fields, "name")
    if not name:
        raise ValueError("name is required")
    primary_metric = _row_value(row, fields, "primary_metric", "conversion_rate") or "conversion_rate"
    mde = _ratio_from_csv(
        _row_value(row, fields, "minimum_detectable_effect")
        or _row_value(row, fields, "mde"),
        payload.default_minimum_detectable_effect,
        "minimum_detectable_effect",
    )
    control = MeasurementVariantInput(
        key="control",
        label=_row_value(row, fields, "control_label", "Control") or "Control",
        visitors=_integer(_row_value(row, fields, "control_visitors"), "control_visitors"),
        conversions=_integer(_row_value(row, fields, "control_conversions"), "control_conversions"),
        revenue=_number(_row_value(row, fields, "control_revenue"), "control_revenue"),
        allocation=_ratio_from_csv(_row_value(row, fields, "control_allocation"), 0.5, "control_allocation") or 0.5,
    )
    treatment = MeasurementVariantInput(
        key="treatment",
        label=_row_value(row, fields, "treatment_label", "Treatment") or "Treatment",
        visitors=_integer(_row_value(row, fields, "treatment_visitors"), "treatment_visitors"),
        conversions=_integer(_row_value(row, fields, "treatment_conversions"), "treatment_conversions"),
        revenue=_number(_row_value(row, fields, "treatment_revenue"), "treatment_revenue"),
        allocation=_ratio_from_csv(_row_value(row, fields, "treatment_allocation"), 0.5, "treatment_allocation") or 0.5,
    )
    request = MeasurementAnalyzeRequest(
        name=name,
        primary_metric=primary_metric,
        minimum_detectable_effect=mde,
        control=control,
        treatment=treatment,
    )
    return MeasurementReportCreate(
        source=_row_value(row, fields, "source", payload.source) or payload.source,
        notes=_row_value(row, fields, "notes"),
        request=request,
    )


def import_measurement_reports_from_csv(payload: MeasurementCsvImportRequest) -> MeasurementCsvImportRead:
    reader = csv.DictReader(io.StringIO(payload.csv_text.strip()))
    fields = _field_map(reader.fieldnames)
    missing = [column for column in REQUIRED_CSV_COLUMNS if column not in fields]
    if missing:
        return MeasurementCsvImportRead(
            accepted=0,
            rejected=1,
            errors=[MeasurementCsvImportError(row_number=1, message=f"Missing columns: {', '.join(missing)}")],
            required_columns=REQUIRED_CSV_COLUMNS,
        )

    reports: list[MeasurementReportRead] = []
    errors: list[MeasurementCsvImportError] = []
    for index, row in enumerate(reader, start=2):
        if index > _MAX_IMPORT_ROWS + 1:
            errors.append(
                MeasurementCsvImportError(
                    row_number=index,
                    message=f"Import is limited to {_MAX_IMPORT_ROWS} rows per request.",
                )
            )
            break
        if not any(str(value or "").strip() for value in row.values()):
            continue
        try:
            report_payload = _csv_row_to_report(row, fields, payload)
            report = create_measurement_report(report_payload) if payload.save_reports else _new_measurement_report(report_payload)
            reports.append(report)
        except Exception as exc:
            errors.append(MeasurementCsvImportError(row_number=index, message=str(exc)))

    return MeasurementCsvImportRead(
        accepted=len(reports),
        rejected=len(errors),
        reports=reports,
        errors=errors,
        required_columns=REQUIRED_CSV_COLUMNS,
    )
