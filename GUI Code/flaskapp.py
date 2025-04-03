from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
import os

from Scraper_Files_New.amazon.lambda_function import lambda_handler as amazon_lambda_handler
from Scraper_Files_New.bestbuy.lambda_function import lambda_handler as bestbuy_lambda_handler
from Scraper_Files_New.costco.lambda_function import lambda_handler as costco_lambda_handler
from Scraper_Files_New.homedepot.lambda_function import lambda_handler as homedepot_lambda_handler
from Scraper_Files_New.lowes.lambda_function import lambda_handler as lowes_lambda_handler
from Scraper_Files_New.walmart.lambda_function import lambda_handler as walmart_lambda_handler

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
scraped_product_df_global = pd.DataFrame()
scraped_reviews_df_global = pd.DataFrame()

def allowed_file(filename):
    # Check if the uploaded file has an allowed extension.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to find all product CSV files from scrapers
def find_all_product_csvs():
    product_csv_files = [f for f in os.listdir(os.getcwd()) if f.endswith('df.csv')]
    return product_csv_files

# Function to merge all product CSV files
def merge_product_csv_files():
    product_csv_files = find_all_product_csvs()
    
    if not product_csv_files:
        return None  # No CSVs found

    df_list = [pd.read_csv(f) for f in product_csv_files]  # Read each CSV
    merged_df = pd.concat(df_list, ignore_index=True)  # Merge all CSVs
    
    return merged_df

# Function to find all reviews CSV files from scrapers
def find_all_reviews_csvs():
    reviews_csv_files = [f for f in os.listdir(os.getcwd()) if f.endswith('reviews.csv')]
    return reviews_csv_files

# Function to merge all reviews CSV files
def merge_reviews_csv_files():
    reviews_csv_files = find_all_reviews_csvs()
    
    if not reviews_csv_files:
        return None  # No CSVs found

    df_list = [pd.read_csv(f) for f in reviews_csv_files]  # Read each CSV
    merged_df = pd.concat(df_list, ignore_index=True)  # Merge all CSVs
    
    return merged_df

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
    global scraped_product_df_global
    global scraped_reviews_df_global
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    
    search_term = request.form.get('search_term')
    
    if not search_term:
        flash("Please enter a valid product name.", "danger")
        return redirect(url_for('search_page'))
    
    days_ago = request.form.get('num_days_ago')

    API_KEY = 'adff6cceb29315f1739939650cdf1cf79bbbed28'
    bucket = None
    context = None
    cookie_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'cookie.txt')
    if os.path.exists(cookie_file_path):
        with open(cookie_file_path, 'r') as file:
            cookie = file.read().strip()  # Read and strip any unnecessary whitespace
    else:
        flash("Cookie file not found! Using default empty cookie.", "warning")
        cookie = ""
    
    amazon_event = {
        'search_term' : search_term,
        'api_key' : API_KEY,
        'destination_bucket' : bucket,
        'cookie' : cookie,
        'days_ago' : days_ago,
    }

    event = {
        'search_term' : search_term,
        'api_key' : API_KEY,
        'destination_bucket' : bucket,
        'days_ago' : days_ago,
    }
    
    #amazon_lambda_handler(amazon_event, context)
    #bestbuy_lambda_handler(event, context)
    #costco_lambda_handler(event, context)
    #homedepot_lambda_handler(event, context)
    #lowes_lambda_handler(event, context)
    walmart_lambda_handler(event, context)

    merged_product_df = merge_product_csv_files()
    if not merged_product_df.empty:
        total_product_results = len(merged_product_df)
    else:
        total_product_results = 0
    
    merged_reviews_df = merge_reviews_csv_files()
    if not merged_reviews_df.empty:
        total_reviews_results = len(merged_reviews_df)
    else:
        total_reviews_results = 0
    
    if merged_product_df is not None:
        # Extract first 10 and last 10 rows
        if len(merged_product_df) >= 20:
            display_rows = pd.concat([merged_product_df.head(10), merged_product_df.tail(10)])
        else:
            display_rows = merged_product_df  # If less than 20 rows, show all
        
        scraped_product_results = display_rows.to_dict(orient="records")
        scraped_product_df_global = merged_product_df
    else:
        flash("No data found. Please try again.", "danger")
        scraped_product_results = []
        scraped_product_df_global = []
    
    if merged_reviews_df is not None:
        # Extract first 10 and last 10 rows
        if len(merged_reviews_df) >= 20:
            display_rows = pd.concat([merged_reviews_df.head(10), merged_reviews_df.tail(10)])
        else:
            display_rows = merged_reviews_df  # If less than 20 rows, show all
        
        scraped_reviews_results = display_rows.to_dict(orient="records")
        scraped_reviews_df_global = merged_reviews_df
    else:
        flash("No data found. Please try again.", "danger")
        scraped_reviews_results = []
        scraped_reviews_df_global = []
    
    return render_template('search.html', scraped_product_results=scraped_product_results, scraped_reviews_results=scraped_reviews_results, total_product_results=total_product_results, total_reviews_results=total_reviews_results ,user=user)

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
    
    # Validate if URLs is Supported by the Scraper
    for product_url in product_urls:
        response_df, details_df, scraped_results = validate_product_url(product_url)

    # Store scraped data globally for downloading
    scraped_data_global = response_df
    scraped_data_dictionary_global = details_df

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

    # Validate if URLs is Supported by the Scraper
    for review_url in review_urls:
        response_df, reviews_df, scraped_results = validate_review_url(review_url, num_pages)
    
    scraped_data_global = response_df
    scraped_data_dictionary_global = reviews_df
    
    return render_template('review.html', scraped_results=scraped_results, user=user)

