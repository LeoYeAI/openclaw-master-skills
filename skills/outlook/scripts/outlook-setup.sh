#!/bin/bash
# Outlook OAuth Setup via Azure CLI
# Automatically creates App Registration and configures OAuth

set -e

CONFIG_DIR="$HOME/.outlook-mcp"
CONFIG_FILE="$CONFIG_DIR/config.json"
CREDS_FILE="$CONFIG_DIR/credentials.json"

APP_NAME="Clawdbot-Outlook"
REDIRECT_URI="http://localhost"
SCOPES="https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Calendars.ReadWrite offline_access"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Outlook OAuth Setup ===${NC}"
echo ""

# Check prerequisites
check_prereqs() {
    if ! command -v az &> /dev/null; then
        echo -e "${RED}Error: Azure CLI not installed${NC}"
        echo "Install with: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}Error: jq not installed${NC}"
        echo "Install with: sudo apt install jq"
        exit 1
    fi
}

# Step 1: Azure Login
azure_login() {
    echo -e "${YELLOW}Step 1: Azure Login${NC}"
    
    # Check if already logged in
    if az account show &> /dev/null; then
        CURRENT_USER=$(az account show --query user.name -o tsv)
        echo -e "Currently logged in as: ${GREEN}$CURRENT_USER${NC}"
        read -p "Continue with this account? [Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            az logout 2>/dev/null || true
        else
            return 0
        fi
    fi
    
    echo "Opening browser for Azure login..."
    echo "(If no browser available, use: az login --use-device-code)"
    
    if ! az login --use-device-code; then
        echo -e "${RED}Login failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Logged in successfully${NC}"
}

# Step 2: Create App Registration
create_app() {
    echo ""
    echo -e "${YELLOW}Step 2: Creating App Registration${NC}"
    
    # Check if app already exists
    EXISTING_APP=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv 2>/dev/null)
    
    if [ -n "$EXISTING_APP" ] && [ "$EXISTING_APP" != "null" ]; then
        echo -e "App '$APP_NAME' already exists: ${BLUE}$EXISTING_APP${NC}"
        read -p "Use existing app? [Y/n] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            APP_ID="$EXISTING_APP"
            echo -e "${GREEN}✓ Using existing app${NC}"
            return 0
        fi
        APP_NAME="$APP_NAME-$(date +%s)"
        echo "Creating new app: $APP_NAME"
    fi
    
    # Create new app
    APP_RESULT=$(az ad app create \
        --display-name "$APP_NAME" \
        --sign-in-audience "AzureADandPersonalMicrosoftAccount" \
        --web-redirect-uris "$REDIRECT_URI" \
        --query "{appId: appId, objectId: id}" -o json)
    
    APP_ID=$(echo "$APP_RESULT" | jq -r '.appId')
    echo -e "${GREEN}✓ App created: $APP_ID${NC}"
}

# Step 3: Create Client Secret
create_secret() {
    echo ""
    echo -e "${YELLOW}Step 3: Creating Client Secret${NC}"
    
    SECRET_RESULT=$(az ad app credential reset \
        --id "$APP_ID" \
        --display-name "clawdbot-secret" \
        --years 2 \
        --query "{clientId: appId, clientSecret: password}" -o json 2>&1)
    
    CLIENT_ID=$(echo "$SECRET_RESULT" | jq -r '.clientId')
    CLIENT_SECRET=$(echo "$SECRET_RESULT" | jq -r '.clientSecret')
    
    if [ -z "$CLIENT_SECRET" ] || [ "$CLIENT_SECRET" = "null" ]; then
        echo -e "${RED}Failed to create secret${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Secret created${NC}"
}

# Step 4: Add API Permissions
add_permissions() {
    echo ""
    echo -e "${YELLOW}Step 4: Adding API Permissions${NC}"
    
    # Microsoft Graph API ID
    GRAPH_API="00000003-0000-0000-c000-000000000000"
    
    # Get permission IDs
    MAIL_RW_ID=$(az ad sp show --id "$GRAPH_API" --query "oauth2PermissionScopes[?value=='Mail.ReadWrite'].id" -o tsv 2>/dev/null)
    MAIL_SEND_ID=$(az ad sp show --id "$GRAPH_API" --query "oauth2PermissionScopes[?value=='Mail.Send'].id" -o tsv 2>/dev/null)
    CAL_RW_ID=$(az ad sp show --id "$GRAPH_API" --query "oauth2PermissionScopes[?value=='Calendars.ReadWrite'].id" -o tsv 2>/dev/null)
    USER_READ_ID=$(az ad sp show --id "$GRAPH_API" --query "oauth2PermissionScopes[?value=='User.Read'].id" -o tsv 2>/dev/null)
    
    # Add permissions
    az ad app permission add --id "$APP_ID" \
        --api "$GRAPH_API" \
        --api-permissions "$MAIL_RW_ID=Scope" "$MAIL_SEND_ID=Scope" "$CAL_RW_ID=Scope" "$USER_READ_ID=Scope" 2>/dev/null || true
    
    echo -e "${GREEN}✓ Permissions added (Mail.ReadWrite, Mail.Send, Calendars.ReadWrite, User.Read)${NC}"
}

