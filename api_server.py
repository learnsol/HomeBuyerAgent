"""
Flask API Server for ADK Home Buyer Application
Provides REST API endpoints for the React frontend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
import logging
from datetime import datetime
from orchestrator_adk import create_adk_home_buying_orchestrator
from config import settings
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize orchestrator
orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = create_adk_home_buying_orchestrator()
        logger.info("🏠 ADK Home Buying Orchestrator initialized")
    return orchestrator

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'ADK Home Buyer API',
        'version': '1.0.0'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_home_buying_request():
    """
    Main API endpoint to analyze home buying request
    Expected request format:
    {
        "search_criteria": {
            "price_max": 750000,
            "price_min": 300000,
            "bedrooms_min": 3,
            "bathrooms_min": 2,
            "keywords": ["modern kitchen", "large backyard"]
        },
        "user_financial_info": {
            "annual_income": 120000,
            "down_payment_percentage": 20,
            "monthly_debts": 800
        },
        "priorities": ["safety", "good school district"]
    }
    """
    try:        # Get request data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        user_request = request.get_json()
        logger.info(f"🎯 Received home buying request: {json.dumps(user_request, indent=2)}")
        
        # Log specifically the user_financial_info
        logger.info(f"💰 user_financial_info in request: {user_request.get('user_financial_info', 'MISSING')}")
        
        # Validate required fields
        if 'search_criteria' not in user_request:
            return jsonify({'error': 'search_criteria is required'}), 400
        
        # Add default values if missing
        if 'user_financial_info' not in user_request:
            user_request['user_financial_info'] = {
                'annual_income': 80000,
                'down_payment_percentage': 20,
                'monthly_debts': 0
            }
        
        if 'priorities' not in user_request:
            user_request['priorities'] = ['affordability', 'safety']
        
        # Get orchestrator and run analysis
        orch = get_orchestrator()
        
        # Run the async analysis in a new event loop
        try:
            # Create new event loop for this request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(orch.run_full_analysis(user_request))
            loop.close()
        except Exception as async_error:
            logger.error(f"❌ Async analysis error: {async_error}", exc_info=True)
            return jsonify({
                'error': f'Analysis failed: {str(async_error)}',
                'details': 'The AI analysis encountered an error. Please try again.'
            }), 500
        
        # Check for errors in result
        if result.get('error'):
            logger.error(f"❌ Analysis returned error: {result['error']}")
            return jsonify({
                'error': result['error'],
                'details': 'The analysis completed but encountered issues with your criteria.'
            }), 400
        
        # Transform result for frontend
        transformed_result = transform_result_for_frontend(result)
        
        logger.info(f"✅ Analysis completed successfully")
        logger.info(f"   📊 Found {len(transformed_result.get('top_recommendations', []))} recommendations")
        
        return jsonify(transformed_result)
        
    except Exception as error:
        logger.error(f"❌ API error: {error}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'details': str(error)
        }), 500

def transform_result_for_frontend(backend_result):
    """Transform backend result format to frontend-friendly format"""
    try:
        # Extract recommendations
        recommendations = backend_result.get('top_recommendations', [])
        
        # Transform each recommendation
        transformed_recommendations = []
        for rec in recommendations:
            transformed_rec = {
                'listing_id': rec.get('listing_id'),
                'address': rec.get('address', 'Unknown Address'),
                'price': rec.get('price', 0),
                'bedrooms': rec.get('bedrooms', 'N/A'),
                'bathrooms': rec.get('bathrooms', 'N/A'),
                'square_footage': rec.get('square_footage'),
                'description': rec.get('description', ''),
                'total_score': rec.get('total_score', 0),
                'pros': rec.get('pros', []),
                'cons': rec.get('cons', []),
                'recommendation_summary': rec.get('recommendation_summary', ''),
                # Extract sub-scores if available
                'affordability_score': extract_score(rec, 'affordability'),
                'locality_score': extract_score(rec, 'locality'),
                'safety_score': extract_score(rec, 'hazard', 'overall_safety_score')
            }
            transformed_recommendations.append(transformed_rec)
        
        # Create summary
        summary = {
            'total_listings': len(backend_result.get('all_listings_ranked', [])),
            'recommended_count': len(transformed_recommendations),
            'average_score': calculate_average_score(transformed_recommendations)
        }
        
        return {
            'top_recommendations': transformed_recommendations,
            'summary': summary,
            'analysis_timestamp': datetime.now().isoformat(),
            'success': True
        }
        
    except Exception as e:
        logger.error(f"❌ Result transformation error: {e}")
        return {
            'top_recommendations': [],
            'summary': {'total_listings': 0, 'recommended_count': 0},
            'error': 'Failed to process analysis results'
        }

def extract_score(recommendation, analysis_type, score_key=None):
    """Extract score from recommendation analysis"""
    try:
        analysis_key = f'{analysis_type}_analysis'
        analysis = recommendation.get(analysis_key, {})
        
        if score_key:
            return analysis.get(score_key, 0)
        else:
            # Try common score field names
            for key in ['score', 'total_score', 'overall_score']:
                if key in analysis:
                    return analysis[key]
            return 0
    except:
        return 0

def calculate_average_score(recommendations):
    """Calculate average score of recommendations"""
    if not recommendations:
        return 0
    
    total_score = sum(rec.get('total_score', 0) for rec in recommendations)
    return round(total_score / len(recommendations), 1)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting ADK Home Buyer API Server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"📍 Health check: http://localhost:{port}/api/health")
    logger.info(f"🎯 Analysis endpoint: http://localhost:{port}/api/analyze")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
