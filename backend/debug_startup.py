try:
    from aegis.api.schemas import ChatCompletionResponse
    print("Schema imported successfully")
except Exception as e:
    print(f"SCHEMA ERROR: {e}")

try:
    from aegis.api.router import router
    print("Router imported successfully")
except Exception as e:
    print(f"ROUTER ERROR: {e}")
