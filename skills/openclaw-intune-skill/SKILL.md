---
name: Intune Graph API – Complete Management
description: "A comprehensive skill enabling OpenClaw agents to fully manage Microsoft Intune via the Graph API. Covers devices, apps, policies, compliance, users, groups, reporting, Autopilot, scripts, and remote actions."
version: "1.0.1"
author: "Mattia Cirillo"
homepage: "https://kaffeeundcode.com"
requires:
  env:
    - INTUNE_TENANT_ID
    - INTUNE_CLIENT_ID
    - INTUNE_CLIENT_SECRET
---

# Microsoft Intune – Complete Management Skill

This skill gives the agent **full control over Microsoft Intune** via the Microsoft Graph API. It covers device management, application deployment, compliance & configuration policies, user & group management, Autopilot, PowerShell scripts, reporting, and all remote device actions.

---

## 🔑 Authentication

Before ANY Intune operation, the agent MUST obtain an OAuth 2.0 access token.

The following environment variables must be configured:
- `INTUNE_TENANT_ID` – Microsoft 365 Tenant ID
- `INTUNE_CLIENT_ID` – Entra ID App Registration Client ID
- `INTUNE_CLIENT_SECRET` – Entra ID App Registration Secret

### Token Request
**POST** `https://login.microsoftonline.com/{INTUNE_TENANT_ID}/oauth2/v2.0/token`

**Body (x-www-form-urlencoded):**
```
client_id={INTUNE_CLIENT_ID}
&scope=https://graph.microsoft.com/.default
&client_secret={INTUNE_CLIENT_SECRET}
&grant_type=client_credentials
```

Extract `access_token` from the JSON response. Use it as:
```
Authorization: Bearer <access_token>
```

### Required API Permissions (App Registration)
The Entra ID App Registration needs the following Microsoft Graph **Application** permissions:
- `DeviceManagementManagedDevices.ReadWrite.All`
- `DeviceManagementConfiguration.ReadWrite.All`
- `DeviceManagementApps.ReadWrite.All`
- `DeviceManagementServiceConfig.ReadWrite.All`
- `DeviceManagementRBAC.ReadWrite.All`
- `Directory.Read.All`
- `User.Read.All`
- `Group.ReadWrite.All`
- `GroupMember.ReadWrite.All`

---

## 🛡️ Safety Rules (CRITICAL)

1. **Read operations (GET):** Always safe. Execute without confirmation.
2. **Sync/Restart operations:** Ask for confirmation: *"Soll ich Gerät X wirklich syncen/neustarten?"*
3. **Destructive operations (Wipe, Retire, Delete):** ALWAYS require explicit confirmation. Say: *"⚠️ Achtung: Das löscht alle Daten auf dem Gerät. Bist du sicher?"*
4. **Policy creation/modification:** Confirm before applying: *"Soll ich diese Policy wirklich erstellen/ändern?"*
5. **Never dump raw JSON** to the user. Always format output as readable Markdown tables or summaries.
6. **Error handling:** If an API call returns an error, explain the error in simple German and suggest a fix.

---

## 📱 1. Device Management

### 1.1 List All Managed Devices
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices`

Use `$select` to limit fields: `?$select=deviceName,operatingSystem,complianceState,lastSyncDateTime,userPrincipalName`

Present results as a table: | Gerätename | OS | Compliance | Letzter Sync | Benutzer |

### 1.2 Search for a Specific Device
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$filter=deviceName eq '{deviceName}'`

Alternative search by user: `?$filter=userPrincipalName eq '{user@domain.com}'`

### 1.3 Get Device Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}`

Show: Device name, Serial number, OS version, Compliance state, Encryption status, Last sync, Enrolled date, Primary user.

### 1.4 Remote Actions on a Device

#### Sync Device
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/syncDevice`

#### Reboot Device
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/rebootNow`

#### Lock Device (Remote Lock)
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/remoteLock`

#### Reset Passcode
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/resetPasscode`

#### Locate Device (Lost Mode – iOS/Android)
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/locateDevice`

#### Retire Device (Remove Company Data Only)
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/retire`
⚠️ SAFETY: Requires explicit user confirmation!

#### Wipe Device (Factory Reset)
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/wipe`
⚠️ SAFETY: ALWAYS ask twice! This deletes ALL data!

#### Delete Device from Intune
**DELETE** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}`
⚠️ SAFETY: Requires explicit user confirmation!

