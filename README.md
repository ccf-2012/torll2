# torll2

## 安装
- 前端 
```sh 
cd frontend; npm install; npm run build
```

- 后端 
```sh
cd backend; 
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 启动
- 前端
```sh
cd frontend; npm start
```

- 后湍
```sh
cd backend; source venv/bin/activate
uvicorn app.main:app --port 5006 --reload
```

## 接口文档
* `/docs`, `/redoc` 
* 主要查询接口为： `/api/query`
