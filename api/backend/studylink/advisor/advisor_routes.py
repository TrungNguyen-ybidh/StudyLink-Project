from flask import Blueprint, jsonify, request
from backend.db_connection import db
from flask import current_app

advisor_bp = Blueprint('advisor', __name__, url_prefix='/api/advisor')


# ============================================
# GET ALL ADVISORS
# ============================================
@advisor_bp.route("/", methods=["GET"])
def get_advisors():
    """Return all advisors in the system."""
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            SELECT advisorID, fname, lName, email, department 
            FROM advisor
            ORDER BY lName, fname
        """)
        advisors = cursor.fetchall()
        cursor.close()
        return jsonify(advisors), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching advisors: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# GET ADVISOR BY ID
# ============================================
@advisor_bp.route("/<int:advisor_id>", methods=["GET"])
def get_advisor(advisor_id):
    """Return a specific advisor by ID."""
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            SELECT advisorID, fname, lName, email, department 
            FROM advisor
            WHERE advisorID = %s
        """, (advisor_id,))
        advisor = cursor.fetchone()
        cursor.close()
        
        if not advisor:
            return jsonify({"error": "Advisor not found"}), 404
        
        return jsonify(advisor), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching advisor: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# LOOKUP ADVISOR BY EMAIL
# ============================================
@advisor_bp.route("/lookup/<path:email>", methods=["GET"])
def lookup_advisor(email):
    """Return advisor info by email."""
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            SELECT advisorID, fname, lName, email, department
            FROM advisor
            WHERE email = %s
        """, (email,))
        advisor = cursor.fetchone()
        cursor.close()

        if not advisor:
            return jsonify({"error": "Advisor not found"}), 404

        return jsonify(advisor), 200
    except Exception as e:
        current_app.logger.error(f"Error looking up advisor: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# GET STUDENTS FOR AN ADVISOR
# ============================================
@advisor_bp.route("/<int:advisor_id>/students", methods=["GET"])
def get_advisor_students(advisor_id):
    """Return all students assigned to a specific advisor."""
    try:
        current_app.logger.info(f"Fetching students for advisor_id: {advisor_id}")
        
        cursor = db.get_db().cursor()
        
        # First, let's check what we get with a simple query
        cursor.execute("SELECT COUNT(*) as count FROM student WHERE advisorID = %s", (advisor_id,))
        count_result = cursor.fetchone()
        current_app.logger.info(f"Count of students for advisor {advisor_id}: {count_result}")
        
        # Students are linked via student.advisorID foreign key
        cursor.execute("""
            SELECT 
                s.studentID,
                s.fName,
                s.lName,
                s.email,
                s.major,
                s.minor,
                s.GPA,
                s.riskFlag,
                s.enrollmentStatus,
                s.totalCredits,
                s.enrollmentYear
            FROM student s
            WHERE s.advisorID = %s
            ORDER BY s.lName, s.fName
        """, (advisor_id,))
        
        students = cursor.fetchall()
        current_app.logger.info(f"Fetched {len(students)} students")
        current_app.logger.info(f"Students data: {students}")
        
        cursor.close()
        
        # Convert Decimal GPA to float for JSON
        for student in students:
            if student.get('GPA'):
                student['GPA'] = float(student['GPA'])
        
        return jsonify(students), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching students: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ============================================
# GET REPORTS FOR AN ADVISOR
# ============================================
@advisor_bp.route("/<int:advisor_id>/reports", methods=["GET"])
def get_advisor_reports(advisor_id):
    """Return all reports created by a specific advisor."""
    try:
        cursor = db.get_db().cursor()
        
        # Using advisorReport table from your schema
        cursor.execute("""
            SELECT 
                r.reportID,
                r.studentID,
                r.advisorID,
                r.reportDesc,
                r.dateCreated,
                r.filePath,
                r.type,
                r.description,
                CONCAT(s.fName, ' ', s.lName) AS studentName
            FROM advisorReport r
            LEFT JOIN student s ON r.studentID = s.studentID
            WHERE r.advisorID = %s
            ORDER BY r.dateCreated DESC
        """, (advisor_id,))
        
        reports = cursor.fetchall()
        cursor.close()
        
        # Convert datetime to string for JSON
        for report in reports:
            if report.get('dateCreated'):
                report['dateCreated'] = str(report['dateCreated'])
        
        return jsonify(reports), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching reports: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# GET SINGLE REPORT
# ============================================
@advisor_bp.route("/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    """Return a specific report by ID."""
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            SELECT 
                r.reportID,
                r.studentID,
                r.advisorID,
                r.reportDesc,
                r.dateCreated,
                r.filePath,
                r.type,
                r.description,
                CONCAT(s.fName, ' ', s.lName) AS studentName
            FROM advisorReport r
            LEFT JOIN student s ON r.studentID = s.studentID
            WHERE r.reportID = %s
        """, (report_id,))
        
        report = cursor.fetchone()
        cursor.close()
        
        if not report:
            return jsonify({"error": "Report not found"}), 404
        
        if report.get('dateCreated'):
            report['dateCreated'] = str(report['dateCreated'])
        
        return jsonify(report), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching report: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# CREATE NEW REPORT
