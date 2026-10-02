运行方式：
''
    cd src
    //D:\develop\projects\Agent\Rgent\ragent\src>
    python -m loop.Agent
    将src目录加入sys.path，后续所有自定义模块包均从src下开始找
''

架构：
ragent
     |_src
     |   |_loop
     |   |_hooks
     |   |_tools
     |_test
     |_workspace