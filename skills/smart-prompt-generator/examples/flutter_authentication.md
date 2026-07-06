# Example: Flutter Authentication Feature

This example demonstrates how to use the AI Prompt Generator skill to create a comprehensive authentication feature for a Flutter app.

## 📋 Request to Skill

**User says:**
```
Create a prompt for implementing user authentication in my Flutter e-commerce app
```

## 🎨 Generated Prompt

```dart
Implement user authentication in a Flutter e-commerce app with the following requirements:

AUTHENTICATION METHODS:
- Email/Password: With email validation and strong password requirements
- Social Login: Google Sign-In, Apple Sign-In
- Phone Auth: SMS verification (optional)
- Biometric: Face ID/Touch ID for quick login

STATE MANAGEMENT:
- Solution: Riverpod for auth state management
- Persistence: Keep user logged in across app restarts using SharedPreferences
- Token Management: Secure storage using flutter_secure_storage
- Session Handling: Auto-refresh tokens, handle expiry

SECURITY:
- Password Policy:
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 number
  - At least 1 special character
- Token Storage: Use flutter_secure_storage for iOS Keychain and Android Keystore
- Session Timeout: 30 days, configurable
- Rate Limiting: Max 5 login attempts per 15 minutes

UI COMPONENTS:
1. Login Screen
   - Email/password input fields
   - "Forgot Password" link
   - Social login buttons (Google, Apple)
   - "Remember me" checkbox
   - Form validation with real-time feedback
   - Loading states and error messages

2. Registration Screen
   - Multi-step form (3 steps):
     Step 1: Email and password
     Step 2: Personal info (name, phone)
     Step 3: Preferences (notifications, terms)
   - Progress indicator
   - Back navigation
   - Data persistence between steps

3. Forgot Password Screen
   - Email input
   - Success confirmation
   - Resend option

4. Profile Screen
   - User info display
   - Edit profile option
   - Change password
   - Logout button
   - Delete account option

ERROR HANDLING:
- Network Errors: Show offline banner, queue requests
- Validation Errors: Real-time field validation
- Auth Errors: User-friendly messages (e.g., "Invalid email or password")
- Server Errors: Generic message with retry option
- Rate Limiting: Show cooldown timer

VALIDATION:
- Email: Valid format, not disposable email
- Password: Strength meter, confirmation match
- Phone: Format validation based on country
- Name: Min 2 characters, allow spaces and hyphens

PROVIDE:
1. Complete authentication service with Firebase Auth
2. Riverpod providers setup (StateNotifier for auth state)
3. UI screens with form validation
4. Error handling strategy with custom exceptions
5. Testing approach:
   - Unit tests for auth service
   - Widget tests for screens
   - Integration tests for full flow
6. Example usage in widgets:
   - Protected route wrapper
   - Auth state listener
   - Conditional UI based on auth status

ADDITIONAL FEATURES:
- Email verification flow
- Password strength indicator
- Remember me functionality
- Social login error handling
- Account linking (email + social)
- Anonymous to permanent account upgrade

PERFORMANCE:
- Lazy loading of auth state
- Optimistic UI updates
- Debounced form validation
- Cached user profile

ACCESSIBILITY:
- Screen reader support
- High contrast mode
- Font scaling
- Keyboard navigation
```

## 🤖 AI Tool Response Example

When you paste this prompt into ChatGPT or Claude, you'll get a comprehensive response with:

1. **Complete Code Implementation**
   ```dart
   // auth_service.dart
   class AuthService {
     final FirebaseAuth _firebaseAuth;
     final GoogleSignIn _googleSignIn;
     // ... implementation
   }
   ```

2. **State Management Setup**
   ```dart
   // auth_provider.dart
   final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
     return AuthNotifier(ref.read(authServiceProvider));
   });
   ```

3. **UI Components**
   ```dart
   // login_screen.dart
   class LoginScreen extends ConsumerWidget {
     // ... complete implementation
   }
   ```

4. **Error Handling**
   ```dart
   // auth_exceptions.dart
   class AuthException implements Exception {
     final String message;
     // ... custom exceptions
   }
   ```

5. **Testing Examples**
   ```dart
   // auth_service_test.dart
   void main() {
     test('should login user with valid credentials', () async {
       // ... test implementation
     });
   }
   ```

## 📊 Results

### What You Get

✅ **Complete Implementation** - All code files needed
✅ **Best Practices** - Security, performance, accessibility
✅ **Error Handling** - Comprehensive error management
✅ **Testing** - Unit, widget, and integration tests
✅ **Documentation** - Comments and usage examples

### Time Saved

| Task | Manual | With Prompt |
|------|--------|-------------|
| Architecture design | 2-3 hours | 10 minutes |
| Code implementation | 8-10 hours | 30 minutes |
| Testing setup | 2-3 hours | 15 minutes |
| Documentation | 1-2 hours | 5 minutes |
| **Total** | **13-18 hours** | **1 hour** |

## 🎯 Customization Options

### Adjust Complexity

**Simpler Version:**
```dart
Implement basic email/password authentication for a Flutter app:
- Login and registration screens
- Form validation
- State management with Provider
- Simple error handling
```

**More Complex Version:**
```dart
Implement enterprise-grade authentication with:
- Multi-factor authentication (MFA)
- Single Sign-On (SSO) integration
- Role-based access control (RBAC)
- Audit logging
- Security monitoring
- Compliance features (GDPR, SOC2)
```

### Change Technologies

**Using Firebase:**
```dart
Use Firebase Authentication as the backend
```

**Using Custom API:**
```dart
Use custom REST API at api.example.com/auth with JWT tokens
```

**Using Supabase:**
```dart
Use Supabase Auth with Row Level Security (RLS)
```

## 💡 Pro Tips

1. **Iterate**: Start with basic version, add complexity as needed
2. **Test Early**: Run generated code immediately to validate
3. **Customize**: Adjust generated code to match your style
4. **Save**: Keep successful prompts for future use
5. **Share**: Contribute successful prompts back to community

## 🔗 Related Examples

- [E-Commerce App](./ecommerce_app.md)
- [Social Media App](./social_media_app.md)
- [Chat App](./chat_app.md)
- [Fitness App](./fitness_app.md)

---

**Next**: [Example: Flutter Game Jump Mechanic](./game_jump_mechanic.md)
