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
MAX_WORKERS = 20  # 减少并发数，避免GitHub限制

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
        
        # 添加用户代理头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        
        # 添加超时控制
        response = requests.get(
            TEST_URL, 
            proxies=proxies, 
            timeout=TIMEOUT,
            headers=headers,
            verify=False  # 避免证书验证问题
        )
        
        if response.status_code == 204:
            return True, proxy
    except Exception as e:
        # 记录错误详情
        logger.debug(f"代理 {proxy} 失败: {str(e)}")
    
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
            raw_proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        if not raw_proxies:
            logger.error(f"错误: {INPUT_FILE} 为空")
            sys.exit(1)
            
        # 限制最大测试数量
        proxies = raw_proxies[:MAX_TEST_COUNT]
        logger.info(f"测试 {len(proxies)} 个代理 (共找到 {len(raw_proxies)} 个)")
    except Exception as e:
        logger.error(f"文件读取错误: {str(e)}")
        sys.exit(1)
    
    # 清空输出文件
    with open(OUTPUT_FILE, "w") as f:
        pass
    
    valid_proxies = []
    start_time = time.time()
    
    # 使用线程池并发测试 - 修复等待逻辑
    logger.info("开始测试代理...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有测试任务
        futures = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            proxy = futures[future]
            try:
                success, proxy = future.result()
                if success:
                    valid_proxies.append(proxy)
                    # 实时写入结果
                    with open(OUTPUT_FILE, "a") as out:
                        out.write(f"{proxy}\n")
            except Exception as e:
                logger.error(f"测试异常: {str(e)}")
    
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
    
    # 额外调试信息
    if len(valid_proxies) == 0:
        logger.warning("未找到任何有效代理，可能原因:")
        logger.warning("1. 所有代理均不可用")
        logger.warning("2. GitHub Actions 网络限制")
        logger.warning("3. 测试URL被阻止")
        logger.warning("建议手动测试几个代理以验证")

if __name__ == "__main__":
    main()