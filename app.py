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


def train_lstm_model(file_path):
    try:
        import pandas as pd
        import numpy as np
        from keras.models import Sequential
        from keras.layers import LSTM, Dense

        data = pd.read_csv(file_path)
        features = data[['et', 'storage', 'rainfall']].values
        targets = data['inflow'].values

        # Reshape for LSTM (samples, timesteps, features)
        features = features.reshape((features.shape[0], 1, features.shape[1]))

        model = Sequential([
            LSTM(50, activation='relu', input_shape=(1, 3)),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        model.fit(features, targets, epochs=50, batch_size=32)

        model.save('lstm_model.h5')
    except Exception as e:
        print(e)
        raise e

def calculate_10Q7(inflow_tmc):
    # Convert inflow to a 10-day flow (1 TMC = 10^9 cubic meters)
    daily_flow_cubic_meters = (inflow_tmc * 10**9) / 10  # Divide by 10 days
    return daily_flow_cubic_meters / (7 * 24 * 60 * 60 * 365)  # Convert to m³/s

def predict_inflow(evapotranspiration, storage, rainfall_value):
    import numpy as np
    from keras.models import load_model

    model = load_model('lstm_model.h5')
    input_data = np.array([[evapotranspiration, storage, rainfall_value]])
    input_data = input_data.reshape((1, 1, 3))

    prediction = model.predict(input_data)
    return float(prediction[0][0])
  

@ns.route('/upload_train_data')
class UploadTrainData(Resource):
    @ns.doc('upload_train_data')
    def post(self):
        """Upload training data and train the LSTM model."""
        if 'file' not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return {"error": "Invalid file type. Only CSV files are allowed."}, 400

        file_path = os.path.join("files", file.filename)
        file.save(file_path)

        try:
            train_lstm_model(file_path)
            return {"message": "Training completed successfully."}, 200
        except Exception as e:
            print(e)
            return {"error": str(e)}, 500


@ns.route('/predict_inflow')
class PredictInflow(Resource):
    @ns.doc('predict_inflow')
    def post(self):
        """Predict inflow based on input parameters."""
        data = request.json
        try:
            evapotranspiration = float(data['evapotranspiration'])
            storage = float(data['storage'])
            rainfall_value = float(data['rainfallValue'])

            inflow = predict_inflow(evapotranspiration, storage, rainfall_value)
            dqt = calculate_10Q7(inflow)

            return {"predicted_inflow": inflow, "dqt": dqt}, 200
        except Exception as e:
            return {"error": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)

