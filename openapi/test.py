import json
import yaml

# Load JSON data from a file
with open('openapi/spec/conf.json', 'r') as json_file:
    data = json.load(json_file)

# Convert and save as YAML
with open('openapi/spec/confluence.yaml', 'w') as yaml_file:
    yaml.dump(data, yaml_file, sort_keys=False)
