# Verschlüsselung & IT-Sicherheit — Referenz

## Symmetrische vs. Asymmetrische Verschlüsselung

| Eigenschaft | Symmetrisch | Asymmetrisch |
|-------------|------------|--------------|
| Schlüssel | 1 (gleicher für Ver-/Entschlüsselung) | 2 (Public + Private Key) |
| Geschwindigkeit | Schnell | Langsam (100-1000x) |
| Schlüsselaustausch | Problem (wie sicher übertragen?) | Kein Problem (Public Key öffentlich) |
| Algorithmen | AES, ChaCha20, 3DES | RSA, ECDSA, Ed25519 |
| Einsatz | Datenverschlüsselung, VPN | Schlüsselaustausch, Signaturen, Zertifikate |

## TLS-Handshake (vereinfacht)

1. **ClientHello**: Client sendet unterstützte TLS-Versionen und Cipher-Suites
2. **ServerHello**: Server wählt Cipher-Suite, sendet Zertifikat (Public Key)
3. **Schlüsselaustausch**: Client erzeugt Pre-Master-Secret, verschlüsselt mit Server-Public-Key
4. **Session-Key**: Beide Seiten berechnen gemeinsamen Session-Key (symmetrisch)
5. **Verschlüsselte Kommunikation**: Ab jetzt symmetrisch (AES) verschlüsselt

→ **Hybrid**: Asymmetrisch für Schlüsselaustausch, Symmetrisch für Datenübertragung

## Hashing (Einweg-Funktionen)
- **MD5**: 128 Bit — UNSICHER, nur noch für Checksummen
- **SHA-256**: 256 Bit — Standard für Passwort-Hashing, Zertifikate
- **bcrypt/argon2**: Passwort-Hashing mit Salt und Kosten-Faktor

## Zertifikate (X.509)
- CA (Certificate Authority) signiert Zertifikate
- Zertifikatskette: Root-CA → Intermediate-CA → Server-Zertifikat
- Let's Encrypt: Kostenlose TLS-Zertifikate (90 Tage gültig)
