from flask import Flask, jsonify, render_template_string, request
import os
import logging
import sys
import psycopg2

# Configure structured logging for CloudWatch
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("innovate-api")

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "innovate-dev-db.cmho0428anv7.us-east-1.rds.amazonaws.com")
DB_NAME = os.environ.get("DB_NAME", "innovate_dev")
DB_USER = os.environ.get("DB_USER", "dbadmin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "DevPassword2026!")

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Innovate Inc. Dev Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 font-sans antialiased min-h-screen flex flex-col justify-between">
    <div class="max-w-4xl mx-auto px-6 py-12 w-full">
        <header class="mb-10 border-b border-gray-800 pb-6 flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight text-white">Innovate Inc. Control Center</h1>
                <p class="text-sm text-gray-400 mt-1">EKS Fargate & Amazon RDS PostgreSQL Integration</p>
            </div>
            <span class="px-3 py-1 text-xs font-semibold bg-emerald-900/50 text-emerald-400 border border-emerald-700/50 rounded-full">Environment: {{ environment }}</span>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <!-- API Status Card -->
            <div class="bg-gray-800/60 border border-gray-700/60 rounded-xl p-6 shadow-lg backdrop-blur-sm">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-lg font-semibold text-gray-200">API Service</h2>
                    <span class="h-3 w-3 rounded-full bg-emerald-500 animate-pulse"></span>
                </div>
                <p class="text-sm text-gray-400 mb-4">Flask backend container running securely on AWS EKS Fargate.</p>
                <a href="/health" target="_blank" class="inline-flex items-center text-sm font-medium text-indigo-400 hover:text-indigo-300">
                    Check /health Endpoint &rarr;
                </a>
            </div>

            <!-- Database Status Card -->
            <div class="bg-gray-800/60 border border-gray-700/60 rounded-xl p-6 shadow-lg backdrop-blur-sm">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-lg font-semibold text-gray-200">PostgreSQL Database</h2>
                    <span class="h-3 w-3 rounded-full {% if db_status == 'success' %}bg-emerald-500{% else %}bg-rose-500{% endif %}"></span>
                </div>
                <p class="text-sm text-gray-400 mb-2">Connected to Amazon RDS instance (`innovate-dev-db`).</p>
                <div class="bg-gray-900/80 rounded p-3 text-xs font-mono text-gray-300 mb-4 overflow-x-auto border border-gray-800">
                    {{ db_message }}
                </div>
                <a href="/db-test" target="_blank" class="inline-flex items-center text-sm font-medium text-indigo-400 hover:text-indigo-300">
                    Test /db-test Endpoint &rarr;
                </a>
            </div>
        </div>
    </div>
    
    <footer class="border-t border-gray-800 py-6 text-center text-xs text-gray-500">
        Innovate Inc. Infrastructure &bull; Secured via AWS VPC & EKS Fargate &bull; CloudWatch Monitored
    </footer>
</body>
</html>
"""

@app.before_request
def log_request_info():
    logger.info(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")

@app.route("/")
def home():
    env = os.environ.get("APP_ENV", "dev")
    db_status = "error"
    db_message = "Not connected"
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=5432,
            connect_timeout=3
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()[0]
        cur.close()
        conn.close()
        db_status = "success"
        db_message = db_version
    except Exception as e:
        logger.error(f"Database connection error on home route: {str(e)}")
        db_message = str(e)

    return render_template_string(DASHBOARD_TEMPLATE, environment=env, db_status=db_status, db_message=db_message)

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/db-test")
def db_test():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=5432,
            connect_timeout=3
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        logger.info("Database test query executed successfully.")
        return jsonify({
            "status": "success",
            "database_version": db_version[0]
        }), 200
    except Exception as e:
        logger.error(f"Database test query failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
