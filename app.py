"""Flask app for Permitting Agent: web UI + API for SaaS."""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add src so permitting_agent is importable when not installed (e.g. Render, python app.py)
_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from flask import Flask, jsonify, render_template, request, redirect, url_for, session, Response

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")


@app.route("/")
def index():
    return render_template("index.html")


# ----- Submit online application flow -----

@app.route("/submit-online", methods=["GET"])
def submit_online_start():
    return render_template("submit_online_start.html")


@app.route("/submit-online/info", methods=["GET", "POST"])
def submit_online_info():
    if request.method == "GET":
        return redirect(url_for("submit_online_start"))
    portal_url = request.form.get("portal_url", "").strip()
    if not portal_url:
        return render_template("submit_online_start.html", error="Portal URL is required."), 422
    return render_template(
        "submit_online_info.html",
        portal_url=portal_url,
        username=request.form.get("username", ""),
        password=request.form.get("password", ""),
    )


@app.route("/submit-online/review", methods=["GET", "POST"])
def submit_online_review():
    if request.method == "GET":
        return redirect(url_for("submit_online_start"))
    portal_url = request.form.get("portal_url", "").strip()
    applicant_name = request.form.get("applicant_name", "").strip()
    jurisdiction = request.form.get("jurisdiction", "").strip()
    address = request.form.get("address", "").strip()
    if not all([portal_url, applicant_name, jurisdiction, address]):
        return redirect(url_for("submit_online_start"))
    return render_template(
        "submit_online_review.html",
        portal_url=portal_url,
        username=request.form.get("username", ""),
        password=request.form.get("password", ""),
        applicant_name=applicant_name,
        jurisdiction=jurisdiction,
        address=address,
        scope=request.form.get("scope", "small_cell"),
        contact_email=request.form.get("contact_email", ""),
        contact_phone=request.form.get("contact_phone", ""),
    )


@app.route("/submit-online/run", methods=["POST"])
def submit_online_run():
    applicant_name = request.form.get("applicant_name", "").strip()
    jurisdiction = request.form.get("jurisdiction", "").strip()
    address = request.form.get("address", "").strip()
    if not all([applicant_name, jurisdiction, address]):
        return redirect(url_for("submit_online_start"))
    return render_template(
        "submit_online_done.html",
        applicant_name=applicant_name,
        jurisdiction=jurisdiction,
        address=address,
    )


# ----- Fill out application flow -----

DEFAULT_FILL_FIELDS = [
    {"name": "applicant_name", "label": "Applicant / Company name", "value": "", "placeholder": "e.g. Acme Telecom"},
    {"name": "jurisdiction", "label": "Jurisdiction", "value": "", "placeholder": "e.g. City of Sample"},
    {"name": "address", "label": "Site address", "value": "", "placeholder": "e.g. 123 Main St"},
    {"name": "scope", "label": "Scope of work", "value": "small_cell", "placeholder": ""},
    {"name": "contact_email", "label": "Contact email", "value": "", "placeholder": "you@company.com"},
    {"name": "contact_phone", "label": "Contact phone", "value": "", "placeholder": "(555) 123-4567"},
]


@app.route("/fill-application", methods=["GET"])
def fill_application_start():
    return render_template("fill_application_start.html")


@app.route("/fill-application/parse", methods=["POST"])
def fill_application_parse():
    form_url = request.form.get("form_url", "").strip()
    form_file = request.files.get("form_file")
    fields = list(DEFAULT_FILL_FIELDS)

    if form_file and form_file.filename:
        try:
            suffix = Path(form_file.filename).suffix.lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                form_file.save(tmp.name)
                tmp_path = Path(tmp.name)
            try:
                from permitting_agent.document_review.parsers import parse_document
                result = parse_document(tmp_path)
                if result.success and result.artifact and result.artifact.extracted_fields:
                    for ef in result.artifact.extracted_fields:
                        fields.append({
                            "name": ef.name,
                            "label": ef.name.replace("_", " ").title(),
                            "value": ef.value or "",
                            "placeholder": "",
                        })
            finally:
                tmp_path.unlink(missing_ok=True)
        except Exception as e:
            return render_template("fill_application_start.html", error=str(e)), 422
    elif form_url:
        session["fill_form_url"] = form_url
        # URL parsing: for MVP we keep default fields only

    session["fill_fields"] = fields
    return redirect(url_for("fill_application_fields"))


@app.route("/fill-application/fields", methods=["GET"])
def fill_application_fields():
    fields = session.get("fill_fields", DEFAULT_FILL_FIELDS)
    return render_template("fill_application_fields.html", fields=fields)


@app.route("/fill-application/done", methods=["POST"])
def fill_application_done():
    action = request.form.get("action", "use_for_submission")
    data = {k.replace("field_", ""): v for k, v in request.form.items() if k.startswith("field_") and v}
    session["filled_application_data"] = data
    if action == "download":
        return Response(
            json.dumps(data, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=application-data.json"},
        )
    return render_template("fill_application_done.html", action=action)


# ----- Legacy / Jurisdictions -----

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
    })


@app.route("/api/adapters")
def adapters():
    try:
        from permitting_agent.adapters import list_adapters
        return jsonify({"adapters": list_adapters()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
