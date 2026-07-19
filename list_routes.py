from backend.app import create_app
app = create_app()

rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)
for r in rules:
    methods = sorted(r.methods - set(['HEAD','OPTIONS']))
    print(f"{r.rule:40} -> {','.join(methods)}")
