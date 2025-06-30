import requests
from concurrent.futures import ThreadPoolExecutor

# 测试的目标链接
TEST_URL = "http://www.gstatic.com/generate_204"

# 代理列表文件路径
PROXY_FILE = "proxies.txt"

# 输出结果文件路径
RESULTS_FILE = "results.txt"

# 仅保存连通性正常的代理的文件路径
WORKING_PROXIES_FILE = "working_proxies.txt"

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
            return f"SUCCESS: {proxy}"
        else:
            return f"FAILED: {proxy} - Status Code: {response.status_code}"
    except Exception as e:
        return f"FAILED: {proxy} - Error: {e}"

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
    批量测试代理
    """
    results = []
    working_proxies = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        for result in executor.map(test_proxy, proxies):
            results.append(result)
            if result.startswith("SUCCESS"):
                # 确保字符串闭合（修复错误）
                working_proxies.append(result.split("SUCCESS: ")[1])

    return results, working_proxies

# 主函数
if __name__ == "__main__":
    # 加载代理列表
    proxies = load_proxies(PROXY_FILE)

    # 测试代理
    print(f"Testing {len(proxies)} proxies...")
    results, working_proxies = test_proxies(proxies)

    # 保存所有结果到文件
    with open(RESULTS_FILE, "w") as file:
        file.write("\n".join(results))

    # 保存连通性正常的代理到文件
    with open(WORKING_PROXIES_FILE, "w") as file:
        file.write("\n".join(working_proxies))

    print(f"Testing completed. Results saved to {RESULTS_FILE}.")
    print(f"Working proxies saved to {WORKING_PROXIES_FILE}.")