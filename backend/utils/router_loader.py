from importlib import import_module
from pathlib import Path

from fastapi import FastAPI


def include_feature_routers(app: FastAPI) -> None:
    app_root = Path(__file__).resolve().parents[1]
    feature_root = app_root / "app_features"

    for router_path in sorted(feature_root.rglob("router.py")):
        module_path = ".".join(router_path.relative_to(app_root).with_suffix("").parts)
        module = import_module(module_path)
        router = getattr(module, "router", None)
        if router is not None:
            app.include_router(router)
