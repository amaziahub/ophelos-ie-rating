# ophelos-ie-rating

## Income & Expenditure Rating API
This project provides an API to enable users to create, retrieve, and rate income and expenditure statements.
The application calculates disposable income and provides an I&E rating of the customer based on a predefined grading scale.

---

## 📌 Assumptions
1. Each statement belongs to a specific user.
2. Users are created initially, and the app assumes existing users for statements.
3. Rating calculation is based on a ratio between expenditures and incomes.
4. API can be accessed via Swagger for testing and documenting.
5. The app supports period-based rating calculation.
6. Database cleanup in tests preserves the user table.

##### All APIs include a user_id parameter to support multi-user functionality. Due to time constraints, I didn't implement a full authentication mechanism, such as token-based authentication. However, for this exercise, the user_id parameter serves as a basic approach for handling multi-user support in version 1.

---

## 🚀 Features

- Create Income & Expenditure Statements
- Calculate Disposable Income & I&E Rating
- Support Rating Calculation Over a Period of Time (feature I added, was not in requirements)
- Swagger Documentation
- Database Persistence using SQLite
- Docker Support

---

## 📂 Technologies

- Python 3.12
- FastAPI (Web Framework)
- SQLAlchemy (Database ORM)
- SQLite (Embedded Database)
- Pytest & Hamcrest (Testing Frameworks)
- Docker (Containerization)

---

## 📦 Installation

### Requirements

- Python 3.12
- Docker (For containerized deployment)
- Make (I've assembled commands in a make file for simplify common operations)

#### Available Commands

- `make install` - Install dependencies.
- `make test` - Run the test suite.
- `make run` - Start the application using Uvicorn.
- `make docker-build` - Build the Docker image.
- `make docker-run` - Run the Docker container.

You can run these commands by simply typing:

```shell
make <command>
```
Example:

```shell
make install
make run
```

#### Local Installation
```shell
# Clone the repository
$ git clone <repo_url>
$ cd <repo_name>

# Create a virtual environment
$ python3.12 -m venv venv
$ source venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt

# Run migrations and start the app
$ python app.py
```

## 🐳 Docker Usage
```shell
# Build Docker Image
$ docker build -t ie-rating-app .

# Run Docker Container
$ docker run -d -p 8080:8080 ie-rating-app
```

---

## 📖 API Documentation

The API documentation is available via Swagger UI once the application is running:

There are 2 users that are comes with the application embedded already:
**`ophelos` -> id `1` and `guest` -> id `2` please use these user_id's to test with swagger client**

```shell
http://localhost:8080/docs
```

---

## 📌 Endpoints Overview

- POST /api/statements - Submit a new statement.
- GET /api/statements?id={report_id}&user={user_id} - Retrieve a statement by ID.
- GET /api/ratings?user_id={user_id}&report_id{report_id} - Retrieve rating for specific statement.
- GET /api/ratings?user_id={user_id}&start_date={start_date}&end_date={end_date} - Retrieve rating over a period of time.

---

## 🔍 Testing
```shell
pytest
```

---
## 📌 Notes

Use valid ISO 8601 datetime format when querying period ratings.
