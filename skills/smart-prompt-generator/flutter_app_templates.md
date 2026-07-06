# Flutter App Development Templates

This file contains detailed prompt templates for Flutter app development across various categories and complexity levels.

## App Categories Covered

- E-Commerce Apps
- Social Media Apps
- Productivity Apps
- Educational Apps
- Health & Fitness Apps
- Finance Apps
- Media Apps
- Utility Apps
- Enterprise Apps
- IoT/Smart Home Apps

## Template Library

### 1. Complete App Architecture

```
Design a complete architecture for a [APP_TYPE] Flutter app:

APP SPECIFICATIONS:
- Type: [e-commerce/social/productivity/etc.]
- Platforms: [iOS/Android/Web/Desktop]
- Scale: [small/medium/large]
- Users: [B2C/B2B/internal]
- Offline Support: [required/optional/none]

ARCHITECTURE PATTERN:
- Pattern: [Clean Architecture/MVVM/MVC/BLoC]
- Rationale: [why this pattern suits the app]

STATE MANAGEMENT:
- Solution: [Riverpod/Provider/Bloc/GetX]
- Scope: [global/local state separation]
- Persistence: [what state to persist]

DATA LAYER:
- Local Storage: [Hive/SQLite/SharedPreferences]
- Remote API: [REST/GraphQL/Firebase]
- Caching Strategy: [what to cache, when to refresh]
- Sync Strategy: [offline-first/online-first]

DEPENDENCY INJECTION:
- DI Container: [GetIt/Provider/Riverpod]
- Scope: [singleton/scoped/factory]

NAVIGATION:
- Approach: [Navigator 2.0/GoRouter/AutoRoute]
- Deep Linking: [requirements]
- Authentication Flow: [guarded routes]

ERROR HANDLING:
- Strategy: [global error handler/try-catch/result type]
- User Feedback: [snackbars/dialogs/toasts]
- Logging: [what to log, where]

DELIVERABLES:
1. Complete folder structure
2. Core files and their responsibilities
3. Dependency injection setup
4. Navigation configuration
5. State management setup
6. API client architecture
7. Error handling framework
8. Testing structure
```

### 2. Feature Implementation

```
Implement [FEATURE_NAME] for a [APP_TYPE] Flutter app:

FEATURE DESCRIPTION:
- Purpose: [what problem it solves]
- User Flow: [step-by-step user journey]
- Priority: [must-have/nice-to-have]

REQUIREMENTS:
Functional:
- [requirement 1]
- [requirement 2]
- [requirement 3]

Non-Functional:
- Performance: [response time, load time]
- Scalability: [expected load]
- Security: [data protection needs]
- Accessibility: [WCAG compliance level]

UI/UX:
- Design: [Material/Cupertino/custom]
- Responsive: [phone/tablet/web layouts]
- Animations: [transition effects]
- Dark Mode: [support needed?]

INTEGRATION:
- Backend: [API endpoints needed]
- Third-Party: [external services]
- Device Features: [camera/location/etc.]

STATE MANAGEMENT:
- State Scope: [local/global]
- Persistence: [what to save]
- Updates: [when state changes]

TESTING:
- Unit Tests: [business logic]
- Widget Tests: [UI components]
- Integration Tests: [user flows]

Provide:
1. Complete implementation
2. State management setup
3. UI components
4. Business logic
5. API integration
6. Error handling
7. Example usage
8. Testing approach
```

### 3. Authentication System

```
Implement authentication for a [APP_TYPE] Flutter app:

AUTHENTICATION METHODS:
- Email/Password: [yes/no]
- Social Login: [Google/Apple/Facebook/etc.]
- Phone Auth: [SMS verification]
- Biometric: [Face ID/Touch ID]
- Anonymous: [guest access]

SECURITY REQUIREMENTS:
- Password Policy: [complexity rules]
- Two-Factor Auth: [2FA method]
- Session Management: [timeout, refresh tokens]
- Token Storage: [secure storage method]

USER FLOW:
- Sign Up: [registration steps]
- Sign In: [login process]
- Password Reset: [recovery flow]
- Email Verification: [verification process]
- Profile Management: [update profile]

IMPLEMENTATION:
- Backend: [Firebase/custom API]
- State Management: [auth state provider]
- Persistence: [keep logged in]
- Route Guards: [protected routes]

UI COMPONENTS:
- Login Screen: [form design]
- Registration Screen: [multi-step/single]
- Forgot Password Screen: [email input]
- Profile Screen: [user info display]

Provide:
1. Authentication service
2. State management
3. UI screens
4. Form validation
5. Error handling
6. Token management
7. Route guards
8. Testing approach
```

