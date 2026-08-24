# Import the function that builds and configures the Flask application.
from backend.app import create_app


# Run this block only when this file is started directly with `python run.py`.
if __name__ == '__main__':
    # Create the configured Flask application, including its routes and login system.
    app = create_app()
    # Print a visual separator so the startup message is easy to spot in the terminal.
    print("==================================================")
    # Tell you which application has started.
    print("  Pickle Legends - Admin Platform Running!")
    # Tell you the local address to open in your web browser.
    print("  Access URL: http://127.0.0.1:5000")
    # Print the closing visual separator.
    print("==================================================")
    # Start Flask on port 5000, accept local-network connections, and enable debug mode.
    app.run(host='0.0.0.0', port=5000, debug=True)