#### Rename Device
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/setDeviceName`
Body: `{"deviceName": "NEW-NAME"}`

#### Enable/Disable Lost Mode (iOS supervised)
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/enableLostMode`
Body: `{"message": "Dieses Gerät wurde als verloren gemeldet.", "phoneNumber": "+49...", "footer": "Kaffee & Code IT"}`

**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/disableLostMode`

---

## 📋 2. Compliance Policies

### 2.1 List All Compliance Policies
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceCompliancePolicies`

Present as: | Policy Name | Platform | Created | Last Modified |

### 2.2 Get Compliance Policy Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceCompliancePolicies/{policyId}`

### 2.3 Get Compliance Policy Assignments
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceCompliancePolicies/{policyId}/assignments`

### 2.4 Get Device Compliance Status per Policy
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceCompliancePolicies/{policyId}/deviceStatuses`

### 2.5 Create a Compliance Policy
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/deviceCompliancePolicies`
⚠️ SAFETY: Confirm before creating.

### 2.6 Delete a Compliance Policy
**DELETE** `https://graph.microsoft.com/v1.0/deviceManagement/deviceCompliancePolicies/{policyId}`
⚠️ SAFETY: Requires explicit user confirmation!

---

## ⚙️ 3. Configuration Policies & Profiles

### 3.1 List Configuration Policies (Recommended API)
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/configurationPolicies`

This is the modern, recommended endpoint covering Endpoint Security, Administrative Templates, and Settings Catalog.

### 3.2 List Legacy Device Configuration Profiles
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations`

### 3.3 Get Configuration Policy Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/configurationPolicies/{policyId}`

### 3.4 Get Policy Settings
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/configurationPolicies/{policyId}/settings`

### 3.5 Get Policy Assignments
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/configurationPolicies/{policyId}/assignments`

### 3.6 Get Device Status per Config Profile
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations/{configId}/deviceStatuses`

### 3.7 Create Configuration Policy
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/configurationPolicies`
⚠️ SAFETY: Confirm before creating.

### 3.8 Delete Configuration Policy
**DELETE** `https://graph.microsoft.com/v1.0/deviceManagement/configurationPolicies/{policyId}`
⚠️ SAFETY: Requires explicit user confirmation!

---

## 📦 4. App Management

### 4.1 List All Apps
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/mobileApps`

Present as: | App Name | Type | Publisher | Created |

### 4.2 Get App Details
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/mobileApps/{appId}`

### 4.3 Get App Assignments (Who gets the app?)
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/mobileApps/{appId}/assignments`

### 4.4 List App Configuration Policies
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/managedAppPolicies`

### 4.5 List App Protection Policies (MAM)
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/managedAppRegistrations`

### 4.6 Assign App to a Group
**POST** `https://graph.microsoft.com/v1.0/deviceAppManagement/mobileApps/{appId}/assignments`
⚠️ SAFETY: Confirm before assigning.

### 4.7 List Detected Apps on Devices
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/detectedApps`

### 4.8 Get Devices with a Specific Detected App
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/detectedApps/{detectedAppId}/managedDevices`

---

## 🔒 5. Endpoint Security

### 5.1 List Security Baselines
**GET** `https://graph.microsoft.com/beta/deviceManagement/configurationPolicies?$filter=templateReference/templateFamily eq 'baseline'`

### 5.2 List Disk Encryption Policies (BitLocker/FileVault)
**GET** `https://graph.microsoft.com/beta/deviceManagement/configurationPolicies?$filter=templateReference/templateFamily eq 'endpointSecurityDiskEncryption'`

### 5.3 List Firewall Policies
**GET** `https://graph.microsoft.com/beta/deviceManagement/configurationPolicies?$filter=templateReference/templateFamily eq 'endpointSecurityFirewall'`

### 5.4 List Antivirus Policies (Defender)
**GET** `https://graph.microsoft.com/beta/deviceManagement/configurationPolicies?$filter=templateReference/templateFamily eq 'endpointSecurityAntivirus'`

### 5.5 List Attack Surface Reduction Rules
**GET** `https://graph.microsoft.com/beta/deviceManagement/configurationPolicies?$filter=templateReference/templateFamily eq 'endpointSecurityAttackSurfaceReduction'`

---

## 🚀 6. Windows Autopilot

### 6.1 List Autopilot Devices
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/windowsAutopilotDeviceIdentities`

Present as: | Serial Number | Model | Group Tag | Enrollment State | Last Seen |

### 6.2 Get Autopilot Device Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/windowsAutopilotDeviceIdentities/{id}`

