---
name: fastlane
emoji: "\U0001F680"
requires: fastlane
install: brew install fastlane
description: iOS/macOS app automation — builds, signing, TestFlight, App Store via CLI
---

# Fastlane

Automate iOS and macOS builds, code signing, TestFlight distribution, and App Store submissions — all from one-off CLI commands. No Fastfile required.

---

## Verify Installation

```bash
fastlane --version
```

If not installed:

```bash
brew install fastlane
```

Or via RubyGems:

```bash
sudo gem install fastlane -NV
```

After install, add to your shell profile:

```bash
export PATH="$HOME/.fastlane/bin:$PATH"
```

---

## Authentication

### App Store Connect API Key (Preferred)

API keys avoid 2FA prompts and are the recommended approach for automation and CI.

1. Generate a key at [App Store Connect → Users and Access → Keys](https://appstoreconnect.apple.com/access/api).
2. Download the `.p8` file.
3. Set environment variables:

```bash
export APP_STORE_CONNECT_API_KEY_KEY_ID="XXXXXXXXXX"
export APP_STORE_CONNECT_API_KEY_ISSUER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export APP_STORE_CONNECT_API_KEY_KEY_FILEPATH="/path/to/AuthKey_XXXXXXXXXX.p8"
```

Or pass the key inline as JSON:

```bash
export APP_STORE_CONNECT_API_KEY_KEY='{"key_id":"XXXXXXXXXX","issuer_id":"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx","key_filepath":"/path/to/AuthKey.p8"}'
```

> **Agent guidance:** Always prefer API key authentication. Only fall back to Apple ID when the user explicitly does not have API key access.

### Apple ID Fallback

```bash
export FASTLANE_USER="user@example.com"
export FASTLANE_PASSWORD="app-specific-password"
```

Generate an app-specific password at [appleid.apple.com](https://appleid.apple.com). If 2FA is enabled, you may also need:

```bash
export FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export SPACESHIP_2FA_SMS_DEFAULT_PHONE_NUMBER="+1 (xxx) xxx-xxxx"
```

### Environment Variables — Authentication Reference

| Variable | Purpose |
|---|---|
| `APP_STORE_CONNECT_API_KEY_KEY_ID` | API key ID from App Store Connect |
| `APP_STORE_CONNECT_API_KEY_ISSUER_ID` | Issuer ID from App Store Connect |
| `APP_STORE_CONNECT_API_KEY_KEY_FILEPATH` | Path to the `.p8` private key file |
| `APP_STORE_CONNECT_API_KEY_KEY` | Inline JSON containing all key fields |
| `FASTLANE_USER` | Apple ID email |
| `FASTLANE_PASSWORD` | Apple ID password or app-specific password |
| `FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD` | App-specific password for 2FA accounts |
| `MATCH_PASSWORD` | Encryption password for match certificates repo |
| `MATCH_GIT_URL` | Git URL for match certificates repository |

---

## One-Off Action Execution

Fastlane actions can be run directly from the CLI without a Fastfile:

```bash
fastlane run <action_name> key:value key2:value2
```

Discover available actions:

```bash
fastlane actions                    # List all actions
fastlane action <action_name>      # Show details for one action
fastlane search_actions <query>    # Search by keyword
```

> **Agent guidance:** Use `fastlane run <action>` for one-off tasks. This is the core pattern — every section below shows both the shorthand tool command and the `fastlane run` equivalent.

---

## pilot (TestFlight)

### Upload a Build to TestFlight

```bash
fastlane pilot upload --ipa "/path/to/App.ipa"
```

Equivalent:

```bash
fastlane run upload_to_testflight ipa:"/path/to/App.ipa"
```

With API key:

```bash
fastlane pilot upload \
  --ipa "/path/to/App.ipa" \
  --api_key_path "/path/to/api_key.json"
```

### List Builds

```bash
fastlane pilot builds
```

### Manage Testers

```bash
# Add a tester
fastlane pilot add email:"tester@example.com" group_name:"Beta Testers"

# Remove a tester
fastlane pilot remove email:"tester@example.com"

# List testers
fastlane pilot list
```

### Distribute to External Testers

```bash
fastlane pilot distribute \
  --build_number "42" \
  --groups "External Beta" \
  --changelog "Bug fixes and performance improvements"
```

### Common pilot Flags

| Flag | Purpose |
|---|---|
| `--ipa` | Path to IPA file |
| `--app_identifier` | Bundle ID (e.g., `com.example.app`) |
| `--skip_waiting_for_build_processing` | Don't wait for Apple's processing |
| `--distribute_external` | Send to external testers |
| `--groups` | Tester group names (comma-separated) |
| `--changelog` | What to Test text |
| `--beta_app_review_info` | JSON with review info |

---

## deliver (App Store)

### Submit to App Store

```bash
fastlane deliver --ipa "/path/to/App.ipa" --submit_for_review
```

Equivalent:

```bash
fastlane run upload_to_app_store ipa:"/path/to/App.ipa" submit_for_review:true
```

### Upload Metadata Only

```bash
fastlane deliver --skip_binary_upload --skip_screenshots
```

### Upload Screenshots Only

```bash
fastlane deliver --skip_binary_upload --skip_metadata
```

### Download Existing Metadata

```bash
fastlane deliver download_metadata --app_identifier "com.example.app"
```

### Download Existing Screenshots

```bash
fastlane deliver download_screenshots --app_identifier "com.example.app"
```

### Common deliver Flags

| Flag | Purpose |
|---|---|
| `--ipa` | Path to IPA file |
| `--pkg` | Path to PKG file (macOS) |
| `--app_identifier` | Bundle ID |
| `--submit_for_review` | Auto-submit after upload |
| `--automatic_release` | Release automatically after approval |
| `--force` | Skip HTML preview verification |
| `--skip_binary_upload` | Metadata/screenshots only |
| `--skip_metadata` | Binary/screenshots only |
| `--skip_screenshots` | Binary/metadata only |
| `--metadata_path` | Custom metadata folder path |
| `--screenshots_path` | Custom screenshots folder path |
| `--phased_release` | Enable phased release |
| `--reject_if_possible` | Reject current version before uploading |

---

## gym / build_app (Build)

### Build an IPA

```bash
fastlane gym \
  --workspace "App.xcworkspace" \
  --scheme "App" \
  --export_method "app-store" \
  --output_directory "./build"
```

Equivalent:

```bash
fastlane run build_app \
  workspace:"App.xcworkspace" \
  scheme:"App" \
  export_method:"app-store" \
  output_directory:"./build"
```

### Build with Xcode Project (no workspace)

```bash
fastlane gym \
  --project "App.xcodeproj" \
  --scheme "App" \
  --export_method "app-store"
```

### Export Methods

| Method | Use Case |
|---|---|
| `app-store` | App Store and TestFlight submission |
| `ad-hoc` | Direct device installation via profile |
| `development` | Debug builds for registered devices |
| `enterprise` | In-house enterprise distribution |
| `developer-id` | macOS distribution outside App Store |
| `mac-application` | macOS App Store |
| `validation` | Validate without exporting |

### Common gym Flags

| Flag | Purpose |
|---|---|
| `--workspace` | Path to `.xcworkspace` |
| `--project` | Path to `.xcodeproj` |
| `--scheme` | Build scheme |
| `--configuration` | Build config (Debug/Release) |
| `--export_method` | See export methods table |
| `--output_directory` | Where to save the IPA |
| `--output_name` | Custom IPA filename |
| `--clean` | Clean before building |
| `--include_bitcode` | Include bitcode |
| `--include_symbols` | Include dSYM symbols |
| `--xcargs` | Extra xcodebuild arguments |
| `--derived_data_path` | Custom DerivedData path |
| `--catalyst_platform` | `macos` or `ios` for Catalyst apps |

> **Agent guidance:** If the project has a `.xcworkspace` (e.g., uses CocoaPods or SPM), always use `--workspace`. Only use `--project` when there is no workspace.

---

## match (Code Signing)

Sync certificates and provisioning profiles from a shared Git repo or cloud storage.

### Sync for App Store

```bash
fastlane match appstore --app_identifier "com.example.app"
```

Equivalent:

```bash
fastlane run sync_code_signing type:"appstore" app_identifier:"com.example.app"
```

### Sync for Development

```bash
fastlane match development --app_identifier "com.example.app"
```

### Sync for Ad Hoc

```bash
fastlane match adhoc --app_identifier "com.example.app"
```

### Read-Only Mode (CI)

```bash
fastlane match appstore --readonly --app_identifier "com.example.app"
```

> **Agent guidance:** Always use `--readonly` on CI servers. This prevents accidentally creating new certificates and disrupting the team.

### Nuke (Reset All Certificates)

```bash
# Remove all certificates and profiles for a type
fastlane match nuke appstore
fastlane match nuke development
```

> **Warning:** Nuke is destructive and irreversible. Always confirm with the user before running nuke commands.

### Common match Flags

| Flag | Purpose |
|---|---|
| `--type` | `appstore`, `development`, `adhoc`, `enterprise` |
| `--app_identifier` | Bundle ID(s), comma-separated for multiple |
| `--git_url` | Git repo URL for certificates |
| `--readonly` | Don't create new certs/profiles |
| `--force` | Renew existing profile |
| `--team_id` | Apple Developer team ID |
| `--storage_mode` | `git`, `google_cloud`, `s3` |
| `--verbose` | Detailed output |

> **Agent guidance:** Prefer `match` over `cert + sigh` for teams. It centralizes signing and avoids the "works on my machine" problem.

---

## scan / run_tests (Testing)

### Run Tests

```bash
fastlane scan \
  --workspace "App.xcworkspace" \
  --scheme "AppTests" \
  --device "iPhone 16 Pro"
```

Equivalent:

```bash
fastlane run run_tests \
  workspace:"App.xcworkspace" \
  scheme:"AppTests" \
  device:"iPhone 16 Pro"
```

### Run on Multiple Devices

```bash
fastlane scan \
  --workspace "App.xcworkspace" \
  --scheme "AppTests" \
  --devices "iPhone 16 Pro,iPad Pro (13-inch) (M4)"
```

### Output Formats

```bash
fastlane scan \
  --scheme "AppTests" \
  --output_types "html,junit" \
  --output_directory "./test_results"
```

### Common scan Flags

| Flag | Purpose |
|---|---|
| `--workspace` | Path to `.xcworkspace` |
| `--project` | Path to `.xcodeproj` |
| `--scheme` | Test scheme |
| `--device` | Simulator device name |
| `--devices` | Multiple simulators (comma-separated) |
| `--output_types` | `html`, `junit`, `json` |
| `--output_directory` | Where to save results |
| `--code_coverage` | Enable code coverage |
| `--clean` | Clean before testing |
| `--fail_build` | Fail on test failures (default: true) |
| `--xcargs` | Extra xcodebuild arguments |
| `--result_bundle` | Generate Xcode result bundle |

---

## snapshot (Screenshots)

Capture App Store screenshots across devices and languages automatically.

### Capture Screenshots

```bash
fastlane snapshot \
  --workspace "App.xcworkspace" \
  --scheme "AppUITests" \
  --devices "iPhone 16 Pro Max,iPhone SE (3rd generation),iPad Pro (13-inch) (M4)" \
  --languages "en-US,es-ES,fr-FR" \
  --output_directory "./screenshots"
```

Equivalent:

```bash
fastlane run capture_screenshots \
  workspace:"App.xcworkspace" \
  scheme:"AppUITests" \
  devices:"iPhone 16 Pro Max,iPhone SE (3rd generation),iPad Pro (13-inch) (M4)" \
  languages:"en-US,es-ES,fr-FR" \
  output_directory:"./screenshots"
```

### Common snapshot Flags

| Flag | Purpose |
|---|---|
| `--workspace` | Path to `.xcworkspace` |
| `--scheme` | UI test scheme with snapshot calls |
| `--devices` | Simulator names (comma-separated) |
| `--languages` | Locale codes (comma-separated) |
| `--output_directory` | Where to save screenshots |
| `--clear_previous_screenshots` | Clean output folder first |
| `--stop_after_first_error` | Abort on first failure |
| `--override_status_bar` | Clean status bar (9:41, full battery) |

---

## cert + sigh (Certificates & Profiles)

Standalone certificate and provisioning profile management.

### Create/Fetch a Certificate

```bash
fastlane cert --development
fastlane cert  # Distribution certificate by default
```

Equivalent:

```bash
fastlane run get_certificates development:true
```

### Create/Fetch a Provisioning Profile

```bash
# App Store profile
fastlane sigh --app_identifier "com.example.app"

# Development profile
fastlane sigh --development --app_identifier "com.example.app"

# Ad hoc profile
fastlane sigh --adhoc --app_identifier "com.example.app"
```

Equivalent:

```bash
fastlane run get_provisioning_profile app_identifier:"com.example.app"
```

### Repair Profiles

```bash
fastlane sigh repair
```

### Common Flags

| Flag | Purpose |
|---|---|
| `--development` | Development cert/profile |
| `--adhoc` | Ad hoc profile |
| `--app_identifier` | Bundle ID |
| `--team_id` | Developer team ID |
| `--output_path` | Where to save profile |
| `--force` | Renew even if current is valid |
| `--readonly` | Don't create, only fetch |

> **Agent guidance:** For individual developers, `cert + sigh` works fine. For teams, recommend `match` instead — it prevents certificate conflicts.

---

## precheck (Validation)

Validate app metadata before submitting to avoid App Store Review rejections.

```bash
fastlane precheck --app_identifier "com.example.app"
```

Equivalent:

```bash
fastlane run check_app_store_metadata app_identifier:"com.example.app"
```

### What precheck Validates

- Unreachable URLs in metadata
- Mentions of other platforms (Android, etc.)
- Profanity or inappropriate content
- Placeholder text
- Copyright date accuracy

---

## pem (Push Notification Certificates)

Generate push notification certificates for APNs.

```bash
fastlane pem --app_identifier "com.example.app" --output_path "./certs"
```

Equivalent:

```bash
fastlane run get_push_certificate app_identifier:"com.example.app" output_path:"./certs"
```

### Common pem Flags

| Flag | Purpose |
|---|---|
| `--app_identifier` | Bundle ID |
| `--output_path` | Where to save certs |
| `--development` | Development push cert |
| `--generate_p12` | Also generate .p12 file |
| `--p12_password` | Password for .p12 |
| `--force` | Create new even if existing is valid |
| `--team_id` | Developer team ID |

> **Agent guidance:** For modern projects using token-based APNs (`.p8` key), push certs are unnecessary. Only use `pem` if the project specifically uses certificate-based APNs.

---

## frameit (Screenshot Frames)

Add device bezels and titles to screenshots for App Store presentation.

```bash
fastlane frameit --path "./screenshots"
```

With titles:

```bash
fastlane frameit silver --path "./screenshots"
```

Equivalent:

```bash
fastlane run frame_screenshots path:"./screenshots"
```

A `Framefile.json` in the screenshots directory controls titles, fonts, and colors.

---

## Common Workflows

### Build + Upload to TestFlight

```bash
fastlane gym \
  --workspace "App.xcworkspace" \
  --scheme "App" \
  --export_method "app-store" \
  --output_directory "./build" && \
fastlane pilot upload \
  --ipa "./build/App.ipa" \
  --changelog "Latest build from CI"
```

### Build + Submit to App Store

```bash
fastlane gym \
  --workspace "App.xcworkspace" \
  --scheme "App" \
  --export_method "app-store" \
  --output_directory "./build" && \
fastlane deliver \
  --ipa "./build/App.ipa" \
  --submit_for_review \
  --automatic_release \
  --force
```

### Sync Signing + Build + Upload

```bash
fastlane match appstore \
  --app_identifier "com.example.app" \
  --readonly && \
fastlane gym \
  --workspace "App.xcworkspace" \
  --scheme "App" \
  --export_method "app-store" \
  --output_directory "./build" && \
fastlane pilot upload \
  --ipa "./build/App.ipa"
```

### Test + Build + Upload

```bash
fastlane scan \
  --workspace "App.xcworkspace" \
  --scheme "AppTests" && \
fastlane gym \
  --workspace "App.xcworkspace" \
  --scheme "App" \
  --export_method "app-store" \
  --output_directory "./build" && \
fastlane pilot upload \
  --ipa "./build/App.ipa"
```

### Screenshots + Frames + Upload

```bash
fastlane snapshot \
  --workspace "App.xcworkspace" \
  --scheme "AppUITests" \
  --output_directory "./screenshots" && \
fastlane frameit silver --path "./screenshots" && \
fastlane deliver --skip_binary_upload --skip_metadata
```

---

## Environment Variables

### General

| Variable | Purpose |
|---|---|
| `FASTLANE_XCODEBUILD_SETTINGS_TIMEOUT` | Timeout for xcodebuild settings (seconds) |
| `FASTLANE_XCODEBUILD_SETTINGS_RETRIES` | Retry count for xcodebuild |
| `FASTLANE_OPT_OUT_USAGE` | Set to `YES` to disable analytics |
| `FL_OUTPUT_DIR` | Default output directory |
| `FASTLANE_SKIP_UPDATE_CHECK` | Skip update prompts |
| `FASTLANE_HIDE_TIMESTAMP` | Hide log timestamps |
| `FASTLANE_DISABLE_COLORS` | Disable colored output |

### CI-Specific

| Variable | Purpose |
|---|---|
| `CI` | Set to `true` on CI environments |
| `FASTLANE_DONT_STORE_PASSWORD` | Don't save passwords to keychain |
| `MATCH_KEYCHAIN_NAME` | Keychain name for CI |
| `MATCH_KEYCHAIN_PASSWORD` | Keychain password for CI |

### Xcode

| Variable | Purpose |
|---|---|
| `GYM_WORKSPACE` | Default workspace path |
| `GYM_SCHEME` | Default scheme |
| `GYM_OUTPUT_DIRECTORY` | Default output directory |
| `GYM_EXPORT_METHOD` | Default export method |
| `SCAN_WORKSPACE` | Default workspace for tests |
| `SCAN_SCHEME` | Default test scheme |
| `SCAN_DEVICE` | Default test device |

---

## Notes

### CLI Syntax Rules

- All `fastlane run` parameters use `key:value` syntax (no dashes, no equals signs).
- Tool shorthand commands (`fastlane gym`, `fastlane pilot`) use `--key value` or `--key "value"` syntax.
- Boolean parameters: `true`/`false` for `fastlane run`, `--flag`/no flag for shorthand.
- Array parameters: comma-separated strings (e.g., `devices:"iPhone 16,iPad Pro"`).
- Paths with spaces must be quoted.

### Error Handling

- **Session expired:** Re-authenticate with `fastlane spaceauth -u user@example.com` or refresh API key.
- **Code signing errors:** Run `fastlane match` to sync, or `security find-identity -v -p codesigning` to verify local certs.
- **"Could not find App":** Verify `app_identifier` matches the bundle ID registered in App Store Connect.
- **Timeout on upload:** Set `FASTLANE_XCODEBUILD_SETTINGS_TIMEOUT=120` and retry.
- **Profile mismatch:** Run `fastlane sigh repair` or `fastlane match` with `--force`.

### Agent Tips

> When a user asks to "deploy" or "release" an iOS app, the typical flow is: **match** (sign) → **gym** (build) → **pilot** (TestFlight) or **deliver** (App Store).

> If the user has a `Fastfile`, respect it. But for one-off commands, always use the CLI syntax shown in this skill.

> Always check for an existing `.xcworkspace` before defaulting to `.xcodeproj`. Run `ls *.xcworkspace` to verify.

> For CI environments, always use `--readonly` with match and set the `CI=true` environment variable.

> When in doubt about which action to use, run `fastlane actions` or `fastlane search_actions <keyword>` to discover the right one.
