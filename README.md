# 🛡️ **Vulnera**

### ⚠️ **WARNING:** Do not use this in production or on public networks.
**Vulnera** is a *deliberately vulnerable* web application designed for penetration testers to practice and test their skills.

- ❌ **DO NOT** expose this application to the internet.
- ❌ **DO NOT** run it in a production or corporate network.
- ✅ **DO** run it in a local, isolated, sandboxed, or virtualized environment.

Running vulnera on an exposed or production interface may lead to **real-world security breaches** or **unintended access**.

> ⚠️ *All images used in the application are licensed under free use.*

---

## 📦 Requirements

### Manual:
- **Python** 3.8+
- **PostgreSQL**
- **Git**

### Docker:
- **Git**
- **Docker**

---

## 🚀 Installation Guide - Manual

### 1. Clone the Repository

```bash
git clone https://github.com/Xer4n/vulnera.git
cd vulnera
```

---

### 2. Set Up the PostgreSQL Database

```bash
sudo -u postgres psql
```

Inside the PostgreSQL shell:

```sql
CREATE DATABASE vulneradb;
ALTER USER postgres WITH PASSWORD 'vulnera';
```

> 💡 **Tip:** You can use your own database user.
> Just update the credentials in `database.py`.
> This configuration allows for more complex database exploitation scenarios.
> For safer use, set up a regular user and adjust `database.py` accordingly.

---

### 3. Install Python Dependencies

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

---


### 4. Run the Application

You can run the app using either:

**Flask server:**

```bash
flask run
```

**Development server:**

```bash
python3 app.py
```

---

## 🐳 Running with Docker (Single Container)

For an easy setup that runs both the **PostgreSQL database** and the **Flask app** in a single container, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/Xer4n/vulnera.git
cd vulnera
```

### 2. Build the Docker image
```bash
docker build -t vulnera .
```
> 💡 **Tip:** This command might require administrative priviledges (sudo).

### 3. Run the Docker image
```bash
docker run -p 5000:5000 --privileged vulnera
```

---

## 🖥 Accessing the application

Once the application is running (either manually or via Docker):

1. Open your web browser
2. Navigate to ``127.0.0.1:5000`` or ``locahost:5000``

>  ⚠️ **Important:** Ensure that you're accessing the app from a local and isolated environment. **Do not** expose port ``5000`` to public networks or shared systems.

> ✅ On first launch, click the **"Init Database"** button in the bottom-right corner to populate the app with sample products.
## 💰 Codes for valuta

The following codes can be entered in the application to give the user vulnera coins!

- xss
- sqli
- vulnera
- csrf
