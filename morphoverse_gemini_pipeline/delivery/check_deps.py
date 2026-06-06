import importlib, sys
pkgs = ["torch", "transformers", "sentence_transformers", "faiss", "numpy"]
for p in pkgs:
    try:
        m = importlib.import_module(p)
        v = getattr(m, "__version__", "?")
        print(f"OK    {p}=={v}")
    except Exception as e:
        print(f"MISS  {p} -> {e}")
