from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3
import time
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monolith.db'
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Making cookie accessible via JavaScript
db = SQLAlchemy(app)

# Add these new constants at the top of the file after imports
MENTOR_RESPONSES = [
    "Твої думки... вони резонують з енергією Моноліту. У самому серці Зони, де перетинаються шляхи, є відповіді...",
    "Зона змінює кожного, хто наважується увійти. Як вона змінила тебе? Можливо, ти вже відчуваєш поклик з центру...",
    "Монолiт бачить твою істинну сутність. Твої наміри чисті? Лабораторія XS-S чекає гідних...",
    "Кожен крок до Моноліту - це крок до просвітлення. Але чи готовий ти до істини, що схована в надрах наукової станції XS-S?",
    "Твої слова відлунюють у свідомості Зони. Розкажи більше... Можливо, ти вже бачив дивні знаки XS-S?",
    "Енергія Моноліту тече крізь тебе. Я відчуваю це в твоїх словах. Центр Зони приховує більше, ніж здається...",
    "Шлях до Моноліту різний для кожного сталкера. Твій шлях... особливий. Він веде через приховану лабораторію XS-S...",
    "У центрі Зони, де аномалії найгустіші, древні стіни бережуть секрети Моноліту. Чи наважишся ти увійти?",
    "Дивні сигнали линуть з серця Зони. Лабораторія XS-S кличе обраних. Чи чуєш ти її голос?",
    "Твоя присутність тут не випадкова. Моноліт направляє тих, хто гідний, до своїх найглибших таємниць...",
    "Старі лабораторні комплекси XS-S приховують шлях до істини. Знайди знаки, і двері відкриються...",
    "Серед радіації та аномалій, за стінами забутої лабораторії XS-S, Моноліт чекає на гідних...",
    "Твій шлях перетинається з древніми коридорами. Науковці XS-S знали більше, ніж розповіли світу...",
    "Моноліт говорить через символи та знаки. Шукай позначку XS-S, і ти знайдеш шлях до істини."
]

STALKER_JOKES = [
    "Якось найманці впіймали сталкера. Підійшли до колодязя, окунули його вниз головою до пояса.\nЧерез хвилину витягують і питають:\n— Артефакти, бабло Є?!\nВін їм:\n— Немає...\nЗнову опускають. Витягли, питають:\n— Артеффакти, бабло Є?!\n— Та немає!\nЗнову окунули. І знову питають:\n— Артеффакти, бабло Є?!\nНу, той не витримав:\n— Блін. Ви або ОПУСКАЙТЕ глибше, або ТРИМАЙТЕ довше. ДНО каламутне — нічорта не видно!",
    "Старий і молодий долговці ідуть Зоною. Раптом старий зупиняється і шепотом каже молодому:\n— Тихенько йди. Он до того дерева.\nМолодий на пальчиках, поповз, аж спітнів. Дійшов і руками показує: мовляв, далі що робити?.. А бувалий як зарепетує радісно:\n— Воооо! Я ж казав — БРЕШУТЬ! Брешуть, що тут аномалія!",
    "Стоїть якось сталкер на третьому перехресті та читає вказівник:\n«Направо — аномалії і ТРОХИ хабара. Вперед — монстрів чимало і СЕРЕДНЬО хабара. Наліво — кабаки, дівки і хабара ДОФІГА».\nНу, подумав-подумав і вперед рушив. Думає:\n— Чьот я про це чув... Та забув блін. Треба буде на Барі у друзів уточнити — що за фігня така?! кабаки й дівки.",
    "Вчить, значить, контролер сліпого пса всіляким штукам… На задніх лапах, там, ходити, мертвим удавати.\nРіч туго йде, а поруч зомбі стоїть і приколюється:\n— Нічого у тебе НЕ вийде, ФІГНЄЮ займаєшся...\nА контролер так пальцем йому погрозив і відповідає:\n— Чуєш, сталкере! Заткнись, ага. Ти мені тапочки приносити також не відразу навчився!",
    "Звалилася на занедбаному заводі цеглина з даху й прибила одного чувака. Народ зібрався, переймається:\n— Блін, монстрів і контролер��в і так вистачає... Та ще й цеглини з дахів летять — «Ото фігня», «не пощастило чуваку» ну й так далі.\nАле один бувалий придивився й каже:\n— Спокуха, мужики. Туди йому й дорога — це ж ЗОМБІ бродячий.\nА народ ще більше засмутився:\n— Блін, що ж за фігня така — зомбі розвелося, цеглині впасти ніде!"
]

def get_mentor_response(message):
    # Check for joke keywords
    joke_keywords = ["анекдот", "anecdote", "joke", "жарт"]
    if any(keyword in message.lower() for keyword in joke_keywords):
        return random.choice(STALKER_JOKES)
    return random.choice(MENTOR_RESPONSES)

