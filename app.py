from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import database as db
import matcher
import otp_service
import analytics

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed extensions for photo uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
db.init_db()

@app.route('/')
def index():
    """Landing page with stats"""
    stats = db.get_stats()
    recent_recoveries = db.get_recent_recoveries(limit=5)
    return render_template('index.html', stats=stats, recent_recoveries=recent_recoveries)

@app.route('/report_lost', methods=['GET', 'POST'])
def report_lost():
    """Report a lost item"""
    if request.method == 'POST':
        # Get form data
        category = request.form['category']
        item_name = request.form['item_name']
        description = request.form['description']
        color = request.form['color']
        location = request.form['location']
        lost_date = request.form['lost_date']
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']
        contact_email = request.form['contact_email']
        
        # Handle file upload
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"lost_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_path = f"uploads/{filename}"
        
        # Insert into database
        lost_item_id = db.insert_lost_item(
            category, item_name, description, color, location, lost_date,
            contact_name, contact_phone, contact_email, photo_path
        )
        
        # Run AI matching against found items
        matches = matcher.find_matches_for_lost_item(lost_item_id)
        
        if matches:
            # Store matches in database
            for match in matches:
                db.insert_match(
                    lost_item_id, 
                    match['found_item_id'], 
                    match['confidence_score'],
                    match['category_score'],
                    match['location_score'],
                    match['description_score']
                )
            
            flash(f'Lost item reported! We found {len(matches)} potential matches.', 'success')
            return redirect(url_for('matches', lost_item_id=lost_item_id))
        else:
            flash('Lost item reported! We will notify you when a matching item is found.', 'info')
            return redirect(url_for('my_items'))
    
    return render_template('report_lost.html')

@app.route('/report_found', methods=['GET', 'POST'])
def report_found():
    """Report a found item"""
    if request.method == 'POST':
        # Get form data
        category = request.form['category']
        item_name = request.form['item_name']
        description = request.form['description']
        color = request.form['color']
        found_location = request.form['found_location']
        found_date = request.form['found_date']
        current_location = request.form['current_location']
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']
        
        # Handle file upload
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"found_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_path = f"uploads/{filename}"
        
        # Insert into database
        found_item_id = db.insert_found_item(
            category, item_name, description, color, found_location, found_date,
            current_location, contact_name, contact_phone, photo_path
        )
        
        # Run AI matching against lost items
        matches = matcher.find_matches_for_found_item(found_item_id)
        
        if matches:
            # Store matches in database
            for match in matches:
                db.insert_match(
                    match['lost_item_id'], 
                    found_item_id, 
                    match['confidence_score'],
                    match['category_score'],
                    match['location_score'],
                    match['description_score']
                )
            
            flash(f'Found item reported! We found {len(matches)} potential matches.', 'success')
            return redirect(url_for('matches', found_item_id=found_item_id))
        else:
            flash('Found item reported! We will notify owners when there is a match.', 'info')
            return redirect(url_for('index'))
    
    return render_template('report_found.html')

@app.route('/matches')
def matches():
    """Display match results"""
    lost_item_id = request.args.get('lost_item_id', type=int)
    found_item_id = request.args.get('found_item_id', type=int)
    
    if lost_item_id:
        # Show matches for a lost item
        item = db.get_lost_item(lost_item_id)
        match_results = db.get_matches_for_lost_item(lost_item_id)
        item_type = 'lost'
    elif found_item_id:
        # Show matches for a found item
        item = db.get_found_item(found_item_id)
        match_results = db.get_matches_for_found_item(found_item_id)
        item_type = 'found'
    else:
        flash('Invalid request', 'error')
        return redirect(url_for('index'))
    
    return render_template('matches.html', item=item, matches=match_results, item_type=item_type)

@app.route('/claim/<int:match_id>')
def claim_item(match_id):
    """Initiate claim process"""
    match = db.get_match(match_id)
    if not match:
        flash('Match not found', 'error')
        return redirect(url_for('index'))
    
    # Generate OTPs for both parties
    claimer_otp = otp_service.generate_otp()
    finder_otp = otp_service.generate_otp()
    
    # Store verification record
    verification_id = db.insert_verification(match_id, claimer_otp, finder_otp)
    
    # In production, send OTPs via SMS
    # For hackathon, we'll display them
    session['verification_id'] = verification_id
    session['claimer_phone'] = match['lost_contact_phone']
    session['finder_phone'] = match['found_contact_phone']
    
    flash(f'Claim initiated! OTP sent to both parties.', 'success')
    return redirect(url_for('verify', verification_id=verification_id))

@app.route('/verify/<int:verification_id>', methods=['GET', 'POST'])
def verify(verification_id):
    """OTP verification page"""
    verification = db.get_verification(verification_id)
    
    if not verification:
        flash('Verification not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user_type = request.form['user_type']  # 'claimer' or 'finder'
        entered_otp = request.form['otp']
        
        if user_type == 'claimer':
            if entered_otp == verification['claimer_otp']:
                db.update_verification(verification_id, claimer_verified=True)
                flash('Claimer verified successfully!', 'success')
            else:
                flash('Invalid OTP for claimer', 'error')
        
        elif user_type == 'finder':
            if entered_otp == verification['finder_otp']:
                db.update_verification(verification_id, finder_verified=True)
                flash('Finder verified successfully!', 'success')
            else:
                flash('Invalid OTP for finder', 'error')
        
        # Check if both verified
        updated_verification = db.get_verification(verification_id)
        if updated_verification['claimer_verified'] and updated_verification['finder_verified']:
            db.mark_verification_complete(verification_id)
            db.update_match_status(verification['match_id'], 'verified')
            flash('Both parties verified! Handover can proceed.', 'success')
            return redirect(url_for('timeline', match_id=verification['match_id']))
        
        return redirect(url_for('verify', verification_id=verification_id))
    
    # For hackathon demo: show OTPs on screen
    return render_template('verify.html', verification=verification, verification_id=verification_id)

@app.route('/timeline/<int:match_id>')
def timeline(match_id):
    """Display recovery timeline"""
    match = db.get_match(match_id)
    if not match:
        flash('Match not found', 'error')
        return redirect(url_for('index'))
    
    timeline_events = db.get_timeline_events(match_id)
    
    return render_template('timeline.html', match=match, timeline=timeline_events)

@app.route('/analytics')
def analytics_page():
    """Analytics dashboard"""
    # Get analytics data
    category_stats = analytics.get_category_distribution()
    location_stats = analytics.get_location_hotspots()
    recovery_rate = analytics.get_recovery_rate()
    time_to_recovery = analytics.get_average_recovery_time()
    
    return render_template('analytics.html', 
                         category_stats=category_stats,
                         location_stats=location_stats,
                         recovery_rate=recovery_rate,
                         time_to_recovery=time_to_recovery)

@app.route('/my_items')
def my_items():
    """User dashboard - simplified for hackathon"""
    # In production, this would be user-specific
    # For hackathon, show recent items
    lost_items = db.get_recent_lost_items(limit=10)
    found_items = db.get_recent_found_items(limit=10)
    
    return render_template('my_items.html', lost_items=lost_items, found_items=found_items)

@app.route('/mark_recovered/<int:match_id>')
def mark_recovered(match_id):
    """Mark item as successfully recovered"""
    db.update_match_status(match_id, 'recovered')
    flash('Item marked as recovered! Thank you for using Lost&Found AI.', 'success')
    return redirect(url_for('timeline', match_id=match_id))

# API endpoints for AJAX calls
@app.route('/api/stats')
def api_stats():
    """Get current stats"""
    return jsonify(db.get_stats())

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)