from flask import Flask, jsonify
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from hydrological_data import process_hydrological_data

app = Flask(__name__)
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
    @ns.marshal_with(rainfall_inflow_model)
    def get(self):
        """Get a rainfall inflow"""
        from datetime import datetime
        return {
            'message': 'Hello, World!',
            'timestamp': datetime.now(),
            'rainfall_inflow': process_hydrological_data('rainfall.tif'),
        }

@ns.route('/health')
class Health(Resource):
    @ns.doc('get_health')
    def get(self):
        """Get API health status"""
        return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(debug=True)