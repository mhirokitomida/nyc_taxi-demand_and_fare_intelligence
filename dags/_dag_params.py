from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_START_MONTH = "2024-01"
DEFAULT_RERUN_MODE = "fail"
ALL_TARGET_LAYERS = ("bronze", "silver", "gold", "ml")


@dataclass(frozen=True)
class DagRunParameters:
    start_month: str
    end_month: str
    rerun_mode: str
    target_layers: tuple[str, ...]
    run_id: str | None


def _normalize_target_layers(raw_value: Any) -> tuple[str, ...]:
    if raw_value in (None, "", "all"):
        return ALL_TARGET_LAYERS

    if isinstance(raw_value, str):
        values = [part.strip().lower() for part in raw_value.split(",") if part.strip()]
    elif isinstance(raw_value, (list, tuple, set)):
        values = [str(part).strip().lower() for part in raw_value if str(part).strip()]
    else:
        raise ValueError(f"Unsupported target_layers value: {raw_value!r}")

    invalid = [value for value in values if value not in ALL_TARGET_LAYERS]
    if invalid:
        raise ValueError(f"Unsupported target_layers entries: {invalid}")
    return tuple(dict.fromkeys(values)) or ALL_TARGET_LAYERS


def load_dag_run_parameters(context: dict[str, Any]) -> DagRunParameters:
    dag_run = context.get("dag_run")
    conf = getattr(dag_run, "conf", {}) if dag_run else {}
    start_month = conf.get("start_month", DEFAULT_START_MONTH)
    end_month = conf.get("end_month", start_month)
    rerun_mode = conf.get("rerun_mode", DEFAULT_RERUN_MODE)
    target_layers = _normalize_target_layers(conf.get("target_layers"))
    return DagRunParameters(
        start_month=start_month,
        end_month=end_month,
        rerun_mode=rerun_mode,
        target_layers=target_layers,
        run_id=getattr(dag_run, "run_id", None) if dag_run else None,
    )


def should_run_layer(layer: str, selected_layers: tuple[str, ...]) -> bool:
    return layer in selected_layers
