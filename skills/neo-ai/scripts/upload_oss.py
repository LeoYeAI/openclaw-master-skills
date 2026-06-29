#!/usr/bin/env python3
"""
Neodomain AI - Upload file to OSS
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import uuid
from datetime import datetime
import mimetypes

BASE_URL = "https://story.neodomain.cn"


def get_sts_token(token: str):
    """Get OSS STS token."""
    url = f"{BASE_URL}/agent/sts/oss/token"
    headers = {"accessToken": token}
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("success"):
                return result.get("data")
            else:
                print(f"❌ Failed to get STS token: {result.get('errMessage')}", file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def upload_to_oss(local_file: str, token: str):
    """Upload file to OSS using STS token."""
    import oss2
    
    # Get STS token
    sts = get_sts_token(token)
    
    # Initialize OSS client
    auth = oss2.StsAuth(
        sts['accessKeyId'],
        sts['accessKeySecret'],
        sts['securityToken']
    )
    
    bucket = oss2.Bucket(auth, 'oss-cn-shanghai.aliyuncs.com', sts['bucketName'])
    
    # Generate remote path
    filename = os.path.basename(local_file)
    ext = os.path.splitext(filename)[1]
    date_str = datetime.now().strftime("%Y%m%d")
    remote_path = f"temp/{date_str}/{uuid.uuid4().hex[:8]}{ext}"
    
    # Determine content type
    content_type = mimetypes.guess_type(local_file)[0] or 'application/octet-stream'
    
    # Upload
    with open(local_file, 'rb') as f:
        bucket.put_object(remote_path, f, headers={'Content-Type': content_type})
    
    url = f"https://wlpaas.oss-cn-shanghai.aliyuncs.com/{remote_path}"
    return url


def main():
    parser = argparse.ArgumentParser(description="Upload file to OSS")
    parser.add_argument("file", help="Local file path to upload")
    parser.add_argument("--token", "--access-token", dest="token", help="Access token")
    
    args = parser.parse_args()
    
    if not args.token:
        args.token = os.environ.get("NEODOMAIN_ACCESS_TOKEN")
    
    if not args.token:
        print("❌ Error: Access token required", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.file):
        print(f"❌ Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    print(f"📤 Uploading {args.file}...")
    url = upload_to_oss(args.file, args.token)
    print(f"✅ Upload successful!")
    print(f"   URL: {url}")


if __name__ == "__main__":
    main()
