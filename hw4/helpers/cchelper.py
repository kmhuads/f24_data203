'''
    Function access the Common Crawl Index
'''
def search_cc_index(server, url, index_name):
    import requests
    import json
    from urllib.parse import quote_plus

    encoded_url = quote_plus(url)
    index_url = f'{server}{index_name}-index?url={encoded_url}&output=json'
    response = requests.get(index_url)
    
    # print("Response from server:\r\n", response.text)
    if response.status_code == 200:
        records = response.text.strip().split('\n')
        return [json.loads(record) for record in records]
    else:
        return None
        
'''
    Function to fetch content from Common Crawl
'''
def fetch_page_from_cc(records):      
    import requests
    
    # For parsing WARC records:
    from warcio.archiveiterator import ArchiveIterator
    
    for record in records:
        offset, length = int(record['offset']), int(record['length'])
        s3_url = f'https://data.commoncrawl.org/{record["filename"]}'

        # Define the byte range for the request
        byte_range = f'bytes={offset}-{offset+length-1}'

        # Send the HTTP GET request to the S3 URL with the specified byte range
        response = requests.get(
            s3_url,
            headers={'Range': byte_range},
            stream=True
        )
        # Use `stream=True` in the call to `requests.get()` to get a raw
        # byte stream, because it's gzip compressed data
        
        if response.status_code == 206:
            # Create an `ArchiveIterator` object directly from `response.raw`
            # which handles the gzipped WARC content
            
            stream = ArchiveIterator(response.raw)
            for warc_record in stream:
                if warc_record.rec_type == 'response':
                    return warc_record.content_stream().read()
        else:
            print(f"[error]: Failed to fetch data: {response.status_code}")
            return None

    print("[error]: No valid WARC record found in the given records")
    return None


'''
    Function to store the cc pages on the local file system
'''
def store_cc_pages(server, target_url, cc_indices, dest="."):
    import time

    for i in cc_indices:
    
        index_name = f"CC-MAIN-2024-{i:02d}"
        
        records = search_cc_index(server, target_url, index_name)
        if records:
            print(f"[info]: Found {len(records)} record(s) for {target_url}")
        
            # Fetch the page content from the first record
            content = fetch_page_from_cc(records)
            if content:
                print(f"[info]: Successfully fetched content for {target_url}")
                with open(f"{dest}/{index_name}_{target_url.replace('/','_')}.html", "wb") as fo:
                    fo.write(content)
                # You can now process the 'content' variable as needed
                # using something like Beautiful Soup, etc
        else:
            print(f"[warn]: No records found for {target_url}")
    
        time.sleep(5)