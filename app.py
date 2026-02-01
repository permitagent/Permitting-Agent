"""Minimal Flask app for Render: status + optional API stubs for permitting agent."""

import os
from pathlib import Path

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({
        "service": "Permitting + Site Acquisition Agent",
        "status": "running",
        "version": "0.1.0",
        "docs": "CLI-first; use Root Directory 'permitting_agent' and run CLI locally or via API extensions.",
    })


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/adapters")
def adapters():
    """List registered jurisdiction adapters (no auth in MVP)."""
    try:
        from permitting_agent.adapters import list_adapters
        return jsonify({"adapters": list_adapters()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
