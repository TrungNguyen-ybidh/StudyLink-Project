from flask import Blueprint, jsonify, request
from backend.db_connection import db
from flask import current_app


# ============================================
# CALENDAR BLUEPRINT - Maya User Story 1
# ============================================
calendar = Blueprint("calendar", __name__)


@calendar.route("/calendar", methods=["GET"])
def get_student_calendar():
    """Get calendar items for a specific student or all students."""
    try:
        cursor = db.get_db().cursor()
        student_id = request.args.get('studentID')

        # Base query for assignments
        assignment_query = """
            SELECT s.studentID,
                CONCAT(s.fName, ' ', s.lName) AS studentName,
                cs.courseCode,
                cs.courseName,
                a.assignmentID,
                a.assignmentType,
                a.title AS assignmentTitle,
                a.assignmentDate AS dueDate,
                a.assignmentTime AS dueTime,
                a.status,
                a.maxScore,
                'assignment' as itemType
            FROM student s
            JOIN CourseSelectionStudent css ON s.studentID = css.studentID
            JOIN CourseSelection cs ON css.courseID = cs.courseID
            LEFT JOIN assignment a ON cs.courseID = a.courseID
            WHERE a.assignmentID IS NOT NULL
        """
        
        # Base query for events
        event_query = """
            SELECT s.studentID,
                CONCAT(s.fName, ' ', s.lName) AS studentName,
                NULL AS courseCode,
                NULL AS courseName,
                e.eventID AS assignmentID,
                e.type AS assignmentType,
                e.name AS assignmentTitle,
                e.date AS dueDate,
                e.startTime AS dueTime,
                NULL AS status,
                NULL AS maxScore,
                'event' as itemType
            FROM student s
            JOIN attEvent ae ON s.studentID = ae.studentID
            JOIN event e ON ae.eventID = e.eventID
        """
        
        if student_id:
            assignment_query += f" AND s.studentID = {int(student_id)}"
            event_query += f" WHERE s.studentID = {int(student_id)}"
        
        full_query = f"""
                SELECT * FROM (
                    {assignment_query}
                    UNION ALL
                    {event_query}
                ) AS combined
                ORDER BY dueDate, dueTime
                """
        
        cursor.execute(full_query)
        results = cursor.fetchall()
        cursor.close()
        
        # Convert date/time objects to strings for JSON serialization
        for row in results:
            if row.get('dueDate'):
                row['dueDate'] = str(row['dueDate'])
            if row.get('dueTime'):
                row['dueTime'] = str(row['dueTime'])
        
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@calendar.route("/calendar", methods=["POST"])
def add_calendar_item():
    """Add a new event or assignment to the calendar."""
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        if not data or "type" not in data:
            return jsonify({"error": "Missing field: type"}), 400

        if data["type"] == "event":
            required = ["name", "date", "startTime", "studentID"]
            for f in required:
                if f not in data:
                    return jsonify({"error": f"Missing event field: {f}"}), 400

            cursor.execute("""
                INSERT INTO event (name, type, date, startTime, endTime, location)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data["name"],
                data.get("eventType", "academic"),
                data["date"],
                data["startTime"],
                data.get("endTime"),
                data.get("location", "")
            ))

            event_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO attEvent (studentID, eventID)
                VALUES (%s, %s)
            """, (data["studentID"], event_id))

            db.get_db().commit()
            cursor.close()

            return jsonify({
                "message": "Event created successfully",
                "eventID": event_id
            }), 201

        elif data["type"] == "assignment":
            required = ["courseID", "title", "assignmentDate", "assignmentTime", "maxScore"]
            for f in required:
                if f not in data:
                    return jsonify({"error": f"Missing assignment field: {f}"}), 400

            cursor.execute("""
                INSERT INTO assignment (courseID, assignmentType, title, assignmentDate, 
                                       assignmentTime, maxScore, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data["courseID"],
                data.get("assignmentType", "homework"),
                data["title"],
                data["assignmentDate"],
                data["assignmentTime"],
                data["maxScore"],
                data.get("status", "pending")
            ))

            assignment_id = cursor.lastrowid
            db.get_db().commit()
            cursor.close()

            return jsonify({
                "message": "Assignment created successfully",
                "assignmentID": assignment_id
            }), 201

        else:
            return jsonify({"error": "Invalid type. Must be 'event' or 'assignment'"}), 400

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@calendar.route("/calendar/<string:item_type>/<int:item_id>", methods=["PUT"])
def update_calendar(item_type, item_id):
    """Update an existing event or assignment."""
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        if item_type == "event":
            allowed = ["name", "type", "date", "startTime", "endTime", "location"]
            update_fields = []
            params = []

            for f in allowed:
                if f in data:
                    update_fields.append(f"{f} = %s")
                    params.append(data[f])

            if not update_fields:
                return jsonify({"error": "No valid event fields to update"}), 400

            params.append(item_id)

            cursor.execute(f"""
                UPDATE event
                SET {', '.join(update_fields)}
                WHERE eventID = %s
            """, params)

            db.get_db().commit()
            cursor.close()
            return jsonify({"message": "Event updated successfully"}), 200

        elif item_type == "assignment":
            allowed = ["courseID", "assignmentType", "title", "assignmentDate", 
                      "assignmentTime", "status", "scoreReceived", "maxScore", "weight"]
            update_fields = []
            params = []

            for f in allowed:
                if f in data:
                    update_fields.append(f"{f} = %s")
                    params.append(data[f])

            if not update_fields:
                return jsonify({"error": "No valid assignment fields to update"}), 400

            params.append(item_id)

            cursor.execute(f"""
                UPDATE assignment
                SET {', '.join(update_fields)}
                WHERE assignmentID = %s
            """, params)

            db.get_db().commit()
            cursor.close()
            return jsonify({"message": "Assignment updated successfully"}), 200

        else:
            return jsonify({"error": "item_type must be 'event' or 'assignment'"}), 400

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@calendar.route("/calendar/<string:item_type>/<int:item_id>", methods=["DELETE"])
def delete_calendar(item_type, item_id):
    """Delete an event or assignment from the calendar."""
    try:
        cursor = db.get_db().cursor()

        if item_type == "event":
            cursor.execute("SELECT * FROM event WHERE eventID = %s", (item_id,))
            if not cursor.fetchone():
                cursor.close()
                return jsonify({"error": "Event not found"}), 404

            cursor.execute("DELETE FROM attEvent WHERE eventID = %s", (item_id,))
            cursor.execute("DELETE FROM reminder WHERE eventID = %s", (item_id,))
            cursor.execute("DELETE FROM event WHERE eventID = %s", (item_id,))
            
            db.get_db().commit()
            cursor.close()
            return jsonify({"message": "Event deleted successfully"}), 200

        elif item_type == "assignment":
            cursor.execute("SELECT * FROM assignment WHERE assignmentID = %s", (item_id,))
            if not cursor.fetchone():
                cursor.close()
                return jsonify({"error": "Assignment not found"}), 404

            cursor.execute("DELETE FROM reminder WHERE assignmentID = %s", (item_id,))
            cursor.execute("DELETE FROM assignment WHERE assignmentID = %s", (item_id,))
            db.get_db().commit()
            cursor.close()
            return jsonify({"message": "Assignment deleted successfully"}), 200

        else:
            return jsonify({"error": "item_type must be 'event' or 'assignment'"}), 400

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================
# REMINDER BLUEPRINT - Maya User Story 2
# ============================================
reminder = Blueprint("reminder", __name__)


@reminder.route("/reminders", methods=["GET"])
def get_reminders():
    """Get all active reminders for upcoming events or assignments."""
    try:
        cursor = db.get_db().cursor()
        student_id = request.args.get('studentID')

        if student_id:
            query = """
                SELECT DISTINCT r.reminderID,
                       r.message AS reminderMessage,
                       r.date AS reminderDate,
                       r.time AS reminderTime,
                       r.isActive,
                       a.title AS assignmentTitle,
                       a.assignmentDate,
                       a.assignmentTime,
                       e.name AS eventName,
                       e.date AS eventDate,
                       e.startTime AS eventTime
                FROM reminder r
                LEFT JOIN assignment a ON r.assignmentID = a.assignmentID
                LEFT JOIN event e ON r.eventID = e.eventID
                LEFT JOIN attEvent ae ON e.eventID = ae.eventID
                LEFT JOIN CourseSelectionStudent css ON a.courseID = css.courseID
                WHERE r.isActive = TRUE
                  AND r.date >= CURDATE()
                  AND (ae.studentID = %s OR css.studentID = %s)
                ORDER BY r.date, r.time
            """
            cursor.execute(query, (student_id, student_id))
        else:
            query = """
                SELECT r.reminderID,
                       r.message AS reminderMessage,
                       r.date AS reminderDate,
                       r.time AS reminderTime,
                       r.isActive,
                       a.title AS assignmentTitle,
                       a.assignmentDate,
                       e.name AS eventName,
                       e.date AS eventDate
                FROM reminder r
                LEFT JOIN assignment a ON r.assignmentID = a.assignmentID
                LEFT JOIN event e ON r.eventID = e.eventID
                WHERE r.isActive = TRUE
                  AND r.date >= CURDATE()
                ORDER BY r.date, r.time
            """
            cursor.execute(query)

        results = cursor.fetchall()
        cursor.close()
        
        # Convert date/time objects to strings
        for row in results:
            for key in ['reminderDate', 'assignmentDate', 'eventDate']:
                if row.get(key):
                    row[key] = str(row[key])
            for key in ['reminderTime', 'assignmentTime', 'eventTime']:
                if row.get(key):
                    row[key] = str(row[key])
        
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@reminder.route("/reminders", methods=["POST"])
def add_reminder():
    """Create a new reminder for an event or assignment."""
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        required_fields = ["message", "date", "time"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        event_id = data.get("eventID")
        assignment_id = data.get("assignmentID")

        if not event_id and not assignment_id:
            return jsonify({
                "error": "You must include either eventID or assignmentID for a reminder."
            }), 400

        if event_id and assignment_id:
            return jsonify({
                "error": "A reminder can only be linked to ONE item: eventID OR assignmentID, not both."
            }), 400

        cursor.execute("""
            INSERT INTO reminder (eventID, assignmentID, message, date, time, isActive)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (
            event_id,
            assignment_id,
            data["message"],
            data["date"],
            data["time"]
        ))

        reminder_id = cursor.lastrowid
        db.get_db().commit()
        cursor.close()

        return jsonify({
            "message": "Reminder created successfully",
            "reminderID": reminder_id
        }), 201

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@reminder.route("/reminders/<int:reminder_id>", methods=["PUT"])
def update_reminder(reminder_id):
    """Update a reminder's message, status, or time."""
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        allowed_fields = ["message", "date", "time", "isActive"]
        update_fields = []
        params = []

        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(reminder_id)

        cursor.execute("SELECT * FROM reminder WHERE reminderID = %s", (reminder_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Reminder not found"}), 404

        cursor.execute(f"""
            UPDATE reminder
            SET {', '.join(update_fields)}
            WHERE reminderID = %s
        """, params)

        db.get_db().commit()
        cursor.close()
        return jsonify({"message": "Reminder updated successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@reminder.route("/reminders/<int:reminder_id>", methods=["DELETE"])
def delete_reminder(reminder_id):
    """Delete a reminder."""
    try:
        cursor = db.get_db().cursor()

        cursor.execute("SELECT * FROM reminder WHERE reminderID = %s", (reminder_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Reminder not found"}), 404

        cursor.execute("DELETE FROM reminder WHERE reminderID = %s", (reminder_id,))
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Reminder deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================
# GRADES BLUEPRINT - Maya User Story 3
# ============================================
grades = Blueprint("grades", __name__)


@grades.route("/grades", methods=["GET"])
def get_grades():
    """Get grades and calculate weighted scores for a student."""
    try:
        cursor = db.get_db().cursor()
        student_id = request.args.get('studentID')

        query = """
            SELECT s.studentID,
                   CONCAT(s.fName, ' ', s.lName) AS studentName,
                   cs.courseID,
                   cs.courseName,
                   cs.courseCode,
                   a.assignmentID,
                   a.title AS assignmentTitle,
                   a.assignmentType,
                   a.weight,
                   a.maxScore,
                   a.scoreReceived,
                   a.status,
                   CASE 
                       WHEN a.scoreReceived IS NOT NULL AND a.maxScore > 0 
                       THEN ROUND((a.scoreReceived / a.maxScore) * 100, 2)
                       ELSE NULL 
                   END AS percentageScore,
                   CASE 
                       WHEN a.scoreReceived IS NOT NULL AND a.weight IS NOT NULL 
                       THEN ROUND((a.scoreReceived / a.maxScore) * a.weight, 2)
                       ELSE NULL 
                   END AS weightedScore
            FROM student s
            JOIN CourseSelectionStudent css ON s.studentID = css.studentID
            JOIN CourseSelection cs ON css.courseID = cs.courseID
            LEFT JOIN assignment a ON cs.courseID = a.courseID
            WHERE a.assignmentID IS NOT NULL
        """

        if student_id:
            query += f" AND s.studentID = {int(student_id)}"
            query += " ORDER BY cs.courseName, a.assignmentDate"
        else:
            query += " ORDER BY s.studentID, cs.courseName, a.assignmentDate"
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@grades.route("/grades/summary", methods=["GET"])
def get_grade_summary():
    """Get aggregated grade summary by course for a student."""
    try:
        cursor = db.get_db().cursor()
        student_id = request.args.get('studentID')
        
        if not student_id:
            return jsonify({"error": "studentID is required"}), 400

        query = """
            SELECT cs.courseID,
                   cs.courseName,
                   cs.courseCode,
                   COUNT(a.assignmentID) AS totalAssignments,
                   COUNT(CASE WHEN a.status = 'graded' THEN 1 END) AS gradedAssignments,
                   ROUND(AVG(CASE 
                       WHEN a.scoreReceived IS NOT NULL AND a.maxScore > 0 
                       THEN (a.scoreReceived / a.maxScore) * 100 
                       ELSE NULL 
                   END), 2) AS averageScore
            FROM student s
            JOIN CourseSelectionStudent css ON s.studentID = css.studentID
            JOIN CourseSelection cs ON css.courseID = cs.courseID
            LEFT JOIN assignment a ON cs.courseID = a.courseID
            WHERE s.studentID = %s
            GROUP BY cs.courseID, cs.courseName, cs.courseCode
            ORDER BY cs.courseName
        """

        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        cursor.close()
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================
# WORKLOAD BLUEPRINT - Maya User Story 4
# ============================================
workload = Blueprint("workload", __name__)


@workload.route("/workload", methods=["GET"])
def get_workload():
    """Analyze total study hours, assignments, and events to suggest workload intensity."""
    try:
        cursor = db.get_db().cursor()
        student_id = request.args.get('studentID')
        
        if not student_id:
            return jsonify({"error": "studentID is required"}), 400

        # Get assignments per day
        assignment_query = """
            SELECT DAYNAME(a.assignmentDate) AS weekday,
                   DAYOFWEEK(a.assignmentDate) AS dayNum,
                   COUNT(DISTINCT a.assignmentID) AS totalAssignments
            FROM student s
            JOIN CourseSelectionStudent css ON s.studentID = css.studentID
            JOIN assignment a ON css.courseID = a.courseID
            WHERE s.studentID = %s
              AND a.assignmentDate >= CURDATE()
              AND a.assignmentDate <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DAYNAME(a.assignmentDate), DAYOFWEEK(a.assignmentDate)A
        """
        
        cursor.execute(assignment_query, (student_id,))
        assignment_data = {row['dayNum']: row for row in cursor.fetchall()}
        
        # Get events per day
        event_query = """
            SELECT DAYNAME(e.date) AS weekday,
                   DAYOFWEEK(e.date) AS dayNum,
                   COUNT(DISTINCT e.eventID) AS totalEvents
            FROM student s
            JOIN attEvent ae ON s.studentID = ae.studentID
            JOIN event e ON ae.eventID = e.eventID
            WHERE s.studentID = %s
              AND e.date >= CURDATE()
              AND e.date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DAYNAME(e.date), DAYOFWEEK(e.date)
        """
        
        cursor.execute(event_query, (student_id,))
        event_data = {row['dayNum']: row for row in cursor.fetchall()}
        
        # Get student info
        cursor.execute("SELECT CONCAT(fName, ' ', lName) AS studentName FROM student WHERE studentID = %s", (student_id,))
        student_info = cursor.fetchone()
        student_name = student_info['studentName'] if student_info else 'Unknown'
        
        cursor.close()
        
        # Combine results
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        results = []
        
        for day_num in range(1, 8):
            assignments = assignment_data.get(day_num, {}).get('totalAssignments', 0)
            events = event_data.get(day_num, {}).get('totalEvents', 0)
            total = assignments + events
            
            if total <= 1:
                category = 'Low-intensity'
                suggestion = 'Good day for rest or catching up'
            elif total <= 3:
                category = 'Moderate'
                suggestion = 'Normal workload day'
            else:
                category = 'High-intensity'
                suggestion = 'Heavy day - plan study time carefully'
            
            results.append({
                'studentID': student_id,
                'studentName': student_name,
                'weekday': days[day_num - 1],
                'dayNum': day_num,
                'totalAssignments': assignments,
                'totalEvents': events,
                'workloadCategory': category,
                'suggestedAction': suggestion
            })
        
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@workload.route("/workload/summary", methods=["GET"])
def get_study_summary():
    """Get study summary including study hours and sleep data."""
    try:
        cursor = db.get_db().cursor()
        student_id = request.args.get('studentID')
        
        if not student_id:
            return jsonify({"error": "studentID is required"}), 400

        query = """
            SELECT ss.summaryID,
                   ss.totalStudyHrs,
                   ss.avgStudyHrs,
                   ss.avgSleep,
                   ss.periodStart,
                   ss.periodEnd,
                   s.fName,
                   s.lName,
                   s.GPA
            FROM StudySummary ss
            JOIN student s ON ss.studentID = s.studentID
            WHERE ss.studentID = %s
            ORDER BY ss.periodStart DESC
            LIMIT 10
        """

        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        cursor.close()
        
        # Convert datetime objects to strings
        for row in results:
            if row.get('periodStart'):
                row['periodStart'] = str(row['periodStart'])
            if row.get('periodEnd'):
                row['periodEnd'] = str(row['periodEnd'])
            if row.get('GPA'):
                row['GPA'] = float(row['GPA'])
        
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================
# EVENTS BLUEPRINT - Maya User Story 5
# ============================================
events = Blueprint("events", __name__)


@events.route("/events", methods=["GET"])
def get_events():
    """Get all events for a student, optionally filtered by type."""
    try:
        cursor = db.get_db().cursor()
        student_id = request.args.get('studentID')
        event_type = request.args.get('type')

        query = """
            SELECT e.eventID,
                   e.name AS eventName,
                   e.type AS eventType,
                   e.location,
                   e.date,
                   e.startTime,
                   e.endTime
            FROM event e
            JOIN attEvent ae ON e.eventID = ae.eventID
            WHERE 1=1
        """
        
        params = []
        
        if student_id:
            query += " AND ae.studentID = %s"
            params.append(student_id)
        
        if event_type:
            query += " AND e.type = %s"
            params.append(event_type)
        
        query += " ORDER BY e.date, e.startTime"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        # Convert date/time objects to strings
        for row in results:
            if row.get('date'):
                row['date'] = str(row['date'])
            if row.get('startTime'):
                row['startTime'] = str(row['startTime'])
            if row.get('endTime'):
                row['endTime'] = str(row['endTime'])
        
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@events.route("/events", methods=["POST"])
def add_event():
    """Create a new personal, club, or work event."""
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        required = ["studentID", "name", "type", "date", "startTime"]
        for f in required:
            if f not in data:
                return jsonify({"error": f"Missing required field: {f}"}), 400

        valid_types = ["club", "work", "personal", "academic"]
        if data["type"] not in valid_types:
            return jsonify({"error": f"type must be one of: {', '.join(valid_types)}"}), 400

        cursor.execute("""
            INSERT INTO event (name, type, date, startTime, endTime, location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["name"],
            data["type"],
            data["date"],
            data["startTime"],
            data.get("endTime"),
            data.get("location", "")
        ))

        event_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO attEvent (studentID, eventID)
            VALUES (%s, %s)
        """, (data["studentID"], event_id))

        db.get_db().commit()
        cursor.close()

        return jsonify({
            "message": "Event created successfully",
            "eventID": event_id
        }), 201

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@events.route("/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    """Update an existing event."""
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        allowed_fields = ["name", "type", "date", "startTime", "endTime", "location"]
        update_fields = []
        params = []

        for f in allowed_fields:
            if f in data:
                update_fields.append(f"{f} = %s")
                params.append(data[f])

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(event_id)

        cursor.execute("SELECT * FROM event WHERE eventID = %s", (event_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Event not found"}), 404

        cursor.execute(f"""
            UPDATE event
            SET {', '.join(update_fields)}
            WHERE eventID = %s
        """, params)

        db.get_db().commit()
        cursor.close()
        return jsonify({"message": "Event updated successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@events.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    """Delete an event from the planner."""
    try:
        cursor = db.get_db().cursor()

        cursor.execute("SELECT * FROM event WHERE eventID = %s", (event_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Event not found"}), 404

        cursor.execute("DELETE FROM attEvent WHERE eventID = %s", (event_id,))
        cursor.execute("DELETE FROM reminder WHERE eventID = %s", (event_id,))
        cursor.execute("DELETE FROM event WHERE eventID = %s", (event_id,))
        
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Event deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================
# COURSES BLUEPRINT - Maya User Story 6
# ============================================
courses = Blueprint("courses", __name__)


@courses.route("/courses", methods=["GET"])
def get_courses():
    """Get all courses for a student with prerequisite status."""
    try:
        cursor = db.get_db().cursor()
        student_id = request.args.get('studentID')

        query = """
            SELECT s.studentID,
                   CONCAT(s.fName, ' ', s.lName) AS studentName,
                   cs.courseID,
                   cs.courseCode,
                   cs.courseName,
                   cs.department,
                   cs.credits,
                   cs.instructor,
                   cs.location,
                   t.name AS termName,
                   t.startDate AS termStart,
                   t.endDate AS termEnd
            FROM student s
            JOIN CourseSelectionStudent css ON s.studentID = css.studentID
            JOIN CourseSelection cs ON css.courseID = cs.courseID
            LEFT JOIN term t ON cs.termID = t.termID
        """

        if student_id:
            query += f" WHERE s.studentID = {int(student_id)}"
            query += " ORDER BY t.startDate, cs.courseCode"
        else:
            query += " ORDER BY s.studentID, t.startDate, cs.courseCode"
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        
        # Convert date objects to strings
        for row in results:
            if row.get('termStart'):
                row['termStart'] = str(row['termStart'])
            if row.get('termEnd'):
                row['termEnd'] = str(row['termEnd'])
        
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@courses.route("/courses", methods=["POST"])
def add_course():
    """Add a course to a student's plan."""
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        required = ["studentID", "courseID"]
        for f in required:
            if f not in data:
                return jsonify({"error": f"Missing required field: {f}"}), 400

        cursor.execute("""
            SELECT * FROM CourseSelectionStudent
            WHERE studentID = %s AND courseID = %s
        """, (data["studentID"], data["courseID"]))
        
        if cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Student is already enrolled in this course"}), 400

        cursor.execute("""
            INSERT INTO CourseSelectionStudent (studentID, courseID)
            VALUES (%s, %s)
        """, (data["studentID"], data["courseID"]))

        db.get_db().commit()
        cursor.close()
        return jsonify({"message": "Course added to student plan successfully"}), 201

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@courses.route("/courses/<int:student_id>/<int:course_id>", methods=["DELETE"])
def delete_course(student_id, course_id):
    """Remove a course from a student's plan."""
    try:
        cursor = db.get_db().cursor()

        cursor.execute("""
            SELECT * FROM CourseSelectionStudent
            WHERE studentID = %s AND courseID = %s
        """, (student_id, course_id))
        
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Course selection not found"}), 404

        cursor.execute("""
            DELETE FROM CourseSelectionStudent
            WHERE studentID = %s AND courseID = %s
        """, (student_id, course_id))

        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Course removed from student plan"}), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@courses.route("/courses/catalog", methods=["GET"])
def get_course_catalog():
    """Get all available courses in the catalog."""
    try:
        cursor = db.get_db().cursor()
        term_id = request.args.get('termID')
        department = request.args.get('department')

        query = """
            SELECT cs.courseID,
                   cs.courseCode,
                   cs.courseName,
                   cs.department,
                   cs.credits,
                   cs.instructor,
                   cs.location,
                   cs.date,
                   cs.startTime,
                   cs.endTime,
                   t.name AS termName
            FROM CourseSelection cs
            LEFT JOIN term t ON cs.termID = t.termID
            WHERE 1=1
        """
        
        params = []
        
        if term_id:
            query += " AND cs.termID = %s"
            params.append(term_id)
        
        if department:
            query += " AND cs.department = %s"
            params.append(department)
        
        query += " ORDER BY cs.department, cs.courseCode"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        # Convert date/time objects to strings
        for row in results:
            if row.get('date'):
                row['date'] = str(row['date'])
            if row.get('startTime'):
                row['startTime'] = str(row['startTime'])
            if row.get('endTime'):
                row['endTime'] = str(row['endTime'])
        
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500