import database as db
from collections import Counter
from datetime import datetime, timedelta

def get_category_distribution():
    """Get distribution of items by category"""
    lost_items = db.get_all_lost_items()
    
    categories = [item['category'] for item in lost_items if item.get('category')]
    category_counts = Counter(categories)
    
    # Format for Chart.js
    return {
        'labels': list(category_counts.keys()),
        'data': list(category_counts.values())
    }

def get_location_hotspots(top_n=10):
    """Get top locations where items are lost"""
    lost_items = db.get_all_lost_items()
    
    locations = [item['location'] for item in lost_items if item.get('location')]
    location_counts = Counter(locations)
    
    # Get top N locations
    top_locations = location_counts.most_common(top_n)
    
    return {
        'labels': [loc[0] for loc in top_locations],
        'data': [loc[1] for loc in top_locations]
    }

def get_recovery_rate():
    """Calculate recovery success rate"""
    stats = db.get_stats()
    
    total_lost = stats['total_lost']
    total_recovered = stats['total_recovered']
    
    if total_lost == 0:
        recovery_rate = 0
    else:
        recovery_rate = (total_recovered / total_lost) * 100
    
    return {
        'rate': round(recovery_rate, 1),
        'recovered': total_recovered,
        'total': total_lost
    }

def get_average_recovery_time():
    """
    Calculate average time to recovery
    For hackathon: Simplified calculation
    """
    # This is a placeholder calculation
    # In production, you'd track actual timestamps
    
    return {
        'hours': 24,  # Placeholder
        'days': 1
    }

def get_trending_categories(days=7):
    """Get trending lost item categories in last N days"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM lost_items
        WHERE created_at >= ?
        GROUP BY category
        ORDER BY count DESC
        LIMIT 5
    ''', (date_threshold,))
    
    results = cursor.fetchall()
    conn.close()
    
    return {
        'labels': [row['category'] for row in results],
        'data': [row['count'] for row in results]
    }

def get_daily_reports(days=7):
    """Get number of reports per day for last N days"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT DATE(created_at) as report_date, COUNT(*) as count
        FROM lost_items
        WHERE created_at >= ?
        GROUP BY DATE(created_at)
        ORDER BY report_date
    ''', (date_threshold,))
    
    results = cursor.fetchall()
    conn.close()
    
    return {
        'labels': [row['report_date'] for row in results],
        'data': [row['count'] for row in results]
    }

def get_match_accuracy_stats():
    """Get statistics about match accuracy"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    # Get average confidence score
    cursor.execute('SELECT AVG(confidence_score) as avg_score FROM matches')
    avg_score = cursor.fetchone()
    
    # Get matches by confidence range
    cursor.execute('''
        SELECT 
            CASE 
                WHEN confidence_score >= 80 THEN 'High (80-100%)'
                WHEN confidence_score >= 60 THEN 'Medium (60-80%)'
                ELSE 'Low (40-60%)'
            END as confidence_range,
            COUNT(*) as count
        FROM matches
        GROUP BY confidence_range
    ''')
    
    ranges = cursor.fetchall()
    conn.close()
    
    return {
        'average_score': round(avg_score['avg_score'], 1) if avg_score['avg_score'] else 0,
        'distribution': {
            'labels': [row['confidence_range'] for row in ranges],
            'data': [row['count'] for row in ranges]
        }
    }