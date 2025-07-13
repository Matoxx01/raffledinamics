# Dynamic Raffle Web Application

A fast, secure, and dynamic raffle application built with FastAPI, MySQL, and Stripe, allowing users to participate in raffles and administrators to manage prizes and draws effortlessly.

---

## Table of Contents

1. [Features](#features)
2. [Technologies](#technologies)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Database Schema](#database-schema)
7. [Usage](#usage)
8. [Folder Structure](#folder-structure)
9. [Contributing](#contributing)
10. [License](#license)

---

## Features

* **Dynamic Raffle Creation**: Create raffles with custom names, descriptions, costs, and draw dates.
* **User Management**: Register and manage participants, capturing essential details (first name, last name, email, phone).
* **Purchase & Number Allocation**: Users can purchase multiple raffle numbers; each purchase generates unique numbers linked to the purchase.
* **Secure Payments**: Integrated with Stripe for secure payment processing.
* **Email Notifications**: Automated email confirmations via Gmail (using App Passwords.

---

## Technologies

* **Back-end**: Python, FastAPI
* **Database**: MySQL
* **Templating**: Jinja2
* **Front-end**: HTML, CSS, JavaScript
* **Payments**: Stripe API
* **Email**: SMTP (smtplib)
* **Environment Management**: python-dotenv

---

## Prerequisites

* Python 3.9 or higher
* MySQL Server
* Stripe Account
* Gmail Account with App Password

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Matoxx01/raffledinamics.git
   cd raffledinamics
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

1. **Create a ********************************************************************`.env`******************************************************************** file** in the project root:

   ```dotenv
   host=YOUR_DATABASE_HOST
   user=YOUR_DATABASE_USER
   password=YOUR_DATABASE_PASSWORD
   port=YOUR_DATABASE_PORT
   database=YOUR_DATABASE_NAME

   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLIC_KEY=pk_test_...

   DOMAIN=localhost:8000  # or https://example.com

   GMAIL_USER=your.email@gmail.com
   GMAIL_PASS=your_app_password
   ```

2. **Load environment variables**

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## Database Schema

```sql
-- Table: app_user
CREATE TABLE app_user (
  id INT(11) PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL
);

-- Table: prize
CREATE TABLE prize (
  id INT(11) PRIMARY KEY,
  name VARCHAR(100) NOT NULL
);

-- Table: raffle
CREATE TABLE raffle (
  id INT(11) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  cost INT(11) NOT NULL DEFAULT 0,
  datelottery DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Table: purchase
CREATE TABLE purchase (
  id INT(11) PRIMARY KEY,
  user_id INT(11) NOT NULL,
  quantity INT(11) NOT NULL,
  paid TINYINT(1) DEFAULT 0,
  token VARCHAR(255),
  FOREIGN KEY (user_id) REFERENCES app_user(id)
);

-- Table: number
CREATE TABLE number (
  id INT(11) PRIMARY KEY,
  purchase_id INT(11) NOT NULL,
  number INT(11) NOT NULL,
  FOREIGN KEY (purchase_id) REFERENCES purchase(id)
);
```

---

## Usage

1. **Start the FastAPI server**

   ```bash
   uvicorn main:app --reload
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:8000`.

3. **Create a Raffle**

   * Navigate to the admin dashboard and fill out the raffle creation form.

4. **Participate in a Raffle**

   * Register as a user or log in.
   * Select a raffle and choose the quantity of numbers to purchase.
   * Complete the Stripe payment.
   * Receive a confirmation email with your allocated numbers.

---

## Required Libraries

```python
import os
import stripe
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
from pydantic import BaseModel
import smtplib
from email.message import EmailMessage

```
IF YOU PUT `$ pip install -r requirements.txt` ITS FINE


---

## Folder Structure

```
├── main.py             # FastAPI application entrypoint
├── templates/          # Jinja2 templates (HTML files)
├── static/
│   ├── styles.css
│   ├── favicon.ico
│   ├── land.png
│   └── script.js
├── README.md
├── requirements.txt
├── .env
└── schema_report.txt
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for bug fixes, enhancements, or new features.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.