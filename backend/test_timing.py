#!/usr/bin/env python3
"""
HTTP Request Timing Script using pycurl
Provides identical timing information to curl command
"""
import pycurl
import io
import json
import argparse
import sys
import os


def test_with_pycurl(url, host_header=None, verbose=False, verify_ssl=False, timeout=30):
    """
    Test HTTP request with pycurl to get exact curl timing
    """
    
    # Create a buffer to capture response
    response_buffer = io.BytesIO()
    
    # Create pycurl object
    curl = pycurl.Curl()
    
    try:
        # Set basic options
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, response_buffer)
        curl.setopt(pycurl.TIMEOUT, timeout)
        
        # SSL options (equivalent to curl -k)
        if not verify_ssl:
            curl.setopt(pycurl.CAINFO, "")
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        
        # Set headers
        headers = ['User-Agent: pycurl-timing-test/1.0']
        if host_header:
            headers.append(f'Host: {host_header}')
        curl.setopt(pycurl.HTTPHEADER, headers)
        
        # Follow redirects
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        
        if verbose:
            curl.setopt(pycurl.VERBOSE, 1)
        
        # Display request info
        print(f"Testing: {url}")
        if host_header:
            print(f"Host header: {host_header}")
        print("-" * 60)
        
        # Perform the request
        curl.perform()
        
        # Get timing information (exactly like curl)
        time_namelookup = curl.getinfo(pycurl.NAMELOOKUP_TIME)
        time_connect = curl.getinfo(pycurl.CONNECT_TIME)
        time_appconnect = curl.getinfo(pycurl.APPCONNECT_TIME)
        time_pretransfer = curl.getinfo(pycurl.PRETRANSFER_TIME)
        time_redirect = curl.getinfo(pycurl.REDIRECT_TIME)
        time_starttransfer = curl.getinfo(pycurl.STARTTRANSFER_TIME)
        time_total = curl.getinfo(pycurl.TOTAL_TIME)
        
        # Get response info
        response_code = curl.getinfo(pycurl.HTTP_CODE)
        content_type = curl.getinfo(pycurl.CONTENT_TYPE)
        
        # Print timing results (identical to curl format)
        print(f"     time_namelookup:  {time_namelookup:.6f}")
        print(f"        time_connect:  {time_connect:.6f}")
        print(f"     time_appconnect:  {time_appconnect:.6f}")
        print(f"    time_pretransfer:  {time_pretransfer:.6f}")
        print(f"       time_redirect:  {time_redirect:.6f}")
        print(f"  time_starttransfer:  {time_starttransfer:.6f}")
        print("                     ----------")
        print(f"          time_total:  {time_total:.6f}")
        
        # Response details
        response_content = response_buffer.getvalue()
        print("-" * 60)
        print(f"HTTP Status: {int(response_code)}")
        print(f"Content-Type: {content_type}")
        print(f"Content-Length: {len(response_content)} bytes")
        
        # Try to parse JSON if it's an API response
        if content_type and 'application/json' in content_type:
            try:
                data = json.loads(response_content.decode('utf-8'))
                if 'items' in data:
                    print(f"API Items returned: {len(data['items'])}")
                elif 'results' in data:
                    print(f"API Results returned: {len(data['results'])}")
            except Exception:
                pass
        
        if verbose:
            print("\nResponse Headers:")
            print(curl.getinfo(pycurl.INFO_HEADER_OUT))
    
    except pycurl.error as e:
        print(f"pycurl error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        curl.close()


def main():
    parser = argparse.ArgumentParser(description='HTTP Timing Tool using pycurl (identical to curl timing)')
    parser.add_argument('url', nargs='?',
                       default=f"http://localhost:{os.environ.get('DJANGO_PORT', 8000)}/api/v2/networks/?fields=logo_image,regions,subregions,domains,disciplines,asset_types,website_url,has_catalog&limit=500",
                       help='URL to test')
    parser.add_argument('--host-header', '-H',
                       default=os.environ.get('DJANGO_ALLOWED_HOST', 'localhost'),
                       help='Host header to send')
    parser.add_argument('--timeout', '-t', type=int, default=30,
                       help='Request timeout in seconds')
    parser.add_argument('--verify-ssl', action='store_true',
                       help='Verify SSL certificates (default: false, like curl -k)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    test_with_pycurl(
        url=args.url,
        host_header=args.host_header,
        verbose=args.verbose,
        verify_ssl=args.verify_ssl,
        timeout=args.timeout
    )


if __name__ == "__main__":
    main()