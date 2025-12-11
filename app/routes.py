"""
Flask routes for the application.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import CustomerSession
from app.parser import parse_session_data
from app.analytics import get_insights
from app.auth import User

main_bp = Blueprint('main', __name__)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if User.verify_password(username, password):
            user = User(username)
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/')
def index():
    """Home page dashboard."""
    return render_template('index.html')


@main_bp.route('/input')
@login_required
def input_page():
    """Form-based input page."""
    return render_template('input.html')


@main_bp.route('/form-upload', methods=['POST'])
@login_required
def form_upload():
    """Handle form-based data upload."""
    try:
        # Get form data
        customer = request.form.get('customer', '').strip()
        region = request.form.get('region', '').strip()
        sessions = request.form.get('sessions', '').strip()
        source = request.form.get('source', '').strip()
        destination = request.form.get('destination', '').strip()
        time_consumed = request.form.get('time_consumed', '').strip()
        observation = request.form.get('observation', '').strip()
        
        # Validate required fields
        if not all([customer, region, sessions, source, destination]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('main.input_page'))
        
        try:
            sessions_int = int(sessions)
        except ValueError:
            flash('Sessions must be a valid number', 'error')
            return redirect(url_for('main.input_page'))
        
        # Parse time_consumed (convert to int if provided)
        time_consumed_int = None
        if time_consumed:
            try:
                time_consumed_int = int(time_consumed)
                if time_consumed_int < 1 or time_consumed_int > 120:
                    flash('Time consumed must be between 1 and 120 minutes', 'error')
                    return redirect(url_for('main.input_page'))
            except ValueError:
                flash('Time consumed must be a valid number', 'error')
                return redirect(url_for('main.input_page'))
        
        # Create database record
        session = CustomerSession(
            customer=customer,
            region=region,
            sessions=sessions_int,
            source=source,
            destination=destination,
            time_consumed=time_consumed_int,
            observation=observation,
            uploaded_at=datetime.utcnow()
        )
        
        db.session.add(session)
        db.session.commit()
        
        flash(f'Session data for {customer} uploaded successfully!', 'success')
        return redirect(url_for('main.input_page'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error uploading data: {str(e)}', 'error')
        return redirect(url_for('main.input_page'))


@main_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Handle data upload."""
    try:
        text_data = request.form.get('session_data', '').strip()
        
        if not text_data:
            flash('Please provide session data', 'error')
            return redirect(url_for('main.index'))
        
        # Parse the data
        parsed_data = parse_session_data(text_data)
        
        if not parsed_data:
            # Try to identify what's missing
            import re
            missing_fields = []
            required_fields = {
                'customer': r'Customer:\s*(.+?)(?:\s*\[.*?\])?\s*$',
                'region': r'Region:\s*(.+?)\s*$',
                'sessions': r'Sessions:\s*(\d+)\s*$',
                'source': r'Source:\s*(.+?)\s*$',
                'destination': r'Destination:\s*(.+?)\s*$'
            }
            
            for field, pattern in required_fields.items():
                if not re.search(pattern, text_data, re.MULTILINE | re.IGNORECASE):
                    missing_fields.append(field)
            
            if missing_fields:
                flash(f'Failed to parse session data. Missing fields: {", ".join(missing_fields)}. Please check the format.', 'error')
            else:
                flash('Failed to parse session data. Please check the format.', 'error')
            return redirect(url_for('main.index'))
        
        # Parse time_consumed (convert to int if provided)
        time_consumed_int = None
        time_consumed_str = parsed_data.get('time_consumed', '')
        if time_consumed_str:
            try:
                time_consumed_int = int(time_consumed_str)
                if time_consumed_int < 1 or time_consumed_int > 120:
                    time_consumed_int = None  # Invalid range, ignore
            except (ValueError, TypeError):
                time_consumed_int = None  # Not a valid integer, ignore
        
        # Create database record
        session = CustomerSession(
            customer=parsed_data['customer'],
            region=parsed_data['region'],
            sessions=parsed_data['sessions'],
            source=parsed_data['source'],
            destination=parsed_data['destination'],
            time_consumed=time_consumed_int,
            observation=parsed_data.get('observation', ''),
            uploaded_at=datetime.utcnow()
        )
        
        db.session.add(session)
        db.session.commit()
        
        flash('Session data uploaded successfully!', 'success')
        return redirect(url_for('main.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error uploading data: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    """API endpoint for uploading data."""
    try:
        data = request.get_json()
        text_data = data.get('session_data', '').strip()
        
        if not text_data:
            return jsonify({'error': 'No session data provided'}), 400
        
        parsed_data = parse_session_data(text_data)
        
        if not parsed_data:
            return jsonify({'error': 'Failed to parse session data'}), 400
        
        # Parse time_consumed (convert to int if provided)
        time_consumed_int = None
        time_consumed_str = parsed_data.get('time_consumed', '')
        if time_consumed_str:
            try:
                time_consumed_int = int(time_consumed_str)
                if time_consumed_int < 1 or time_consumed_int > 120:
                    time_consumed_int = None  # Invalid range, ignore
            except (ValueError, TypeError):
                time_consumed_int = None  # Not a valid integer, ignore
        
        session = CustomerSession(
            customer=parsed_data['customer'],
            region=parsed_data['region'],
            sessions=parsed_data['sessions'],
            source=parsed_data['source'],
            destination=parsed_data['destination'],
            time_consumed=time_consumed_int,
            observation=parsed_data.get('observation', ''),
            uploaded_at=datetime.utcnow()
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': session.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main_bp.route('/insights')
def insights():
    """Display insights and visualizations."""
    insights_data = get_insights()
    return render_template('insights.html', insights=insights_data)


@main_bp.route('/api/insights')
def api_insights():
    """API endpoint for insights."""
    insights_data = get_insights()
    return jsonify(insights_data)


@main_bp.route('/reports')
def reports():
    """Display tabular reports."""
    # Get all sessions
    sessions = CustomerSession.query.order_by(CustomerSession.uploaded_at.desc()).all()
    
    # Get insights for summary
    insights_data = get_insights()
    
    return render_template('reports.html', sessions=sessions, insights=insights_data)


@main_bp.route('/api/sessions')
def api_sessions():
    """API endpoint to get all sessions."""
    sessions = CustomerSession.query.order_by(CustomerSession.uploaded_at.desc()).all()
    return jsonify([session.to_dict() for session in sessions])


@main_bp.route('/api/sessions/<int:session_id>')
def get_session(session_id):
    """Get a single session record by ID."""
    try:
        session = CustomerSession.query.get_or_404(session_id)
        return jsonify(session.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/sessions/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """Delete a session record."""
    try:
        session = CustomerSession.query.get_or_404(session_id)
        db.session.delete(session)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

