#!/usr/bin/env python3
import os
import sys
import argparse
import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_pytest_tests():
    """Run all tests using pytest with coverage"""
    print("\n===== RUNNING ALL HEALTHCARE MCP TESTS WITH PYTEST =====\n")
    
    # Run pytest with coverage
    args = [
        "-xvs",  # Exit on first failure, verbose, no capture
        "--cov=src",  # Coverage for src directory
        "--cov-report=term",  # Terminal coverage report
        "--cov-report=html:coverage_html",  # HTML coverage report
        "tests/"  # Run all tests
    ]
    
    # Run pytest
    result = pytest.main(args)
    
    if result == 0:
        print("\n===== ALL TESTS PASSED =====\n")
    else:
        print("\n===== SOME TESTS FAILED =====\n")
    
    return result

def test_http_server(port=8000):
    """Test running the HTTP server"""
    print(f"\n=== Testing HTTP Server on port {port} ===\n")
    
    # Import the app
    from src.server import app
    import uvicorn
    
    # Start the server (this will block until Ctrl+C)
    print(f"Starting HTTP server on port {port}...")
    print(f"Open http://localhost:{port}/ in your browser to see the API documentation")
    print("Press Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run tests for Healthcare MCP")
    parser.add_argument("--server", action="store_true", help="Test HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP server (default: 8000)")
    parser.add_argument("--pytest", action="store_true", help="Run tests using pytest with coverage")
    parser.add_argument("--test", type=str, help="Run specific test file or directory")
    args = parser.parse_args()
    
    # Run the appropriate test(s)
    if args.server:
        test_http_server(args.port)
    elif args.pytest:
        sys.exit(run_pytest_tests())
    elif args.test:
        # Run specific test file or directory
        test_path = args.test
        if not os.path.exists(test_path):
            # Try prepending tests/ if not found
            test_path = os.path.join("tests", args.test)
            if not os.path.exists(test_path):
                print(f"Error: Test path '{args.test}' not found")
                sys.exit(1)
        
        # Run pytest on the specific test
        pytest_args = ["-xvs", test_path]
        sys.exit(pytest.main(pytest_args))
    else:
        # Run all tests by default using pytest
        sys.exit(run_pytest_tests())