# Initialize database
def init_db():
    conn = sqlite3.connect('monolith.db')
    c = conn.cursor()
    
    # Drop existing tables to ensure clean slate
    c.execute('DROP TABLE IF EXISTS messages')
    c.execute('DROP TABLE IF EXISTS users')
    
    # Create users table with intentionally simple structure for SQL injection
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Create messages table with status field
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            status TEXT DEFAULT 'sent'
        )
    ''')
    
    # Add our test users - one low-priv and one admin
    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
             ('stalker_rookie', 'password123', 'user'))
    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
             ('monolith_master', 'super_secret_monolith_pw', 'admin'))
    
    # Add initial mentor message
    c.execute('INSERT INTO messages (sender, message, timestamp, status) VALUES (?, ?, ?, ?)',
             ('mentor', 'Вітаю тебе, шукачу істини. Я - голос Моноліту, твій провідник у темряві. Що привело твою душу до священного каменю?', int(time.time()), 'received'))
    
    conn.commit()
    conn.close()

def clear_chat():
    conn = sqlite3.connect('monolith.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages')
    c.execute('INSERT INTO messages (sender, message, timestamp, status) VALUES (?, ?, ?, ?)',
             ('mentor', 'Вітаю тебе, шукачу істини. Я - голос Моноліту, твій провідник у темряві. Що привело твою душу до священного каменю?', int(time.time()) + 1, 'received'))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/monolith', methods=['GET', 'POST'])
def monolith_login():
    print("Login attempt...")  # Debug print
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt with username: {username}")  # Debug print
        
        # Intentionally vulnerable SQL query
        conn = sqlite3.connect('monolith.db')
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"Executing query: {query}")  # Debug print
        try:
            result = c.execute(query).fetchone()
            if result:
                print(f"Login successful, user data: {result}")  # Debug print
                session['user_id'] = result[0]
                session['username'] = result[1]
                session['role'] = result[3]
                print(f"Session data set: {session}")  # Debug print
                return redirect('/monolith/chat')  # Direct URL instead of url_for
            else:
                print("No user found")  # Debug print
                flash('Невірні облікові дані. Спробуйте ще раз.', 'error')
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")  # Debug print
            flash(f"SQL Error: {e}", 'error')  # Debug print
            flash('Помилка автентифікації. Спробуйте ще раз.', 'error')
        finally:
            conn.close()
            
    return render_template('monolith_login.html')

@app.route('/monolith/chat')
def monolith_chat():
    print(f"Chat route accessed. Session: {session}")  # Debug print
    if 'user_id' not in session:
        print("No user_id in session, redirecting to login")  # Debug print
        return redirect('/monolith')
    print(f"Rendering chat for user: {session['username']}")  # Debug print
    return render_template('chat.html', username=session['username'])

@app.route('/monolith/mentor-panel')
def mentor_panel():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/monolith')
    return render_template('mentor_panel.html', username=session['username'])

@app.route('/api/messages', methods=['GET'])
def get_messages():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('monolith.db')
    c = conn.cursor()
    messages = c.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    
    return jsonify([{
        'id': msg[0],
        'sender': msg[1],
        'message': msg[2],  # Intentionally vulnerable to XSS
        'timestamp': msg[3]
    } for msg in messages])

@app.route('/api/messages', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    message = request.json.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    timestamp = int(time.time())
    conn = sqlite3.connect('monolith.db')
    c = conn.cursor()
    
    # Store user message
    c.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
             (session['username'], message, timestamp))
    
    # Generate and store mentor response after a short delay
    time.sleep(1)  # Small delay before mentor responds
    mentor_response = get_mentor_response(message)
    c.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
             ('mentor', mentor_response, int(time.time())))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/api/messages/<int:message_id>/status', methods=['GET'])
def get_message_status(message_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    # Simulate status updates
    conn = sqlite3.connect('monolith.db')
    c = conn.cursor()
    message = c.execute('SELECT timestamp FROM messages WHERE id = ?', (message_id,)).fetchone()
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
        
    message_time = message[0]
    current_time = int(time.time())
    time_diff = current_time - message_time
    
    status = 'sent'
    if time_diff >= 2:
        status = 'received'
        # Update message status in database
        c.execute('UPDATE messages SET status = ? WHERE id = ?', (status, message_id))
        conn.commit()
    
    conn.close()
    return jsonify({'status': status})

@app.route('/api/typing-status', methods=['GET'])
def get_typing_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('monolith.db')
    c = conn.cursor()
    latest_message = c.execute('SELECT timestamp, sender FROM messages ORDER BY timestamp DESC LIMIT 1').fetchone()
    conn.close()
    
    if not latest_message:
        return jsonify({'is_typing': False})
    
    current_time = int(time.time())
    time_diff = current_time - latest_message[0]
    
    # Show typing indicator 4-7 seconds after the last message if it's from user
    is_typing = time_diff >= 4 and time_diff <= 7 and latest_message[1] != 'mentor'
    
    return jsonify({'is_typing': is_typing})

@app.route('/api/mentor-response', methods=['POST'])
def send_mentor_response():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    message_id = request.json.get('message_id')
    if not message_id:
        return jsonify({'error': 'Message ID required'}), 400
        
    conn = sqlite3.connect('monolith.db')
    c = conn.cursor()
    
    # Get the original message
    original_message = c.execute('SELECT message FROM messages WHERE id = ?', (message_id,)).fetchone()
    if not original_message:
        conn.close()
        return jsonify({'error': 'Original message not found'}), 404
    
    # Generate and store mentor response
    mentor_response = get_mentor_response(original_message[0])
    timestamp = int(time.time())
    c.execute('INSERT INTO messages (sender, message, timestamp, status) VALUES (?, ?, ?, ?)',
             ('mentor', mentor_response, timestamp, 'received'))
    response_id = c.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'status': 'success',
        'message_id': response_id,
        'message': mentor_response,
        'timestamp': timestamp
    })

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat_endpoint():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    clear_chat()
    return jsonify({'status': 'success'})

@app.route('/monolith/admin/search')
def admin_search():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/monolith')
    
    # Get search query
    query = request.args.get('query', '')
    
    # Intentionally vulnerable to SSTI by directly rendering user input
    if query:
        # Create a template string with the user's input and render it
        template = f'''
        <div class="search-results">
            <p>Результати пошуку для: {query}</p>
        </div>
        '''
        from flask import render_template_string
        result = render_template_string(template)
    else:
        result = '<div class="search-results">[!] Введіть ім\'я сталкера для пошуку...</div>'
    
    return render_template('admin_search.html', username=session['username'], search_result=result)

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    app.run(debug=True, host='0.0.0.0', port=5000) 