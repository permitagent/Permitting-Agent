"""Flask app for Permitting Agent: web UI + API for SaaS."""

import os
import sys
from pathlib import Path

# Add src so permitting_agent is importable when not installed (e.g. Render, python app.py)
_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from flask import Flask, jsonify, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create-case", methods=["POST"])
def create_case():
    jurisdiction = request.form.get("jurisdiction", "").strip()
    address = request.form.get("address", "").strip()
    scope = request.form.get("scope", "small_cell").strip() or "small_cell"
    if not jurisdiction or not address:
        return redirect(url_for("index"))
    try:
        from permitting_agent.intake import IntakeService
        from permitting_agent.models import IntakeRequest, SiteDetails, ScopeOfWork, ScopeKind
        kind = ScopeKind(scope) if scope in ("small_cell", "fiber", "both") else ScopeKind.SMALL_CELL
        request_obj = IntakeRequest(
            jurisdiction=jurisdiction,
            site=SiteDetails(address=address, jurisdiction=jurisdiction),
            scope=ScopeOfWork(kind=kind),
        )
        data_dir = Path(os.environ.get("DATA_DIR", "data"))
        svc = IntakeService(data_dir=data_dir)
        case = svc.create_case(request_obj)
        return render_template(
            "success.html",
            case_id=case.id,
            jurisdiction=jurisdiction,
            address=address,
            scope=kind.value,
        )
    except Exception as e:
        return render_template("index.html", error=str(e)), 422


@app.route("/jurisdictions")
def adapters_page():
    try:
        from permitting_agent.adapters import list_adapters
        adapters = list_adapters()
    except Exception:
        adapters = []
    return render_template("adapters.html", adapters=adapters)


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/api")
def api_info():
    return jsonify({
        "service": "Permitting + Site Acquisition Agent",
        "status": "running",
        "version": "0.1.0",
        "docs": "CLI-first; run locally or extend with API routes. See README.",
    })


@app.route("/api/adapters")
def adapters():
    """List registered jurisdiction adapters (JSON)."""
    try:
        from permitting_agent.adapters import list_adapters
        return jsonify({"adapters": list_adapters()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
