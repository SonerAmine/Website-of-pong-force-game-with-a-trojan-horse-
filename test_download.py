#!/usr/bin/env python3
"""
Test script to verify Pong Force download functionality
"""

import os
import requests
import sys
from pathlib import Path

def test_file_exists():
    """Test if the executable file exists and has correct size"""
    exe_path = Path("assets/PongForceSetup.exe")
    
    if not exe_path.exists():
        print("ERROR: PongForceSetup.exe not found in assets/")
        return False
    
    file_size = exe_path.stat().st_size
    size_mb = file_size / (1024 * 1024)
    
    print(f"File found: {exe_path}")
    print(f"File size: {size_mb:.1f} MB")
    
    if size_mb < 10:
        print("WARNING: File size seems too small for a complete game")
        return False
    elif size_mb > 50:
        print("WARNING: File size seems too large")
        return False
    else:
        print("File size looks correct")
        return True

def test_website_structure():
    """Test if website files exist"""
    required_files = [
        "index.html",
        "demo.html", 
        "css/style.css",
        "css/responsive.css",
        "js/main.js",
        "js/demo.js",
        "js/particles.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    else:
        print("All website files present")
        return True

def test_download_links():
    """Test if download links in HTML are correct"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        if 'href="assets/PongForceSetup.exe"' in content:
            print("Download link found in index.html")
            return True
        else:
            print("Download link not found in index.html")
            return False
    except Exception as e:
        print(f"Error reading index.html: {e}")
        return False

def test_local_server():
    """Test if we can start a local server"""
    try:
        import http.server
        import socketserver
        import threading
        import time
        
        PORT = 8001
        
        # Start server in background
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"Local server started on port {PORT}")
            
            # Test if we can access the file
            try:
                response = requests.get(f"http://localhost:{PORT}/assets/PongForceSetup.exe", timeout=5)
                if response.status_code == 200:
                    print("File accessible via HTTP")
                    return True
                else:
                    print(f"HTTP error: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"HTTP request failed: {e}")
                return False
                
    except Exception as e:
        print(f"Server test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Pong Force - Download Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Exists", test_file_exists),
        ("Website Structure", test_website_structure), 
        ("Download Links", test_download_links),
        ("Local Server", test_local_server)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"PASSED: {test_name}")
            else:
                print(f"FAILED: {test_name}")
        except Exception as e:
            print(f"ERROR: {test_name} - {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Download functionality is ready.")
        print("\nTo test manually:")
        print("1. Run: python -m http.server 8000")
        print("2. Open: http://localhost:8000")
        print("3. Click 'Download Now' button")
        print("4. Verify file downloads (~16.7 MB)")
        return True
    else:
        print("Some tests failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)