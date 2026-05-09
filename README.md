<div align="center">

# 🔐 NRS ENCRYPTION (v2.0 - Fixed & Improved)
### *Securing secrets with ease*

[![Python](https://img.shields.io/badge/Python-3.14%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)](/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)](/)
[![Author](https://img.shields.io/badge/Author-Mr%20Hoodie-purple?style=for-the-badge)](/)

> A custom-built, multi-layered file encryption tool that locks your entire vault with a single password — no third-party crypto libraries, just raw algorithmic engineering.

</div>

---

## 📖 Table of Contents

- [Version 2.0 - Critical Fixes & Improvements](#-version-20---critical-fixes--improvements)
- [What is NRS Encryption?](#-what-is-nrs-encryption)
- [How It Works](#-how-it-works)
- [Encryption Chain](#-encryption-chain)
- [Security Design](#-security-design)
- [Requirements](#-requirements)
- [Usage](#-usage)
- [Disclaimer](#-disclaimer)

---

## ✅ Version 2.0 - Critical Fixes & Improvements

### 🔴 CRITICAL BUG FIXES

#### 1. **Files with Same Name, Different Extensions Now Handled Correctly** ✓
- **Problem**: `photo.jpg` and `photo.png` would encrypt to the same filename, causing data loss
- **Solution**: Encrypted filename now based on `hash(stem + extension)` instead of just `hash(stem)`
- **Impact**: Files are now uniquely identified and never collide

#### 2. **Encryption/Decryption Fully Reversible** ✓
- **Problem**: XOR implementation used NumPy's random generator inconsistently
- **Solution**: Replaced with pure Python + HMAC-SHA256 for deterministic key derivation
- **Impact**: Encryption is now guaranteed to be reversible; same password+stem always produces same key

#### 3. **Added Integrity Verification** ✓
- **Problem**: No way to detect if decrypted data was corrupted
- **Solution**: Added SHA256 checksums to file headers; verified after decryption
- **Impact**: Corrupted files are immediately detected and reported

### ⚙️ PERFORMANCE IMPROVEMENTS

1. **Removed NumPy Dependency** ⚡
   - Removed unnecessary numpy for XOR operations
   - Pure Python XOR is sufficient and faster for this use case
   - Reduced dependencies from 4 to 3

2. **Improved Error Handling** ⚡
   - Silent failures now tracked and reported
   - Failed decryptions are logged with detailed error messages
   - User can see which files failed and why

3. **Better Parallelization** ⚡
   - Multi-process worker pool uses CPU cores efficiently
   - Progress bar shows real-time status
   - Graceful interrupt handling (Ctrl+C)

### 🛡️ SECURITY ENHANCEMENTS

1. **Header Format Improved**
   - New format: `extension||stem||checksum||encrypted_data`
   - Includes integrity check field
   - Better parsing with error detection

2. **Key Derivation More Robust**
   - File-specific keys: `hash(password + stem + extension)`
   - Manifest key: `hash(password)` only
   - Multiple transformation rounds ensure cryptographic strength

3. **Name Collision Handling**
   - Automatic suffix addition if filename already exists during decryption
   - Files renamed to `filename_1.ext`, `filename_2.ext`, etc.
   - Never overwrites existing files

### 📝 CODE QUALITY IMPROVEMENTS

1. **Added Comprehensive Documentation**
   - Docstrings for all major functions
   - Explained encryption chain in comments
   - Documented reversibility guarantees

2. **Better Exception Handling**
   - Try-catch blocks with detailed error reporting
   - Graceful recovery from partial encryption/decryption
   - Clear error messages for debugging

3. **Removed Dead Code**
   - Cleaned up unused `salt.py`
   - Removed unused `encrypt_folder.py` (functionality in encrypt_file.py)
   - Removed test file `randomexample.py`

---

## 🧠 What is NRS Encryption?

NRS Encryption is a **folder-level file encryption vault** built entirely from scratch in Python. It chains together multiple custom cryptographic operations — hashing, XOR encryption, Base64 encoding, and SHA-256 — to encrypt every file in a target folder and anonymise their filenames.

**What it does:**
- Encrypts every file inside a folder recursively with a unique key per file
- Anonymises filenames so directory listings reveal nothing
- Stores the original filename mapping in an encrypted manifest
- Verifies password integrity via a stored password seal
- Processes files in parallel across all CPU cores
- **Validates data integrity with checksums** (NEW!)
- **Handles files with identical names but different extensions** (NEW!)

NRS operates in two phases — **locking** (encryption) and **unlocking** (decryption).

### Locking a Vault

```
User Password
      │
      ▼
  [ hash() ]           — Deterministic 16-char alphanumeric digest of the password
      │
      ▼
  [ XOR_for_password ] — XOR transform using a seeded pseudorandom key stream
      │
      ▼
  [ Base64 Encode ]    — Encodes binary XOR output to a portable string
      │
      ▼
  [ SHA-256 ]          — Produces the final password seal stored in .nrs_lock
```

For each file in the vault:

```
Original File
      │
      ├──► Read file bytes
      │
      ├──► XOR encrypt  (seed = password + filename stem)
      │        └── Per-file unique key stream via seeded numpy RNG
      │
      ├──► Prepend header:  <ext> || <original_stem> ||
      │
      ├──► Write encrypted blob back to disk
      │
      └──► Rename file:  hash(stem)  →  SHA-256[:15].nrs

Original filenames → saved to .nrs_manifest (itself XOR-encrypted)
```

### Unlocking a Vault

The process runs in reverse. The password is put through the same hashing pipeline and compared against the stored seal in `.nrs_lock`. If they match, each `.nrs` file is:
1. Read and its header parsed to recover the original extension and stem
2. XOR-decrypted using the reconstructed seed (`password + original_stem`)
3. Written back under its original filename
4. The `.nrs` file is deleted

The manifest is decrypted and used to restore exact original filenames.

---

## 🔗 Encryption Chain

The full multi-layer chain is visualised below:

```
┌─────────────────────────────────────────────────────────────┐
│                    NRS ENCRYPTION CHAIN                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PASSWORD ──► hash() ──► XOR ──► Base64 ──► SHA-256        │
│                                                    │        │
│                                             .nrs_lock seal  │
│                                                             │
│  FILE ──► Read bytes                                        │
│               │                                             │
│               ▼                                             │
│          XOR encrypt  ◄── seed: password + filename stem    │
│               │                  │                          │
│               │            numpy RNG (per-file unique)      │
│               ▼                                             │
│          Write header + encrypted bytes                      │
│               │                                             │
│               ▼                                             │
│          Rename ◄── hash(stem) ──► SHA-256[:15].nrs         │
│                                                             │
│  MANIFEST ──► JSON of {new_name: original_name}             │
│               └──► XOR encrypted ──► .nrs_manifest          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
NRS-Encryption/
│
├── main_.py            # Entry point — CLI menu, password policy, orchestration
├── encrypt_file.py     # Folder encryption engine (parallel ProcessPool)
├── decryption.py       # Folder decryption engine (parallel ProcessPool)
├── encrypt_folder.py   # Folder path validation wrapper
│
├── XOR.py              # Core XOR cipher — numpy-accelerated, chunked streaming
├── hashing.py          # Filename/password hashing (seeded PRNG, 16-char digest)
├── salt.py             # Salt token generator
├── SHA256.py           # SHA-256 wrapper for final password seal
├── Convertbase64.py    # Base64 encoder used in password pipeline
│
└── README.md
```

**Generated at runtime (inside the encrypted vault folder):**

| File | Purpose |
|---|---|
| `.nrs_lock` | Stores the hashed password seal for verification |
| `.nrs_manifest` | XOR-encrypted map of `{anonymised_name: original_name}` |
| `*.nrs` | Encrypted file blobs with embedded header |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/NRS-Encryption.git
cd NRS-Encryption

# 2. Install dependencies
pip install numpy tqdm colorama pyfiglet
```

That's it. No external cryptography libraries needed.

---

## 💻 Usage

Run the main entry point:

```bash
python main_.py
```

You'll be greeted with the NRS banner and a simple menu:

```
1. Encrypting a folder
2. Decrypting a folder
3. Exit
```

### Encrypting a Folder

1. Choose option **1**
2. Enter a master password that meets the policy:
   - Minimum **12 characters**
   - At least **1 uppercase**, **1 lowercase**, **1 digit**, **1 special character**
3. Enter the **full path** to the folder you want to lock
4. NRS will encrypt all files in parallel and display a progress bar

```
Securing Vault: 100%|██████████████████████████████| 47/47 [00:02<00:00, 21.3file/s]
[✓] Vault Created Successfully.
```

### Decrypting a Folder

1. Choose option **2**
2. Enter the full path to the locked vault folder
3. Enter your master password
4. NRS verifies the seal — if correct, all files are restored

```
Unlocking Vault: 100%|██████████████████████████████| 47/47 [00:01<00:00, 28.7file/s]
[✓] NRS Vault Decryption Complete.
```

> ⚠️ If you enter the wrong password, decryption is denied immediately. No files are touched.

### Interrupting Mid-operation

Press `Ctrl+C` at any time. NRS catches the signal gracefully — already-processed files remain in their current state and the program exits cleanly without data corruption.

---

## 🛡️ Security Design

### Per-file Unique Key Streams
Every file is encrypted with a different key stream, even if two files have identical content. The XOR seed is derived from `password + filename_stem`, so the key is always unique per file per vault.

### Filename Anonymisation
Original filenames are never left on disk. Each file is renamed to the first 15 characters of a SHA-256 hash derived from a seeded hash of the filename stem. A directory listing of a locked vault reveals nothing about its contents.

### Encrypted Manifest
The mapping between anonymised `.nrs` names and original filenames is stored in `.nrs_manifest`, which is itself XOR-encrypted with the master password. Without the password, the manifest is unreadable.

### Password Seal Verification
The master password goes through a 4-step pipeline (hash → XOR → Base64 → SHA-256) before being stored in `.nrs_lock`. Decryption is only attempted after the entered password's seal matches the stored one exactly.

### Header Embedding
Each encrypted file embeds its own original extension and filename stem in a plaintext header (`<ext>||<stem>||`). This means files can be correctly restored even without the manifest, as a fallback.

### No Dependencies on External Crypto
NRS does not use `cryptography`, `PyCryptodome`, or any other crypto library. Every operation is implemented directly — making the algorithm fully transparent and auditable.

---

## ⚡ Performance

NRS uses `ProcessPoolExecutor` to distribute encryption and decryption work across all available CPU cores. The XOR engine uses **numpy vectorised operations** and **4MB chunked streaming**, replacing the original Python byte-loop which was orders of magnitude slower.

| Metric | Detail |
|---|---|
| Parallelism | `os.cpu_count()` processes — true CPU parallelism, bypasses Python GIL |
| XOR engine | numpy array XOR — ~200× faster than Python byte loop |
| Key generation | Seeded numpy RNG — ~200× faster than original string-building approach |
| Memory safety | 4MB chunks — handles files of any size without running out of RAM |
| Large file (100MB) | ~0.37s encrypt, ~0.38s decrypt |

Performance scales with core count. The more CPUs, the faster the vault locks and unlocks.

---

## 📦 Requirements

| Package | Purpose |
|---|---|
| `numpy` | Vectorised XOR operations and fast key stream generation |
| `tqdm` | Progress bar display |
| `colorama` | Cross-platform terminal colour output |
| `pyfiglet` | ASCII art banner |

All standard library modules used (`hashlib`, `base64`, `random`, `pathlib`, `json`, `signal`, `concurrent.futures`) require no installation.

Install all at once:

```bash
pip install numpy tqdm colorama pyfiglet
```

---

## ⚠️ Disclaimer

NRS Encryption is a **personal project** built for educational purposes and as a demonstration of applied cryptography concepts in Python. It is **not** intended as a replacement for established encryption standards such as AES-256 or ChaCha20.

- Do not use NRS as your sole protection for highly sensitive or irreplaceable data
- Always keep backups of important files before encrypting them
- If you lose or forget the master password, **there is no recovery path** — encrypted files cannot be restored without it
- The author takes no responsibility for data loss resulting from misuse

---

<div align="center">

Built with 🔒 by **Mr Hoodie** &nbsp;|&nbsp; Version 1.0

*"Security is not a product, but a process."*

</div>
