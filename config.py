import json

def config_salver(config):
    
    # Salvar em um arquivo JSON
    with open("config.json", "w", encoding="utf-8") as arquivo:
        json.dump(config, arquivo, ensure_ascii=False, indent=4)

def config_load():
    with open("config.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
