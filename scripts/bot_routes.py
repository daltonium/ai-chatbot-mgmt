from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from collections import Counter
import json
import os
import uuid
from werkzeug.utils import secure_filename

from .models import Chatbot, InteractionLog
from .rasa_integration import RasaNLPEngine
from . import db
from .auth_routes import login_required, current_user

bot_bp = Blueprint('bot', __name__)

UPLOAD_FOLDER = 'instance/training_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bot_bp.route('/')
@login_required
def dashboard():
    user = current_user()
    chatbots = Chatbot.query.all()
    stats = {
        cb.id: InteractionLog.query.filter_by(bot_id=cb.id).count()
        for cb in chatbots
    }
    return render_template('dashboard.html', chatbots=chatbots, stats=stats, user=user)

@bot_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_bot():
    user = current_user()
    if request.method == 'POST':
        name = request.form['name']
        template = request.form['template']
        personality = request.form['personality']

        bot = Chatbot(
            name=name,
            personality=personality,
            template=template,
            config_file=f"{template}_{uuid.uuid4()}.yml",
        )
        db.session.add(bot)
        db.session.commit()
        flash('Chatbot created successfully!')
        return redirect(url_for('bot.dashboard'))

    return render_template('create_bot.html', user=user)

@bot_bp.route('/chat/<int:bot_id>')
@login_required
def chat(bot_id):
    user = current_user()
    bot = Chatbot.query.get_or_404(bot_id)
    return render_template('chat.html', bot=bot, user=user)

@bot_bp.route('/chat_response', methods=['POST'])
@login_required
def chat_response():
    data = request.get_json()
    bot_id = data['bot_id']
    message = data['message']

    bot = Chatbot.query.get(bot_id)
    personality = bot.personality if bot else 'friendly'

    intent, response = RasaNLPEngine.predict_intent(message, personality)

    log = InteractionLog(
        bot_id=bot_id,
        user_message=message,
        bot_response=response,
        intent=intent,
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'response': response})

@bot_bp.route('/analytics/<int:bot_id>')
@login_required
def analytics(bot_id):
    user = current_user()
    bot = Chatbot.query.get_or_404(bot_id)
    logs = InteractionLog.query.filter_by(bot_id=bot_id).all()
    total = len(logs)
    intent_counts = Counter(log.intent for log in logs)
    top_intent = intent_counts.most_common(1)[0][0] if intent_counts else 'None'
    return render_template(
        'analytics.html',
        bot=bot,
        total_interactions=total,
        top_intent=top_intent,
        intent_counts=dict(intent_counts),
        user=user,
    )

@bot_bp.route('/train/<int:bot_id>', methods=['GET', 'POST'])
@login_required
def train_bot(bot_id):
    user = current_user()
    bot = Chatbot.query.get_or_404(bot_id)

    if request.method == 'POST':
        action = request.form.get('action', 'train')

        if action == 'import' and 'dataset' in request.files:
            f = request.files['dataset']
            if f and f.filename:
                filename = secure_filename(f.filename)
                path = os.path.join(UPLOAD_FOLDER, f"{bot_id}_{filename}")
                f.save(path)
                flash(f'Dataset "{filename}" imported for {bot.name}.')
                return redirect(url_for('bot.train_bot', bot_id=bot_id))

        recent_logs = (
            InteractionLog.query.filter_by(bot_id=bot_id)
            .order_by(InteractionLog.timestamp.desc())
            .limit(50)
            .all()
        )
        flash(f'Trained {bot.name} with {len(recent_logs)} recent interactions!')
        return redirect(url_for('bot.dashboard'))

    logs = InteractionLog.query.filter_by(bot_id=bot_id).all()
    dataset = [
        {"message": l.user_message, "response": l.bot_response, "intent": l.intent}
        for l in logs
    ]
    dataset_json = json.dumps(dataset, indent=2, ensure_ascii=False)

    return render_template(
        'train.html',
        bot=bot,
        dataset_json=dataset_json,
        user=user,
    )

@bot_bp.route('/train/export/<int:bot_id>')
@login_required
def export_dataset(bot_id):
    bot = Chatbot.query.get_or_404(bot_id)
    logs = InteractionLog.query.filter_by(bot_id=bot_id).all()
    dataset = [
        {"message": l.user_message, "response": l.bot_response, "intent": l.intent}
        for l in logs
    ]
    return jsonify(dataset)

@bot_bp.route('/deploy/<int:bot_id>')
@login_required
def deploy_bot(bot_id):
    user = current_user()
    if not user or user.role != 'admin':
        flash('Only admins are allowed to deploy chatbots.')
        return redirect(url_for('bot.dashboard'))

    bot = Chatbot.query.get_or_404(bot_id)

    embed_code = f"""<!-- {bot.name} Chatbot Embed -->
<script>
async function initChatbot(botId) {{
    const container = document.getElementById('chatbot-{bot_id}');
    container.innerHTML = '<div style="padding:15px;border:1px solid #ddd;border-radius:8px;background:#f8f9fa;">🤖 <strong>{bot.name}</strong> is ready!</div>';
    
    container.addEventListener('click', async () => {{
        const message = prompt('Talk to {bot.name}:');
        if (message) {{
            try {{
                const response = await fetch("/chat_response", {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify({{bot_id: botId, message: message}})
                }});
                const data = await response.json();
                alert("{bot.name}: " + data.response);
            }} catch (e) {{
                alert("Chatbot temporarily unavailable");
            }}
        }}
    }});
}}
initChatbot({bot_id});
</script>
<div id="chatbot-{bot_id}" style="cursor:pointer;padding:20px;border:2px dashed #007bff;border-radius:12px;text-align:center;font-size:16px;">
    Click to chat with {bot.name}
</div>"""

    return render_template('deploy.html', bot=bot, embed_code=embed_code, user=user)
