from scripts import create_app, db
from scripts.models import Chatbot, InteractionLog
from scripts.nlp import SimpleNLPEngine

TEMPLATES = [
    "general",
    "healthcare",
    "retail",
    "education",
]

PERSONALITIES = [
    "friendly",
    "professional",
    "casual",
    "formal",
    "humorous",
    "empathetic",
]

def seed_agents():
    app = create_app()
    with app.app_context():
        bots_created = 0

        for template in TEMPLATES:
            for personality in PERSONALITIES:
                name = f"{template.capitalize()} - {personality.capitalize()} Bot"

                existing = Chatbot.query.filter_by(
                    name=name,
                    template=template,
                    personality=personality
                ).first()
                if existing:
                    print(f"Skipping existing bot: {name}")
                    continue

                bot = Chatbot(
                    name=name,
                    template=template,
                    personality=personality,
                    config_file=f"{template}_{personality}.yml",
                )
                db.session.add(bot)
                db.session.flush()

                sample_messages = [
                    "hello",
                    "hi",
                    "can you help me?",
                    "i want to buy something",
                    "i have a health question",
                    "bye",
                ]
                for msg in sample_messages:
                    intent, response = SimpleNLPEngine.predict_intent(msg, personality)
                    log = InteractionLog(
                        bot_id=bot.id,
                        user_message=msg,
                        bot_response=response,
                        intent=intent,
                    )
                    db.session.add(log)

                bots_created += 1
                print(f"Created and trained: {name}")

        db.session.commit()
        print(f"\nDone. Total new bots created: {bots_created}")

if __name__ == "__main__":
    seed_agents()
