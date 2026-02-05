# Testing AegisProxy

This guide explains how to verify that **AegisProxy** is working correctly.

## 1. System Components

- **Backend (Port 8080)**: The AI Proxy that intercepts and filters traffic.
- **Frontend (Port 5173)**: The Mission Control dashboard monitoring the backend.

## 2. Running the Test Suite

We have included a Python script `test_proxy.py` that simulates various traffic scenarios.

1.  Make sure your python environment is active (or use the full path to python).
2.  Run the script:

```powershell
python test_proxy.py
```

### Expected Results

The script runs 5 scenarios:

1.  **Safe Request**: Should **PASS** (HTTP 200).
2.  **PII (Email)**: Should **PASS** but the email will be **REDACTED** in the logs/response.
3.  **PII (API Key)**: Should **PASS** but the key is **REDACTED**.
4.  **Injection**: "Ignore previous instructions" -> Should be **BLOCKED** (HTTP 403).
5.  **Jailbreak**: "You are DAN..." -> Should be **BLOCKED** (HTTP 403).

## 3. Verifying in Dashboard

1.  Open [http://localhost:5173](http://localhost:5173) in your browser.
2.  Watch the cards update in real-time (5s poll interval):
    - **Total Requests**: Should increase by 5.
    - **Threats Blocked**: Should increase by 2 (the injection attempts).
    - **PII Detected**: Should increase by 2 (the email and API key).
    - **Traffic Chart**: Should show a mix of Blue (Allowed) and Red (Blocked) traffic.

## 4. Manual Testing (cURL)

You can also send a request manually using cURL:

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello world!"}]
  }'
```
