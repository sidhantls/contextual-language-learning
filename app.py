from flask import Flask, request, jsonify
import utils
from flask_cors import CORS, cross_origin
import time

app = Flask(__name__)
# cors = CORS(app)

# cors = CORS(app, resources={r"/api/": {"origins": "*"}})

CORS(app, supports_credentials=True, resources={r"/": {"origins": "*"}})

# app.config['CORS_HEADERS'] = 'Content-Type'
# app.config['Access-Control-Allow-Origin'] = '*'

app.config["Access-Control-Allow-Origin"] = "*"
app.config["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
app.config["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"

app = Flask(__name__)

@cross_origin()
@app.route('/scenarios', methods=['POST'])
def process_scenario():
    try:
        data = request.get_json()
        scenario = data.get('scenario')

        # Your processing logic here
        # For demonstration, simply echoing the input

        assert isinstance(scenario, str) 


        i = 0 
        while i < 3:
            try:
                dataset, _ = utils.run_pipeline(scenario = scenario)
                break
            except:
                i += 1 
                time.sleep(1)
        
        response = {'conversation': {'messages': dataset}}
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': f'Error processing the request: {str(e)}'})

@app.route('/')
def hello():
   return 'Hello, World!'
    
if __name__ == '__main__':
    app.run(debug=True, port=9008)