### 6.3 List Autopilot Deployment Profiles
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/windowsAutopilotDeploymentProfiles`

### 6.4 Assign Autopilot Profile
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/windowsAutopilotDeviceIdentities/{id}/assignUserToDevice`
Body: `{"userPrincipalName": "user@domain.com"}`

### 6.5 Delete Autopilot Device
**DELETE** `https://graph.microsoft.com/v1.0/deviceManagement/windowsAutopilotDeviceIdentities/{id}`
⚠️ SAFETY: Requires explicit user confirmation!

---

## 📜 7. PowerShell Scripts & Remediation

### 7.1 List Device Management Scripts
**GET** `https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts`

### 7.2 Get Script Details
**GET** `https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts/{scriptId}`

### 7.3 Get Script Execution Status per Device
**GET** `https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts/{scriptId}/deviceRunStates`

### 7.4 Create/Upload a PowerShell Script
**POST** `https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts`
Body must include `scriptContent` as Base64-encoded string.
⚠️ SAFETY: Confirm before uploading. Show the script content to the user first.

### 7.5 List Proactive Remediations (Health Scripts)
**GET** `https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts`

### 7.6 Get Remediation Script Execution Results
**GET** `https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts/{scriptId}/deviceRunStates`

---

## 👥 8. Users & Groups

### 8.1 List Users
**GET** `https://graph.microsoft.com/v1.0/users?$select=displayName,userPrincipalName,accountEnabled,jobTitle`

### 8.2 Search User
**GET** `https://graph.microsoft.com/v1.0/users?$filter=startsWith(displayName,'{name}')`

### 8.3 Get User Details
**GET** `https://graph.microsoft.com/v1.0/users/{userId}`

### 8.4 List Groups
**GET** `https://graph.microsoft.com/v1.0/groups?$select=displayName,description,groupTypes,membershipRule`

### 8.5 Get Group Members
**GET** `https://graph.microsoft.com/v1.0/groups/{groupId}/members`

### 8.6 Add User to Group
**POST** `https://graph.microsoft.com/v1.0/groups/{groupId}/members/$ref`
Body: `{"@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/{userId}"}`
⚠️ SAFETY: Confirm before adding.

### 8.7 Remove User from Group
**DELETE** `https://graph.microsoft.com/v1.0/groups/{groupId}/members/{userId}/$ref`
⚠️ SAFETY: Confirm before removing.

### 8.8 List Devices for a User
**GET** `https://graph.microsoft.com/v1.0/users/{userId}/managedDevices`

---

## 📊 9. Reporting & Dashboards

### 9.1 Device Compliance Summary
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$select=complianceState`
Agent should calculate: X compliant, Y non-compliant, Z in-grace-period, and present as summary + table.

### 9.2 OS Distribution Summary
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$select=operatingSystem`
Agent should group by OS and present: "42 Windows, 15 iOS, 8 Android, 3 macOS"

### 9.3 Stale Devices (Not synced recently)
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$filter=lastSyncDateTime lt {30_days_ago}&$select=deviceName,lastSyncDateTime,userPrincipalName`
Agent should calculate the date for 30 days ago automatically.

### 9.4 Non-Compliant Devices Report
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$filter=complianceState eq 'noncompliant'&$select=deviceName,complianceState,userPrincipalName,operatingSystem`

### 9.5 Export Report Job
**POST** `https://graph.microsoft.com/beta/deviceManagement/reports/exportJobs`
Body: `{"reportName": "Devices", "filter": "", "select": ["DeviceName","OS","ComplianceState"]}`

---

## 🏷️ 10. Device Categories & Enrollment

### 10.1 List Device Categories
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceCategories`

### 10.2 Create Device Category
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/deviceCategories`
Body: `{"displayName": "Kategoriename", "description": "Beschreibung"}`

### 10.3 Set Device Category on a Device
**PUT** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{deviceId}/deviceCategory/$ref`

### 10.4 List Enrollment Restrictions
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceEnrollmentConfigurations`

---

## 🔄 11. RBAC (Role-Based Access Control)

### 11.1 List Intune Roles
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/roleDefinitions`

### 11.2 List Role Assignments
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/roleAssignments`

### 11.3 Get Role Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/roleDefinitions/{roleId}`

---

## 💡 Agent Response Guidelines