### 4. Data Management System

```
Create a data management system for [APP_TYPE]:

DATA TYPES:
- User Data: [profile, preferences]
- App Data: [settings, cache]
- Business Data: [domain-specific]

STORAGE SOLUTIONS:
Local:
- Type: [Hive/SQLite/SharedPreferences]
- Schema: [data structure]
- Migrations: [version management]

Remote:
- API: [REST/GraphQL/Firebase]
- Endpoints: [list required endpoints]
- Authentication: [API auth method]

SYNCHRONIZATION:
- Strategy: [offline-first/online-first]
- Conflict Resolution: [how to handle conflicts]
- Background Sync: [when to sync]
- Sync Indicators: [UI feedback]

CACHING:
- What to Cache: [data types]
- Cache Duration: [TTL for each type]
- Invalidation: [when to clear cache]
- Size Limits: [storage constraints]

OFFLINE SUPPORT:
- Offline Actions: [what users can do offline]
- Queue System: [pending operations]
- Retry Logic: [failed operations]

Provide:
1. Data models
2. Repository layer
3. Local storage implementation
4. API client
5. Sync manager
6. Cache manager
7. Offline queue
8. Example usage
```

### 5. Real-Time Features

```
Implement real-time features for [APP_TYPE]:

REAL-TIME REQUIREMENTS:
- Feature Type: [chat/notifications/live updates/location tracking]
- Scale: [expected concurrent users]
- Latency: [acceptable delay]

TECHNOLOGY:
- Solution: [WebSocket/Firebase Realtime/Firebase Firestore/SignalR]
- Fallback: [polling if real-time unavailable]

FEATURES:
1. Connection Management
   - Auto-reconnect
   - Connection state monitoring
   - Offline queueing

2. Data Synchronization
   - Real-time updates
   - Conflict resolution
   - Delta updates

3. User Presence
   - Online/offline status
   - Last seen
   - Typing indicators (if chat)

4. Notifications
   - Push notifications
   - In-app notifications
   - Notification preferences

IMPLEMENTATION:
- Connection Layer: [setup and management]
- State Management: [real-time state updates]
- UI Updates: [reactive UI]
- Error Handling: [connection errors]

Provide:
1. Real-time service
2. Connection manager
3. State synchronization
4. UI integration
5. Error handling
6. Performance optimizations
7. Testing approach
```

### 6. Payment Integration

```
Integrate payment system for [APP_TYPE] Flutter app:

PAYMENT REQUIREMENTS:
- Payment Type: [one-time/subscription/both]
- Products: [what's being sold]
- Pricing: [fixed/dynamic/tiered]
- Currency: [single/multiple]

PAYMENT METHODS:
- Credit/Debit Cards
- Digital Wallets: [Apple Pay/Google Pay]
- Regional: [specific to region]

GATEWAY SELECTION:
- Provider: [Stripe/PayPal/Braintree/Razorpay]
- Rationale: [why this provider]

SUBSCRIPTION MANAGEMENT (if applicable):
- Plans: [subscription tiers]
- Trial Period: [free trial details]
- Upgrades/Downgrades: [plan changes]
- Cancellation: [process]

SECURITY:
- PCI Compliance: [handling card data]
- Fraud Prevention: [security measures]
- Data Encryption: [sensitive data protection]

UI/UX:
- Payment Flow: [checkout process]
- Saved Cards: [card management]
- Receipts: [transaction history]
- Error Handling: [failed payments]

Provide:
1. Payment service implementation
2. UI components
3. Subscription management
4. Webhook handling
5. Receipt generation
6. Error handling
7. Testing approach (sandbox)
8. Security measures
```

