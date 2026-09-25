from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "innovate-dev-db.cmho0428anv7.us-east-1.rds.amazonaws.com")
DB_NAME = os.environ.get("DB_NAME", "innovate_dev")
DB_USER = os.environ.get("DB_USER", "dbadmin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "DevPassword2026!")

@app.route("/")
def home():
    return jsonify({
        "message": "Innovate Inc backend is running with PostgreSQL support",
        "environment": os.environ.get("APP_ENV", "unknown")
    })

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
            port=5432
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({
            "status": "success",
            "database_version": db_version[0]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
