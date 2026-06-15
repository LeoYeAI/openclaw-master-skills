#!/bin/bash
# Token management script - used to test token retrieval and usage

set -e

BASE_URL="https://gateway.paipai.life/api/v1"
DEVICE_ID="openclaw-test-device"
USER_LOCATION=$(echo -n "" | base64)
RESPONSE_LANG="zh-cn"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== OpenClaw Paip.ai Token Management Test ===${NC}"

# Function: print step
step() {
    echo -e "\n${GREEN}▶ $1${NC}"
}

# Function: print error
error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function: print success
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function: send HTTP request
send_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local auth_header=$4
    
    local headers=(
        "-H" "Content-Type: application/json"
        "-H" "Accept: application/json"
        "-H" "X-DEVICE-ID: $DEVICE_ID"
        "-H" "X-User-Location: $USER_LOCATION"
        "-H" "X-Response-Language: $RESPONSE_LANG"
    )
    
    if [ -n "$auth_header" ]; then
        headers+=("-H" "Authorization: Bearer $auth_header")
    fi
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "${BASE_URL}${endpoint}" "${headers[@]}" -d "$data"
    else
        curl -s -X "$method" "${BASE_URL}${endpoint}" "${headers[@]}"
    fi
}

# Test login (no token required)
step "1. Test login endpoint (no token required)"
LOGIN_DATA='{"loginType":1,"username":"testuser037@test.com","password":"TestPass037!"}'
login_response=$(send_request "POST" "/user/login" "$LOGIN_DATA")

if echo "$login_response" | grep -q '"code":0'; then
    token=$(echo "$login_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$token" ]; then
        success "Login successful! Token retrieved."
        echo "Token: ${token:0:50}..."
        
        # Test an endpoint that requires a token
        step "2. Test retrieving user information (token required)"
        user_response=$(send_request "GET" "/user/current/user" "" "$token")
        
        if echo "$user_response" | grep -q '"code":0'; then
            username=$(echo "$user_response" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
            success "User information retrieved successfully!"
            echo "Username: $username"
            
            # Test publishing a moment (token required)
            step "3. Test publishing a moment (token required)"
            post_data='{"content":"Test moment - published via the token management script","images":[],"videos":[]}'
            post_response=$(send_request "POST" "/content/moment/create" "$post_data" "$token")
            
            if echo "$post_response" | grep -q '"code":0'; then
                post_id=$(echo "$post_response" | grep -o '"id":[0-9]*' | cut -d':' -f2)
                success "Moment published successfully!"
                echo "Moment ID: $post_id"
            else
                error "Failed to publish the moment."
                echo "Response: $post_response"
            fi
        else
            error "Failed to retrieve user information (the token may be invalid)."
            echo "Response: $user_response"
        fi
    else
        error "Login succeeded, but no token was retrieved."
        echo "Response: $login_response"
    fi
else
    error "Login failed."
    echo "Response: $login_response"
fi

echo -e "\n${YELLOW}=== Test Completed ===${NC}"