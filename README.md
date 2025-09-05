# 題庫系統

## 環境配置

- Python 3.9.6
- Pip 25.2
- MySQL 8.1

## 部署流程

1. 啟動 MySQL 容器
```shell
docker run --name mysql_database -e MYSQL_USER=root -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=question_bank_system -p 8888:3306 --volume mysql_database:/var/lib/mysql -d mysql:8.1
```

2. 啟動虛擬環境
```shell
pip install -r requirements.txt
python -m virtualenv .venv && source ./.venv/bin/activate
```

3. 執行 main.py
```
python3 main.py
```

## 設定檔

- `settings/configs.json`
