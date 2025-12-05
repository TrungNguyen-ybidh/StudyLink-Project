"""
Routes for metric data management, corrections, and error tracking
User Stories: 1.1, 1.2, 1.3, 1.4
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Create Blueprint
metrics = Blueprint('metrics', __name__)


# ============================================================================
# METRICS ROUTES (User Stories 1.1, 1.2, 1.3, 1.4)
# ============================================================================

@metrics.route('/metrics', methods=['GET'])
def get_metrics():
    """
    1.1/1.2 - Retrieve metric data with optional filtering
    Supports filtering by studentID, category, metricType, date range
    """
    current_app.logger.info('GET /metrics route')
    cursor = db.get_db().cursor()
    
    student_id = request.args.get('studentID', None)
    category = request.args.get('category', None)
    metric_type = request.args.get('metricType', None)
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)
    
    query = '''
        SELECT
            m.metricID,
            m.studentID,
            CONCAT(s.fName, ' ', s.lName) AS studentName,
            m.courseID,
            m.category,
            m.privacyLevel,
            m.description,
            m.unit,
            m.metricType,
            m.metricName,
            m.metricValue,
            m.metricDate
        FROM metric m
        LEFT JOIN student s ON m.studentID = s.studentID
        WHERE 1=1
    '''
    params = []
    
    if student_id:
        query += " AND m.studentID = %s"
        params.append(student_id)
    if category:
        query += " AND m.category = %s"
        params.append(category)
    if metric_type:
        query += " AND m.metricType = %s"
        params.append(metric_type)
    if start_date:
        query += " AND m.metricDate >= %s"
        params.append(start_date)
    if end_date:
        query += " AND m.metricDate <= %s"
        params.append(end_date)
        
    query += " ORDER BY m.metricDate DESC LIMIT 100"
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@metrics.route('/metrics/<int:metric_id>', methods=['GET'])
def get_metric(metric_id):
    """
    Get a specific metric by ID
    """
    current_app.logger.info(f'GET /metrics/{metric_id} route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            m.metricID,
            m.studentID,
            CONCAT(s.fName, ' ', s.lName) AS studentName,
            m.courseID,
            m.category,
            m.privacyLevel,
            m.description,
            m.unit,
            m.metricType,
            m.metricName,
            m.metricValue,
            m.metricDate
        FROM metric m
        LEFT JOIN student s ON m.studentID = s.studentID
        WHERE m.metricID = %s
    '''
    cursor.execute(query, (metric_id,))
    theData = cursor.fetchone()
    
    if not theData:
        response = make_response(jsonify({"error": "Metric not found"}))
        response.status_code = 404
        return response
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@metrics.route('/metrics', methods=['POST'])
def create_metric():
    """
    1.3 - Create new metric entries from uploaded datasets
    """
    current_app.logger.info('POST /metrics route')
    
    data = request.json
    current_app.logger.info(f'Received data: {data}')
    
    required_fields = ['studentID', 'category', 'metricName', 'metricValue']
    missing = [f for f in required_fields if f not in data]
    if missing:
        response = make_response(jsonify({"error": f"Missing required fields: {', '.join(missing)}"}))
        response.status_code = 400
        return response
    
    cursor = db.get_db().cursor()
    
    query = '''
        INSERT INTO metric (
            studentID, courseID, category, privacyLevel, description,
            unit, metricType, metricName, metricValue, metricDate
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    '''
    cursor.execute(query, (
        data['studentID'],
        data.get('courseID'),
        data['category'],
        data.get('privacyLevel', 'low'),
        data.get('description', ''),
        data.get('unit', ''),
        data.get('metricType', 'numeric'),
        data['metricName'],
        data['metricValue']
    ))
    db.get_db().commit()
    
    new_id = cursor.lastrowid
    
    response = make_response(jsonify({"message": "Metric created", "metricID": new_id}))
    response.status_code = 201
    return response


@metrics.route('/metrics/<int:metric_id>', methods=['PUT'])
def update_metric(metric_id):
    """
    1.4 - Update/correct metric values
    Appends correction timestamp to description for audit trail
    """
    current_app.logger.info(f'PUT /metrics/{metric_id} route')
    
    data = request.json
    
    if not data:
        response = make_response(jsonify({"error": "No data provided"}))
        response.status_code = 400
        return response
    
    cursor = db.get_db().cursor()
    
    # Check if metric exists
    check_query = "SELECT metricID, description FROM metric WHERE metricID = %s"
    cursor.execute(check_query, (metric_id,))
    existing = cursor.fetchone()
    
    if not existing:
        response = make_response(jsonify({"error": "Metric not found"}))
        response.status_code = 404
        return response
    
    # Build update with correction note
    updates = []
    params = []
    
    if 'metricValue' in data:
        updates.append("metricValue = %s")
        params.append(data['metricValue'])
        
        # Append correction note to description
        old_desc = existing['description'] or ''
        new_desc = f"{old_desc} [CORRECTED]"
        updates.append("description = %s")
        params.append(new_desc)
        
    if 'category' in data:
        updates.append("category = %s")
        params.append(data['category'])
    if 'privacyLevel' in data:
        updates.append("privacyLevel = %s")
        params.append(data['privacyLevel'])
        
    if not updates:
        response = make_response(jsonify({"error": "No valid fields to update"}))
        response.status_code = 400
        return response
        
    params.append(metric_id)
    query = f"UPDATE metric SET {', '.join(updates)} WHERE metricID = %s"
    
    cursor.execute(query, params)
    db.get_db().commit()
    
    response = make_response(jsonify({"message": "Metric updated"}))
    response.status_code = 200
    return response


@metrics.route('/metrics/<int:metric_id>', methods=['DELETE'])
def delete_metric(metric_id):
    """
    1.4 - Remove erroneous metric entries
    """
    current_app.logger.info(f'DELETE /metrics/{metric_id} route')
    cursor = db.get_db().cursor()
    
    # Check if metric exists
    check_query = "SELECT metricID FROM metric WHERE metricID = %s"
    cursor.execute(check_query, (metric_id,))
    
    if not cursor.fetchone():
        response = make_response(jsonify({"error": "Metric not found"}))
        response.status_code = 404
        return response
    
    # Perform delete
    delete_query = "DELETE FROM metric WHERE metricID = %s"
    cursor.execute(delete_query, (metric_id,))
    db.get_db().commit()
    
    response = make_response(jsonify({"message": "Metric deleted"}))
    response.status_code = 200
    return response


# ============================================================================
# DATA ERROR ROUTES (User Story 1.4)
# ============================================================================

@metrics.route('/data-errors', methods=['GET'])
def get_data_errors():
    """
    1.4 - Retrieve data error logs with optional filtering
    """
    current_app.logger.info('GET /data-errors route')
    cursor = db.get_db().cursor()
    
    error_type = request.args.get('errorType', None)
    error_status = request.args.get('errorStatus', None)
    admin_id = request.args.get('adminID', None)
    
    query = '''
        SELECT
            de.errorID,
            de.adminID,
            sa.name AS adminName,
            de.detectedAt,
            de.errorType,
            de.errorStatus,
            ij.jobType,
            ij.status AS jobStatus
        FROM DataError de
        LEFT JOIN SystemAdmin sa ON de.adminID = sa.adminID
        LEFT JOIN ImportJobError ije ON de.errorID = ije.errorID
        LEFT JOIN importJob ij ON ije.jobID = ij.jobID
        WHERE 1=1
    '''
    params = []
    
    if error_type:
        query += " AND de.errorType = %s"
        params.append(error_type)
    if error_status:
        query += " AND de.errorStatus = %s"
        params.append(error_status)
    if admin_id:
        query += " AND de.adminID = %s"
        params.append(admin_id)
        
    query += " ORDER BY de.detectedAt DESC"
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@metrics.route('/data-errors', methods=['POST'])
def create_data_error():
    """
    1.4 - Log data errors detected during analysis
    """
    current_app.logger.info('POST /data-errors route')
    
    data = request.json
    
    required_fields = ['errorID', 'adminID', 'errorType', 'errorStatus']
    missing = [f for f in required_fields if f not in data]
    if missing:
        response = make_response(jsonify({"error": f"Missing required fields: {', '.join(missing)}"}))
        response.status_code = 400
        return response
    
    cursor = db.get_db().cursor()
    
    query = '''
        INSERT INTO DataError (errorID, adminID, detectedAt, errorType, errorStatus)
        VALUES (%s, %s, NOW(), %s, %s)
    '''
    cursor.execute(query, (
        data['errorID'],
        data['adminID'],
        data['errorType'],
        data['errorStatus']
    ))
    db.get_db().commit()
    
    response = make_response(jsonify({"message": "Data error logged"}))
    response.status_code = 201
    return response


@metrics.route('/data-errors/<int:error_id>/<int:admin_id>', methods=['PUT'])
def update_data_error(error_id, admin_id):
    """
    1.4 - Update error status (e.g., from 'detected' to 'corrected')
    """
    current_app.logger.info(f'PUT /data-errors/{error_id}/{admin_id} route')
    
    data = request.json
    
    if not data or 'errorStatus' not in data:
        response = make_response(jsonify({"error": "Missing errorStatus field"}))
        response.status_code = 400
        return response
    
    cursor = db.get_db().cursor()
    
    query = '''
        UPDATE DataError
        SET errorStatus = %s
        WHERE errorID = %s AND adminID = %s
    '''
    cursor.execute(query, (data['errorStatus'], error_id, admin_id))
    db.get_db().commit()
    
    if cursor.rowcount == 0:
        response = make_response(jsonify({"error": "Data error not found"}))
        response.status_code = 404
        return response
    
    response = make_response(jsonify({"message": "Error status updated"}))
    response.status_code = 200
    return response


# ============================================================================
# ASSIGNMENT ROUTES (User Stories 1.2, 1.4, 1.6)
# ============================================================================

@metrics.route('/assignments', methods=['GET'])
def get_assignments():
    """
    1.2/1.6 - Retrieve assignment data with filtering
    """
    current_app.logger.info('GET /assignments route')
    cursor = db.get_db().cursor()
    
    course_id = request.args.get('courseID', None)
    status = request.args.get('status', None)
    assignment_type = request.args.get('type', None)
    
    query = '''
        SELECT
            a.assignmentID,
            a.courseID,
            cs.courseName,
            cs.courseCode,
            a.title,
            a.scoreReceived,
            a.weight,
            a.status,
            a.assignmentType,
            a.assignmentDate,
            a.assignmentTime,
            a.maxScore
        FROM assignment a
        LEFT JOIN CourseSelection cs ON a.courseID = cs.courseID
        WHERE 1=1
    '''
    params = []
    
    if course_id:
        query += " AND a.courseID = %s"
        params.append(course_id)
    if status:
        query += " AND a.status = %s"
        params.append(status)
    if assignment_type:
        query += " AND a.assignmentType = %s"
        params.append(assignment_type)
        
    query += " ORDER BY a.assignmentDate DESC"
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@metrics.route('/assignments/<int:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    """
    1.4 - Update assignment scores and status during corrections
    """
    current_app.logger.info(f'PUT /assignments/{assignment_id} route')
    
    data = request.json
    
    if not data:
        response = make_response(jsonify({"error": "No data provided"}))
        response.status_code = 400
        return response
    
    cursor = db.get_db().cursor()
    
    updates = []
    params = []
    
    if 'scoreReceived' in data:
        updates.append("scoreReceived = %s")
        params.append(data['scoreReceived'])
    if 'status' in data:
        updates.append("status = %s")
        params.append(data['status'])
    if 'weight' in data:
        updates.append("weight = %s")
        params.append(data['weight'])
        
    if not updates:
        response = make_response(jsonify({"error": "No valid fields to update"}))
        response.status_code = 400
        return response
        
    params.append(assignment_id)
    query = f"UPDATE assignment SET {', '.join(updates)} WHERE assignmentID = %s"
    
    cursor.execute(query, params)
    db.get_db().commit()
    
    if cursor.rowcount == 0:
        response = make_response(jsonify({"error": "Assignment not found"}))
        response.status_code = 404
        return response
    
    response = make_response(jsonify({"message": "Assignment updated"}))
    response.status_code = 200
    return response