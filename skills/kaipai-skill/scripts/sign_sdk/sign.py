import hashlib
import hmac
import base64
import datetime
import requests
from urllib.parse import urlparse, parse_qs, urlencode

BasicDateFormat = "%Y%m%dT%H%M%SZ"
Algorithm = "SDK-HMAC-SHA256"
HeaderXDate = "X-Sdk-Date"
HeaderHost = "Host"
HeaderAuthorization = "Authorization"
HeaderContentSha256 = "X-Sdk-Content-Sha256"

class Signer:
    def __init__(self, key, secret):
        self.Key = key
        self.Secret = secret

    def sign_string_to_sign(self, string_to_sign, signing_key):
        hm = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256)
        return hm.hexdigest()



    def auth_header_value(self, signature, access_key, signed_headers):
        signed_headers_str = ";".join(signed_headers)
        header_value = f"{Algorithm} Access={access_key}, SignedHeaders={signed_headers_str}, Signature={signature}"
        encoded_value = base64.b64encode(header_value.encode()).decode()
        return "Bearer " + encoded_value

    def canonical_request(self, method, url, headers, body, signed_headers):
        parsed_url = urlparse(url)
        canonical_uri = self.canionical_uri(parsed_url.path)
        sorted_query = sorted(parse_qs(parsed_url.query).items())
        canonical_query_string = urlencode(sorted_query, doseq=True)
        canonical_headers = self.canonical_headers(headers, signed_headers)
        signed_headers_str = ";".join(signed_headers)
        
        hexencode = headers.get(HeaderContentSha256, "")
        if not hexencode:
            hexencode = self.hash_sha256(body)
           

        return f"{method}\n{canonical_uri}\n{canonical_query_string}\n{canonical_headers}\n{signed_headers_str}\n{hexencode}"
   
    def canionical_uri(self, path):
        if not path or not path.endswith("/"):
            path += "/"
        return path
    
    def canonical_headers(self, headers, signed_headers):
        lowheaders = {key.lower(): value.strip() for key, value in headers.items()}
        a = [f"{key}:{lowheaders[key]}" for key in signed_headers]
        return "\n".join(a)

    def signed_headers(self, headers):
        signed_headers = [header.lower() for header in headers]
        signed_headers.sort()
        return signed_headers

    def sign(self, url, method, headers, body):
        dt = headers.get(HeaderXDate, "")
        if not dt:
            t = datetime.datetime.now(datetime.timezone.utc)
            headers[HeaderXDate] = t.strftime(BasicDateFormat)
        else:
            t = datetime.datetime.strptime(dt, BasicDateFormat)

        signed_headers = self.signed_headers(headers)
        canonical_request = self.canonical_request(method, url, headers, body, signed_headers)
        string_to_sign = self.string_to_sign(canonical_request, t.strftime(BasicDateFormat))
        signing_key = self.Secret.encode()
        signature = self.sign_string_to_sign(string_to_sign, signing_key)
        auth_value = self.auth_header_value(signature, self.Key, signed_headers)
        headers[HeaderAuthorization] = auth_value

        request = requests.Request(method, url, headers=headers, data=body)
        signed_request = request.prepare()
        return signed_request


    def string_to_sign(self, canonical_request, time_format):
        hash_obj = hashlib.sha256(canonical_request.encode())
        hash_hex = hash_obj.hexdigest()
        return f"{Algorithm}\n{time_format}\n{hash_hex}"


    def hash_sha256(self, data):
        hash_obj = hashlib.sha256(data.encode())
        return hash_obj.hexdigest()