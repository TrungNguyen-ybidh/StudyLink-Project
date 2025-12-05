from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app


# Calendar Blueprint
calendar = Blueprint("calendar", __name__)


# Maya-1: Return all assignments, exams, and projects with due dates and times for each student
@calendar.route("/calendar", methods=["GET"])
def get_student_calendar():
    try:
        cursor = db.get_db().cursor(dictionary=True)

        query = """
            SELECT s.studentID,
                   CONCAT(s.fName, ' ', s.lName) AS studentName,
                   cs.courseCode,
                   cs.courseName,
                   a.assignmentType,
                   a.title AS assignmentTitle,
                   a.assignmentDate AS dueDate,
                   a.assignmentTime AS dueTime
            FROM student s
            JOIN CourseSelectionStudent css ON s.studentID = css.studentID
            JOIN CourseSelection cs ON css.courseID = cs.courseID
            JOIN assignment a ON cs.courseID = a.courseID
            ORDER BY s.studentID, a.assignmentDate, a.assignmentTime;
        """

        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return jsonify(results), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500



# Maya-1: Add new event or assignment to the centralized calendar
@calendar.route("/calendar", methods=["POST"])
def add_calendar_item():
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        if not data or "type" not in data:
            return jsonify({"error": "Missing field: type"}), 400

        # INSERT EVENT
        if data["type"] == "event":
            required = ["name", "date", "startTime", "endTime", "location", "studentID"]
            for f in required:
                if f not in data:
                    return jsonify({"error": f"Missing event field: {f}"}), 400

            cursor.execute("""
                INSERT INTO event (name, date, startTime, endTime, location)
                VALUES (%s, %s, %s, %s, %s)
            """, (data["name"], data["date"], data["startTime"], data["endTime"], data["location"]))

            event_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO attEvent (studentID, eventID)
                VALUES (%s, %s)
            """, (data["studentID"], event_id))

            db.get_db().commit()
            cursor.close()

            return jsonify({"message": "Event created successfully", "eventID": event_id}), 201


        # INSERT ASSIGNMENT
        elif data["type"] == "assignment":
            required = ["courseID", "assignmentType", "title", "assignmentDate", "assignmentTime"]
            for f in required:
                if f not in data:
                    return jsonify({"error": f"Missing assignment field: {f}"}), 400

            cursor.execute("""
                INSERT INTO assignment (courseID, assignmentType, title, assignmentDate, assignmentTime)
                VALUES (%s, %s, %s, %s, %s)
            """, (data["courseID"], data["assignmentType"], data["title"], data["assignmentDate"], data["assignmentTime"]))

            assignment_id = cursor.lastrowid
            db.get_db().commit()
            cursor.close()

            return jsonify({"message": "Assignment created successfully", "assignmentID": assignment_id}), 201


        else:
            return jsonify({"error": "Invalid type"}), 400

    except Error as e:
        return jsonify({"error": str(e)}), 500



# Maya-1: Update event or assignment details 
@calendar.route("/calendar/<string:item_type>/<int:item_id>", methods=["PUT"])
def update_calendar(item_type, item_id):
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        # UPDATE EVENT
        if item_type == "event":
            allowed = ["name", "date", "startTime", "endTime", "location"]

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

        # UPDATE ASSIGNMENT
        elif item_type == "assignment":
            allowed = ["courseID", "assignmentType", "title", "assignmentDate", "assignmentTime"]

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

    except Error as e:
        return jsonify({"error": str(e)}), 500



# Maya-1: Remove outdated events or assignments 
@calendar.route("/calendar", methods=["DELETE"])
def delete_calendar():
    try:
        data = request.get_json()

        if not data or "item_type" not in data or "item_id" not in data:
            return jsonify({"error": "item_type and item_id required"}), 400

        item_type = data["item_type"]
        item_id = data["item_id"]

        cursor = db.get_db().cursor()

        # DELETE EVENT
        if item_type == "event":
            cursor.execute("SELECT * FROM event WHERE eventID = %s", (item_id,))
            if not cursor.fetchone():
                cursor.close()
                return jsonify({"error": "Event not found"}), 404

            cursor.execute("DELETE FROM event WHERE eventID = %s", (item_id,))
            db.get_db().commit()
            cursor.close()
            return jsonify({"message": "Event deleted successfully"}), 200

        # DELETE ASSIGNMENT
        elif item_type == "assignment":
            cursor.execute("SELECT * FROM assignment WHERE assignmentID = %s", (item_id,))
            if not cursor.fetchone():
                cursor.close()
                return jsonify({"error": "Assignment not found"}), 404

            cursor.execute("DELETE FROM assignment WHERE assignmentID = %s", (item_id,))
            db.get_db().commit()
            cursor.close()
            return jsonify({"message": "Assignment deleted successfully"}), 200

        else:
            return jsonify({"error": "item_type must be 'event' or 'assignment'"}), 400

    except Error as e:
        return jsonify({"error": str(e)}), 500



# Create a Blueprint for reminder routes
reminder = Blueprint("reminder", __name__)

# Maya-2: Return all active reminders and notifications for upcoming events or assignments
@reminder.route("/reminder", methods=["GET"])
def get_reminder():
    try:
        cursor = db.get_db().cursor()

        query = """
        SELECT s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS studentName,
            a.title AS assignmentTitle,
            a.assignmentDate,
            a.assignmentTime,
            e.name AS eventName,
            e.date AS eventDate,
            e.startTime AS eventTime,
            r.message AS reminderMessage,
            r.date AS reminderDate,
            r.time AS reminderTime,
            r.isActive
        FROM student s
        JOIN CourseSelectionStudent css ON s.studentID = css.studentID
        JOIN CourseSelection cs ON css.courseID = cs.courseID
        JOIN assignment a ON cs.courseID = a.courseID
        JOIN attEvent ae ON s.studentID = ae.studentID
        JOIN event e ON ae.eventID = e.eventID
        JOIN reminder r ON (e.eventID = r.eventID OR a.assignmentID = r.assignmentID)
        WHERE r.isActive = TRUE
        AND r.date >= CURDATE()
        ORDER BY s.studentID, r.date, r.time
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        return jsonify(results), 200

    except Error as e:
        current_app.longer.error(f"Database error: {str(e)}")
        return jsonify({"error: str(e)"}), 500