# Validate Search URL ** Validate Search Term
def validate_search_url(url, num_pages=1):
    if 'amazon' in url:
        flash("Missing Amazon Website Scraper", "success")
        #url_list = [url]
        #response_df = unwrangle_amazon_products.get_products_df(url, API_KEY) # Input: Search Term, API Key | Output: response_df
        response_df = ("0", "0", "0")
        if response_df.empty:
            flash("No data found for the given URLs.", "danger")
            return redirect(url_for('search_page'))
        else:
            flash(f"Scraped {len(response_df)} products successfully!", "success")
        scraped_results = response_df.to_dict(orient='records')
        return response_df, scraped_results
    elif 'bestbuy' in url:
        flash("Missing Best Buy Website Scraper", "success")
        #url_list = [url]
        #response_df = unwrangle_bestbuy_products.get_products_df(url, API_KEY) # Input: Search Term, API Key | Output: response_df
        response_df = ("0", "0", "0")
        if response_df.empty:
            flash("No data found for the given URLs.", "danger")
            return redirect(url_for('search_page'))
        else:
            flash(f"Scraped {len(response_df)} products successfully!", "success")
        scraped_results = response_df.to_dict(orient='records')
        return response_df, scraped_results
    elif 'costco' in url:
        flash("Missing Costco Website Scraper", "success")
        #url_list = [url]
        #response_df = unwrangle_costco_products.get_products_df(url, API_KEY) # Input: Search Term, API Key | Output: response_df
        response_df = ("0", "0", "0")
        if response_df.empty:
            flash("No data found for the given URLs.", "danger")
            return redirect(url_for('search_page'))
        else:
            flash(f"Scraped {len(response_df)} products successfully!", "success")
        scraped_results = response_df.to_dict(orient='records')
        return response_df, scraped_results
    elif 'homedepot' in url:
        flash("Missing Home Depot Website Scraper", "success")
        #url_list = [url]
        #response_df = unwrangle_homedepot_products.get_products_df(url, API_KEY) # Input: Search Term, API Key | Output: response_df
        response_df = ("0", "0", "0")
        if response_df.empty:
            flash("No data found for the given URLs.", "danger")
            return redirect(url_for('search_page'))
        else:
            flash(f"Scraped {len(response_df)} products successfully!", "success")
        scraped_results = response_df.to_dict(orient='records')
        return response_df, scraped_results
    elif 'lowes' in url:
        flash("Missing Lowes Website Scraper", "success")
        #url_list = [url]
        #response_df = unwrangle_lowes_products.get_products_df(url, API_KEY) # Input: Search Term, API Key | Output: response_df
        response_df = ("0", "0", "0")
        if response_df.empty:
            flash("No data found for the given URLs.", "danger")
            return redirect(url_for('search_page'))
        else:
            flash(f"Scraped {len(response_df)} products successfully!", "success")
        scraped_results = response_df.to_dict(orient='records')
        return response_df, scraped_results
    elif 'walmart' in url:
        flash("Walmart Website","success")
        #url_list = [url]
        response_df = unwrangle_walmart_products.search_products(url, API_KEY) # Input: Search Term, API Key | Output: response_df
        if response_df.empty:
            flash("No data found for the given URLs.", "danger")
            return redirect(url_for('search_page'))
        else:
            flash(f"Scraped {len(response_df)} products successfully!", "success")
        scraped_results = response_df.to_dict(orient='records')
        return response_df, scraped_results
    else:
        flash(f"Sorry, the product name \"{url}\" is currently not supported by this scraper.", "danger")
        response_df = ("0", "0", "0")
        return response_df

