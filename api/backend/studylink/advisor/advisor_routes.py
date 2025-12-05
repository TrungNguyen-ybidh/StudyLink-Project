import logging
from flask import Blueprint, request, jsonify
from backend.db_connection import db

logger = logging.getLogger(__name__)

advisor_bp = Blueprint('advisor', __name__, url_prefix='/api/advisor')

#GET /advisor
@advisor_bp.get('/')
def get_advisors():
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT advisorID, fName, lName, department, email FROM advisor")
    advisors = cursor.fetchall()
    return jsonify(advisors), 200