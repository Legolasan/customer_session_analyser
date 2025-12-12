"""
Analytics and insights generation for customer session data.
"""

from collections import Counter
from datetime import datetime
from typing import Dict, List
from sqlalchemy import func
from app import db
from app.models import CustomerSession


def get_insights() -> Dict:
    """
    Generate insights and statistics from customer session data.
    
    Returns:
        Dictionary containing various insights
    """
    total_sessions = db.session.query(func.sum(CustomerSession.sessions)).scalar() or 0
    total_customers = db.session.query(func.count(func.distinct(CustomerSession.customer))).scalar() or 0
    total_records = db.session.query(func.count(CustomerSession.id)).scalar() or 0
    
    # Get duplicate customers
    customer_counts = db.session.query(
        CustomerSession.customer,
        func.count(CustomerSession.id).label('count')
    ).group_by(CustomerSession.customer).having(func.count(CustomerSession.id) > 1).all()
    
    duplicate_customers = [
        {'customer': customer, 'occurrences': count}
        for customer, count in customer_counts
    ]
    
    # Get region distribution
    region_counts = db.session.query(
        CustomerSession.region,
        func.count(CustomerSession.id).label('count')
    ).group_by(CustomerSession.region).all()
    
    region_distribution = {region: count for region, count in region_counts}
    
    # Get source distribution
    source_counts = db.session.query(
        CustomerSession.source,
        func.count(CustomerSession.id).label('count')
    ).group_by(CustomerSession.source).all()
    
    source_distribution = {source: count for source, count in source_counts}
    
    # Get destination distribution
    destination_counts = db.session.query(
        CustomerSession.destination,
        func.count(CustomerSession.id).label('count')
    ).group_by(CustomerSession.destination).all()
    
    destination_distribution = {dest: count for dest, count in destination_counts}
    
    # Get customer-source-destination combinations
    combinations = db.session.query(
        CustomerSession.customer,
        CustomerSession.source,
        CustomerSession.destination,
        func.count(CustomerSession.id).label('count')
    ).group_by(
        CustomerSession.customer,
        CustomerSession.source,
        CustomerSession.destination
    ).all()
    
    # Get time-based data
    uploads_by_date = db.session.query(
        func.date(CustomerSession.uploaded_at).label('date'),
        func.count(CustomerSession.id).label('count')
    ).group_by(func.date(CustomerSession.uploaded_at)).order_by('date').all()
    
    uploads_by_date_data = [
        {'date': str(date), 'count': count}
        for date, count in uploads_by_date
    ]
    
    # Get daily time consumed (minutes per day)
    daily_time = db.session.query(
        func.date(CustomerSession.uploaded_at).label('date'),
        func.sum(CustomerSession.time_consumed).label('total_minutes'),
        func.count(CustomerSession.id).label('session_count')
    ).filter(
        CustomerSession.time_consumed.isnot(None)
    ).group_by(func.date(CustomerSession.uploaded_at)).order_by('date').all()
    
    daily_time_data = [
        {
            'date': str(date),
            'total_minutes': int(total_minutes) if total_minutes else 0,
            'session_count': session_count,
            'hours': round((total_minutes or 0) / 60, 2)
        }
        for date, total_minutes, session_count in daily_time
    ]
    
    # Total time consumed across all sessions
    total_time_consumed = db.session.query(
        func.sum(CustomerSession.time_consumed)
    ).filter(CustomerSession.time_consumed.isnot(None)).scalar() or 0
    
    total_time_hours = round(total_time_consumed / 60, 2) if total_time_consumed else 0
    
    # Get time consumed statistics
    sessions_with_time = db.session.query(
        func.count(CustomerSession.id).label('count')
    ).filter(CustomerSession.time_consumed.isnot(None)).scalar() or 0
    
    # Get time consumed distribution
    time_consumed_distribution = db.session.query(
        CustomerSession.time_consumed,
        func.count(CustomerSession.id).label('count')
    ).filter(CustomerSession.time_consumed.isnot(None)).group_by(CustomerSession.time_consumed).order_by(CustomerSession.time_consumed).all()
    
    time_consumed_distribution_dict = {int(time): count for time, count in time_consumed_distribution if time is not None}
    
    # Count unique regions, sources, and destinations
    regions_covered = len(region_distribution)
    sources_covered = len(source_distribution)
    destinations_covered = len(destination_distribution)
    
    return {
        'total_sessions_reviewed': int(total_sessions),
        'total_customers': total_customers,
        'total_records': total_records,
        'duplicate_customers': duplicate_customers,
        'duplicate_customers_count': len(duplicate_customers),
        'region_distribution': region_distribution,
        'regions_covered': regions_covered,
        'source_distribution': source_distribution,
        'sources_covered': sources_covered,
        'destination_distribution': destination_distribution,
        'destinations_covered': destinations_covered,
        'uploads_by_date': uploads_by_date_data,
        'sessions_with_time_consumed': sessions_with_time,
        'time_consumed_distribution': time_consumed_distribution_dict,
        'daily_time_consumed': daily_time_data,
        'total_time_consumed_minutes': int(total_time_consumed),
        'total_time_consumed_hours': total_time_hours,
        'combinations': [
            {
                'customer': customer,
                'source': source,
                'destination': destination,
                'count': count
            }
            for customer, source, destination, count in combinations
        ]
    }

