from scripts import create_app
import os

app = create_app()

if __name__ == '__main__':
    ssl_context = None
    cert_path = 'cert/cert.pem'
    key_path = 'cert/key.pem'
    if os.path.exists(cert_path) and os.path.exists(key_path):
        ssl_context = (cert_path, key_path)
        print("Running with HTTPS (self-signed).")
    else:
        print("Running without SSL (dev).")

    app.run(host='0.0.0.0', port=5000, debug=True)
