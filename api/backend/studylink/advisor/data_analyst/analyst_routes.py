"""
Routes for analytics dashboard, engagement tracking, and student reports
User Stories: 1.1, 1.2, 1.6
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Create Blueprint
analyst = Blueprint('analyst', __name__)


# ============================================================================
# DASHBOARD ROUTES (User Story 1.1)
# ============================================================================

@analyst.route('/dashboard', methods=['GET'])
def get_dashboard_summary():
    """
    1.1 - Get dashboard summarizing study time, sleep, and GPA
    Returns aggregated metrics for the past week
    """
    current_app.logger.info('GET /dashboard route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS studentName,
            s.GPA,
            ss.periodStart,
            ss.periodEnd,
            ss.totalStudyHrs,
            ss.avgStudyHrs,
            ss.avgSleep,
            MAX(CASE WHEN m.metricName = 'study_hr' THEN m.metricValue END) AS latestDailyStudyHrs,
            MAX(CASE WHEN m.metricName = 'sleep' THEN m.metricValue END) AS latestDailySleepHrs
        FROM student s
        LEFT JOIN StudySummary ss ON ss.studentID = s.studentID
        LEFT JOIN metric m ON m.studentID = s.studentID
        WHERE ss.periodStart >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
           OR m.metricDate >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY s.studentID, s.fName, s.lName, s.GPA,
                 ss.periodStart, ss.periodEnd, ss.totalStudyHrs, ss.avgStudyHrs, ss.avgSleep
        ORDER BY s.studentID, ss.periodStart DESC
    '''
    cursor.execute(query)
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@analyst.route('/dashboard/summary', methods=['GET'])
def get_aggregate_summary():
    """
    1.1 - Get aggregate summary statistics across all students
    """
    current_app.logger.info('GET /dashboard/summary route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            COUNT(DISTINCT s.studentID) AS totalStudents,
            ROUND(AVG(s.GPA), 2) AS avgGPA,
            ROUND(AVG(ss.avgStudyHrs), 2) AS avgStudyHours,
            ROUND(AVG(ss.avgSleep), 2) AS avgSleepHours,
            SUM(CASE WHEN s.riskFlag = 1 THEN 1 ELSE 0 END) AS studentsAtRisk
        FROM student s
        LEFT JOIN StudySummary ss ON s.studentID = ss.studentID
        WHERE ss.periodStart >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    '''
    cursor.execute(query)
    theData = cursor.fetchone()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


# ============================================================================
# ENGAGEMENT ROUTES (User Story 1.2)
# ============================================================================

@analyst.route('/engagement', methods=['GET'])
def get_engagement_trends():
    """
    1.2 - Get daily and weekly engagement trends for the past 30 days
    """
    current_app.logger.info('GET /engagement route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS student_name,
            DATE(m.metricDate) AS metric_date,
            WEEK(m.metricDate) AS week_number,
            COUNT(DISTINCT m.metricID) AS daily_metric_entries,
            SUM(CASE WHEN m.metricName = 'study_hr'
                THEN CAST(m.metricValue AS DECIMAL(5,2)) ELSE 0 END) AS total_study_hours,
            COUNT(DISTINCT ae.eventID) AS events_attended,
            COUNT(DISTINCT a.assignmentID) AS assignments_submitted,
            AVG(a.scoreReceived) AS avg_assignment_score,
            cc.lastSyncedAt AS last_calendar_sync,
            DATEDIFF(NOW(), cc.lastSyncedAt) AS days_since_last_sync
        FROM student s
        LEFT JOIN metric m ON s.studentID = m.studentID
        LEFT JOIN attEvent ae ON s.studentID = ae.studentID
        LEFT JOIN CourseSelectionStudent css ON s.studentID = css.studentID
        LEFT JOIN assignment a ON css.courseID = a.courseID
            AND a.status IN ('submitted', 'graded')
        LEFT JOIN CalendarConnection cc ON s.studentID = cc.studentID
        WHERE m.metricDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY s.studentID, DATE(m.metricDate), WEEK(m.metricDate), cc.lastSyncedAt
        ORDER BY s.studentID, metric_date DESC
    '''
    cursor.execute(query)
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@analyst.route('/engagement/<int:student_id>', methods=['GET'])
def get_student_engagement(student_id):
    """
    1.2 - Get engagement trends for a specific student
    """
    current_app.logger.info(f'GET /engagement/{student_id} route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS student_name,
            DATE(m.metricDate) AS metric_date,
            COUNT(DISTINCT m.metricID) AS daily_metric_entries,
            SUM(CASE WHEN m.metricName = 'study_hr'
                THEN CAST(m.metricValue AS DECIMAL(5,2)) ELSE 0 END) AS total_study_hours,
            COUNT(DISTINCT ae.eventID) AS events_attended
        FROM student s
        LEFT JOIN metric m ON s.studentID = m.studentID
        LEFT JOIN attEvent ae ON s.studentID = ae.studentID
        WHERE s.studentID = %s
          AND m.metricDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY s.studentID, DATE(m.metricDate)
        ORDER BY metric_date DESC
    '''
    cursor.execute(query, (student_id,))
    theData = cursor.fetchall()
    
    if not theData:
        response = make_response(jsonify({"message": "No engagement data found"}))
        response.status_code = 404
        return response
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


# ============================================================================
# STUDENT REPORT ROUTES (User Story 1.6)
# ============================================================================

@analyst.route('/students/<int:student_id>/report', methods=['GET'])
def get_student_report(student_id):
    """
    1.6 - Get comprehensive student report for advisor presentations
    """
    current_app.logger.info(f'GET /students/{student_id}/report route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS student_name,
            s.email,
            s.major,
            s.minor,
            s.GPA,
            s.enrollmentStatus,
            s.riskFlag,
            s.totalCredits,
            CONCAT(a.fName, ' ', a.lName) AS advisor_name,
            a.department AS advisor_department,
            ss.totalStudyHrs AS weekly_study_hours,
            ss.avgStudyHrs AS avg_daily_study,
            ss.avgSleep AS avg_sleep_hours,
            COUNT(DISTINCT css.courseID) AS enrolled_courses,
            ROUND(AVG(CASE WHEN asn.status = 'graded'
                THEN asn.scoreReceived ELSE NULL END), 2) AS avg_assignment_score,
            COUNT(DISTINCT CASE WHEN asn.status = 'graded'
                THEN asn.assignmentID END) AS completed_assignments,
            COUNT(DISTINCT ae.eventID) AS events_attended,
            CASE
                WHEN s.riskFlag = 1 THEN 'At Risk'
                WHEN s.GPA < 2.5 THEN 'Warning'
                WHEN ss.avgStudyHrs < 2 THEN 'Low Engagement'
                ELSE 'Good Standing'
            END AS status_summary,
            sp.status AS study_plan_status,
            sp.versionNum AS plan_version
        FROM student s
        LEFT JOIN advisor a ON s.advisorID = a.advisorID
        LEFT JOIN StudySummary ss ON s.studentID = ss.studentID
        LEFT JOIN CourseSelectionStudent css ON s.studentID = css.studentID
        LEFT JOIN assignment asn ON css.courseID = asn.courseID
        LEFT JOIN attEvent ae ON s.studentID = ae.studentID
        LEFT JOIN StudyPlan sp ON s.studentID = sp.studentID
        WHERE s.studentID = %s
        GROUP BY s.studentID, s.fName, s.lName, s.email, s.major, s.minor,
                 s.GPA, s.enrollmentStatus, s.riskFlag, s.totalCredits,
                 a.fName, a.lName, a.department, ss.totalStudyHrs, ss.avgStudyHrs,
                 ss.avgSleep, sp.status, sp.versionNum
    '''
    cursor.execute(query, (student_id,))
    theData = cursor.fetchone()
    
    if not theData:
        response = make_response(jsonify({"message": "Student not found"}))
        response.status_code = 404
        return response
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@analyst.route('/students/reports', methods=['GET'])
def get_all_student_reports():
    """
    1.6 - Get summary reports for all students (for export)
    """
    current_app.logger.info('GET /students/reports route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS student_name,
            s.major,
            s.GPA,
            s.riskFlag,
            ss.avgStudyHrs,
            ss.avgSleep,
            CASE
                WHEN s.riskFlag = 1 THEN 'At Risk'
                WHEN s.GPA < 2.5 THEN 'Warning'
                ELSE 'Good Standing'
            END AS status_summary
        FROM student s
        LEFT JOIN StudySummary ss ON s.studentID = ss.studentID
        ORDER BY s.riskFlag DESC, s.GPA ASC
    '''
    cursor.execute(query)
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response