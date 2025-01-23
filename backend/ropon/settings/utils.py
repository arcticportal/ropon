# Helper functions for settings
def build_urls_from_hosts(hostnames, existing_urls=None, add_http=True):
    """
    Build a list of URLs from hostnames, optionally adding http/https prefix.
    
    Args:
        hostnames (str|list): Comma-separated string or list of hostnames
        existing_urls (list, optional): List of existing URLs to include
        add_http (bool): If True, adds 'http://', else adds 'https://'
    
    Returns:
        list: Unique list of URLs with proper prefixes
    """
    if not hostnames:
        return existing_urls or []  # Return empty list instead of None

    if isinstance(hostnames, str):
        hostnames = [h.strip() for h in hostnames.split(',') if h.strip()]
    
    urls = []
    for host in hostnames:
        if host.startswith(('http://', 'https://')):
            urls.append(host)
            continue
        
        urls.append(f'https://{host}')
        if add_http:
            urls.append(f'http://{host}')
        
        
    if existing_urls:
        urls.extend(existing_urls)
            
    return list(set(urls))  # Remove any duplicates