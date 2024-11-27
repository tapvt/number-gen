import os
from dotenv import load_dotenv
from api.index import app, init_db

# Load environment variables
load_dotenv()

def main():
    # Initialize the database
    init_db()

    # Run the Flask app in debug mode on port 5003
    app.run(debug=True, host='0.0.0.0', port=5003)

if __name__ == '__main__':
    main()
