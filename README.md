# torll2

## 安装
* 前端 
```sh 
cd frontend/torll 
# 在 torll2/frontend/torll 目录下
npm install; npm run build
```

* 后端 
```sh
cd backend; 
# 在 torll2/backend 目录下
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
* 初始化数据库
```sh
cd backend; 
# 在 torll2/backend 目录下
alembic upgrade head
```


### 启动
* 前端，启动在5106
```sh
cd frontend/torll 
# 在 torll2/frontend/torll 目录下
npm start
```
> 端口设置在 package.json 


* 后湍，启动在5006
```sh
cd backend; 
# 在 torll2/backend 目录下
source venv/bin/activate
uvicorn torll.main:app --port 5006 --reload
```
> 后端监听端口要配合前端所设proxy地址，另将来会接收来自torfilter的api请求，届时还需有 `--host 0.0.0.0` 参数



## 接口文档
* `/docs`, `/redoc` 
* 主要查询接口为： `/api/query`



## vscode中调试
* launch.json
```json
{
    // torll2/.vscode/launch.json
    "version": "0.2.0",
    "configurations": [
   
        {
            "name": "Python Debugger: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "torll.main:app",
                "--reload"
            ],
            "cwd": "${workspaceFolder}/backend",
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```


