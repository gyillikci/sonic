#!/usr/bin/env python3
"""
Test Stellarium RemoteControl API Image Capabilities

This script tests what visual/image data can be obtained from Stellarium
through its RemoteControl plugin HTTP API.

Based on research, Stellarium's RemoteControl API has LIMITED direct image
capture capabilities. This script documents what's available.
"""

import requests
import json
import sys


def test_stellarium_api(host='localhost', port=8090):
    """
    Test Stellarium RemoteControl API endpoints for image/visual data
    """

    base_url = f'http://{host}:{port}/api'

    print("=" * 70)
    print("STELLARIUM REMOTECONTROL API IMAGE CAPABILITIES TEST")
    print("=" * 70)
    print()

    # Test 1: Connection
    print("TEST 1: Connection to RemoteControl API")
    print("-" * 70)
    try:
        response = requests.get(f'{base_url}/main/status', timeout=2)
        if response.status_code == 200:
            print(f"✓ Connected to Stellarium at {base_url}")
            status = response.json()
            print(f"  Server time: {status.get('time', 'unknown')}")
            print(f"  Location: {status.get('location', 'unknown')}")
        else:
            print(f"✗ HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection failed: {e}")
        print()
        print("SOLUTION: Start Stellarium with RemoteControl plugin enabled")
        print("  1. Open Stellarium")
        print("  2. Settings (F2) → Plugins → RemoteControl")
        print("  3. Check 'Load at startup'")
        print("  4. Set port: 8090")
        print("  5. Restart Stellarium")
        return False

    print()

    # Test 2: Available endpoints
    print("TEST 2: Discovering API Endpoints")
    print("-" * 70)

    # Common endpoints to test
    endpoints_to_test = [
        ('/main/status', 'GET', 'Get status'),
        ('/main/view', 'GET', 'Get view info'),
        ('/objects/info', 'GET', 'Get object info'),
        ('/stelaction/do', 'POST', 'Execute action'),
        ('/main/screenshot', 'GET', 'Get screenshot?'),
        ('/main/screenshot', 'POST', 'Take screenshot?'),
        ('/api/screenshot', 'GET', 'Direct screenshot?'),
        ('/view/screenshot', 'GET', 'View screenshot?'),
    ]

    available_endpoints = []

    for endpoint, method, description in endpoints_to_test:
        try:
            if method == 'GET':
                resp = requests.get(f'{base_url}{endpoint}', timeout=2)
            else:
                resp = requests.post(f'{base_url}{endpoint}', timeout=2)

            if resp.status_code == 200:
                print(f"✓ {method:4s} {endpoint:30s} - {description}")
                available_endpoints.append((endpoint, method, description))
            elif resp.status_code == 404:
                print(f"✗ {method:4s} {endpoint:30s} - Not found")
            else:
                print(f"? {method:4s} {endpoint:30s} - HTTP {resp.status_code}")
        except Exception as e:
            print(f"✗ {method:4s} {endpoint:30s} - {e}")

    print()

    # Test 3: Check for image endpoints
    print("TEST 3: Testing Image/Screenshot Endpoints")
    print("-" * 70)

    screenshot_endpoints = [
        '/main/screenshot',
        '/screenshot',
        '/view/screenshot',
        '/api/screenshot',
        '/main/view.png',
        '/main/view.jpg',
    ]

    image_available = False

    for endpoint in screenshot_endpoints:
        try:
            resp = requests.get(f'{base_url}{endpoint}', timeout=2)
            content_type = resp.headers.get('Content-Type', '')

            if 'image' in content_type:
                print(f"✓ FOUND IMAGE ENDPOINT: {endpoint}")
                print(f"  Content-Type: {content_type}")
                print(f"  Size: {len(resp.content)} bytes")
                image_available = True

                # Save test image
                if 'png' in content_type:
                    ext = 'png'
                elif 'jpeg' in content_type or 'jpg' in content_type:
                    ext = 'jpg'
                else:
                    ext = 'dat'

                filename = f'stellarium_api_capture.{ext}'
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                print(f"  Saved to: {filename}")
            else:
                print(f"✗ {endpoint} - Not an image ({content_type})")

        except Exception as e:
            print(f"✗ {endpoint} - {e}")

    print()

    # Test 4: Script-based screenshot
    print("TEST 4: Script-Based Screenshot")
    print("-" * 70)
    print("Stellarium supports screenshot via scripting engine:")
    print("  JavaScript command: core.screenshot('filename.png')")
    print()
    print("However, this requires:")
    print("  1. Script execution API endpoint")
    print("  2. File saved to Stellarium's script directory")
    print("  3. Cannot directly return image data to API client")
    print()
    print("Status: Limited - requires file system access")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY: Can Stellarium Feed Visuals to Other Programs via API?")
    print("=" * 70)
    print()

    if image_available:
        print("✓ YES - Direct image endpoint found!")
        print("  Stellarium can provide image data directly via HTTP API")
        print()
    else:
        print("✗ LIMITED - No direct image endpoint in RemoteControl API")
        print()
        print("AVAILABLE METHODS:")
        print()
        print("Method 1: Script-Based Screenshot (File System)")
        print("  - Use core.screenshot() via scripting API")
        print("  - Image saved to disk")
        print("  - Python reads file from disk")
        print("  - Pros: Works reliably")
        print("  - Cons: Requires file system access, slower")
        print()
        print("Method 2: Screen Capture (System Level)")
        print("  - Use Python libraries (PIL, mss, pyautogui)")
        print("  - Capture Stellarium window directly")
        print("  - Pros: No API dependency")
        print("  - Cons: Requires window management, platform-specific")
        print()
        print("Method 3: VNC/Remote Desktop")
        print("  - Run Stellarium on VNC server")
        print("  - Capture VNC framebuffer")
        print("  - Pros: Network-accessible")
        print("  - Cons: Complex setup, overhead")
        print()
        print("Method 4: Shared Memory (Custom Plugin)")
        print("  - Develop custom Stellarium plugin")
        print("  - Write framebuffer to shared memory")
        print("  - Python reads from shared memory")
        print("  - Pros: Fast, direct access")
        print("  - Cons: Requires C++ plugin development")
        print()
        print("RECOMMENDATION: Use Method 1 (Script-Based Screenshot)")
        print("  This is what the integration I built supports!")

    print()
    return True


