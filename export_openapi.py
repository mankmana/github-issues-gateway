import yaml

from main import app


with open("openapi.yaml", "w") as file:
    yaml.safe_dump(app.openapi(), file, sort_keys=False)

print("Created openapi.yaml")
