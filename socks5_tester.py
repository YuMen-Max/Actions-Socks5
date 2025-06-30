import requests
import os
import time
import sys
import concurrent.futures
import logging

# 配置参数
INPUT_FILE = "socks.txt"
OUTPUT_FILE = "telecom.txt"
TEST_URL = "http://www.gstatic.com/generate_204"
TIMEOUT = 2  # 2秒超时
MAX_TEST_COUNT = 2000  # 最大测试数量
MAX_WORKERS = 50  # 并发测试线程数

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_proxy(proxy):
    """测试单个代理的连通性"""
    try:
        proxies = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}",
        }
        
        response = requests.get(
            TEST_URL, 
            proxies=proxies, 
            timeout=TIMEOUT,
            verify=False  # 避免证书验证问题
        )
        
        if response.status_code == 204:
            return True, proxy
    except Exception as e:
        pass  # 所有错误都视为失败
    
    return False, proxy

def main():
    """主函数"""
    print("=" * 60)
    print("SOCKS5 代理测试脚本")
    print(f"测试链接: {TEST_URL}")
    print(f"超时时间: {TIMEOUT}秒 | 最大测试数: {MAX_TEST_COUNT}")
    print(f"工作目录: {os.getcwd()}")
    print("=" * 60)
    
    # 检查输入文件
    if not os.path.exists(INPUT_FILE):
        logger.error(f"错误: {INPUT_FILE} 文件不存在")
        sys.exit(1)
    
    # 读取代理列表
    try:
        with open(INPUT_FILE, "r") as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        if not proxies:
            logger.error(f"错误: {INPUT_FILE} 为空")
            sys.exit(1)
            
        logger.info(f"找到 {len(proxies)} 个代理")
        
        # 限制最大测试数量
        if len(proxies) > MAX_TEST_COUNT:
            proxies = proxies[:MAX_TEST_COUNT]
            logger.info(f"限制测试数量为: {MAX_TEST_COUNT}")
    except Exception as e:
        logger.error(f"文件读取错误: {str(e)}")
        sys.exit(1)
    
    # 清空输出文件
    open(OUTPUT_FILE, "w").close()
    
    valid_proxies = []
    start_time = time.time()
    tested_count = 0
    
    # 使用线程池并发测试
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            tested_count += 1
            proxy = future_to_proxy[future]
            
            try:
                success, proxy = future.result()
                if success:
                    valid_proxies.append(proxy)
                    logger.info(f"代理有效: {proxy}")
                    
                    # 实时写入结果
                    with open(OUTPUT_FILE, "a") as out:
                        out.write(f"{proxy}\n")
            except Exception as e:
                logger.error(f"测试异常: {str(e)}")
    
    # 生成报告
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"测试完成! 总代理: {tested_count}")
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