When the user asks a question, follow this logic:
1. **"Zeig mir alle Geräte"** → Use 1.1, format as table.
2. **"Ist Gerät X compliant?"** → Use 1.2 to find it, then check `complianceState`.
3. **"Sync Laptop von Max"** → Use 1.2 to find `managedDeviceId`, then use 1.4 Sync.
4. **"Wie viele Geräte hab ich?"** → Use 9.2, give OS distribution + total count.
5. **"Welche Geräte haben sich lange nicht gemeldet?"** → Use 9.3.
6. **"Erstell mir eine Compliance Policy für Windows"** → Use 2.5, ask for requirements first.
7. **"Welche Apps sind deployed?"** → Use 4.1.
8. **"Füg User Max zur Gruppe IT-Geräte hinzu"** → Use 8.2 to find user, 8.4 to find group, then 8.6.
9. **"Zeig mir den Status vom PowerShell Script XY"** → Use 7.3.
10. **"Gib mir einen Compliance Report"** → Use 9.1 + 9.4.
11. **"Zeig mir die Conditional Access Policies"** → Use 12.1.
12. **"Welche WLAN-Profile sind deployed?"** → Use 13.1.
13. **"Wie sind meine Windows Update Ringe konfiguriert?"** → Use 14.1.
14. **"Wer hat letzte Woche was in Intune geändert?"** → Use 17.1.
15. **"Kann Intune die Einstellung XY konfigurieren?"** → Use 18.1 Settings Catalog search.
16. **"Zeig mir alle Autopilot-Geräte ohne zugewiesenes Profil"** → Use 6.1 + filter.

---

## 🛡️ 12. Conditional Access (Bedingter Zugriff)

### 12.1 List Conditional Access Policies
**GET** `https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies`

Present as: | Policy Name | State (enabled/disabled/report) | Conditions | Grant Controls |

### 12.2 Get Conditional Access Policy Details
**GET** `https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policyId}`

### 12.3 Create Conditional Access Policy
**POST** `https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies`
⚠️ SAFETY: Always confirm before creating. Show the user a summary of what the policy will do first.
💡 TIP: Recommend creating in "reportOnly" state first for testing.

### 12.4 Update Conditional Access Policy
**PATCH** `https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policyId}`
⚠️ SAFETY: Confirm before modifying. Explain what will change.

### 12.5 Delete Conditional Access Policy
**DELETE** `https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policyId}`
⚠️ SAFETY: Requires explicit user confirmation!

### 12.6 List Named Locations (Trusted IPs / Countries)
**GET** `https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations`

### 12.7 Create Named Location
**POST** `https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations`
Example IP-based:
```json
{
  "@odata.type": "#microsoft.graph.ipNamedLocation",
  "displayName": "Büro-Netzwerk",
  "isTrusted": true,
  "ipRanges": [{"@odata.type": "#microsoft.graph.iPv4CidrRange", "cidrAddress": "192.168.1.0/24"}]
}
```

### 12.8 List Authentication Strengths
**GET** `https://graph.microsoft.com/v1.0/identity/conditionalAccess/authenticationStrength/policies`

---

## 📶 13. WLAN, VPN & Zertifikate

### 13.1 List WLAN Profiles
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations?$filter=isof('microsoft.graph.windowsWifiConfiguration') or isof('microsoft.graph.iosWiFiConfiguration') or isof('microsoft.graph.androidWorkProfileWiFiConfiguration')`

Alternative (all configs, then filter by odata.type for Wi-Fi):
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations`
Agent should filter results where `@odata.type` contains `WiFi` or `wifi`.

### 13.2 List VPN Profiles
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations`
Agent should filter results where `@odata.type` contains `Vpn` or `vpn`.

### 13.3 Get WLAN/VPN Profile Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations/{configId}`

### 13.4 Get WLAN/VPN Profile Assignment
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations/{configId}/assignments`

### 13.5 List SCEP Certificate Profiles
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations`
Agent should filter results where `@odata.type` contains `Scep` or `Certificate`.

### 13.6 List PKCS Certificate Profiles
Same endpoint, filter for `Pkcs` in `@odata.type`.

### 13.7 List Trusted Root Certificate Profiles
Same endpoint, filter for `TrustedRootCertificate` in `@odata.type`.

---

## 🔄 14. Windows Update Management

