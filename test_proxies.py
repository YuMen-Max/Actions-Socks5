import requests
from concurrent.futures import ThreadPoolExecutor

# 测试的目标链接
TEST_URL = "http://www.gstatic.com/generate_204"

# 代理列表文件路径
PROXY_FILE = "proxies.txt"

# 输出结果文件路径
RESULTS_FILE = "results.txt"

# 最大测试的代理数量
MAX_PROXIES = 2000

# 读取代理列表
def load_proxies(file_path):
    """
    从文件中加载代理列表，限制最大代理数量
    """
    with open(file_path, "r") as file:
        proxies = file.read().splitlines()
    return proxies[:MAX_PROXIES]  # 限制代理数量

# 测试单个代理连通性
def test_proxy(proxy):
    """
    测试单个代理是否可以连通到目标 URL
    """
    try:
        # 解析代理
        user, password, host, port = parse_proxy(proxy)

        # 设置代理
        proxies = {
            "http": f"socks5://{user}:{password}@{host}:{port}",
            "https": f"socks5://{user}:{password}@{host}:{port}",
        }

        # 发送请求
        response = requests.get(TEST_URL, proxies=proxies, timeout=5)
        
        # 如果返回 204 状态码，表示代理正常
        if response.status_code == 204:
            return proxy  # 直接返回原始代理字符串
        else:
            return None  # 返回 None 表示失败
    except Exception:
        return None  # 返回 None 表示失败

# 解析代理字符串 (user:password@127.0.0.1:1080)
def parse_proxy(proxy):
    """
    解析代理字符串为 user, password, host, port
    """
    try:
        credentials, address = proxy.split("@")
        user, password = credentials.split(":")
        host, port = address.split(":")
        return user, password, host, port
    except ValueError:
        raise ValueError(f"Invalid proxy format: {proxy}")

# 批量测试代理
def test_proxies(proxies):
    """
    批量测试代理，返回连通性测试通过的代理列表
    """
    working_proxies = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        for result in executor.map(test_proxy, proxies):
            if result:  # 如果测试通过，result 不为 None
                working_proxies.append(result)

    return working_proxies

# 主函数
if __name__ == "__main__":
    # 清空 results.txt 文件内容
    with open(RESULTS_FILE, "w") as file:
        file.write("")  # 清空文件内容

    # 加载代理列表
    proxies = load_proxies(PROXY_FILE)

    # 测试代理
    print(f"Testing {len(proxies)} proxies...")
    working_proxies = test_proxies(proxies)

    # 保存连通性正常的代理到 results.txt
    with open(RESULTS_FILE, "w") as file:
        file.write("\n".join(working_proxies))

    print(f"Testing completed. Working proxies saved to {RESULTS_FILE}.")