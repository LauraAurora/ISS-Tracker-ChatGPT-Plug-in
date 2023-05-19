from flask import Flask, jsonify, send_from_directory
from waitress import serve
import requests

app = Flask(__name__)


@app.route('/iss_location', methods=['GET'])
def get_iss_location():
  try:
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()

    iss_position = response.json()["iss_position"]
    message = f"The ISS current location is: Latitude: {iss_position['latitude']} Longitude: {iss_position['longitude']}"
    location = get_location_from_coordinates(iss_position['latitude'],
                                             iss_position['longitude'])
    return jsonify({'message': message, 'location': location})
  except requests.exceptions.RequestException as err:
    return jsonify({'error': str(err)}), 500


# @app.route('/iss_location_details', methods=['GET'])
# def get_location_from_coordinates_route():
#     latitude = request.args.get('latitude')
#     longitude = request.args.get('longitude')
#     return jsonify(get_location_from_coordinates(latitude, longitude))


@app.route('/astronauts', methods=['GET'])
def astronauts_in_space():
  try:
    response = requests.get(url="http://api.open-notify.org/astros.json")
    response.raise_for_status()
    data = response.json()

    number = data['number']
    astronauts = [{
      'name': astronaut['name'],
      'craft': astronaut['craft']
    } for astronaut in data['people']]

    return jsonify({'number': number, 'astronauts': astronauts})
  except requests.exceptions.RequestException as err:
    return jsonify({'error': str(err)}), 500


# https://iss-tracking-plugin.devsociety.repl.co.well-known/ai-plugin.json
@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
  return send_from_directory('.',
                             'ai-plugin.json',
                             mimetype='application/json')


# https://iss-tracking-plugin.devsociety.repl.co/.well-known/openapi.yaml
@app.route('/.well-known/openapi.yaml')
def serve_openapi_yaml():
  return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')


def get_location_from_coordinates(latitude, longitude):
  try:
    response = requests.get(
      url=
      f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1"
    )
    response.raise_for_status()

    data = response.json()
    address = data.get('address', {})
    country = address.get('country', 'Unknown')
    state = address.get('state', 'Unknown')

    return {'state': state, 'country': country}
  except requests.exceptions.RequestException as err:
    return {'error': str(err)}


if __name__ == '__main__':
  serve(app, host="0.0.0.0", port=8080)