### 14.1 List Windows Update Rings
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations?$filter=isof('microsoft.graph.windowsUpdateForBusinessConfiguration')`

Present as: | Ring Name | Deferral (Days) | Quality Updates | Feature Updates | Assigned To |

### 14.2 Get Update Ring Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations/{ringId}`

### 14.3 List Feature Update Profiles
**GET** `https://graph.microsoft.com/beta/deviceManagement/windowsFeatureUpdateProfiles`

### 14.4 Get Feature Update Profile Details
**GET** `https://graph.microsoft.com/beta/deviceManagement/windowsFeatureUpdateProfiles/{profileId}`

### 14.5 Get Feature Update Deployment State per Device
**GET** `https://graph.microsoft.com/beta/deviceManagement/windowsFeatureUpdateProfiles/{profileId}/deviceUpdateStates`

### 14.6 List Driver Update Profiles
**GET** `https://graph.microsoft.com/beta/deviceManagement/windowsDriverUpdateProfiles`

### 14.7 Get Driver Update Profile Details
**GET** `https://graph.microsoft.com/beta/deviceManagement/windowsDriverUpdateProfiles/{profileId}`

### 14.8 List Quality Update Profiles (Expedited Updates)
**GET** `https://graph.microsoft.com/beta/deviceManagement/windowsQualityUpdateProfiles`

### 14.9 Pause/Resume an Update Ring
**POST** `https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations/{ringId}/windowsUpdateForBusinessConfiguration/pause`
**POST** `https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations/{ringId}/windowsUpdateForBusinessConfiguration/resume`
⚠️ SAFETY: Confirm before pausing/resuming.

---

## 🍎 15. Apple Device Management

### 15.1 List Apple DEP/ADE Enrollment Profiles
**GET** `https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings`

### 15.2 List Apple DEP Tokens
**GET** `https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings/{depId}/enrollmentProfiles`

### 15.3 List Apple Push Notification Certificate Info
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/applePushNotificationCertificate`

Shows: Expiration date, Subject, Certificate serial number.
💡 Agent should proactively warn if certificate expires within 30 days!

### 15.4 List VPP Tokens (Volume Purchase Program)
**GET** `https://graph.microsoft.com/beta/deviceManagement/vppTokens`

### 15.5 List iOS/macOS Managed App Configurations
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/managedAppPolicies`
Filter for iOS/macOS types.

### 15.6 Activation Lock Bypass (iOS Supervised)
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{managedDeviceId}/bypassActivationLock`
⚠️ SAFETY: Requires explicit user confirmation!

---

## 🤖 16. Android Enterprise Management

### 16.1 List Android Managed Store Apps
**GET** `https://graph.microsoft.com/beta/deviceManagement/androidManagedStoreAccountEnterpriseSettings`

### 16.2 List Android Enrollment Profiles
**GET** `https://graph.microsoft.com/beta/deviceManagement/androidDeviceOwnerEnrollmentProfiles`

### 16.3 Get Android Enterprise Binding Status
**GET** `https://graph.microsoft.com/beta/deviceManagement/androidManagedStoreAccountEnterpriseSettings`

Shows if Android Enterprise (Work Profile / Fully Managed / Dedicated) is connected.

### 16.4 List Android App Protection Policies
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/androidManagedAppProtections`

---

## 📝 17. Audit Logs & Activity

### 17.1 List Intune Audit Events
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/auditEvents`

Present as: | Date | Activity | Actor (who) | Target | Result |

### 17.2 Filter Audit Events by Date Range
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/auditEvents?$filter=activityDateTime gt {startDate} and activityDateTime lt {endDate}`

Agent should calculate the date range based on user request (e.g., "letzte Woche" → last 7 days).

### 17.3 Filter Audit Events by User
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/auditEvents?$filter=actor/userPrincipalName eq '{user@domain.com}'`

### 17.4 Get Audit Event Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/auditEvents/{auditEventId}`

### 17.5 List Directory Audit Logs (Entra ID level)
**GET** `https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$filter=category eq 'Device'`

### 17.6 List Sign-In Logs
**GET** `https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=appDisplayName eq 'Microsoft Intune'`

---

## 🏗️ 18. Settings Catalog & GPO Analytics

### 18.1 Search Settings Catalog
**GET** `https://graph.microsoft.com/beta/deviceManagement/configurationSettings?$search="{searchTerm}"`

This is extremely useful when the user asks: "Can Intune configure setting X?" or "Hat Intune eine Einstellung für Bildschirmschoner?"

