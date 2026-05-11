# LinkedIn Routing Reference

**App name:** `linkedin`
**Base URL proxied:** `api.linkedin.com`

## API Path Pattern

```
/linkedin/v2/{resource}
```

## Required Headers

```
X-Restli-Protocol-Version: 2.0.0
```

## Common Endpoints

### Get User Info (OpenID Connect)
```bash
GET /linkedin/v2/userinfo
```

### Get Current User Profile
```bash
GET /linkedin/v2/me
```

With projection:
```bash
GET /linkedin/v2/me?projection=(id,firstName,lastName)
```

### Create Text Post
```bash
POST /linkedin/v2/ugcPosts
Content-Type: application/json
X-Restli-Protocol-Version: 2.0.0

{
  "author": "urn:li:person:{personId}",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {"text": "Hello LinkedIn!"},
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

### Create Article/URL Share
```bash
POST /linkedin/v2/ugcPosts
Content-Type: application/json
X-Restli-Protocol-Version: 2.0.0

{
  "author": "urn:li:person:{personId}",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {"text": "Check this out!"},
      "shareMediaCategory": "ARTICLE",
      "media": [{
        "status": "READY",
        "originalUrl": "https://example.com",
        "title": {"text": "Title"},
        "description": {"text": "Description"}
      }]
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

### Register Image Upload
```bash
POST /linkedin/v2/assets?action=registerUpload
Content-Type: application/json
X-Restli-Protocol-Version: 2.0.0

{
  "registerUploadRequest": {
    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
    "owner": "urn:li:person:{personId}",
    "serviceRelationships": [{
      "relationshipType": "OWNER",
      "identifier": "urn:li:userGeneratedContent"
    }]
  }
}
```

### Ad Library - Search Ads
```bash
GET /linkedin/rest/adLibrary?q=criteria&keyword=linkedin
```

Required headers:
- `LinkedIn-Version: 202502`

### Job Library - Search Jobs
```bash
GET /linkedin/rest/jobLibrary?q=criteria&keyword=software
```

Required headers:
- `LinkedIn-Version: 202506`

## Marketing API (Advertising)

Required headers for all Marketing API calls:
```
X-Restli-Protocol-Version: 2.0.0
LinkedIn-Version: 202502
```

### List Ad Accounts
```bash
GET /linkedin/rest/adAccounts?q=search
```

### Get Ad Account
```bash
GET /linkedin/rest/adAccounts/{adAccountId}
```

### Create Ad Account
```bash
POST /linkedin/rest/adAccounts
Content-Type: application/json

{
  "name": "Ad Account Name",
  "currency": "USD",
  "reference": "urn:li:organization:{orgId}",
  "type": "BUSINESS"
}
```

### List Campaign Groups
```bash
GET /linkedin/rest/adAccounts/{adAccountId}/adCampaignGroups
```

### Create Campaign Group
```bash
POST /linkedin/rest/adAccounts/{adAccountId}/adCampaignGroups
Content-Type: application/json

{
  "name": "Campaign Group Name",
  "status": "DRAFT"
}
```

### Get Campaign Group
```bash
GET /linkedin/rest/adAccounts/{adAccountId}/adCampaignGroups/{campaignGroupId}
```

### List Campaigns
```bash
GET /linkedin/rest/adAccounts/{adAccountId}/adCampaigns
```

### Create Campaign
```bash
POST /linkedin/rest/adAccounts/{adAccountId}/adCampaigns
Content-Type: application/json

{
  "campaignGroup": "urn:li:sponsoredCampaignGroup:{groupId}",
  "name": "Campaign Name",
  "status": "DRAFT",
  "objectiveType": "BRAND_AWARENESS"
}
```

### Get Campaign
```bash
GET /linkedin/rest/adAccounts/{adAccountId}/adCampaigns/{campaignId}
```

### List Organization ACLs
```bash
GET /linkedin/v2/organizationAcls?q=roleAssignee
```

### Lookup Organization by Vanity Name
```bash
GET /linkedin/rest/organizations?q=vanityName&vanityName=microsoft
```

### Get Organization Share Statistics
```bash
GET /linkedin/rest/organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity=urn:li:organization:12345
```

### Get Organization Posts
```bash
GET /linkedin/rest/posts?q=author&author=urn:li:organization:12345
```

## Media Upload (REST API)

Required headers:
- `LinkedIn-Version: 202502`

### Initialize Image Upload
```bash
POST /linkedin/rest/images?action=initializeUpload
Content-Type: application/json

{"initializeUploadRequest": {"owner": "urn:li:person:{personId}"}}
```

### Initialize Video Upload
```bash
POST /linkedin/rest/videos?action=initializeUpload
Content-Type: application/json

{"initializeUploadRequest": {"owner": "urn:li:person:{personId}", "fileSizeBytes": 10000000}}
```

### Initialize Document Upload
```bash
POST /linkedin/rest/documents?action=initializeUpload
Content-Type: application/json

{"initializeUploadRequest": {"owner": "urn:li:person:{personId}"}}
```

## Ad Targeting

### Get Targeting Facets
```bash
GET /linkedin/rest/adTargetingFacets
```

Returns 31 targeting facets (skills, industries, titles, locations, etc.)

## Notes

- Authentication is automatic - the router injects the OAuth token
- Include `X-Restli-Protocol-Version: 2.0.0` header for all v2 API calls
- Author URN format: `urn:li:person:{personId}`
- Get person ID from `/v2/me` endpoint
- Image uploads are 3-step: register, upload binary, create post
- Rate limits: 150 requests/day per member, 100K/day per app

## Visibility Options

- `PUBLIC` - Viewable by anyone
- `CONNECTIONS` - 1st-degree connections only

## Share Media Categories

- `NONE` - Text only
- `ARTICLE` - URL share
- `IMAGE` - Image post
- `VIDEO` - Video post

## Resources

- [LinkedIn API Overview](https://learn.microsoft.com/en-us/linkedin/)
- [Share on LinkedIn](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [Profile API](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-api)
- [Marketing API](https://learn.microsoft.com/en-us/linkedin/marketing/)
- [Ad Accounts](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts)
- [Campaigns](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns)
