# ASC-Vulnerable-Blog-Website
Basic Python-Flask Server built for a Kali Linux Virtual Machine used to host a vulnerable Blog Website for web application penetration testing. 

This project is used for my Advanced Software Security (ASC) module in Asia Pacific University.

## Installation
1. Clone this repository

```
git clone https://github.com/Jon-OP/ASC-Vulnerable-Blog-Website.git
```

2. Create a Python Virtualized Environment to avoid installing Pip packages globally.

```
cd ASC-Vulnerable-Blog-Website
python -m venv venv
```

3. Enable Python's Virtualized Environment & Install Required Packages
* For Kali Linux Environments:
```
source venv/bin/activate
pip install -r requirements.txt
```
* For Window Environments
```
venv\Scripts\activate
pip install -r requirements.txt
```

4. SQLite3 Database:
* Initialize the SQLite3 Database by entering:
```
flask --app apu_blog init-db
```
* Showing all rows in the SQLite3 Database by entering:
```
flask --app apu_blog show-db
```

5. Starting the Server (Set xxx.xxx.xxx.xxx as your IP address)
```
flask --app apu_blog run --debug --host xxx.xxx.xxx.xxx -p 5000
```

## Vulnerabilities & Solutions
There are Four Vulnerabilities in this Web Application. CTRL+F the code in bracket to find the relevant functions.

There will be duplicated functions with the same name. The commented function is the vulnerable function. 
Uncomment the vulnerable function and comment the secured function to make the web application vulnerable.
#### 1. \[ VULNERABILITY-01 \] Credentials-based Vulnerabilities (auth.py)
---
1. \[ SOLUTION-01 \] Username lacks complexity; Users can enter single-character usernames.
2. \[ SOLUTION-02 \] Lack of Password Complexity Policies.
3. \[ SOLUTION-03 \] Password stored in plaintext instead of Hash Digests.

#### 2. \[ VULNERABILITY-02 \] Login Page Vulnerability: SQL Injection & Lack of 2-Factor Authentication (auth.py)
---
1. \[ SOLUTION-04 \] Generate OTP Code & Sending OTP Code to user via email; I did not implement email-check mechanisms here.
2. \[ SOLUTION-05 \] Restrict Login Attempts to 5 times every 20 minutes.
3. \[ SOLUTION-06 \] Implement Parameterization when querying SQLite3 Database.

#### 3. \[ VULNERABILITY-03 \] Unrestricted File Upload Vulnerability (auth.py)
---
1. \[ SOLUTION-07 \] Validate & Sanitized Files uploaded by Users. This includes:
* Checking whether file exists.
* Checking whether uploaded file format is valid (eg: jpg, jpeg, png, etc).
* Assigning Unique IDs to each image file to prevent unintended overwriting.
* Sanitizing File Names to prevent Directory Traversal attacks (Strips '../' in file name).

#### 4. \[ VULNERABILITY-04 \] Server-Side Template Injection (SSTI) Vulnerability (\_\_init\_\_.py)
---
1. \[ SOLUTION-08 \] Uses Vulnerable render_template_string() function instead of render_template() function to render Jinja2 Templates.
