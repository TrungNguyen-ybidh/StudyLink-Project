
from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

# Blueprint for admin route
admin = Blueprint("admin", __name__)


# 1) Calendar connection: Get a student's calendar connection
@admin.route("/students/<int:student_id>/calendar", methods=["GET"])
def get_calendar_connection(student_id):
    try:
        current_app.logger.info("Starting get_calendar_connection request")
        cursor = db.get_db().cursor()

        query = """
        SELECT
            s.studentID,
            s.fName,
            s.lName,
            cc.externalCalendarID,
            cc.syncStatus,
            cc.lastSyncedAt
        FROM student AS s
        LEFT JOIN CalendarConnection AS cc
          ON s.studentID = cc.studentID
        WHERE s.studentID = %s;
        """
        cursor.execute(query, (student_id,))
        row = cursor.fetchone()
        cursor.close()

        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_calendar_connection: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 1) Calendar connection: Upsert calendar connection for student
@admin.route("/students/<int:student_id>/calendar", methods=["PUT"])
def upsert_calendar_connection(student_id):
    try:
        current_app.logger.info("Starting upsert_calendar_connection request")
        data = request.get_json(silent=True) or {}

        external_calendar_id = data.get("externalCalendarID")
        sync_status = data.get("syncStatus", "pending")

        if external_calendar_id is None:
            return jsonify({"error": "externalCalendarID is required"}), 400

        cursor = db.get_db().cursor()

        cursor.execute(
            "SELECT 1 FROM CalendarConnection WHERE studentID = %s;",
            (student_id,),
        )
        exists = cursor.fetchone() is not None

        if exists:
            query = """
            UPDATE CalendarConnection
            SET externalCalendarID = %s,
                syncStatus = %s,
                lastSyncedAt = NOW()
            WHERE studentID = %s;
            """
            cursor.execute(query, (external_calendar_id, sync_status, student_id))
        else:
            query = """
            INSERT INTO CalendarConnection (studentID, externalCalendarID, lastSyncedAt, syncStatus)
            VALUES (%s, %s, NOW(), %s);
            """
            cursor.execute(query, (student_id, external_calendar_id, sync_status))

        db.get_db().commit()
        cursor.close()

        return jsonify({"studentID": student_id, "syncStatus": sync_status}), 200
    except Error as e:
        current_app.logger.error(f"Database error in upsert_calendar_connection: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 1) Calendar connection: Delete a student's calendar connection
@admin.route("/students/<int:student_id>/calendar", methods=["DELETE"])
def delete_calendar_connection(student_id):
    try:
        current_app.logger.info("Starting delete_calendar_connection request")
        cursor = db.get_db().cursor()

        cursor.execute(
            "DELETE FROM CalendarConnection WHERE studentID = %s;",
            (student_id,),
        )
        db.get_db().commit()
        cursor.close()

        return jsonify({"deleted": True, "studentID": student_id}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_calendar_connection: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 2) Terms: List all terms
@admin.route("/terms", methods=["GET"])
def get_terms():
    try:
        current_app.logger.info("Starting get_terms request")
        cursor = db.get_db().cursor()

        cursor.execute("SELECT termID, name, startDate, endDate FROM term ORDER BY startDate DESC;")
        terms = cursor.fetchall()
        cursor.close()

        return jsonify(terms), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_terms: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 2) Terms: Create a term
@admin.route("/terms", methods=["POST"])
def create_term():
    try:
        current_app.logger.info("Starting create_term request")
        data = request.get_json(silent=True) or {}

        name = data.get("name")
        start_date = data.get("startDate")
        end_date = data.get("endDate")

        if not name or not start_date or not end_date:
            return jsonify({"error": "name, startDate, endDate are required"}), 400

        cursor = db.get_db().cursor()
        cursor.execute(
            "INSERT INTO term (name, startDate, endDate) VALUES (%s, %s, %s);",
            (name, start_date, end_date),
        )
        db.get_db().commit()
        term_id = cursor.lastrowid
        cursor.close()

        return jsonify({"message": "Term created successfully", "termID": term_id}), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_term: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 2) Courses: Preview all courses for a term
@admin.route("/terms/<int:term_id>/courses", methods=["GET"])
def get_term_courses(term_id):
    try:
        current_app.logger.info("Starting get_term_courses request")
        cursor = db.get_db().cursor()

        query = """
        SELECT
            courseID,
            termID,
            courseCode,
            courseName,
            location,
            credits,
            instructor,
            department,
            date,
            startTime,
            endTime
        FROM CourseSelection
        WHERE termID = %s
        ORDER BY courseCode;
        """
        cursor.execute(query, (term_id,))
        courses = cursor.fetchall()
        cursor.close()

        return jsonify(courses), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_term_courses: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 2) Courses: Add a course to a term