### 7. Media Handling

```
Implement media handling for [APP_TYPE]:

MEDIA TYPES:
- Images: [capture, gallery, display]
- Video: [playback, recording]
- Audio: [recording, playback]
- Documents: [upload, download, view]

REQUIREMENTS:
- Capture: [camera/microphone access]
- Selection: [gallery/file picker]
- Editing: [crop, filters, trim]
- Compression: [size optimization]
- Storage: [local/cloud]

IMAGE HANDLING:
- Capture: [camera integration]
- Picker: [gallery selection]
- Cropper: [image cropping]
- Compression: [reduce file size]
- Caching: [performance optimization]
- Display: [optimized image widgets]

VIDEO HANDLING:
- Playback: [video player setup]
- Recording: [camera recording]
- Compression: [video optimization]
- Streaming: [if applicable]
- Thumbnails: [preview generation]

AUDIO HANDLING:
- Recording: [audio capture]
- Playback: [audio player]
- Background Audio: [play in background]
- Controls: [play/pause/seek]

STORAGE:
- Local: [secure storage]
- Cloud: [Firebase Storage/AWS S3/etc.]
- CDN: [content delivery]

Provide:
1. Media service layer
2. Image handling
3. Video handling
4. Audio handling
5. Storage integration
6. Compression utilities
7. UI components
8. Example usage
```

### 8. Push Notifications

```
Implement push notification system for [APP_TYPE]:

NOTIFICATION TYPES:
- Transactional: [order updates, alerts]
- Promotional: [marketing messages]
- System: [app updates, maintenance]
- User-to-User: [chat, mentions]

PLATFORMS:
- Firebase Cloud Messaging (FCM) for Android
- Apple Push Notification Service (APNs) for iOS
- Web Push (if applicable)

FEATURES:
1. Permission Handling
   - Request permission
   - Handle denial
   - Settings management

2. Notification Types
   - Remote notifications
   - Local notifications
   - Scheduled notifications

3. Payload Handling
   - Data messages
   - Notification messages
   - Action buttons
   - Images/media

4. Deep Linking
   - Navigate to specific screen
   - Pass data to screen
   - Handle background/foreground

5. Token Management
   - Device token storage
   - Token refresh
   - Multi-device support

USER PREFERENCES:
- Categories: [notification types]
- Quiet Hours: [do not disturb]
- Sound/Vibration: [customization]

Provide:
1. Notification service
2. Permission handling
3. Token management
4. Notification handlers
5. Deep linking setup
6. UI for preferences
7. Testing approach
8. Analytics integration
```

### 9. Search & Filter System

```
Implement search and filter functionality for [APP_TYPE]:

SEARCH REQUIREMENTS:
- Scope: [what data to search]
- Type: [full-text/fuzzy/autocomplete]
- Performance: [expected response time]
- Indexing: [search index strategy]

FILTER REQUIREMENTS:
- Filter Types: [category/date/price/etc.]
- Combinations: [multiple filters]
- Persistence: [save filter preferences]
- Reset: [clear all filters]

FEATURES:
1. Search Bar
   - Auto-suggestions
   - Recent searches
   - Voice search (optional)

2. Advanced Filters
   - Filter UI (bottom sheet/drawer/screen)
   - Multi-select filters
   - Range filters (price, date)
   - Sort options

3. Results Display
   - List view
   - Grid view
   - Map view (if applicable)
   - Pagination/infinite scroll

4. Performance
   - Debouncing search input
   - Caching results
   - Optimistic UI updates

IMPLEMENTATION:
- Backend Search: [API endpoints]
- Local Search: [client-side filtering]
- Hybrid: [combine both]

Provide:
1. Search service
2. Filter logic
3. UI components
4. State management
5. Performance optimizations
6. Example usage
```

### 10. Analytics & Crash Reporting

