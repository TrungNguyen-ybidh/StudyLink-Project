"""
Routes for metric data management, corrections, and error tracking
Location: api/backend/studylink/data_analyst/metric_routes.py
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
    """
    current_app.logger.info('GET /data/metrics route')
    cursor = db.get_db().cursor()
    
    student_id = request.args.get('studentID', None)
    category = request.args.get('category', None)
    metric_type = request.args.get('metricType', None)
    
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
    if category and category != 'All':
        query += " AND m.category = %s"
        params.append(category)
    if metric_type and metric_type != 'All':
        query += " AND m.metricType = %s"
        params.append(metric_type)
        
    query += " ORDER BY m.metricDate DESC LIMIT 100"
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    # Convert Decimal to float for JSON
    for row in theData:
        if 'metricValue' in row and row['metricValue'] is not None:
            row['metricValue'] = float(row['metricValue'])
    
    current_app.logger.info(f'Metrics returned {len(theData)} records')
    return make_response(jsonify(theData), 200)


@metrics.route('/metrics/<int:metric_id>', methods=['GET'])
def get_metric(metric_id):
    """Get a specific metric by ID"""
    current_app.logger.info(f'GET /data/metrics/{metric_id} route')
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
        return make_response(jsonify({"error": "Metric not found"}), 404)
    
    if 'metricValue' in theData and theData['metricValue'] is not None:
        theData['metricValue'] = float(theData['metricValue'])
    
    return make_response(jsonify(theData), 200)


@metrics.route('/metrics', methods=['POST'])
def create_metric():
    """1.3 - Create new metric entries"""
    current_app.logger.info('POST /data/metrics route')
    
    data = request.json
    current_app.logger.info(f'Received data: {data}')
    
    required_fields = ['studentID', 'category', 'metricName', 'metricValue']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return make_response(jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400)
    
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
    return make_response(jsonify({"message": "Metric created", "metricID": new_id}), 201)


@metrics.route('/metrics/<int:metric_id>', methods=['PUT'])
def update_metric(metric_id):
    """1.4 - Update/correct metric values"""
    current_app.logger.info(f'PUT /data/metrics/{metric_id} route')
    
    data = request.json
    if not data:
        return make_response(jsonify({"error": "No data provided"}), 400)
    
    cursor = db.get_db().cursor()
    
    # Check if metric exists
    cursor.execute("SELECT metricID, description FROM metric WHERE metricID = %s", (metric_id,))
    existing = cursor.fetchone()
    
    if not existing:
        return make_response(jsonify({"error": "Metric not found"}), 404)
    
    updates = []
    params = []
    
    if 'metricValue' in data:
        updates.append("metricValue = %s")
        params.append(data['metricValue'])
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
        return make_response(jsonify({"error": "No valid fields to update"}), 400)
        
    params.append(metric_id)
    query = f"UPDATE metric SET {', '.join(updates)} WHERE metricID = %s"
    
    cursor.execute(query, params)
    db.get_db().commit()
    
    return make_response(jsonify({"message": "Metric updated"}), 200)


@metrics.route('/metrics/<int:metric_id>', methods=['DELETE'])
def delete_metric(metric_id):
    """1.4 - Remove erroneous metric entries"""
    current_app.logger.info(f'DELETE /data/metrics/{metric_id} route')
    cursor = db.get_db().cursor()
    
    cursor.execute("SELECT metricID FROM metric WHERE metricID = %s", (metric_id,))
    if not cursor.fetchone():
        return make_response(jsonify({"error": "Metric not found"}), 404)
    
    cursor.execute("DELETE FROM metric WHERE metricID = %s", (metric_id,))
    db.get_db().commit()
    
    return make_response(jsonify({"message": "Metric deleted"}), 200)


# ============================================================================
# DATA ERROR ROUTES (User Story 1.4)
# ============================================================================

@metrics.route('/data-errors', methods=['GET'])
def get_data_errors():
    """1.4 - Retrieve data error logs"""
    current_app.logger.info('GET /data/data-errors route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            de.errorID,
            de.adminID,
            sa.name AS adminName,
            de.detectedAt,
            de.errorType,
            de.errorStatus
        FROM DataError de
        LEFT JOIN SystemAdmin sa ON de.adminID = sa.adminID
        ORDER BY de.detectedAt DESC
        LIMIT 100
    '''
    
    cursor.execute(query)
    theData = cursor.fetchall()
    
    current_app.logger.info(f'Data errors returned {len(theData)} records')
    return make_response(jsonify(theData), 200)


@metrics.route('/data-errors', methods=['POST'])
def create_data_error():
    """1.4 - Log data errors detected during analysis"""
    current_app.logger.info('POST /data/data-errors route')
    
    data = request.json
    
    required_fields = ['errorID', 'adminID', 'errorType', 'errorStatus']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return make_response(jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400)
    
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
    
    return make_response(jsonify({"message": "Data error logged"}), 201)


@metrics.route('/data-errors/<int:error_id>/<int:admin_id>', methods=['PUT'])
def update_data_error(error_id, admin_id):
    """1.4 - Update error status"""
    current_app.logger.info(f'PUT /data/data-errors/{error_id}/{admin_id} route')
    
    data = request.json
    if not data or 'errorStatus' not in data:
        return make_response(jsonify({"error": "Missing errorStatus field"}), 400)
    
    cursor = db.get_db().cursor()
    
    query = '''
        UPDATE DataError
        SET errorStatus = %s
        WHERE errorID = %s AND adminID = %s
    '''
    cursor.execute(query, (data['errorStatus'], error_id, admin_id))
    db.get_db().commit()
    
    if cursor.rowcount == 0:
        return make_response(jsonify({"error": "Data error not found"}), 404)
    
    return make_response(jsonify({"message": "Error status updated"}), 200)


# ============================================================================
# ASSIGNMENT ROUTES (User Stories 1.2, 1.4, 1.6)
# ============================================================================

@metrics.route('/assignments', methods=['GET'])
def get_assignments():
    """1.2/1.6 - Retrieve assignment data"""
    current_app.logger.info('GET /data/assignments route')
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
    if status and status != 'All':
        query += " AND a.status = %s"
        params.append(status)
    if assignment_type and assignment_type != 'All':
        query += " AND a.assignmentType = %s"
        params.append(assignment_type)
        
    query += " ORDER BY a.assignmentDate DESC LIMIT 100"
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    # Convert Decimal to float
    for row in theData:
        if 'scoreReceived' in row and row['scoreReceived'] is not None:
            row['scoreReceived'] = float(row['scoreReceived'])
        if 'weight' in row and row['weight'] is not None:
            row['weight'] = float(row['weight'])
    
    current_app.logger.info(f'Assignments returned {len(theData)} records')
    return make_response(jsonify(theData), 200)


@metrics.route('/assignments/<int:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    """1.4 - Update assignment scores and status"""
    current_app.logger.info(f'PUT /data/assignments/{assignment_id} route')
    
    data = request.json
    if not data:
        return make_response(jsonify({"error": "No data provided"}), 400)
    
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
        return make_response(jsonify({"error": "No valid fields to update"}), 400)
        
    params.append(assignment_id)
    query = f"UPDATE assignment SET {', '.join(updates)} WHERE assignmentID = %s"
    
    cursor.execute(query, params)
    db.get_db().commit()
    
    if cursor.rowcount == 0:
        return make_response(jsonify({"error": "Assignment not found"}), 404)
    
    return make_response(jsonify({"message": "Assignment updated"}), 200)