# Maya-2: Add a new reminder or notification 
@reminder.route("/reminder", methods=["POST"])
def add_reminder():
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        # Validate required fields
        required_fields = ["studentID", "message", "date", "time"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Must specify EITHER eventID or assignmentID
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

        # Insert reminder
        insert_query = """
            INSERT INTO reminder (studentID, eventID, assignmentID, message, date, time, isActive)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """

        cursor.execute(insert_query, (
            data["studentID"],
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

    except Error as e:
        return jsonify({"error": str(e)}), 500

# Maya-2: Update an existing reminder’s message, status, or time
@reminder.route("/reminder/<int:reminder_id>", methods=["PUT"])
def update_reminder(reminder_id):
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        # Allowed fields to update
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

        # Check reminder exists
        cursor.execute("SELECT * FROM reminder WHERE reminderID = %s", (reminder_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Reminder not found"}), 404

        # Update reminder
        update_query = f"""
            UPDATE reminder
            SET {', '.join(update_fields)}
            WHERE reminderID = %s
        """

        cursor.execute(update_query, params)
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Reminder updated successfully"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500


# Maya-2: Delete a reminder
@reminder.route("/reminder", methods=["DELETE"])
def delete_reminder():
    try:
        data = request.get_json()

        if not data or "reminder_id" not in data:
            return jsonify({"error": "Request must include reminder_id"}), 400

        reminder_id = data["reminder_id"]

        cursor = db.get_db().cursor()

        # Check reminder exists
        cursor.execute("SELECT * FROM reminder WHERE reminderID = %s", (reminder_id,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            return jsonify({"error": "Reminder not found"}), 404

        # Delete reminder
        cursor.execute("DELETE FROM reminder WHERE reminderID = %s", (reminder_id,))
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Reminder deleted successfully"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500



# Create a Blueprint for grades routes
grades = Blueprint("grades", __name__)

# Maya-3: Retrieve all grades, assignment weights, and calculated outcomes
@grades.route("/grade", methods["GET"])
def get_grades():
    try:
        cursor = db.get_db().cursor()

        query = """
                SELECT s.studentID,
                    CONCAT(s.fName, ' ', s.lName) AS studentName,
                    cs.courseName,
                    a.assignmentID,
                            a.title AS assignmentTitle,
                        a.weight,
                        a.maxScore,
                        a.scoreReceived,
                        ROUND((a.scoreReceived / a.maxScore) * a.weight, 2) AS weightedScore,
                        ROUND(100 - SUM(a.weight), 2) AS remainingWeight
                    FROM student s
                    JOIN CourseSelectionStudent css ON s.studentID = css.studentID
                    JOIN CourseSelection cs ON css.courseID = cs.courseID
                    JOIN assignment a ON cs.courseID = a.courseID
                    GROUP BY s.studentID, c.courseID, c.courseName
                    ORDER BY s.studentID, c.courseName;
                """

        cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Database error: {str(e)}")



# Create a Blueprint for workload routes
workload = Blueprint("workload", __name__)

# Maya-4: Analyze total study hours, assignments, and events to suggest workload intensity per weekday
@workload.route("/workload", methods=["GET"])
def get_workload():
    try:
        cursor = db.get_db().cursor()

        query = """
                SELECT s.studentID,
                    CONCAT(s.fName, ' ', s.lName) AS studentName,
                        DAYNAME(ss.periodStart) AS weekday,
                        ROUND(SUM(ss.totalStudyHrs), 2) AS totalStudyHours,
                        COUNT(DISTINCT a.assignmentID) AS totalAssignments,
                        COUNT(DISTINCT e.eventID) AS totalEvents
                        CASE
                            WHEN SUM(ss.totalStudyHrs) < 3 AND COUNT(DISTINCT a.assignmentID <= 1 AND      COUNT(DISTINCT e.eventID) <= 1 THEN ‘Low-intensity workload’
                            WHEN SUM(ss.totalStudyHrs) BETWEEN 3 AND 7 THEN ‘Moderate workload’
                            ELSE THEN ‘High workload’
                            END AS workloadCategory
                    FROM student s
                    LEFT JOIN StudySummary ss ON s.studentID = ss.StudySummary
                    LEFT JOIN CourseSelectionStudent css ON s.studentID = css.studentID
                    LEFT JOIN CourseSelection cs ON css.courseID = cs.courseID
                    LEFT JOIN assignment a ON cs.courseID = a.courseID
                    LEFT JOIN attEvent ae ON s.studentID = ae.studentID
                    LEFT JOIN event e ON ae.eventID = e.eventID
                    GROUP BY s.studentID, studentName, weekday
                    ORDER BY s.studentID, FIELD(weekDay, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday');
                """
        
        cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Database error: {str(e)}")


# Create a Blueprint for events routes
events = Blueprint("events", __name__)

# Maya-5: Retrieve all personal events (clubs, work shifts, personal) 
@events.route("/events", methods=["GET"])
def get_events():
    try:
        cursor = db.get_db().cursor()

        query = """
                SELECT s.studentID,
                CONCAT(s.fName, ' ', s.lName) AS studentName,
                    e.name AS eventName,
                    e.type AS eventType,
                    e.location,
                        e.date,
                        e.startTime,
                        e.endTime
                FROM student s
                JOIN attEvent ae ON s.studentID = ae.studentID
                JOIN event e ON ae.eventID = e.eventID
                WHERE e.type IN ('club', 'work', 'personal')
                GROUP BY s.studentID, studentName
                ORDER BY s.studentID, e.date, e.startTime;
                """
        cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Database error: {str(e)}")

# Maya-5: Add new personal/club/work event 
@events.route("/events", methods=["POST"])
def add_event():
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        required = ["studentID", "name", "type", "date", "startTime", "endTime", "location"]
        for f in required:
            if f not in data:
                return jsonify({"error": f"Missing required field: {f}"}), 400

        # Validate type is allowed
        if data["type"] not in ["club", "work", "personal"]:
            return jsonify({"error": "type must be 'club', 'work', or 'personal'"}), 400

        # Insert event
        insert_event_query = """
            INSERT INTO event (name, type, date, startTime, endTime, location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_event_query, (
            data["name"],
            data["type"],
            data["date"],
            data["startTime"],
            data["endTime"],
            data["location"]
        ))

        event_id = cursor.lastrowid

        # Link event to student in attEvent
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

    except Error as e:
        return jsonify({"error": str(e)}), 500


# Maya-5: Update event details (type, time, location)
@events.route("/events/<string:item_type>/<int:item_id>", methods=["PUT"])
def update_events(item_type, item_id):
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        # Only allow updates if the item_type is "event"
        if item_type != "event":
            return jsonify({"error": "item_type must be 'event'"}), 400

        # Allowed editable fields
        allowed_fields = ["name", "type", "date", "startTime", "endTime", "location"]

        update_fields = []
        params = []

        # Build update list dynamically
        for f in allowed_fields:
            if f in data:
                update_fields.append(f"{f} = %s")
                params.append(data[f])

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        # Add event ID at the end of params list
        params.append(item_id)

        update_query = f"""
            UPDATE event
            SET {', '.join(update_fields)}
            WHERE eventID = %s
        """

        cursor.execute(update_query, params)
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Event updated successfully"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500


# Maya-5: Delete an event from the planner 
@events.route("/events", methods=["DELETE"])
def delete_events():
    try:
        data = request.get_json()

        if not data or "eventID" not in data:
            return jsonify({"error": "Request must include eventID"}), 400

        event_id = data["eventID"]

        cursor = db.get_db().cursor()

        # Check if event exists
        cursor.execute("SELECT * FROM event WHERE eventID = %s", (event_id,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            return jsonify({"error": "Event not found"}), 404
        
        # Delete from event table
        cursor.execute("DELETE FROM event WHERE eventID = %s", (event_id,))
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Event deleted successfully"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500



# Create a Blueprint for courses routes
courses = Blueprint("courses", __name__)

# Maya-6: Retrieve current and planned courses with prerequisite status 
@courses.route("/courses", methods=["GET"])
def get_courses():
    try:
        cursor = db.get_db().cursor()

        query = """
                SELECT s.studentID,
                CONCAT(s.fName, ' ', s.lName) AS studentName,
                cs.courseID,
                cs.courseCode,
                cs.courseName,
                cs.department,
                cs.credits,
                t.name AS term,
                CASE
                    WHEN prereq.courseID IS NULL THEN 'No prerequisites'
                    WHEN prereq.courseID IS NOT NULL
                        AND prereq.courseID IN (
                            SELECT courseID
                            FROM CourseSelectionStudent css2
                            WHERE css2.studentID = s.studentID
                        )
                        THEN 'Prerequisite satisfied'
                    ELSE 'Missing prerequisite'
                END AS prerequisiteStatus
            FROM student s
            JOIN CourseSelectionStudent css ON s.studentID = css.studentID
            JOIN CourseSelection cs ON css.courseID = cs.courseID
            LEFT JOIN term t ON cs.termID = t.termID
            LEFT JOIN CourseSelection prereq 
                ON prereq.department = cs.department 
                AND prereq.courseCode LIKE CONCAT(LEFT(cs.courseCode, 2), '1%')
            WHERE cs.courseCode LIKE '3%' OR cs.courseCode LIKE '4%'
            ORDER BY s.studentID, cs.courseCode;
                """

        cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"Database error: {str(e)}")

# Maya-6: Add a new course selection to plan
@courses.route("/courses", methods=["POST"])
def add_courses():
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        # Required fields
        required = ["studentID", "courseID", "termID"]
        for f in required:
            if f not in data:
                return jsonify({"error": f"Missing required field: {f}"}), 400

        # Insert into CourseSelectionStudent
        insert_query = """
            INSERT INTO CourseSelectionStudent (studentID, courseID, termID)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (
            data["studentID"],
            data["courseID"],
            data["termID"]
        ))

        db.get_db().commit()
        cursor.close()
        return jsonify({"message": "Course added to student plan successfully"}), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500


# Maya-6: Update course information (term, status, prerequisite)
@courses.route("/courses/<int:courseSelectionID>", methods=["PUT"])
def update_course(courseSelectionID):
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()

        allowed_fields = ["termID", "status"]
        update_fields = []
        params = []

        for f in allowed_fields:
            if f in data:
                update_fields.append(f"{f} = %s")
                params.append(data[f])

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(courseSelectionID)

        update_query = f"""
            UPDATE CourseSelectionStudent
            SET {', '.join(update_fields)}
            WHERE courseSelectionID = %s
        """

        cursor.execute(update_query, params)
        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Course selection updated successfully"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500


# Maya-6: Remove a course from student plan
@courses.route("/courses", methods=["DELETE"])
def delete_course():
    try:
        data = request.get_json()
        
        if not data or "courseSelectionID" not in data:
            return jsonify({"error": "courseSelectionID is required"}), 400

        courseSelectionID = data["courseSelectionID"]

        cursor = db.get_db().cursor()

        # Check existence
        cursor.execute("""
            SELECT * FROM CourseSelectionStudent
            WHERE courseSelectionID = %s
        """, (courseSelectionID,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            return jsonify({"error": "Course selection not found"}), 404

        # Delete
        cursor.execute("""
            DELETE FROM CourseSelectionStudent
            WHERE courseSelectionID = %s
        """, (courseSelectionID,))

        db.get_db().commit()
        cursor.close()

        return jsonify({"message": "Course removed from student plan"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500