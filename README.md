<img src='../NRS_ENCRYPTION.png' width=600px justify-content=center>

# NRS ENCRYPTION
This project is about an encryption chain that utilizes the power of randomness and total obfuscation. This encryption tool can be used to encrypting any type of files and folders within the Windows, Linux, and MacOS. The files will be totally encrypted and obfuscated into a file type called `.nrs`. So even though unauthorized users can see the existence of the files, they wont be able to the content and what type of file is.

# How does it work?
First it asks the user for the folder path, and the master key a.k.a the password. It then scans the whole selected folder for files, and subfolders. It then encrypts the files and folder one by one using the encryption algorithm. 

# Pre-requisites
- Python 3.14
- pip3 26.0.1 

# Installation Steps
1. Clone the Repository

```git
git clone https://github.com/NotReallySerious/NRS_ENCRYPTION.git
```

2. Install the required Libraries
```python
pip3 install -r requirements.txt
```

3. run the main.py

```python
python3 -u main_.py
```
# IMPORTANT NOTE ⚠️⚠️⚠️
- The bigger the file, the longer it takes to encrypt it. Same goes to the folder.
- Make sure you have a copy of the password because THE KEY WILL ALSO BE ENCRYPTED AND CANNOT BE ACCESSED.
