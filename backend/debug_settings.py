from aegis.config import get_settings
try:
    s = get_settings()
    print(f"Settings loaded: {s.model_dump()}")
except Exception as e:
    import traceback
    traceback.print_exc()
