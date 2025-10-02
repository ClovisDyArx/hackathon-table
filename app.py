from flask import Flask, render_template, jsonify, request

# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def main_app():
    """
    Renders the main application page.
    """
    return render_template('index.html')

@app.route('/joke')
def joke_page():
    """
    Renders the initial joke/splash page.
    This will be the first page the user sees.
    """
    return render_template('joke.html')

@app.route('/api/process_table', methods=['POST'])
def process_table():
    """
    A placeholder API endpoint for your GenAI model.
    For the hackathon, it simulates processing and returns a fixed table structure.
    In a real application, this is where you would call your Python model
    to process the incoming text or image data.
    """
    # You can get data from the request like this:
    # data = request.json
    # print("Received data for processing:", data)

    # Simulate a successful AI processing response
    mock_table_data = {
        "headers": ["Product ID", "Item", "Stock", "Price"],
        "rows": [
            ["#1024", "Oak Coffee Table", "15", "$250.00"],
            ["#1025", "Leather Sofa", "8", "$800.00"],
            ["#1026", "Floor Lamp", "32", "$75.00"]
        ]
    }
    return jsonify(mock_table_data)


if __name__ == '__main__':
    # Run the app in debug mode, which is great for development.
    # The default URL will be http://127.0.0.1:5000
    # To start, navigate to http://127.0.0.1:5000/joke
    app.run(debug=True)
