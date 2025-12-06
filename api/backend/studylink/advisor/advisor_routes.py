from flask import Blueprint, jsonify, request
import logging
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

logger = logging.getLogger(__name__)

advisor_bp = Blueprint('advisor', __name__, url_prefix='/api/advisor')

#GET /api/advisor
@advisor_bp.route("/", methods=["GET"])
def get_advisors():
    """Return all advisors in the system."""
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT advisorID, fName, lName, email FROM advisor")
    advisors = cursor.fetchall()
    return jsonify(advisors), 200

#GET /api/advisor/<advisor_id>/students
@advisor_bp.route("/<int:advisor_id>/students", methods=["GET"])
def get_advisor_students(advisor_id):
    """Return all students assigned to a specific advisor."""
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.studentID, s.fName, s.lName, s.email
        FROM student s
        JOIN advisor_student ast ON s.studentID = ast.studentID
        WHERE ast.advisorID = %s
    """, (advisor_id,))
    students = cursor.fetchall()
    return jsonify(students), 200

#GET /api/studylink/advisor/<advisor_id>/reports
@advisor_bp.route("/<int:advisor_id>/reports", methods=["GET"])
def get_advisor_reports(advisor_id):
    """Return all reports created by a specific advisor."""
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.reportID, r.title, r.content, r.created_at
        FROM report r
        JOIN advisor_report ar ON r.reportID = ar.reportID
        WHERE ar.advisorID = %s
    """, (advisor_id,))
    reports = cursor.fetchall()
    return jsonify(reports), 200

#POST /advisor/<advisor_id>/reports
@advisor_bp.route("/<int:advisor_id>/reports", methods=["POST"])
def create_advisor_report(advisor_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO report (title, content, created_at)
        VALUES (%s, %s, NOW())
        RETURNING reportID
    """, (title, content))
    report_id = cursor.fetchone()['reportID']

    cursor.execute("""
        INSERT INTO advisor_report (advisorID, reportID)
        VALUES (%s, %s)
    """, (advisor_id, report_id))

    conn.commit()
    return jsonify({"message": "Report created", "reportID": report_id}), 201

#PUT /advisor/reports/<report_id>
@advisor_bp.route("/reports/<int:report_id>", methods=["PUT"])
def update_advisor_report(report_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title and not content:
        return jsonify({"error": "At least one of title or content must be provided"}), 400

    conn = db.get_db()
    cursor = conn.cursor()

    if title:
        cursor.execute("UPDATE report SET title = %s WHERE reportID = %s", (title, report_id))
    if content:
        cursor.execute("UPDATE report SET content = %s WHERE reportID = %s", (content, report_id))

    conn.commit()
    return jsonify({"message": "Report updated"}), 200 

#DELETE /advisor/reports/<report_id>
@advisor_bp.route("/reports/<int:report_id>", methods=["DELETE"])
def delete_advisor_report(report_id):
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM advisor_report WHERE reportID = %s", (report_id,))
    cursor.execute("DELETE FROM report WHERE reportID = %s", (report_id,))

    conn.commit()
    return jsonify({"message": "Report deleted"}), 200