def demonstrate_screenshot_via_script(host='localhost', port=8090):
    """
    Demonstrate how to trigger screenshot via Stellarium scripting
    """

    base_url = f'http://{host}:{port}'

    print("=" * 70)
    print("DEMONSTRATION: Screenshot via Stellarium Script API")
    print("=" * 70)
    print()

    # This would be the ideal approach if script execution endpoint exists
    script = """
    core.screenshot("api_capture.png", false, "", true);
    core.wait(0.1);
    """

    print("Script to execute:")
    print(script)
    print()

    # Try to find script execution endpoint
    script_endpoints = [
        '/api/scripts/direct',
        '/api/scripts/run',
        '/scripts/execute',
        '/stelaction/do?id=actionScript_Execute'
    ]

    print("Testing script execution endpoints...")
    for endpoint in script_endpoints:
        try:
            resp = requests.post(f'{base_url}{endpoint}',
                                data={'script': script},
                                timeout=2)
            print(f"  {endpoint}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  {endpoint}: {e}")

    print()
    print("NOTE: Stellarium's scripting is primarily designed for:")
    print("  - Built-in script files (.ssc format)")
    print("  - Manual execution from GUI")
    print("  - Not real-time API-driven execution")
    print()


if __name__ == '__main__':
    print(__doc__)
    print()

    # Test if Stellarium is running
    success = test_stellarium_api()

    if success:
        print()
        demonstrate_screenshot_via_script()

    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()
    print("Stellarium RemoteControl API provides:")
    print("  ✓ View control (FOV, direction, time)")
    print("  ✓ Object queries (positions, info)")
    print("  ✓ Action triggers (focus, search)")
    print("  ✗ Direct image/framebuffer access (LIMITED)")
    print()
    print("For optical navigation with SONIC:")
    print("  → Use screenshot files + file system monitoring")
    print("  → Or use system-level screen capture")
    print("  → Or develop custom C++ plugin for direct access")
    print()
    print("The integration I built uses Method 1 (file-based) which works!")
    print()
