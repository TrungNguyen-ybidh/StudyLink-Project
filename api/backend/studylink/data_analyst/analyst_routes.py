"""
Routes for analytics dashboard, engagement tracking, and student reports
Location: api/backend/studylink/data_analyst/analyst_routes.py
User Stories: 1.1, 1.2, 1.6

FIXED: Removed strict date filters that were causing empty results
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Create Blueprint
analyst = Blueprint('analyst', __name__)


# ============================================================================
# HEALTH CHECK (for debugging)
# ============================================================================

@analyst.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API and database connectivity"""
    current_app.logger.info('GET /analyst/health route')
    
    try:
        cursor = db.get_db().cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM student")
        student_count = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as count FROM metric")
        metric_count = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as count FROM dataset")
        dataset_count = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as count FROM StudySummary")
        summary_count = cursor.fetchone()
        
        response_data = {
            "status": "healthy",
            "database": "connected",
            "counts": {
                "students": student_count['count'] if student_count else 0,
                "metrics": metric_count['count'] if metric_count else 0,
                "datasets": dataset_count['count'] if dataset_count else 0,
                "study_summaries": summary_count['count'] if summary_count else 0
            }
        }
        
        return make_response(jsonify(response_data), 200)
        
    except Exception as e:
        current_app.logger.error(f'Health check failed: {str(e)}')
        return make_response(jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500)


# ============================================================================
# DASHBOARD ROUTES (User Story 1.1)
# ============================================================================

@analyst.route('/dashboard', methods=['GET'])
def get_dashboard_summary():
    """
    1.1 - Get dashboard summarizing study time, sleep, and GPA
    Returns student data with their most recent study summaries
    """
    current_app.logger.info('GET /analyst/dashboard route')
    cursor = db.get_db().cursor()
    
    # FIXED: Removed date filter, get most recent summary per student
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS studentName,
            s.GPA,
            s.riskFlag,
            ss.periodStart,
            ss.periodEnd,
            ss.totalStudyHrs,
            ss.avgStudyHrs,
            ss.avgSleep
        FROM student s
        LEFT JOIN StudySummary ss ON s.studentID = ss.studentID
        WHERE ss.summaryID = (
            SELECT ss2.summaryID 
            FROM StudySummary ss2 
            WHERE ss2.studentID = s.studentID 
            ORDER BY ss2.periodStart DESC 
            LIMIT 1
        )
        OR ss.summaryID IS NULL
        ORDER BY s.studentID
        LIMIT 50
    '''
    
    try:
        cursor.execute(query)
        theData = cursor.fetchall()
        current_app.logger.info(f'Dashboard returned {len(theData)} records')
    except Exception as e:
        current_app.logger.error(f'Dashboard query error: {str(e)}')
        # Fallback to simpler query
        cursor.execute('''
            SELECT s.studentID, CONCAT(s.fName, ' ', s.lName) AS studentName,
                   s.GPA, s.riskFlag, NULL as periodStart, NULL as periodEnd,
                   NULL as totalStudyHrs, NULL as avgStudyHrs, NULL as avgSleep
            FROM student s LIMIT 50
        ''')
        theData = cursor.fetchall()
    
    return make_response(jsonify(theData), 200)


@analyst.route('/dashboard/summary', methods=['GET'])
def get_aggregate_summary():
    """
    1.1 - Get aggregate summary statistics across all students
    """
    current_app.logger.info('GET /analyst/dashboard/summary route')
    cursor = db.get_db().cursor()
    
    # FIXED: No date filter, aggregate all available data
    query = '''
        SELECT
            COUNT(DISTINCT s.studentID) AS totalStudents,
            ROUND(AVG(s.GPA), 2) AS avgGPA,
            ROUND(AVG(ss.avgStudyHrs), 2) AS avgStudyHours,
            ROUND(AVG(ss.avgSleep), 2) AS avgSleepHours,
            SUM(CASE WHEN s.riskFlag = 1 THEN 1 ELSE 0 END) AS studentsAtRisk
        FROM student s
        LEFT JOIN StudySummary ss ON s.studentID = ss.studentID
    '''
    
    try:
        cursor.execute(query)
        theData = cursor.fetchone()
        
        # Convert Decimal types to float for JSON serialization
        if theData:
            theData = {
                'totalStudents': int(theData.get('totalStudents') or 0),
                'avgGPA': float(theData.get('avgGPA') or 0),
                'avgStudyHours': float(theData.get('avgStudyHours') or 0),
                'avgSleepHours': float(theData.get('avgSleepHours') or 0),
                'studentsAtRisk': int(theData.get('studentsAtRisk') or 0)
            }
        else:
            theData = {
                'totalStudents': 0,
                'avgGPA': 0,
                'avgStudyHours': 0,
                'avgSleepHours': 0,
                'studentsAtRisk': 0
            }
            
        current_app.logger.info(f'Summary data: {theData}')
        
    except Exception as e:
        current_app.logger.error(f'Summary query error: {str(e)}')
        theData = {
            'totalStudents': 0,
            'avgGPA': 0,
            'avgStudyHours': 0,
            'avgSleepHours': 0,
            'studentsAtRisk': 0
        }
    
    return make_response(jsonify(theData), 200)


# ============================================================================
# ENGAGEMENT ROUTES (User Story 1.2)
# ============================================================================

@analyst.route('/engagement', methods=['GET'])
def get_engagement_trends():
    """
    1.2 - Get daily and weekly engagement trends
    """
    current_app.logger.info('GET /analyst/engagement route')
    cursor = db.get_db().cursor()
    
    # FIXED: Simplified query to ensure data returns
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS student_name,
            DATE(m.metricDate) AS metric_date,
            WEEK(m.metricDate) AS week_number,
            COUNT(DISTINCT m.metricID) AS daily_metric_entries,
            SUM(CASE WHEN m.category = 'Study' THEN COALESCE(m.metricValue, 0) ELSE 0 END) AS total_study_hours
        FROM student s
        INNER JOIN metric m ON s.studentID = m.studentID
        GROUP BY s.studentID, s.fName, s.lName, DATE(m.metricDate), WEEK(m.metricDate)
        ORDER BY metric_date DESC
        LIMIT 100
    '''
    
    try:
        cursor.execute(query)
        theData = cursor.fetchall()
        
        # Convert any Decimal values to float
        for row in theData:
            if 'total_study_hours' in row and row['total_study_hours'] is not None:
                row['total_study_hours'] = float(row['total_study_hours'])
                
        current_app.logger.info(f'Engagement returned {len(theData)} records')
        
    except Exception as e:
        current_app.logger.error(f'Engagement query error: {str(e)}')
        theData = []
    
    return make_response(jsonify(theData), 200)


