import requests
import subprocess
import time
import os

RASA_SERVER_URL = "http://localhost:5005"

class RasaNLPEngine:
    """Rasa AI integration for intent prediction"""
    
    @staticmethod
    def is_rasa_running():
        """Check if Rasa server is running"""
        try:
            response = requests.get(f"{RASA_SERVER_URL}/status", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def predict_intent(message, personality='friendly'):
        """
        Send message to Rasa and get intent + response
        Falls back to simple NLP if Rasa is not running
        """
        if not RasaNLPEngine.is_rasa_running():
            # Fallback to simple NLP
            from .nlp import SimpleNLPEngine
            return SimpleNLPEngine.predict_intent(message, personality)
        
        try:
            # Call Rasa REST API
            response = requests.post(
                f"{RASA_SERVER_URL}/model/parse",
                json={"text": message},
                timeout=5
            )
            
            if response.status_code != 200:
                raise Exception("Rasa API error")
            
            data = response.json()
            intent = data.get('intent', {}).get('name', 'unknown')
            confidence = data.get('intent', {}).get('confidence', 0)
            
            # Map intent to personality-specific response
            response_key = f"utter_{intent}_{personality}"
            
            # Get response from Rasa (if available) or use default
            bot_response = RasaNLPEngine._get_response(intent, personality)
            
            return intent, bot_response
            
        except Exception as e:
            print(f"Rasa error: {e}, falling back to SimpleNLP")
            from .nlp import SimpleNLPEngine
            return SimpleNLPEngine.predict_intent(message, personality)
    
    @staticmethod
    def _get_response(intent, personality):
        """Get personality-specific response for intent"""
        responses = {
            'greet': {
                'friendly': 'Hello! How can I help? 😊',
                'professional': 'Hello! How may I assist you today?',
                'casual': 'Hey! What\'s up? 😎',
                'formal': 'Good day! How may I be of service?',
                'humorous': 'Hello! I\'m your friendly AI overlord! 😄',
                'empathetic': 'Hi there! I\'m here for you! ❤️',
            },
            'goodbye': {
                'friendly': 'Goodbye! Have a great day! 👋',
                'professional': 'Thank you. Goodbye.',
                'casual': 'Catch ya later! ✌️',
                'formal': 'Farewell. Have a pleasant day.',
                'humorous': 'Bye! Don\'t forget to feed your robot! 🤖',
                'empathetic': 'Take care! I\'m always here if you need me! 💕',
            },
            'info': 'This is a demo chatbot powered by AI Chatbot Management System with Rasa AI.',
            'purchase': 'You can buy products from our store! 🛒',
            'health': 'Please consult a healthcare professional. 🩺',
            'unknown': 'Sorry, I did not understand. 😅'
        }
        
        if intent in ['greet', 'goodbye']:
            return responses[intent].get(personality, responses[intent]['friendly'])
        else:
            return responses.get(intent, responses['unknown'])


def train_rasa_model():
    """Train Rasa model (run this once after setup)"""
    import sys
    rasa_dir = os.path.join(os.path.dirname(__file__), '..', 'rasa_project')
    rasa_dir = os.path.abspath(rasa_dir)
    
    print("Training Rasa model... (this may take 2-5 minutes)")
    print(f"Using Rasa project directory: {rasa_dir}")
    
    # Use python -m rasa instead of rasa command directly
    result = subprocess.run(
        [sys.executable, '-m', 'rasa', 'train'],
        cwd=rasa_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Rasa model trained successfully!")
        print(result.stdout)
        return True
    else:
        print(f"❌ Rasa training failed:")
        print(result.stderr)
        return False


def start_rasa_server():
    """Start Rasa server in background (for development)"""
    import sys
    rasa_dir = os.path.join(os.path.dirname(__file__), '..', 'rasa_project')
    rasa_dir = os.path.abspath(rasa_dir)
    
    print("Starting Rasa server on port 5005...")
    subprocess.Popen(
        [sys.executable, '-m', 'rasa', 'run', '--enable-api', '--cors', '*', '--port', '5005'],
        cwd=rasa_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server to start
    for i in range(30):
        time.sleep(1)
        if RasaNLPEngine.is_rasa_running():
            print("✅ Rasa server started successfully!")
            return True
    
    print("❌ Rasa server failed to start")
    return False
