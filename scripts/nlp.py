class SimpleNLPEngine:
    @staticmethod
    def predict_intent(message, personality='friendly'):
        message_lower = message.lower()

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
            'info': 'This is a demo chatbot powered by AI Chatbot Management System.',
            'purchase': 'You can buy products from our store! 🛒',
            'health': 'Please consult a healthcare professional. 🩺',
        }

        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return 'greet', responses['greet'].get(personality, responses['greet']['friendly'])
        elif 'bye' in message_lower:
            return 'goodbye', responses['goodbye'].get(personality, responses['goodbye']['friendly'])
        elif 'info' in message_lower or 'help' in message_lower:
            return 'info', responses['info']
        elif 'buy' in message_lower or 'purchase' in message_lower:
            return 'purchase', responses['purchase']
        elif 'doctor' in message_lower or 'health' in message_lower:
            return 'health', responses['health']
        return 'unknown', 'Sorry, I did not understand. 😅'