@admin.route("/terms/<int:term_id>/courses", methods=["POST"])
def add_course_to_term(term_id):
    try:
        current_app.logger.info("Starting add_course_to_term request")
        data = request.get_json(silent=True) or {}

        required_fields = ["courseCode", "courseName", "credits", "department"]
        for field in required_fields:
            if field not in data or data.get(field) in (None, ""):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        cursor = db.get_db().cursor()
        query = """
        INSERT INTO CourseSelection
            (termID, courseCode, courseName, location, credits, instructor, department, date, startTime, endTime)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(
            query,
            (
                term_id,
                data.get("courseCode"),
                data.get("courseName"),
                data.get("location"),
                data.get("credits"),
                data.get("instructor"),
                data.get("department"),
                data.get("date"),
                data.get("startTime"),
                data.get("endTime"),
            ),
        )
        db.get_db().commit()
        course_id = cursor.lastrowid
        cursor.close()

        return jsonify({"message": "Course added successfully", "courseID": course_id}), 201
    except Error as e:
        current_app.logger.error(f"Database error in add_course_to_term: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 2) Courses: Delete a course from a term
@admin.route("/terms/<int:term_id>/courses/<int:course_id>", methods=["DELETE"])
def delete_course(term_id, course_id):
    try:
        current_app.logger.info("Starting delete_course request")
        cursor = db.get_db().cursor()

        cursor.execute(
            "DELETE FROM CourseSelection WHERE courseID = %s AND termID = %s;",
            (course_id, term_id),
        )
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Course deleted successfully", "courseID": course_id}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_course: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 3) Import metrics + link to an importJob
@admin.route("/imports/metrics", methods=["POST"])
def import_metrics():
    try:
        current_app.logger.info("Starting import_metrics request")
        data = request.get_json(silent=True) or {}

        admin_id = data.get("adminID")
        job_type = data.get("jobType", "Metric Import")
        metrics = data.get("metrics")

        if admin_id is None:
            return jsonify({"error": "adminID is required"}), 400
        if not isinstance(metrics, list) or len(metrics) == 0:
            return jsonify({"error": "metrics must be a non-empty list"}), 400

        required = ["studentID", "category", "privacyLevel", "unit", "metricType", "metricName", "metricValue"]
        for m in metrics:
            for field in required:
                if field not in m or m.get(field) in (None, ""):
                    return jsonify({"error": f"Each metric must include {required}"}), 400

        cursor = db.get_db().cursor()

        cursor.execute(
            """
            INSERT INTO importJob (errorCount, jobType, StartTime, endTime, Status, adminID)
            VALUES (0, %s, NOW(), NOW(), 'Completed', %s);
            """,
            (job_type, admin_id),
        )
        job_id = cursor.lastrowid

        inserted_metric_ids = []
        for m in metrics:
            cursor.execute(
                """
                INSERT INTO metric
                    (studentID, courseID, category, privacyLevel, description, unit, metricType, metricName, metricValue)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    m.get("studentID"),
                    m.get("courseID"),
                    m.get("category"),
                    m.get("privacyLevel"),
                    m.get("description"),
                    m.get("unit"),
                    m.get("metricType"),
                    m.get("metricName"),
                    m.get("metricValue"),
                ),
            )
            metric_id = cursor.lastrowid
            inserted_metric_ids.append(metric_id)

            cursor.execute(
                "INSERT INTO ImportJob_Metric (jobID, metricID) VALUES (%s, %s);",
                (job_id, metric_id),
            )

        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Metrics imported", "jobID": job_id, "insertedMetricIDs": inserted_metric_ids}), 201
    except Error as e:
        current_app.logger.error(f"Database error in import_metrics: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 4) Log a data error tied to a job (ImportJobError + DataError)
@admin.route("/jobs/<int:job_id>/errors", methods=["POST"])
def log_job_error(job_id):
    try:
        current_app.logger.info("Starting log_job_error request")
        data = request.get_json(silent=True) or {}

        admin_id = data.get("adminID")
        if admin_id is None:
            return jsonify({"error": "adminID is required"}), 400

        error_type = data.get("errorType", "unknown")
        error_status = data.get("errorStatus", "open")

        cursor = db.get_db().cursor()

        cursor.execute("INSERT INTO ImportJobError (jobID) VALUES (%s);", (job_id,))
        error_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO DataError (errorID, adminID, errorType, errorStatus)
            VALUES (%s, %s, %s, %s);
            """,
            (error_id, admin_id, error_type, error_status),
        )

        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Error logged", "jobID": job_id, "errorID": error_id}), 201
    except Error as e:
        current_app.logger.error(f"Database error in log_job_error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 5) Rebuild a student's plan (new StudyPlan + new PlanBlocks)
@admin.route("/students/<int:student_id>/plans/rebuild", methods=["POST"])
def rebuild_student_plan(student_id):
    try:
        current_app.logger.info("Starting rebuild_student_plan request")
        data = request.get_json(silent=True) or {}

        blocks = data.get("blocks", [])
        if not isinstance(blocks, list):
            return jsonify({"error": "blocks must be a list"}), 400

        for b in blocks:
            if not isinstance(b, dict) or b.get("isLocked") is None:
                return jsonify({"error": "Each block must include isLocked"}), 400

        cursor = db.get_db().cursor()

        cursor.execute(
            "SELECT COALESCE(MAX(versionNum), 0) AS maxVer FROM StudyPlan WHERE studentID = %s;",
            (student_id,),
        )
        max_ver_row = cursor.fetchone()
        next_ver = int(max_ver_row["maxVer"]) + 1

        cursor.execute(
            "UPDATE StudyPlan SET status = 'Archived' WHERE studentID = %s AND status = 'Active';",
            (student_id,),
        )

        cursor.execute(
            """
            INSERT INTO StudyPlan (studentID, status, versionNum, notes, currentCredits)
            VALUES (%s, 'Active', %s, %s, %s);
            """,
            (student_id, next_ver, data.get("notes"), data.get("currentCredits")),
        )
        plan_id = cursor.lastrowid

        for b in blocks:
            cursor.execute(
                """
                INSERT INTO PlanBlock (planID, blockType, isLocked, startTime, endTime)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (plan_id, b.get("blockType"), b.get("isLocked"), b.get("startTime"), b.get("endTime")),
            )

        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Plan rebuilt", "studentID": student_id, "planID": plan_id, "versionNum": next_ver}), 201
    except Error as e:
        current_app.logger.error(f"Database error in rebuild_student_plan: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 6) Schedule health check: find overlaps in active plan blocks
@admin.route("/students/<int:student_id>/health/overlaps", methods=["GET"])
def find_overlapping_blocks(student_id):
    try:
        current_app.logger.info("Starting find_overlapping_blocks request")
        cursor = db.get_db().cursor()

        cursor.execute(
            """
            SELECT pb.blockID, pb.blockType, pb.startTime, pb.endTime
            FROM StudyPlan sp
            JOIN PlanBlock pb ON sp.planID = pb.planID
            WHERE sp.studentID = %s
              AND sp.status = 'Active'
              AND pb.startTime IS NOT NULL
              AND pb.endTime IS NOT NULL
            ORDER BY pb.startTime;
            """,
            (student_id,),
        )
        blocks = cursor.fetchall()
        cursor.close()

        overlaps = []
        for i in range(len(blocks) - 1):
            a = blocks[i]
            b = blocks[i + 1]
            if a["endTime"] > b["startTime"]:
                overlaps.append({"blockA": a, "blockB": b})

        return jsonify({"studentID": student_id, "overlaps": overlaps}), 200
    except Error as e:
        current_app.logger.error(f"Database error in find_overlapping_blocks: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 7) Weekly usage export (StudySummary in a date range)
@admin.route("/usage/weekly", methods=["GET"])
def weekly_usage():
    try:
        current_app.logger.info("Starting weekly_usage request")
        start = request.args.get("start")
        end = request.args.get("end")

        if not start or not end:
            return jsonify({"error": "start and end query params are required"}), 400

        cursor = db.get_db().cursor()
        query = """
        SELECT
            s.studentID,
            s.fName,
            s.lName,
            ss.summaryID,
            ss.totalStudyHrs,
            ss.avgStudyHrs,
            ss.avgSleep,
            ss.periodStart,
            ss.periodEnd
        FROM StudySummary ss
        JOIN student s ON ss.studentID = s.studentID
        WHERE ss.periodStart >= %s AND ss.periodEnd <= %s
        ORDER BY ss.periodStart, s.studentID;
        """
        cursor.execute(query, (start, end))
        rows = cursor.fetchall()
        cursor.close()

        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Database error in weekly_usage: {str(e)}")
        return jsonify({"error": str(e)}), 500