# ============================================
@advisor_bp.route("/<int:advisor_id>/reports", methods=["POST"])
def create_advisor_report(advisor_id):
    """Create a new report for a student."""
    try:
        data = request.get_json()
        
        # Validate required fields
        student_id = data.get('studentID')
        report_desc = data.get('reportDesc')
        report_type = data.get('type', 'meeting_note')
        description = data.get('description', '')
        file_path = data.get('filePath', '')

        if not student_id:
            return jsonify({"error": "studentID is required"}), 400

        cursor = db.get_db().cursor()

        # Insert new report
        cursor.execute("""
            INSERT INTO advisorReport 
                (studentID, advisorID, reportDesc, filePath, type, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, advisor_id, report_desc, file_path, report_type, description))

        report_id = cursor.lastrowid
        db.get_db().commit()
        cursor.close()

        return jsonify({
            "message": "Report created successfully",
            "reportID": report_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating report: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# UPDATE REPORT
# ============================================
@advisor_bp.route("/reports/<int:report_id>", methods=["PUT"])
def update_advisor_report(report_id):
    """Update an existing report."""
    try:
        data = request.get_json()
        
        cursor = db.get_db().cursor()
        
        # Check if report exists
        cursor.execute("SELECT * FROM advisorReport WHERE reportID = %s", (report_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Report not found"}), 404
        
        # Build update query dynamically
        allowed_fields = ['reportDesc', 'type', 'description', 'filePath']
        update_fields = []
        params = []
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        params.append(report_id)
        
        cursor.execute(f"""
            UPDATE advisorReport 
            SET {', '.join(update_fields)}
            WHERE reportID = %s
        """, params)
        
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Report updated successfully"}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating report: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# DELETE REPORT
# ============================================
@advisor_bp.route("/reports/<int:report_id>", methods=["DELETE"])
def delete_advisor_report(report_id):
    """Delete a report."""
    try:
        cursor = db.get_db().cursor()
        
        # Check if report exists
        cursor.execute("SELECT * FROM advisorReport WHERE reportID = %s", (report_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Report not found"}), 404
        
        cursor.execute("DELETE FROM advisorReport WHERE reportID = %s", (report_id,))
        db.get_db().commit()
        cursor.close()
        
        return jsonify({"message": "Report deleted successfully"}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting report: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# GET ALL REPORTS FOR A STUDENT
# ============================================
@advisor_bp.route("/student/<int:student_id>/reports", methods=["GET"])
def get_student_reports(student_id):
    """Return all reports for a specific student."""
    try:
        cursor = db.get_db().cursor()
        
        cursor.execute("""
            SELECT 
                r.reportID,
                r.studentID,
                r.advisorID,
                r.reportDesc,
                r.dateCreated,
                r.filePath,
                r.type,
                r.description,
                CONCAT(a.fname, ' ', a.lName) AS advisorName
            FROM advisorReport r
            LEFT JOIN advisor a ON r.advisorID = a.advisorID
            WHERE r.studentID = %s
            ORDER BY r.dateCreated DESC
        """, (student_id,))
        
        reports = cursor.fetchall()
        cursor.close()
        
        for report in reports:
            if report.get('dateCreated'):
                report['dateCreated'] = str(report['dateCreated'])
        
        return jsonify(reports), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching student reports: {e}")
        return jsonify({"error": str(e)}), 500