# Validate Product URL
def validate_product_url(url):
    if 'amazon' in url:
        flash("Missing Amazon Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'bestbuy' in url:
        flash("Missing Best Buy Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'costco' in url:
        flash("Missing Costco Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'homedepot' in url:
        flash("Missing Home Depot Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'lowes' in url:
        flash("Missing Lowes Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'walmart' in url:
        flash("Walmart Website","success")
        df = pd.DataFrame({'url': [url]})
        details_df = unwrangle_walmart_products.get_product_data(df, API_KEY) # Input: df, API Key | Output: details_df
        if details_df.empty:
            flash("No data found for the given URLs.", "danger")
            return redirect(url_for('data_page'))
        else:
            flash(f"Scraped {len(details_df)} products successfully!", "success")
        scraped_results = details_df.to_dict(orient='records')
        return details_df, scraped_results
    else:
        flash("Sorry, this website is currently not supported by this scraper.", "danger")
        response_df = ("0", "0", "0")
        return response_df

# Validate Review URL
def validate_review_url(url, num_pages=1):
    if 'amazon' in url:
        flash("Missing Amazon Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'bestbuy' in url:
        flash("Missing Best Buy Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'costco' in url:
        flash("Missing Costco Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'homedepot' in url:
        flash("Missing Home Depot Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'lowes' in url:
        flash("Missing Lowes Website Scraper", "success")
        url_list = [url]
        response_df = ("0", "0", "0")
        return response_df
    elif 'walmart' in url:
        flash("Walmart Website","success")
        url_list = [url]
        #response_df, reviews_df = unwrangle_walmart_product(url_list, num_pages) # Input: URL List, Number of Pages | Output: response_df, reviews_df
        response_df = ("0", "0", "0")
        reviews_df = ("0", "0", "0")
        if response_df.empty:
            flash("No data found for the given URLs.", "danger")
            return redirect(url_for('review_page'))
        else:
            flash(f"Scraped {len(response_df)} products successfully!", "success")
        scraped_results = response_df.to_dict(orient='records')
        return response_df, reviews_df, scraped_results
    else:
        flash("Sorry, this website is currently not supported by this scraper.", "danger")
        response_df = ("0", "0", "0")
        return response_df

# Download Product Results
@app.route('/download_product_dataset', methods=['GET', 'POST'])
def download_product_dataset():
    global scraped_product_df_global
    
    previous_page = request.referrer  # Get the referring page (where the request came from)
    
    # If no dataset is available, redirect back to the previous page dynamically
    if scraped_product_df_global.empty:
        flash('No results available to download.', 'danger')
        return redirect(previous_page or url_for('dashboard'))  # Default to dashboard if referrer is unavailable
    
    # If data exists, generate CSV for download
    else:
        csv_data = scraped_product_df_global.to_csv(index=False)
    
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = 'attachment; filename=scraped_product_data.csv'
        response.headers['Content-Type'] = 'text/csv'

    return response

# Download Reviews Results
@app.route('/download_reviews_dataset', methods=['GET', 'POST'])
def download_reviews_dataset():
    global scraped_reviews_df_global
    
    previous_page = request.referrer  # Get the referring page (where the request came from)
    
    # If no dataset is available, redirect back to the previous page dynamically
    if scraped_reviews_df_global.empty:
        flash('No results available to download.', 'danger')
        return redirect(previous_page or url_for('dashboard'))  # Default to dashboard if referrer is unavailable
    
    # If data exists, generate CSV for download
    else:
        csv_data = scraped_reviews_df_global.to_csv(index=False)
    
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = 'attachment; filename=scraped_reviews_data.csv'
        response.headers['Content-Type'] = 'text/csv'

    return response

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