@analyst.route('/engagement/<int:student_id>', methods=['GET'])
def get_student_engagement(student_id):
    """
    1.2 - Get engagement trends for a specific student
    """
    current_app.logger.info(f'GET /analyst/engagement/{student_id} route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS student_name,
            DATE(m.metricDate) AS metric_date,
            COUNT(DISTINCT m.metricID) AS daily_metric_entries,
            SUM(CASE WHEN m.category = 'Study' THEN COALESCE(m.metricValue, 0) ELSE 0 END) AS total_study_hours
        FROM student s
        LEFT JOIN metric m ON s.studentID = m.studentID
        WHERE s.studentID = %s
        GROUP BY s.studentID, s.fName, s.lName, DATE(m.metricDate)
        ORDER BY metric_date DESC
    '''
    
    cursor.execute(query, (student_id,))
    theData = cursor.fetchall()
    
    if not theData:
        return make_response(jsonify({"message": "No engagement data found"}), 404)
    
    return make_response(jsonify(theData), 200)


# ============================================================================
# STUDENT REPORT ROUTES (User Story 1.6)
# ============================================================================

@analyst.route('/students/<int:student_id>/report', methods=['GET'])
def get_student_report(student_id):
    """
    1.6 - Get comprehensive student report for advisor presentations
    """
    current_app.logger.info(f'GET /analyst/students/{student_id}/report route')
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
            CASE
                WHEN s.riskFlag = 1 THEN 'At Risk'
                WHEN s.GPA < 2.5 THEN 'Warning'
                ELSE 'Good Standing'
            END AS status_summary
        FROM student s
        LEFT JOIN advisor a ON s.advisorID = a.advisorID
        WHERE s.studentID = %s
    '''
    
    cursor.execute(query, (student_id,))
    theData = cursor.fetchone()
    
    if not theData:
        return make_response(jsonify({"message": "Student not found"}), 404)
    
    # Add additional stats via separate queries
    try:
        # Get study summary stats
        cursor.execute('''
            SELECT AVG(avgStudyHrs) as avg_daily_study, AVG(avgSleep) as avg_sleep_hours
            FROM StudySummary WHERE studentID = %s
        ''', (student_id,))
        study_stats = cursor.fetchone()
        if study_stats:
            theData['avg_daily_study'] = float(study_stats['avg_daily_study'] or 0)
            theData['avg_sleep_hours'] = float(study_stats['avg_sleep_hours'] or 0)
        
        # Get course count
        cursor.execute('''
            SELECT COUNT(*) as enrolled_courses 
            FROM CourseSelectionStudent WHERE studentID = %s
        ''', (student_id,))
        course_count = cursor.fetchone()
        theData['enrolled_courses'] = course_count['enrolled_courses'] if course_count else 0
        
        # Get events attended
        cursor.execute('''
            SELECT COUNT(*) as events_attended 
            FROM attEvent WHERE studentID = %s
        ''', (student_id,))
        events = cursor.fetchone()
        theData['events_attended'] = events['events_attended'] if events else 0
        
        # Get avg assignment score
        cursor.execute('''
            SELECT AVG(a.scoreReceived) as avg_assignment_score
            FROM assignment a
            INNER JOIN CourseSelectionStudent css ON a.courseID = css.courseID
            WHERE css.studentID = %s AND a.status = 'graded'
        ''', (student_id,))
        scores = cursor.fetchone()
        theData['avg_assignment_score'] = float(scores['avg_assignment_score'] or 0) if scores else 0
        
    except Exception as e:
        current_app.logger.error(f'Error fetching additional stats: {str(e)}')
    
    # Convert GPA to float
    if 'GPA' in theData and theData['GPA'] is not None:
        theData['GPA'] = float(theData['GPA'])
    
    return make_response(jsonify(theData), 200)


@analyst.route('/students/reports', methods=['GET'])
def get_all_student_reports():
    """
    1.6 - Get summary reports for all students (for export)
    """
    current_app.logger.info('GET /analyst/students/reports route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            s.studentID,
            CONCAT(s.fName, ' ', s.lName) AS student_name,
            s.major,
            s.GPA,
            s.riskFlag,
            CASE
                WHEN s.riskFlag = 1 THEN 'At Risk'
                WHEN s.GPA < 2.5 THEN 'Warning'
                ELSE 'Good Standing'
            END AS status_summary
        FROM student s
        ORDER BY s.riskFlag DESC, s.GPA ASC
    '''
    
    cursor.execute(query)
    theData = cursor.fetchall()
    
    # Convert Decimal GPA to float
    for row in theData:
        if 'GPA' in row and row['GPA'] is not None:
            row['GPA'] = float(row['GPA'])
    
    current_app.logger.info(f'Student reports returned {len(theData)} records')
    
    return make_response(jsonify(theData), 200)