import requests
from requests.exceptions import RequestException
import os
import time
import sys

# 配置参数
input_file = "socks.txt"
output_file = "telecom.txt"
test_url = "http://www.gstatic.com/generate_204"
timeout = 5  # 增加超时时间
max_test_count = 2000

def debug_print(message):
    """带时间戳的调试输出"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_proxy(proxy):
    """测试代理连通性，返回布尔值和详细信息"""
    try:
        proxies = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}",
        }
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
        
        debug_print(f"测试代理: {proxy}")
        start_time = time.time()
        
        response = requests.get(
            test_url, 
            proxies=proxies, 
            timeout=timeout,
            headers=headers
        )
        
        latency = (time.time() - start_time) * 1000
        debug_print(f"代理 {proxy} 响应时间: {latency:.2f}ms, 状态码: {response.status_code}")
        
        return response.status_code == 204
    
    except RequestException as e:
        debug_print(f"代理 {proxy} 请求失败: {type(e).__name__} - {str(e)}")
        return False
    except Exception as e:
        debug_print(f"代理 {proxy} 发生未知错误: {str(e)}")
        return False

def main():
    """主函数，处理代理测试流程"""
    debug_print("=" * 50)
    debug_print("开始代理测试脚本")
    debug_print(f"工作目录: {os.getcwd()}")
    
    # 检查输入文件
    if not os.path.exists(input_file):
        debug_print(f"错误: 输入文件 {input_file} 不存在!")
        debug_print("请确保文件位于脚本同一目录")
        sys.exit(1)
    
    # 检查文件内容
    with open(input_file, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]
    
    if not proxies:
        debug_print(f"错误: 输入文件 {input_file} 为空!")
        debug_print("请添加代理地址，格式如: 127.0.0.1:1080 或 user:pass@192.168.1.1:1080")
        sys.exit(1)
    
    debug_print(f"找到 {len(proxies)} 个代理，开始测试...")
    debug_print(f"测试URL: {test_url}")
    
    # 初始化输出文件
    open(output_file, "w").close()
    
    valid_proxies = []
    total_count = len(proxies)
    
    for i, proxy in enumerate(proxies):
        if len(valid_proxies) >= max_test_count:
            debug_print(f"已达到最大测试数量 {max_test_count}，停止测试")
            break
            
        debug_print(f"进度: {i+1}/{total_count} | 有效: {len(valid_proxies)}")
        
        if test_proxy(proxy):
            debug_print(f"[成功] 代理 {proxy} 有效")
            valid_proxies.append(proxy)
            
            # 实时写入结果
            with open(output_file, "a") as out_file:
                out_file.write(f"{proxy}\n")
        else:
            debug_print(f"[失败] 代理 {proxy} 无效")
    
    # 最终报告
    debug_print("=" * 50)
    debug_print(f"测试完成! 总代理: {total_count}, 有效代理: {len(valid_proxies)}")
    
    if valid_proxies:
        debug_print(f"有效代理已保存到: {os.path.abspath(output_file)}")
        debug_print("前5个有效代理:")
        for i, proxy in enumerate(valid_proxies[:5]):
            debug_print(f"{i+1}. {proxy}")
    else:
        debug_print("没有找到有效代理，请检查代理列表和网络连接")

if __name__ == "__main__":
    main()