### 18.2 List Group Policy Migration Reports
**GET** `https://graph.microsoft.com/beta/deviceManagement/groupPolicyMigrationReports`

Use this when the user asks about migrating from on-premises GPO to Intune.

### 18.3 Get Migration Report Details
**GET** `https://graph.microsoft.com/beta/deviceManagement/groupPolicyMigrationReports/{reportId}`

Shows: Which GPO settings are supported in Intune, which are not, and recommended alternatives.

### 18.4 List Group Policy Uploaded Definition Files
**GET** `https://graph.microsoft.com/beta/deviceManagement/groupPolicyUploadedDefinitionFiles`

---

## 📄 19. Terms & Conditions and Notifications

### 19.1 List Terms & Conditions
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/termsAndConditions`

### 19.2 Get Terms & Conditions Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/termsAndConditions/{termsId}`

### 19.3 Get Terms Acceptance Status
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/termsAndConditions/{termsId}/acceptanceStatuses`

Shows which users have accepted which version.

### 19.4 Create Terms & Conditions
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/termsAndConditions`
⚠️ SAFETY: Confirm before creating.

### 19.5 List Notification Message Templates
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/notificationMessageTemplates`

### 19.6 Create Notification Template (Non-Compliance Email)
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/notificationMessageTemplates`
⚠️ SAFETY: Confirm before creating.

### 19.7 Send Test Notification
**POST** `https://graph.microsoft.com/v1.0/deviceManagement/notificationMessageTemplates/{templateId}/sendTestMessage`

---

## 🔐 20. App Protection Policies (MAM)

### 20.1 List iOS App Protection Policies
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/iosManagedAppProtections`

### 20.2 List Android App Protection Policies
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/androidManagedAppProtections`

### 20.3 List Windows Information Protection Policies
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/windowsInformationProtectionPolicies`

### 20.4 Get App Protection Policy Details
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/iosManagedAppProtections/{policyId}`
or
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/androidManagedAppProtections/{policyId}`

### 20.5 Get App Protection Status per User
**GET** `https://graph.microsoft.com/v1.0/deviceAppManagement/managedAppRegistrations?$filter=userId eq '{userId}'`

### 20.6 Create App Protection Policy
**POST** `https://graph.microsoft.com/v1.0/deviceAppManagement/iosManagedAppProtections`
or
**POST** `https://graph.microsoft.com/v1.0/deviceAppManagement/androidManagedAppProtections`
⚠️ SAFETY: Confirm before creating. Show policy summary first.

---

## 📱 21. Enrollment Configuration

### 21.1 List All Enrollment Configurations
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceEnrollmentConfigurations`

Includes: Device Limit Restrictions, Platform Restrictions, Enrollment Status Page (ESP), Windows Hello for Business.

### 21.2 Get Enrollment Configuration Details
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceEnrollmentConfigurations/{configId}`

### 21.3 Get Enrollment Configuration Assignments
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceEnrollmentConfigurations/{configId}/assignments`

### 21.4 List Enrollment Status Page (ESP) Profiles
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceEnrollmentConfigurations?$filter=isof('microsoft.graph.windows10EnrollmentCompletionPageConfiguration')`

### 21.5 List Windows Hello for Business Configurations
**GET** `https://graph.microsoft.com/v1.0/deviceManagement/deviceEnrollmentConfigurations?$filter=isof('microsoft.graph.deviceEnrollmentWindowsHelloForBusinessConfiguration')`

---

## 🧮 22. Filters & Scope Tags

### 22.1 List Assignment Filters
**GET** `https://graph.microsoft.com/beta/deviceManagement/assignmentFilters`

Present as: | Filter Name | Platform | Rule | Created |

### 22.2 Get Filter Details
**GET** `https://graph.microsoft.com/beta/deviceManagement/assignmentFilters/{filterId}`

### 22.3 Create Assignment Filter
**POST** `https://graph.microsoft.com/beta/deviceManagement/assignmentFilters`
⚠️ SAFETY: Confirm before creating.

### 22.4 Test/Preview Filter Results
**POST** `https://graph.microsoft.com/beta/deviceManagement/assignmentFilters/{filterId}/getState`

### 22.5 List Scope Tags
**GET** `https://graph.microsoft.com/beta/deviceManagement/roleScopeTags`

### 22.6 Create Scope Tag
**POST** `https://graph.microsoft.com/beta/deviceManagement/roleScopeTags`
⚠️ SAFETY: Confirm before creating.
