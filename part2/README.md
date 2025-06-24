
# HBnB API Testing Report

This document summarizes the manual cURL-based tests performed against the HBnB Flask-RESTx API. It includes the commands used, expected vs. actual results, and Pass/Fail status for each test.

---

## Prerequisites

* Python 3.10+, Flask-RESTx
* Server running at `http://127.0.0.1:5000`
* No server restart between dependent tests (in-memory store)

---

## Test Summary

| Test # | Endpoint                          | Scenario               | Expected Status |         Actual Status         | Pass/Fail | Notes                                      |
| :----: | --------------------------------- | ---------------------- | :-------------: | :---------------------------: | :-------: | ------------------------------------------ |
|    1   | `POST /api/v1/users/`             | Create valid user      |   201 Created   |          201 Created          |    Pass   |                                            |
|    2   | `POST /api/v1/users/`             | Invalid user data      | 400 Bad Request |        400 Bad Request        |    Pass   | Returned `{ message: Invalid input data }` |
|    3   | `GET /api/v1/users/{nonexistent}` | Retrieve missing user  |  404 Not Found  |         404 Not Found         |    Pass   | `{ message: User not found }`              |
|    4   | `POST /api/v1/places/`            | Create valid place     |   201 Created   |          201 Created          |    Pass   |                                            |
|    5   | `POST /api/v1/places/`            | Negative price         | 400 Bad Request |        400 Bad Request        |    Pass   | `{ message: Invalid input data }`          |
|    6   | `POST /api/v1/places/`            | Latitude out of range  | 400 Bad Request |        400 Bad Request        |    Pass   | `{ message: Invalid input data }`          |
|    7   | `POST /api/v1/reviews/`           | Create valid review    |   201 Created   |        400 Bad Request        |    Fail   | In-memory user not found                   |
|    8   | `POST /api/v1/reviews/`           | Empty review text      | 400 Bad Request |        400 Bad Request        |    Fail   | Fails earlier on invalid user\_id          |
|    9   | `POST /api/v1/reviews/`           | Non-existent relations | 400 Bad Request | *not tested due to 7 failure* |   *n/a*   |                                            |

---

## Detailed Test Commands

### 1) Create User (Valid)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name":  "Smith",
    "email":      "alice.smith@example.org"
  }'
```

### 2) Create User (Invalid)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "",
    "last_name":  "",
    "email":      "not-an-email"
  }'
```

### 3) Retrieve Non-Existent User

```bash
curl -i http://127.0.0.1:5000/api/v1/users/00000000-0000-0000-0000-000000000000
```

### 4) Create Place (Valid)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/places/ \
  -H "Content-Type: application/json" \
  -d '{
    "title":       "Cozy Cabin",
    "description": "A secluded mountain retreat",
    "price":       120.50,
    "latitude":    45.123,
    "longitude":   -73.456,
    "owner_id":    "<USER_ID>",
    "amenities":   []
  }'
```

### 5) Create Place (Negative Price)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/places/ \
  -H "Content-Type: application/json" \
  -d '{
    "title":     "Budget Room",
    "price":     -10,
    "latitude":  10,
    "longitude": 10,
    "owner_id":  "<USER_ID>",
    "amenities": []
  }'
```

### 6) Create Place (Latitude OOR)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/places/ \
  -H "Content-Type: application/json" \
  -d '{
    "title":     "Polar Station",
    "price":     200,
    "latitude":  123.456,
    "longitude": 0,
    "owner_id":  "<USER_ID>",
    "amenities": []
  }'
```

### 7) Create Review (Valid)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":  "<USER_ID>",
    "place_id": "<PLACE_ID>",
    "text":     "Loved my stay!",
    "rating":   5
  }'
```

### 8) Create Review (Empty Text)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":  "<USER_ID>",
    "place_id": "<PLACE_ID>",
    "text":     "",
    "rating":   5
  }'
```

### 9) Create Review (Bad Relations)

```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":  "00000000-0000-0000-0000-000000000000",
    "place_id": "00000000-0000-0000-0000-000000000000",
    "text":     "Test",
    "rating":   3
  }'
```

---

## Notes & Next Steps

* **In-memory store** clears on server restart. Keep the process alive when chaining dependent tests.
* Implement persistence for longevity or run automated unit tests with fixtures.
* Fix the reviews endpoint to check `text` before `user_id`, if desired.

---

*End of Report*
