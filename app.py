from flask import Flask, jsonify
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from hydrological_data import process_hydrological_data
import random
import os
import string
from flask import request, jsonify
from flask_restx import Resource, Namespace
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  
app.wsgi_app = ProxyFix(app.wsgi_app)

api = Api(
    app,
    version='1.0',
    title='Flask API Template',
    description='A simple Flask API template with Swagger UI',
    doc='/docs'
)

ns = api.namespace('api/v1', description='API operations')

rainfall_inflow_model = api.model('RainfallInflow', {
    'message': fields.String(required=True, description='Returns Rainfall Inflow'),
    'timestamp': fields.DateTime(required=True, description='Current timestamp'),
    'rainfall_inflow': fields.Float(required=True, description='Rainfall Inflow')
})

@ns.route('/get_rainfall_inflow')
class RainfallInflow(Resource):
    @ns.doc('get_rainfall_inflow')
    def post(self):
        """Upload a rainfall TIFF file and return rainfall inflow."""
        if 'file' not in request.files:
            return {"error": "No file provided"}, 400

        uploaded_file = request.files['file']

        # Generate a random filename
        random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".tif"
        file_path = os.path.join("files", random_filename)

        # Save the file
        uploaded_file.save(file_path)

        # Process the file to calculate rainfall inflow
        try:
            rainfall_inflow = process_hydrological_data(file_path)
        except Exception as e:
            return {"error": str(e)}, 500

        # Return the result
        return jsonify({
            "message": "Rainfall inflow calculated successfully.",
            "rainfall_inflow": rainfall_inflow,
            "filename": random_filename
        })


@ns.route('/health')
class Health(Resource):
    @ns.doc('get_health')
    def get(self):
        """Get API health status"""
        return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(debug=True)