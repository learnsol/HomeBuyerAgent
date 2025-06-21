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
from query_history_cloud import query_history
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Log query history backend being used
logger.info(f"📊 Query History Backend: {type(query_history.backend).__name__}")
logger.info(f"🔧 Backend Configuration: {query_history.backend.__dict__ if hasattr(query_history.backend, '__dict__') else 'N/A'}")

# Initialize orchestrator
orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = create_adk_home_buying_orchestrator()
        logger.info("🏠 ADK Home Buying Orchestrator initialized")
    return orchestrator

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - available at both /health and /api/health"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'ADK Home Buyer API',
        'version': '1.0.0',
        'port': os.environ.get('PORT', '8080')
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
          # Save query to history
        try:
            logger.info(f"💾 Saving query to history using backend: {type(query_history.backend).__name__}")
            query_id = query_history.add_query(
                user_input=user_request,
                result=result,
                session_id=result.get('session_id')
            )
            transformed_result['query_id'] = query_id
            logger.info(f"✅ Query saved to history with ID: {query_id}")
        except Exception as history_error:
            logger.error(f"❌ Failed to save query history: {history_error}", exc_info=True)
        
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
        # Extract recommendations from the orchestrator result structure
        recommendations_data = backend_result.get('recommendations', {})
        all_ranked_listings = recommendations_data.get('ranked_listings', [])
        
        # Categorize listings by recommendation level
        highly_recommended = [l for l in all_ranked_listings if l.get('overall_score', 0) >= 80]
        recommended = [l for l in all_ranked_listings if 60 <= l.get('overall_score', 0) < 80]
        consider_with_caution = [l for l in all_ranked_listings if 40 <= l.get('overall_score', 0) < 60]
        
        # Determine what to show and generate appropriate messages
        recommendations_to_show = []
        guidance_message = ""
        recommendation_status = ""
        
        if highly_recommended:
            # Best case: Show highly recommended properties
            recommendations_to_show = highly_recommended
            recommendation_status = "excellent"
            guidance_message = f"Great news! We found {len(highly_recommended)} highly recommended properties that meet your criteria."
            
        elif recommended:
            # Good case: Show recommended properties
            recommendations_to_show = recommended
            recommendation_status = "good"
            guidance_message = f"We found {len(recommended)} recommended properties for you. While not highly recommended, these are solid options that meet most of your criteria."
            
        elif consider_with_caution:
            # Fallback case: Show best available with caution message
            recommendations_to_show = consider_with_caution[:3]  # Limit to top 3
            recommendation_status = "caution"
            guidance_message = f"No properties met our 'Recommended' threshold. Here are the {len(recommendations_to_show)} best available options, but you may want to adjust your search criteria for better matches."
            
        else:
            # Worst case: No decent options
            recommendation_status = "none"
            guidance_message = "No suitable properties found with your current criteria. Consider adjusting your budget, location preferences, or other requirements and try again."
        
        # Transform each recommendation
        transformed_recommendations = []
        for rec in recommendations_to_show:
            summary = rec.get('summary', {})
            transformed_rec = {
                'listing_id': rec.get('listing_id'),
                'address': summary.get('address', 'Unknown Address'),
                'price': summary.get('price', 0),
                'bedrooms': summary.get('bedrooms', 'N/A'),
                'bathrooms': summary.get('bathrooms', 'N/A'),
                'square_footage': summary.get('square_footage'),
                'description': '', # Not in summary, could extract from details
                'total_score': rec.get('overall_score', 0),
                'pros': rec.get('pros', []),
                'cons': rec.get('cons', []),
                'recommendation_summary': rec.get('recommendation', ''),
                # Extract sub-scores from details if available
                'affordability_score': extract_affordability_score(rec),
                'locality_score': extract_locality_score(rec),
                'safety_score': extract_safety_score(rec)
            }
            transformed_recommendations.append(transformed_rec)
        
        # Create enhanced summary with guidance
        summary = {
            'total_listings': len(all_ranked_listings),
            'recommended_count': len(recommended) + len(highly_recommended),
            'highly_recommended_count': len(highly_recommended),
            'average_score': calculate_average_score(transformed_recommendations),
            'recommendation_status': recommendation_status,
            'guidance_message': guidance_message,
            'criteria_suggestions': generate_criteria_suggestions(all_ranked_listings, backend_result.get('user_criteria', {}))
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
            'summary': {
                'total_listings': 0, 
                'recommended_count': 0, 
                'average_score': 0,
                'recommendation_status': 'error',
                'guidance_message': 'Failed to process analysis results. Please try again.'
            },
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

@app.route('/api/history', methods=['GET'])
def get_query_history():
    """Get recent query history for debugging"""
    try:
        limit = request.args.get('limit', 5, type=int)
        recent_queries = query_history.get_recent_queries(limit)
        
        # Return summary information (not full data for privacy)
        summary = []
        for i, query in enumerate(recent_queries, 1):
            summary.append({
                'id': i,
                'timestamp': query.get('timestamp'),
                'session_id': query.get('session_id'),
                'status': query.get('result', {}).get('status'),
                'found_listings': query.get('result', {}).get('found_listings_count', 0),
                'recommendations': query.get('result', {}).get('recommendations_count', 0)
            })
        
        return jsonify({
            'backend_type': type(query_history.backend).__name__,
            'total_queries': len(recent_queries),
            'queries': summary
        })
    except Exception as e:
        logger.error(f"❌ Error retrieving history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/status', methods=['GET'])
def history_status():
    """Get query history backend status"""
    try:
        return jsonify({
            'backend_type': type(query_history.backend).__name__,
            'backend_config': getattr(query_history.backend, '__dict__', {}),
            'environment': {
                'GOOGLE_CLOUD_PROJECT': os.getenv('GOOGLE_CLOUD_PROJECT'),
                'QUERY_HISTORY_BACKEND': os.getenv('QUERY_HISTORY_BACKEND', 'auto'),
                'ENABLE_QUERY_HISTORY': os.getenv('ENABLE_QUERY_HISTORY', 'true')
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_affordability_score(rec):
    """Extract affordability score from recommendation details"""
    try:
        details = rec.get('details', {})
        affordability = details.get('affordability_details', {})
        if affordability.get('is_affordable'):
            return affordability.get('affordability_ratio', 0)
        return 0
    except:
        return 0

def extract_locality_score(rec):
    """Extract locality score from recommendation details"""
    try:
        details = rec.get('details', {})
        locality = details.get('locality_details', {})
        return locality.get('overall_score', 0)
    except:
        return 0

def extract_safety_score(rec):
    """Extract safety score from recommendation details"""
    try:
        details = rec.get('details', {})
        hazard = details.get('hazard_details', {})
        return hazard.get('overall_safety_score', 0)
    except:
        return 0

def generate_criteria_suggestions(all_ranked_listings, user_criteria):
    """Generate suggestions for improving search criteria based on analysis results"""
    suggestions = []
    
    if not all_ranked_listings:
        return ["Try expanding your search area", "Consider increasing your budget", "Reduce minimum bedroom/bathroom requirements"]
    
    # Analyze why properties scored low
    avg_score = sum(l.get('overall_score', 0) for l in all_ranked_listings) / len(all_ranked_listings)
    
    if avg_score < 40:
        suggestions.append("Consider significantly increasing your budget for better property options")
        suggestions.append("Expand your search to include more neighborhoods")
        
    elif avg_score < 60:
        # Check common issues in properties
        affordability_issues = sum(1 for l in all_ranked_listings 
                                 if not l.get('details', {}).get('affordability_details', {}).get('is_affordable', True))
        
        if affordability_issues > len(all_ranked_listings) * 0.5:
            current_price = user_criteria.get('search_criteria', {}).get('price_max', 0)
            if current_price:
                suggested_price = int(current_price * 0.8)
                suggestions.append(f"Consider lowering your price range to around ${suggested_price:,} for better affordability")
            suggestions.append("Consider increasing your down payment or improving your debt-to-income ratio")
            
        suggestions.append("Look for properties in emerging neighborhoods with good growth potential")
        suggestions.append("Consider slightly older properties that may offer better value")
        
    else:
        suggestions.append("Your criteria are well-balanced - try expanding the search area for more options")    
    return suggestions[:3]  # Limit to top 3 suggestions



if __name__ == '__main__':
    # Enhanced startup logging for Cloud Run debugging
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting ADK Home Buyer API Server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"📦 Python path: {os.environ.get('PYTHONPATH', 'not set')}")
    logger.info(f"📍 Health check: http://0.0.0.0:{port}/health")
    logger.info(f"🎯 Analysis endpoint: http://0.0.0.0:{port}/api/analyze")
    
    try:
        logger.info("⚡ Testing initial imports...")
        from google.adk.agents import SequentialAgent
        logger.info("✅ Google ADK imports successful")
        
        logger.info("📊 Testing query history...")
        logger.info(f"📊 Query History Backend: {type(query_history.backend).__name__}")
        
        logger.info("🎬 Starting Flask server...")
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        raise
