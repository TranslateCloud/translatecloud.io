import json
import traceback

def handler(event, context):
    """Test handler to diagnose Lambda errors"""
    try:
        # Try to import the main app
        from src.main import app
        from mangum import Mangum

        # If we get here, imports work
        handler = Mangum(app, lifespan="off")
        return handler(event, context)

    except Exception as e:
        # Return detailed error information
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(error_details)
        }
