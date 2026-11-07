try:
    a=bytearray(1024*1024*1024)
    print("MEMORY_NOT_LIMITED",flush=True)
    raise SystemExit(5)
except MemoryError:
    print("MEMORY_LIMIT_ENFORCED",flush=True)
