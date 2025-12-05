"""
Dataset Routes (Persona 1: Jordan Lee)
Location: api/backend/studylink/data_analyst/dataset_routes.py

Routes for dataset management, uploads, and archiving
User Stories: 1.3, 1.5
"""

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Create Blueprint
datasets = Blueprint('datasets', __name__)


# ============================================================================
# DATASET ROUTES (User Stories 1.3, 1.5)
# ============================================================================

@datasets.route('/datasets', methods=['GET'])
def get_all_datasets():
    """
    1.3/1.5 - Retrieve list of all datasets with metadata
    Supports filtering by category and archive status
    """
    current_app.logger.info('GET /datasets route')
    cursor = db.get_db().cursor()
    
    category = request.args.get('category', None)
    archived = request.args.get('archived', None)
    
    query = '''
        SELECT
            d.dataID,
            d.name AS dataset_name,
            d.category,
            d.source,
            d.created_at,
            COUNT(DISTINCT u.uploadID) AS total_uploads,
            COUNT(DISTINCT u.metricID) AS metrics_affected,
            MIN(u.uploadDate) AS first_upload,
            MAX(u.uploadDate) AS last_upload
        FROM dataset d
        LEFT JOIN upload u ON d.dataID = u.dataID
        WHERE 1=1
    '''
    params = []
    
    if archived == 'true':
        query += " AND d.category LIKE 'ARCHIVED_%%'"
    elif archived == 'false':
        query += " AND d.category NOT LIKE 'ARCHIVED_%%'"
        
    if category:
        query += " AND (d.category = %s OR d.category = CONCAT('ARCHIVED_', %s))"
        params.extend([category, category])
        
    query += '''
        GROUP BY d.dataID, d.name, d.category, d.source, d.created_at
        ORDER BY d.created_at DESC
    '''
    
    cursor.execute(query, params)
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@datasets.route('/datasets/<int:data_id>', methods=['GET'])
def get_dataset(data_id):
    """
    Get a specific dataset by ID
    """
    current_app.logger.info(f'GET /datasets/{data_id} route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            d.dataID,
            d.name,
            d.category,
            d.source,
            d.created_at,
            COUNT(DISTINCT u.uploadID) AS total_uploads
        FROM dataset d
        LEFT JOIN upload u ON d.dataID = u.dataID
        WHERE d.dataID = %s
        GROUP BY d.dataID
    '''
    cursor.execute(query, (data_id,))
    theData = cursor.fetchone()
    
    if not theData:
        response = make_response(jsonify({"error": "Dataset not found"}))
        response.status_code = 404
        return response
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@datasets.route('/datasets', methods=['POST'])
def create_dataset():
    """
    1.3 - Create a new dataset record when uploading a new CSV file
    """
    current_app.logger.info('POST /datasets route')
    
    data = request.json
    current_app.logger.info(f'Received data: {data}')
    
    # Validate required fields
    if not data or 'name' not in data or 'category' not in data:
        response = make_response(jsonify({"error": "Missing required fields: name, category"}))
        response.status_code = 400
        return response
    
    name = data['name']
    category = data['category']
    source = data.get('source', 'csv')
    
    cursor = db.get_db().cursor()
    
    query = '''
        INSERT INTO dataset (name, category, source, created_at)
        VALUES (%s, %s, %s, NOW())
    '''
    cursor.execute(query, (name, category, source))
    db.get_db().commit()
    
    new_id = cursor.lastrowid
    
    response = make_response(jsonify({"message": "Dataset created", "dataID": new_id}))
    response.status_code = 201
    return response


@datasets.route('/datasets/<int:data_id>', methods=['PUT'])
def update_dataset(data_id):
    """
    1.5 - Update dataset metadata
    """
    current_app.logger.info(f'PUT /datasets/{data_id} route')
    
    data = request.json
    
    if not data:
        response = make_response(jsonify({"error": "No data provided"}))
        response.status_code = 400
        return response
    
    cursor = db.get_db().cursor()
    
    # Build dynamic update query
    updates = []
    params = []
    
    if 'name' in data:
        updates.append("name = %s")
        params.append(data['name'])
    if 'category' in data:
        updates.append("category = %s")
        params.append(data['category'])
    if 'source' in data:
        updates.append("source = %s")
        params.append(data['source'])
        
    if not updates:
        response = make_response(jsonify({"error": "No valid fields to update"}))
        response.status_code = 400
        return response
        
    params.append(data_id)
    query = f"UPDATE dataset SET {', '.join(updates)} WHERE dataID = %s"
    
    cursor.execute(query, params)
    db.get_db().commit()
    
    if cursor.rowcount == 0:
        response = make_response(jsonify({"error": "Dataset not found"}))
        response.status_code = 404
        return response
    
    response = make_response(jsonify({"message": "Dataset updated"}))
    response.status_code = 200
    return response


@datasets.route('/datasets/<int:data_id>/archive', methods=['PUT'])
def archive_dataset(data_id):
    """
    1.5 - Archive a dataset by updating its category and name
    """
    current_app.logger.info(f'PUT /datasets/{data_id}/archive route')
    cursor = db.get_db().cursor()
    
    query = '''
        UPDATE dataset
        SET category = CONCAT('ARCHIVED_', category),
            name = CONCAT('[ARCHIVED] ', name)
        WHERE dataID = %s
          AND category NOT LIKE 'ARCHIVED_%%'
    '''
    cursor.execute(query, (data_id,))
    db.get_db().commit()
    
    if cursor.rowcount == 0:
        response = make_response(jsonify({"error": "Dataset not found or already archived"}))
        response.status_code = 404
        return response
    
    response = make_response(jsonify({"message": "Dataset archived"}))
    response.status_code = 200
    return response


@datasets.route('/datasets/<int:data_id>', methods=['DELETE'])
def delete_dataset(data_id):
    """
    1.5 - Permanently remove archived datasets
    """
    current_app.logger.info(f'DELETE /datasets/{data_id} route')
    cursor = db.get_db().cursor()
    
    # First check if it exists and is archived
    check_query = "SELECT category FROM dataset WHERE dataID = %s"
    cursor.execute(check_query, (data_id,))
    result = cursor.fetchone()
    
    if not result:
        response = make_response(jsonify({"error": "Dataset not found"}))
        response.status_code = 404
        return response
        
    # Only allow deletion of archived datasets
    if not result['category'].startswith('ARCHIVED_'):
        response = make_response(jsonify({"error": "Only archived datasets can be deleted. Archive first."}))
        response.status_code = 400
        return response
    
    delete_query = "DELETE FROM dataset WHERE dataID = %s"
    cursor.execute(delete_query, (data_id,))
    db.get_db().commit()
    
    response = make_response(jsonify({"message": "Dataset deleted"}))
    response.status_code = 200
    return response


# ============================================================================
# UPLOAD ROUTES (User Story 1.3)
# ============================================================================

@datasets.route('/datasets/<int:data_id>/uploads', methods=['GET'])
def get_dataset_uploads(data_id):
    """
    1.3 - Retrieve all upload records for a specific dataset
    """
    current_app.logger.info(f'GET /datasets/{data_id}/uploads route')
    cursor = db.get_db().cursor()
    
    query = '''
        SELECT
            u.uploadID,
            u.dataID,
            u.metricID,
            u.filePath,
            u.uploadDate,
            m.metricName,
            m.category AS metricCategory
        FROM upload u
        LEFT JOIN metric m ON u.metricID = m.metricID
        WHERE u.dataID = %s
        ORDER BY u.uploadDate DESC
    '''
    cursor.execute(query, (data_id,))
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response


@datasets.route('/datasets/<int:data_id>/uploads', methods=['POST'])
def create_upload(data_id):
    """
    1.3 - Create new upload records linking a dataset to metrics
    """
    current_app.logger.info(f'POST /datasets/{data_id}/uploads route')
    
    data = request.json
    
    if not data or 'metricID' not in data or 'filePath' not in data:
        response = make_response(jsonify({"error": "Missing required fields: metricID, filePath"}))
        response.status_code = 400
        return response
    
    cursor = db.get_db().cursor()
    
    # Verify dataset exists
    check_query = "SELECT dataID FROM dataset WHERE dataID = %s"
    cursor.execute(check_query, (data_id,))
    if not cursor.fetchone():
        response = make_response(jsonify({"error": "Dataset not found"}))
        response.status_code = 404
        return response
    
    query = '''
        INSERT INTO upload (dataID, metricID, filePath, uploadDate)
        VALUES (%s, %s, %s, NOW())
    '''
    cursor.execute(query, (data_id, data['metricID'], data['filePath']))
    db.get_db().commit()
    
    new_id = cursor.lastrowid
    
    response = make_response(jsonify({"message": "Upload created", "uploadID": new_id}))
    response.status_code = 201
    return response