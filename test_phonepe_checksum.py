#!/usr/bin/env python3
"""
PhonePe X-VERIFY Checksum Verification Script
Run this to verify your checksum generation is correct
"""
import base64
import hashlib
import json

# Your credentials
MERCHANT_ID = "M227BOU8BBNV7"
SALT_KEY = "5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d"
SALT_INDEX = 1

# Sample payload
payload = {
    "merchantId": MERCHANT_ID,
    "merchantTransactionId": "TXNTEST123456789",
    "merchantUserId": "U1",
    "amount": 10000,
    "redirectUrl": "https://yourdomain.com/callback/",
    "redirectMode": "POST",
    "callbackUrl": "https://yourdomain.com/callback/",
    "paymentInstrument": {
        "type": "PAY_PAGE"
    }
}

# Generate X-VERIFY
def generate_x_verify(payload_dict, endpoint, salt_key, salt_index):
    """Generate X-VERIFY checksum"""
    # Convert to JSON (compact, no spaces)
    payload_json = json.dumps(payload_dict, separators=(',', ':'))
    
    # Base64 encode
    payload_base64 = base64.b64encode(payload_json.encode()).decode()
    
    # Generate checksum
    string_to_hash = f"{payload_base64}{endpoint}{salt_key}"
    sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
    x_verify = f"{sha256_hash}###{salt_index}"
    
    return payload_base64, x_verify

# Test
endpoint = "/pg/v1/pay"
payload_base64, x_verify = generate_x_verify(payload, endpoint, SALT_KEY, SALT_INDEX)

print("=" * 80)
print("PhonePe X-VERIFY Checksum Test")
print("=" * 80)
print(f"\nMerchant ID: {MERCHANT_ID}")
print(f"Salt Key: {SALT_KEY[:10]}...")
print(f"Salt Index: {SALT_INDEX}")
print(f"\nPayload JSON:")
print(json.dumps(payload, indent=2))
print(f"\nPayload Base64 (first 100 chars):")
print(payload_base64[:100] + "...")
print(f"\nEndpoint: {endpoint}")
print(f"\nString to hash (first 150 chars):")
string_to_hash = f"{payload_base64}{endpoint}{SALT_KEY}"
print(string_to_hash[:150] + "...")
print(f"\nSHA256 Hash:")
sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
print(sha256_hash)
print(f"\nX-VERIFY:")
print(x_verify)
print("\n" + "=" * 80)
print("✅ If this matches your implementation, checksum is correct!")
print("=" * 80)

# Test request body
request_body = {
    "request": payload_base64
}

print(f"\nRequest Body:")
print(json.dumps(request_body, indent=2))

print(f"\nRequest Headers:")
print(json.dumps({
    "Content-Type": "application/json",
    "X-VERIFY": x_verify
}, indent=2))

print("\n" + "=" * 80)
print("Copy the X-VERIFY value and compare with your Django logs")
print("=" * 80)
