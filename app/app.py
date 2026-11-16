from flask import Flask, jsonify, render_template_string, request
import os
import logging
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("innovate-api")

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "postgres-svc")
DB_NAME = os.environ.get("DB_NAME", "innovate_dev")
DB_USER = os.environ.get("DB_USER", "dbadmin")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=5432,
        connect_timeout=3
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
            status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Innovate Inc. Control Center ({{ environment }})</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 font-sans antialiased min-h-screen flex flex-col justify-between">
    <div class="max-w-4xl mx-auto px-6 py-12 w-full">
        <header class="mb-10 border-b border-gray-800 pb-6 flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight text-white">Innovate Inc. Control Center</h1>
                <p class="text-sm text-gray-400 mt-1">Kind Kubernetes &bull; ArgoCD GitOps &bull; PostgreSQL 16</p>
            </div>
            <div class="text-right">
                <span class="px-3 py-1 text-xs font-semibold bg-emerald-900/50 text-emerald-400 border border-emerald-700/50 rounded-full">Environment: {{ environment }}</span>
                <p class="text-xs text-gray-500 mt-2">DB: {{ db_name }} | Pod: {{ hostname }}</p>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-gray-800/60 border border-gray-700/60 rounded-xl p-6 shadow-lg">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-lg font-semibold text-gray-200">API Service</h2>
                    <span class="h-3 w-3 rounded-full bg-emerald-500 animate-pulse"></span>
                </div>
                <p class="text-sm text-gray-400 mb-4">Flask backend deployed via ArgoCD on Kind cluster <code class="text-indigo-300">innovate</code>.</p>
                <a href="/health" target="_blank" class="inline-flex items-center text-sm font-medium text-indigo-400 hover:text-indigo-300">
                    Check /health Endpoint &rarr;
                </a>
            </div>

            <div class="bg-gray-800/60 border border-gray-700/60 rounded-xl p-6 shadow-lg">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-lg font-semibold text-gray-200">PostgreSQL Database</h2>
                    <span class="h-3 w-3 rounded-full {% if db_status == 'success' %}bg-emerald-500{% else %}bg-rose-500{% endif %}"></span>
                </div>
                <p class="text-sm text-gray-400 mb-2">Connected to <code class="text-indigo-300">{{ db_host }}/{{ db_name }}</code>.</p>
                <div class="bg-gray-900/80 rounded p-3 text-xs font-mono text-gray-300 mb-4 overflow-x-auto border border-gray-800">
                    {{ db_message }}
                </div>
                <a href="/db-test" target="_blank" class="inline-flex items-center text-sm font-medium text-indigo-400 hover:text-indigo-300">
                    Test /db-test Endpoint &rarr;
                </a>
            </div>
        </div>

        <!-- Incident Log Section -->
        <div class="bg-gray-800/60 border border-gray-700/60 rounded-xl p-6 shadow-lg">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-gray-200">Emergency Incident Feed ({{ incidents|length }})</h2>
                <a href="/api/incidents" target="_blank" class="text-xs font-medium text-indigo-400 hover:text-indigo-300">JSON API &rarr;</a>
            </div>

            <form id="incidentForm" class="flex flex-col sm:flex-row gap-3 mb-6">
                <input type="text" id="title" placeholder="Describe incident (e.g., High latency on ingress)" required
                    class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm text-gray-100 focus:outline-none focus:border-indigo-500">
                <select id="severity" class="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100">
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM" selected>MEDIUM</option>
                    <option value="CRITICAL">CRITICAL</option>
                </select>
                <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-4 py-2 rounded-lg">
                    Log Incident
                </button>
            </form>

            <div class="space-y-2">
                {% for item in incidents %}
                <div class="flex items-center justify-between bg-gray-900/70 border border-gray-800 rounded-lg px-4 py-3 text-sm">
                    <div>
                        <span class="font-medium text-gray-100">{{ item.title }}</span>
                        <span class="text-xs text-gray-500 ml-2">#{{ item.id }} &bull; {{ item.created_at }}</span>
                    </div>
                    <span class="px-2 py-0.5 text-xs font-semibold rounded
                        {% if item.severity == 'CRITICAL' %}bg-rose-900/60 text-rose-300 border border-rose-700/50
                        {% elif item.severity == 'MEDIUM' %}bg-amber-900/60 text-amber-300 border border-amber-700/50
                        {% else %}bg-sky-900/60 text-sky-300 border border-sky-700/50{% endif %}">
                        {{ item.severity }}
                    </span>
                </div>
                {% else %}
                <p class="text-sm text-gray-500">No incidents recorded in {{ db_name }} yet.</p>
                {% endfor %}
            </div>
        </div>
    </div>

    <footer class="border-t border-gray-800 py-6 text-center text-xs text-gray-500">
        Innovate Inc. Local GitOps Platform &bull; Kind + Ingress-NGINX + ArgoCD
    </footer>

    <script>
        document.getElementById('incidentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('title').value;
            const severity = document.getElementById('severity').value;
            const res = await fetch('/api/incidents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, severity })
            });
            if (res.ok) window.location.reload();
        });
    </script>
</body>
</html>
"""


@app.before_request
def log_request_info():
    logger.info(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")


@app.route("/")
def home():
    env = os.environ.get("APP_ENV", "dev")
    hostname = os.environ.get("HOSTNAME", "local")
    db_status = "error"
    db_message = "Not connected"
    incidents = []
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT version();")
        db_message = cur.fetchone()["version"]
        cur.execute("SELECT id, title, severity, status, to_char(created_at, 'YYYY-MM-DD HH24:MI') AS created_at FROM incidents ORDER BY id DESC LIMIT 10;")
        incidents = cur.fetchall()
        cur.close()
        conn.close()
        db_status = "success"
    except Exception as e:
        logger.error(f"Database error on home route: {str(e)}")
        db_message = str(e)

    return render_template_string(
        DASHBOARD_TEMPLATE,
        environment=env,
        hostname=hostname,
        db_host=DB_HOST,
        db_name=DB_NAME,
        db_status=db_status,
        db_message=db_message,
        incidents=incidents
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "environment": os.environ.get("APP_ENV", "dev"),
        "pod": os.environ.get("HOSTNAME", "local")
    }), 200


@app.route("/db-test")
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({
            "status": "success",
            "environment": os.environ.get("APP_ENV", "dev"),
            "database": DB_NAME,
            "database_version": db_version[0]
        }), 200
    except Exception as e:
        logger.error(f"Database test query failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/incidents", methods=["GET", "POST"])
def incidents_api():
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            title = (data.get("title") or "").strip()
            severity = (data.get("severity") or "MEDIUM").upper()
            if not title:
                return jsonify({"error": "title is required"}), 400
            if severity not in ("LOW", "MEDIUM", "CRITICAL"):
                severity = "MEDIUM"
            cur.execute(
                "INSERT INTO incidents (title, severity) VALUES (%s, %s) RETURNING id, title, severity, status, created_at;",
                (title, severity)
            )
            created = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return jsonify(created), 201

        cur.execute("SELECT id, title, severity, status, created_at FROM incidents ORDER BY id DESC LIMIT 25;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"environment": os.environ.get("APP_ENV", "dev"), "count": len(rows), "incidents": rows}), 200
    except Exception as e:
        logger.error(f"Incidents API error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
