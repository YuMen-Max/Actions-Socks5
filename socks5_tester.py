import requests
from requests.exceptions import RequestException
import os

# 输入和输出文件路径
input_file = "socks.txt"  # 输入文件，保存需要测试的 SOCKS5 代理列表
output_file = "telecom.txt"  # 输出文件，仅保存测试通过的代理

# 测试 URL 和超时时间
test_url = "http://www.gstatic.com/generate_204"
timeout = 2  # 设置超时时间为 2 秒

# 测试最大代理数量
max_test_count = 2000

def test_proxy(proxy):
    """
    测试单个 SOCKS5 代理的连通性
    :param proxy: 代理地址，格式为 user:password@127.0.0.1:1080
    :return: 是否测试通过
    """
    try:
        proxies = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}",
        }
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        return response.status_code == 204  # 返回 204 表示成功
    except RequestException:
        return False

def main():
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"输入文件 {input_file} 不存在，请创建并填入代理列表。")
        return

    # 每次运行前清空输出文件内容
    open(output_file, "w").close()

    # 读取代理 IP 列表
    with open(input_file, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]

    # 初始化通过代理的结果列表
    valid_proxies = []

    # 测试代理连通性
    print(f"开始测试代理，共 {len(proxies)} 个代理...")
    for i, proxy in enumerate(proxies):
        # 达到测试上限时停止
        if len(valid_proxies) >= max_test_count:
            print("达到最大测试数量，停止测试。")
            break

        print(f"正在测试第 {i + 1}/{len(proxies)} 个代理: {proxy}")
        if test_proxy(proxy):
            print(f"代理 {proxy} 测试通过！")
            valid_proxies.append(proxy)
        else:
            print(f"代理 {proxy} 测试失败。")

    # 保存通过的代理到输出文件
    with open(output_file, "w") as file:
        file.write("\n".join(valid_proxies))

    print(f"测试完成，共有 {len(valid_proxies)} 个代理通过测试，结果已保存到 {output_file}。")

if __name__ == "__main__":
    main()
