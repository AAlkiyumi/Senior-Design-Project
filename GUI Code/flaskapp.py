from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import plotly.express as px
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
import os
from unwrangle_walmart_product_data import unwrangle_walmart_product_data
#import unwrangle_walmart_product_reviews
#import unwrangle_walmart_product_search

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')  # Upload Folder
db = SQLAlchemy(app)

# List of Allowed File Extensions for Uploads
ALLOWED_EXTENSIONS = {'csv'}

# Ensure the Upload Folder Exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Global Variable for Dataset
scraped_data_global = pd.DataFrame()
scraped_data_dictionary_global = pd.DataFrame()

def allowed_file(filename):
    # Check if the uploaded file has an allowed extension.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Demo Page (Default)
@app.route('/')
def demo():
    return render_template('demo.html')

# Index Page
@app.route('/')
def index():
    return render_template('index.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login_input']  # Either Username or Email
        password = request.form['password']
        user = User.query.filter((User.username == login_input) | (User.email == login_input)).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Error: Username already exists. Please choose a different username.', 'danger')
            return render_template('register.html')
        elif User.query.filter_by(email=email).first():
            flash('Error: Email already registered. Please use a different email.', 'danger')
            return render_template('register.html')
        else:
            hashed_password = generate_password_hash(password)  # Securely Hash Password
            db.session.add(User(username=username, email=email, password=hashed_password))
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('register.html')

# Scrape in 🔍 Search Mode
@app.route('/scrape_search', methods=['GET', 'POST'])
def scrape_search():
    global scraped_data_global
    global scraped_data_dictionary_global
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    
    search_url = request.form.get('search_url')
    num_pages = request.form.get('num_pages')
    
    if not search_url:
        flash("Please enter a valid URL.", "danger")
        return redirect(url_for('search_page'))
    
    response_df, results_dictionary_df = unwrangle_walmart_product_search(search_url, num_pages) # Input: Search Term, Number of Pages | Output: response_df, results_dictionary_df
    
    if response_df.empty:
        flash("No data found for the given URLs.", "danger")
        return redirect(url_for('search_page'))
    else:
        flash(f"Scraped {len(response_df)} products successfully!", "success")
    
    scraped_data_global = response_df
    scraped_data_dictionary_global = results_dictionary_df
    
    scraped_results = response_df.to_dict(orient='records')

    return render_template('search.html', scraped_results=scraped_results, user=user)

# Scrape in 📊 Data Mode
@app.route('/scrape_data', methods=['GET', 'POST'])
def scrape_data():
    global scraped_data_global
    global scraped_data_dictionary_global
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    
    product_urls = request.form.getlist('product_urls[]')  # Get multiple URLs

    if not product_urls:
        flash("Please enter at least one URL.", "danger")
        return redirect(url_for('data_page'))

    response_df, details_df = unwrangle_walmart_product_data(product_urls) # Input: URL List | Output: response_df, details_df

    if response_df.empty:
        flash("No data found for the given URLs.", "danger")
        return redirect(url_for('data_page'))
    else:
        flash(f"Scraped {len(response_df)} products successfully!", "success")

    # Store scraped data globally for downloading
    scraped_data_global = response_df
    scraped_data_dictionary_global = details_df

    # Convert DataFrame to list of dictionaries (for template rendering)
    scraped_results = response_df.to_dict(orient='records')

    # Store results in session or pass to template
    return render_template('data.html', scraped_results=scraped_results, user=user)

# Scrape in ⭐️ Review Mode
@app.route('/scrape_reviews', methods=['GET', 'POST'])
def scrape_reviews():
    global scraped_data_global
    global scraped_data_dictionary_global
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    
    review_urls = request.form.getlist('review_urls[]')
    num_pages = request.form.get('num_pages')
    
    if not review_urls:
        flash("Please enter at least one review URL.", "danger")
        return redirect(url_for('review_page'))

    response_df, reviews_df = unwrangle_walmart_product_reviews(review_urls, num_pages) # Input: URL List, Number of Pages | Output: response_df, reviews_df

    if response_df.empty:
        flash("No data found for the given URLs.", "danger")
        return redirect(url_for('data_page'))
    else:
        flash(f"Scraped {len(response_df)} products successfully!", "success")
    
    scraped_data_global = response_df
    scraped_data_dictionary_global = reviews_df
    
    scraped_results = response_df.to_dict(orient='records')
    
    return render_template('review.html', scraped_results=scraped_results, user=user)

# Download Results
@app.route('/download_dataset', methods=['GET', 'POST'])
def download_dataset():
    global scraped_data_global
    global scraped_data_dictionary_global
    
    previous_page = request.referrer  # Get the referring page (where the request came from)

    # If no dataset is available, redirect back to the previous page dynamically
    if scraped_data_global.empty and scraped_data_dictionary_global.empty:
        flash('No results available to download.', 'danger')
        return redirect(previous_page or url_for('dashboard'))  # Default to dashboard if referrer is unavailable

    # If data exists, generate CSV for download
    csv_data = scraped_data_global.to_csv(index=False)
    csv_data_dictionary = scraped_data_dictionary_global.to_csv(index=False)
    
    response1 = make_response(csv_data)
    response1.headers['Content-Disposition'] = 'attachment; filename=scraped_data.csv'
    response1.headers['Content-Type'] = 'text/csv'
    
    response2 = make_response(csv_data_dictionary)
    response2.headers['Content-Disposition'] = 'attachment; filename=scraped_data_dictionary.csv'
    response2.headers['Content-Type'] = 'text/csv'

    return response1, response2

# Home Dashboard Page Button
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])

    return render_template('dashboard.html', user=user)

# Search Mode Page Button
@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
        
    return render_template('search.html', user=user)

# Data Mode Page Button
@app.route('/data', methods=['GET', 'POST'])
def data_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])

    return render_template('data.html', user=user)

# Review Mode Page Button
@app.route('/review', methods=['GET', 'POST'])
def review_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])

    return render_template('review.html', user=user)

# FAQ Button
@app.route('/FAQ')
def faq():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])

    return render_template('faq.html', user=user)

# About Us Button
@app.route('/about')
def about_us():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])

    return render_template('about.html', user=user)

# Profile Button
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])

    return render_template('profile.html', user=user)

# History Button
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    
    return render_template('history.html')

# Settings Button
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    changes_made = False  # Track if any changes were made

    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()

        if new_username and new_username != user.username:
            if User.query.filter_by(username=new_username).first():
                flash('Username already taken.', 'danger')
            else:
                user.username = new_username
                changes_made = True

        if new_email and new_email != user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Email already in use.', 'danger')
            else:
                user.email = new_email
                changes_made = True

        if new_password:
            user.password = generate_password_hash(new_password)
            changes_made = True

        if changes_made:
            db.session.commit()
            flash('Changes saved successfully!', 'success')

        return redirect(url_for('settings'))

    return render_template('settings.html', user=user)

# Logout Button
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():  # Ensure the application context is active
        db.create_all()      # Create the database tables
    app.run(debug=True)