# Step 5: Save Config
save_config() {
    echo ""
    echo -e "${YELLOW}Step 5: Saving Configuration${NC}"
    
    mkdir -p "$CONFIG_DIR"
    
    cat > "$CONFIG_FILE" << EOF
{
  "client_id": "$CLIENT_ID",
  "client_secret": "$CLIENT_SECRET"
}
EOF
    
    chmod 600 "$CONFIG_FILE"
    echo -e "${GREEN}✓ Config saved to $CONFIG_FILE${NC}"
}

# Step 6: User Authorization
authorize() {
    echo ""
    echo -e "${YELLOW}Step 6: User Authorization${NC}"
    echo ""
    
    AUTH_URL="https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=$CLIENT_ID&response_type=code&redirect_uri=$REDIRECT_URI&scope=$(echo $SCOPES | sed 's/ /%20/g')&response_mode=query"
    
    echo "Open this URL in your browser:"
    echo ""
    echo -e "${BLUE}$AUTH_URL${NC}"
    echo ""
    echo "After authorizing, you'll be redirected to a page that won't load."
    echo "Copy the FULL URL from the address bar and paste it here:"
    echo ""
    read -p "URL: " REDIRECT_URL
    
    # Extract code from URL
    AUTH_CODE=$(echo "$REDIRECT_URL" | grep -oP 'code=\K[^&]+' || echo "")
    
    if [ -z "$AUTH_CODE" ]; then
        echo -e "${RED}Could not extract authorization code from URL${NC}"
        exit 1
    fi
    
    echo ""
    echo "Exchanging code for tokens..."
    
    TOKEN_RESPONSE=$(curl -s -X POST "https://login.microsoftonline.com/common/oauth2/v2.0/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&code=$AUTH_CODE&redirect_uri=$REDIRECT_URI&grant_type=authorization_code&scope=$SCOPES")
    
    if echo "$TOKEN_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
        echo "$TOKEN_RESPONSE" > "$CREDS_FILE"
        chmod 600 "$CREDS_FILE"
        echo -e "${GREEN}✓ Tokens saved to $CREDS_FILE${NC}"
    else
        echo -e "${RED}Failed to get tokens:${NC}"
        echo "$TOKEN_RESPONSE" | jq '.error_description // .'
        exit 1
    fi
}

# Step 7: Test Connection
test_connection() {
    echo ""
    echo -e "${YELLOW}Step 7: Testing Connection${NC}"
    
    ACCESS_TOKEN=$(jq -r '.access_token' "$CREDS_FILE")
    
    INBOX=$(curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    
    if echo "$INBOX" | jq -e '.totalItemCount' > /dev/null 2>&1; then
        TOTAL=$(echo "$INBOX" | jq '.totalItemCount')
        UNREAD=$(echo "$INBOX" | jq '.unreadItemCount')
        echo -e "${GREEN}✓ Connection successful!${NC}"
        echo ""
        echo -e "Inbox: ${BLUE}$TOTAL${NC} emails (${YELLOW}$UNREAD${NC} unread)"
    else
        echo -e "${RED}Connection test failed${NC}"
        echo "$INBOX" | jq '.error.message // .'
        exit 1
    fi
}

# Main
main() {
    check_prereqs
    azure_login
    create_app
    create_secret
    add_permissions
    save_config
    authorize
    test_connection
    
    echo ""
    echo -e "${GREEN}=== Setup Complete! ===${NC}"
    echo ""
    echo "You can now use:"
    echo "  outlook-mail.sh inbox       - List emails"
    echo "  outlook-mail.sh unread      - List unread"
    echo "  outlook-mail.sh search X    - Search emails"
    echo "  outlook-calendar.sh today   - Today's events"
    echo "  outlook-calendar.sh week    - This week's events"
    echo "  outlook-token.sh refresh    - Refresh token"
}

main "$@"
