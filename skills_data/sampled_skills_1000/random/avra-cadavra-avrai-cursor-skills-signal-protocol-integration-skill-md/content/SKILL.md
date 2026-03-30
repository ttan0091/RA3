---
name: signal-protocol-integration
description: Guides Signal protocol integration: encryption/decryption, key management, session management, FFI bindings, security best practices. Use when implementing encryption, secure communication, or Signal protocol features.
---

# Signal Protocol Integration

## Core Purpose

Signal protocol provides end-to-end encryption for secure communication in AI2AI system.

## Key Components

### Signal Protocol Service
- Encryption/decryption
- Key management
- Session management
- FFI bindings

### Signal Key Manager
- Key generation
- Key storage
- Key rotation
- Pre-key bundles

### Signal Session Manager
- Session establishment
- Session storage
- Session updates

## Implementation Pattern

```dart
import 'package:avrai/core/crypto/signal/signal_protocol_service.dart';

class SecureCommunicationService {
  final SignalProtocolService _signalService;
  
  SecureCommunicationService({
    required SignalProtocolService signalService,
  }) : _signalService = signalService;
  
  /// Encrypt message using Signal protocol
  Future<EncryptedMessage> encryptMessage({
    required String recipientId,
    required String message,
  }) async {
    // Get or create session with recipient
    await _signalService.ensureSession(recipientId);
    
    // Encrypt message
    final encrypted = await _signalService.encryptMessage(
      recipientId: recipientId,
      plaintext: message,
    );
    
    return EncryptedMessage(
      recipientId: recipientId,
      ciphertext: encrypted,
      timestamp: DateTime.now(),
    );
  }
  
  /// Decrypt message using Signal protocol
  Future<String> decryptMessage({
    required String senderId,
    required String ciphertext,
  }) async {
    final decrypted = await _signalService.decryptMessage(
      senderId: senderId,
      ciphertext: ciphertext,
    );
    
    return decrypted;
  }
}
```

## Key Management

```dart
/// Signal Key Manager
/// 
/// Manages Signal protocol keys: identity keys, pre-keys, signed pre-keys
class SignalKeyManager {
  final SignalProtocolService _signalService;
  
  /// Generate and store identity key pair
  Future<void> initializeKeys() async {
    await _signalService.generateIdentityKeyPair();
  }
  
  /// Get pre-key bundle for new session
  Future<PreKeyBundle> getPreKeyBundle(String userId) async {
    return await _signalService.getPreKeyBundle(userId);
  }
  
  /// Rotate pre-keys (security best practice)
  Future<void> rotatePreKeys() async {
    await _signalService.rotatePreKeys();
  }
}
```

## Session Management

```dart
/// Signal Session Manager
/// 
/// Manages Signal protocol sessions with other devices
class SignalSessionManager {
  final SignalProtocolService _signalService;
  
  /// Establish session with device
  Future<void> establishSession({
    required String deviceId,
    required PreKeyBundle preKeyBundle,
  }) async {
    await _signalService.createSession(
      deviceId: deviceId,
      preKeyBundle: preKeyBundle,
    );
  }
  
  /// Check if session exists
  Future<bool> hasSession(String deviceId) async {
    return await _signalService.hasSession(deviceId);
  }
}
```

## FFI Bindings

Signal protocol uses Rust FFI bindings:

```dart
import 'package:avrai/core/crypto/signal/signal_ffi_bindings.dart';

/// Use FFI bindings for Signal protocol operations
final bindings = SignalFFIBindings.instance;

// Initialize Signal protocol
await bindings.initialize();

// Use Signal protocol functions
final encrypted = await bindings.encrypt(plaintext, recipientId);
```

## Security Best Practices

1. **Key Rotation** - Regularly rotate pre-keys
2. **Session Verification** - Verify session integrity
3. **Secure Storage** - Store keys securely (encrypted storage)
4. **Error Handling** - Handle encryption failures gracefully
5. **No Plaintext Storage** - Never store plaintext messages

## Reference

- `lib/core/crypto/signal/signal_protocol_service.dart`
- `lib/core/crypto/signal/signal_key_manager.dart`
- `lib/core/crypto/signal/signal_session_manager.dart`
- `lib/core/crypto/signal/signal_ffi_bindings.dart`
