from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import datetime

app = Flask(__name__)

# Configuration - uses /app/storage for persistent data
STORAGE_PATH = os.environ.get('STORAGE_PATH', '/app/storage')
DB_PATH = os.path.join(STORAGE_PATH, 'app.db')

# Create storage directory
os.makedirs(STORAGE_PATH, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    page = db.Column(db.String(100))

    def __repr__(self):
        return f'<Visit {self.id} at {self.timestamp}>'

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQLite Migration Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        h2 { color: #555; margin-top: 30px; }
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }
        .success {
            background: #c8e6c9;
            border-left-color: #4CAF50;
        }
        .warning {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .stat-box {
            padding: 20px;
            background: #f5f5f5;
            border-radius: 5px;
            text-align: center;
        }
        .stat-number {
            font-size: 36px;
            font-weight: bold;
            color: #2196F3;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        form {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        input[type="text"], input[type="email"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0 15px 0;
            border: 1px solid #ddd;
            border-radius: 3px;
            box-sizing: border-box;
        }
        button, input[type="submit"] {
            background: #2196F3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover, input[type="submit"]:hover {
            background: #1976D2;
        }
        .user-list, .visit-list {
            margin: 20px 0;
        }
        .user-item, .visit-item {
            padding: 10px;
            margin: 5px 0;
            background: #f9f9f9;
            border-radius: 3px;
            border-left: 3px solid #2196F3;
        }
        .paths {
            font-family: monospace;
            font-size: 12px;
            color: #666;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
        }
        .test-instructions {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .test-instructions ol {
            margin: 10px 0;
            padding-left: 20px;
        }
        .test-instructions li {
            margin: 8px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗄️ SQLite Migration Test</h1>

        <div class="test-instructions">
            <strong>🧪 Test Instructions:</strong>
            <ol>
                <li><strong>Add some users</strong> using the form below</li>
                <li><strong>Note the counts</strong> (users and visits)</li>
                <li><strong>Stop and remove the container</strong></li>
                <li><strong>Add a new migration</strong> (e.g., add a 'bio' field to User model)</li>
                <li><strong>Rebuild and restart</strong> the container</li>
                <li><strong>Run migrations</strong> (<code>flask db upgrade</code> in container)</li>
                <li><strong>Check if data persisted</strong> - users should still be there!</li>
            </ol>
        </div>

        {% if message %}
        <div class="info-box success">
            {{ message }}
        </div>
        {% endif %}

        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ total_visits }}</div>
                <div class="stat-label">Total Visits</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ total_users }}</div>
                <div class="stat-label">Users Created</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ db_exists }}</div>
                <div class="stat-label">DB File Exists</div>
            </div>
        </div>

        <h2>➕ Add New User</h2>
        <form method="POST" action="/add_user">
            <label>Username:</label>
            <input type="text" name="username" required placeholder="johndoe">

            <label>Email:</label>
            <input type="email" name="email" required placeholder="john@example.com">

            <input type="submit" value="Create User">
        </form>

        <h2>👥 Users ({{ total_users }})</h2>
        <div class="user-list">
            {% if users %}
                {% for user in users %}
                <div class="user-item">
                    <strong>{{ user.username }}</strong> ({{ user.email }})<br>
                    <small style="color: #666;">Created: {{ user.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</small>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #999;">No users yet. Add one above!</p>
            {% endif %}
        </div>

        <h2>📊 Recent Visits (Last 10)</h2>
        <div class="visit-list">
            {% if visits %}
                {% for visit in visits %}
                <div class="visit-item">
                    Visit #{{ visit.id }} - {{ visit.page }}<br>
                    <small style="color: #666;">{{ visit.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</small>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #999;">No visits recorded yet</p>
            {% endif %}
        </div>

        <div class="info-box" style="margin-top: 30px;">
            <strong>🗂️ Storage Information:</strong>
            <div class="paths">
                STORAGE_PATH: {{ storage_path }}<br>
                DATABASE_PATH: {{ db_path }}<br>
                DB_EXISTS: {{ db_exists }}<br>
                MIGRATIONS_DIR: /app/migrations (check if exists in container)
            </div>
        </div>

        <div class="info-box warning" style="margin-top: 20px;">
            <strong>⚠️ What to Expect:</strong><br>
            <strong>Current Setup (Volume at /app):</strong> Data will be LOST on redeploy<br>
            <strong>Fixed Setup (Volume at /app/storage):</strong> Data will PERSIST on redeploy
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    # Log this visit
    visit = Visit(page='home')
    db.session.add(visit)
    db.session.commit()

    users = User.query.order_by(User.created_at.desc()).all()
    visits = Visit.query.order_by(Visit.timestamp.desc()).limit(10).all()
    total_visits = Visit.query.count()
    total_users = User.query.count()
    db_exists = "✅ YES" if os.path.exists(DB_PATH) else "❌ NO"

    return render_template_string(
        HTML_TEMPLATE,
        users=users,
        visits=visits,
        total_visits=total_visits,
        total_users=total_users,
        storage_path=STORAGE_PATH,
        db_path=DB_PATH,
        db_exists=db_exists,
        message=request.args.get('message')
    )

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')

    # Check if user exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return redirect(url_for('index', message=f'User {username} already exists!'))

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return redirect(url_for('index', message=f'Email {email} already in use!'))

    # Create new user
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('index', message=f'User {username} created successfully!'))

@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'users': User.query.count(),
        'visits': Visit.query.count(),
        'db_exists': os.path.exists(DB_PATH)
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