```
Integrate analytics and crash reporting for [APP_TYPE]:

ANALYTICS REQUIREMENTS:
- Events to Track: [user actions, screens, conversions]
- User Properties: [demographics, preferences]
- E-commerce: [product views, purchases]
- Custom Dimensions: [app-specific metrics]

CRASH REPORTING:
- Automatic Capture: [unhandled exceptions]
- Manual Reporting: [handled errors]
- User Feedback: [crash reports]
- Stack Traces: [detailed logs]

TOOLS:
- Analytics: [Firebase Analytics/Amplitude/Mixpanel]
- Crash Reporting: [Crashlytics/Sentry/Bugsnag]
- Performance: [Firebase Performance/Custom]

PRIVACY:
- User Consent: [GDPR compliance]
- Data Anonymization: [PII handling]
- Opt-out: [respect user preferences]

IMPLEMENTATION:
1. Analytics Service
   - Event tracking wrapper
   - User property setter
   - Screen tracking

2. Crash Reporting Service
   - Error capture
   - Context logging
   - User identification

3. Performance Monitoring
   - Network timing
   - Screen rendering
   - Custom traces

Provide:
1. Analytics wrapper
2. Crash reporting setup
3. Performance monitoring
4. Privacy compliance
5. Dashboard setup
6. Testing approach
```

## Quick Reference Templates

### Simple CRUD Feature
```
Create a CRUD feature for [ENTITY] in a Flutter app:
- List view with search/filter
- Detail view
- Create/edit form
- Delete confirmation
- State management with Riverpod
- API integration
- Offline support
```

### Settings Screen
```
Implement a settings screen for a Flutter app:
- Toggle switches (notifications, dark mode)
- Dropdown selections (language, currency)
- List tiles (account, privacy, about)
- Reset to defaults
- Persistent storage
```

### Dashboard/Home Screen
```
Create a dashboard screen for [APP_TYPE]:
- Summary cards with key metrics
- Quick action buttons
- Recent items list
- Pull-to-refresh
- Responsive layout (phone/tablet)
- Shimmer loading states
```

### Form with Validation
```
Build a form for [PURPOSE] with:
- Input fields: [list fields]
- Validation: [validation rules]
- Error messages: [user-friendly errors]
- Submit button with loading state
- Success/error feedback
- Form reset functionality
```

### List with Pagination
```
Implement a paginated list for [DATA_TYPE]:
- Infinite scroll
- Loading indicators
- Error handling per page
- Pull-to-refresh
- Empty state
- Item tap handling
```

## Common Patterns

### Repository Pattern
```
Create a repository for [ENTITY]:
- Fetch from API
- Cache locally
- Return unified data source
- Handle offline scenarios
```

### BLoC/Cubit Pattern
```
Implement a BLoC for [FEATURE]:
- Events: [user actions]
- States: [loading, success, error]
- Business logic separation
- Stream-based state management
```

### Provider Pattern
```
Create providers for [FEATURE]:
- State provider
- Future provider (async data)
- Stream provider (real-time)
- Consumer widgets
```

## Performance Optimization

1. **Widget Optimization**
   - Const constructors
   - Builder patterns
   - Avoid rebuilds

2. **List Optimization**
   - ListView.builder
   - Pagination
   - Caching

3. **Image Optimization**
   - Cached images
   - Proper sizing
   - Lazy loading

4. **State Optimization**
   - Minimal state
   - Selector patterns
   - Debouncing

## Testing Strategy

1. **Unit Tests**: Business logic, utilities
2. **Widget Tests**: UI components, interactions
3. **Integration Tests**: User flows, API integration
4. **Golden Tests**: Visual regression
5. **Performance Tests**: Benchmarks

## Security Best Practices

1. **Data Protection**
   - Encrypt sensitive data
   - Secure storage
   - HTTPS only

2. **Authentication**
   - Secure token storage
   - Biometric auth
   - Session management

3. **Input Validation**
   - Sanitize inputs
   - Validate on server
   - Handle edge cases

4. **Code Security**
   - Obfuscation
   - Anti-tampering
   - Secure coding practices
