from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import database as db
import re

def clean_text(text):
    """Clean and preprocess text"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text

def create_feature_text(item):
    """Combine item features into a single text for matching"""
    features = []
    
    # Add category (weighted more by repeating)
    if 'category' in item and item['category']:
        features.append(item['category'].lower() * 2)  # Repeat for emphasis
    
    # Add item name
    if 'item_name' in item and item['item_name']:
        features.append(item['item_name'].lower())
    
    # Add description
    if 'description' in item and item['description']:
        features.append(item['description'].lower())
    
    # Add color
    if 'color' in item and item['color']:
        features.append(item['color'].lower())
    
    # Combine all features
    combined = ' '.join(features)
    return clean_text(combined)

def calculate_location_score(location1, location2):
    """Calculate location similarity score"""
    if not location1 or not location2:
        return 0.0
    
    loc1 = clean_text(location1)
    loc2 = clean_text(location2)
    
    # Exact match
    if loc1 == loc2:
        return 1.0
    
    # Partial match (one contains the other)
    if loc1 in loc2 or loc2 in loc1:
        return 0.7
    
    # Check for common words
    words1 = set(loc1.split())
    words2 = set(loc2.split())
    
    if words1 and words2:
        common_words = words1.intersection(words2)
        if common_words:
            jaccard = len(common_words) / len(words1.union(words2))
            return jaccard * 0.5
    
    return 0.0

def calculate_category_score(category1, category2):
    """Calculate category match score"""
    if not category1 or not category2:
        return 0.0
    
    # Exact match
    if category1.lower() == category2.lower():
        return 1.0
    
    return 0.0

def find_matches_for_lost_item(lost_item_id, top_n=3, threshold=0.40):
    """
    Find matching found items for a lost item using AI
    Returns top N matches above threshold
    """
    # Get the lost item
    lost_item = db.get_lost_item(lost_item_id)
    if not lost_item:
        return []
    
    # Get all found items
    found_items = db.get_all_found_items()
    if not found_items:
        return []
    
    # Create feature text for lost item
    lost_text = create_feature_text(lost_item)
    
    # Create feature texts for all found items
    found_texts = [create_feature_text(item) for item in found_items]
    
    # Combine all texts for TF-IDF
    all_texts = [lost_text] + found_texts
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        max_features=100,
        ngram_range=(1, 2),  # Use unigrams and bigrams
        min_df=1
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
    except:
        # If TF-IDF fails, return empty results
        return []
    
    # Calculate cosine similarity
    lost_vector = tfidf_matrix[0:1]
    found_vectors = tfidf_matrix[1:]
    
    similarities = cosine_similarity(lost_vector, found_vectors)[0]
    
    # Calculate comprehensive scores
    matches = []
    for idx, found_item in enumerate(found_items):
        description_score = float(similarities[idx])
        
        # Calculate location score
        location_score = calculate_location_score(
            lost_item.get('location', ''),
            found_item.get('found_location', '')
        )
        
        # Calculate category score
        category_score = calculate_category_score(
            lost_item.get('category', ''),
            found_item.get('category', '')
        )
        
        # Weighted final score
        # Description: 60%, Category: 25%, Location: 15%
        confidence_score = (
            description_score * 0.60 +
            category_score * 0.25 +
            location_score * 0.15
        )
        
        # Only include matches above threshold
        if confidence_score >= threshold:
            matches.append({
                'found_item_id': found_item['id'],
                'confidence_score': confidence_score * 100,  # Convert to percentage
                'description_score': description_score * 100,
                'category_score': category_score * 100,
                'location_score': location_score * 100,
                'found_item': found_item
            })
    
    # Sort by confidence score and return top N
    matches.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return matches[:top_n]

def find_matches_for_found_item(found_item_id, top_n=3, threshold=0.40):
    """
    Find matching lost items for a found item using AI
    Returns top N matches above threshold
    """
    # Get the found item
    found_item = db.get_found_item(found_item_id)
    if not found_item:
        return []
    
    # Get all lost items
    lost_items = db.get_all_lost_items()
    if not lost_items:
        return []
    
    # Create feature text for found item
    found_text = create_feature_text(found_item)
    
    # Create feature texts for all lost items
    lost_texts = [create_feature_text(item) for item in lost_items]
    
    # Combine all texts for TF-IDF
    all_texts = [found_text] + lost_texts
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        max_features=100,
        ngram_range=(1, 2),
        min_df=1
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
    except:
        return []
    
    # Calculate cosine similarity
    found_vector = tfidf_matrix[0:1]
    lost_vectors = tfidf_matrix[1:]
    
    similarities = cosine_similarity(found_vector, lost_vectors)[0]
    
    # Calculate comprehensive scores
    matches = []
    for idx, lost_item in enumerate(lost_items):
        description_score = float(similarities[idx])
        
        # Calculate location score
        location_score = calculate_location_score(
            found_item.get('found_location', ''),
            lost_item.get('location', '')
        )
        
        # Calculate category score
        category_score = calculate_category_score(
            found_item.get('category', ''),
            lost_item.get('category', '')
        )
        
        # Weighted final score
        confidence_score = (
            description_score * 0.60 +
            category_score * 0.25 +
            location_score * 0.15
        )
        
        # Only include matches above threshold
        if confidence_score >= threshold:
            matches.append({
                'lost_item_id': lost_item['id'],
                'confidence_score': confidence_score * 100,
                'description_score': description_score * 100,
                'category_score': category_score * 100,
                'location_score': location_score * 100,
                'lost_item': lost_item
            })
    
    # Sort by confidence score and return top N
    matches.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return matches[:top_n]

def explain_match(confidence_score, category_score, location_score, description_score):
    """
    Generate human-readable explanation for a match
    """
    explanations = []
    
    if category_score >= 100:
        explanations.append("✓ Exact category match")
    elif category_score > 0:
        explanations.append("~ Similar category")
    
    if location_score >= 70:
        explanations.append("✓ Same or nearby location")
    elif location_score >= 40:
        explanations.append("~ Similar area")
    
    if description_score >= 70:
        explanations.append("✓ Very similar description")
    elif description_score >= 50:
        explanations.append("~ Matching description elements")
    elif description_score >= 30:
        explanations.append("~ Some description overlap")
    
    if confidence_score >= 80:
        verdict = "Strong match - highly likely to be your item"
    elif confidence_score >= 60:
        verdict = "Good match - worth investigating"
    elif confidence_score >= 40:
        verdict = "Possible match - check carefully"
    else:
        verdict = "Weak match - proceed with caution"
    
    return {
        'verdict': verdict,
        'reasons': explanations
    }