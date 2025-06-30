import requests
import os
import time
import sys
import platform
import subprocess

# 配置参数
INPUT_FILE = "socks.txt"
OUTPUT_FILE = "telecom.txt"
TEST_URLS = [
    "http://www.gstatic.com/generate_204",
    "http://captive.apple.com",
    "http://www.msftconnecttest.com/connecttest.txt"
]
TIMEOUT = 8  # 增加超时时间以适应 GitHub Actions 环境
MAX_TEST_COUNT = 2000

def debug_print(message):
    """带时间戳的调试输出"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def setup_environment():
    """检查并安装必要依赖"""
    try:
        import requests
        debug_print(f"requests 版本: {requests.__version__}")
    except ImportError:
        debug_print("正在安装 requests 库...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
            debug_print("requests 安装成功")
        except Exception as e:
            debug_print(f"安装失败: {str(e)}")
            sys.exit(1)

def test_proxy(proxy):
    """测试代理连通性"""
    try:
        proxies = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }
        
        debug_print(f"测试代理: {proxy}")
        
        for url in TEST_URLS:
            try:
                start_time = time.time()
                response = requests.get(
                    url, 
                    proxies=proxies, 
                    timeout=TIMEOUT,
                    headers=headers,
                    verify=False  # 避免证书验证问题
                )
                
                latency = (time.time() - start_time) * 1000
                debug_print(f"  √ {url} 响应时间: {latency:.2f}ms, 状态码: {response.status_code}")
                
                # 检查不同服务的成功响应
                if "gstatic.com" in url and response.status_code == 204:
                    return True
                if "apple.com" in url and "Success" in response.text:
                    return True
                if "msftconnecttest.com" in url and "Microsoft Connect Test" in response.text:
                    return True
                    
            except Exception as e:
                debug_print(f"  × {url} 失败: {type(e).__name__}")
                continue
                
        return False
        
    except Exception as e:
        debug_print(f"代理测试异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("GitHub Actions 代理测试脚本")
    print("=" * 60)
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print("=" * 60)
    
    # 安装依赖
    setup_environment()
    
    # 检查输入文件
    if not os.path.exists(INPUT_FILE):
        debug_print(f"错误: {INPUT_FILE} 文件不存在")
        sys.exit(1)
    
    # 读取代理列表
    try:
        with open(INPUT_FILE, "r") as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        if not proxies:
            debug_print(f"错误: {INPUT_FILE} 为空")
            sys.exit(1)
            
        debug_print(f"找到 {len(proxies)} 个代理")
    except Exception as e:
        debug_print(f"文件读取错误: {str(e)}")
        sys.exit(1)
    
    # 初始化输出文件
    open(OUTPUT_FILE, "w").close()
    
    valid_proxies = []
    start_time = time.time()
    
    # 测试代理
    for i, proxy in enumerate(proxies):
        if len(valid_proxies) >= MAX_TEST_COUNT:
            debug_print(f"达到最大测试数 {MAX_TEST_COUNT}")
            break
            
        debug_print(f"测试代理 {i+1}/{len(proxies)}: {proxy}")
        
        if test_proxy(proxy):
            debug_print("  成功: 代理有效")
            valid_proxies.append(proxy)
            
            # 实时写入结果
            with open(OUTPUT_FILE, "a") as out:
                out.write(f"{proxy}\n")
        else:
            debug_print("  失败: 代理无效")
    
    # 生成报告
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"测试完成! 总代理: {len(proxies)}")
    print(f"有效代理: {len(valid_proxies)}")
    print(f"耗时: {elapsed:.2f} 秒")
    
    if valid_proxies:
        print("\n前5个有效代理:")
        for proxy in valid_proxies[:5]:
            print(f"  - {proxy}")
        print(f"\n完整结果已保存到 {OUTPUT_FILE}")
    else:
        print("\n未找到有效代理")
    
    print("=" * 60)

if __name__ == "__main__":
    main()