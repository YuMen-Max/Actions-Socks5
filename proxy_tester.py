import os
import time
import re
import requests
from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, ConnectionError
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_proxy(line):
    pattern = r'(?:socks5://)?([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)(?:#.*)?'
    match = re.search(pattern, line)
    return match.group(1) if match else None

def test_proxy(proxy):
    proxies = {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
    try:
        start = time.time()
        response = requests.get('http://www.gstatic.com/generate_204', proxies=proxies, timeout=2)
        latency = int((time.time() - start) * 1000)
        if response.status_code == 204:
            logging.info(f"✅ 有效代理: {proxy} | 延迟: {latency}ms")
            return proxy
    except (ProxyError, ConnectTimeout, ReadTimeout, ConnectionError):
        pass
    except Exception as e:
        logging.warning(f"⚠️ 测试异常: {proxy} | 错误: {str(e)}")
    logging.info(f"❌ 无效代理: {proxy}")
    return None

def read_input_proxies(input_file):
    if not os.path.exists(input_file):
        logging.warning(f"⚠️ 输入文件不存在: {input_file}")
        return []
    try:
        with open(input_file, 'r') as f:
            proxies = [extract_proxy(line.strip()) for line in f if line.strip()]
            proxies = [p for p in proxies if p]
            logging.info(f"📖 从 {input_file} 提取 {len(proxies)} 个代理")
            return proxies
    except Exception as e:
        logging.error(f"⚠️ 读取文件 {input_file} 失败: {str(e)}")
        return []

def save_valid_proxies(valid_proxies, output_file):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write('\n'.join(valid_proxies))
        logging.info(f"📁 保存 {len(valid_proxies)} 个有效代理到 {output_file}")
        return True
    except Exception as e:
        logging.error(f"⚠️ 保存文件 {output_file} 失败: {str(e)}")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "china.txt")
    output_file = os.path.join(script_dir, "telecom.txt")
    logging.info(f"📂 脚本目录: {script_dir}")
    logging.info(f"📝 输入文件路径: {input_file}")
    logging.info(f"💾 输出文件路径: {output_file}")

    if not os.path.exists(input_file):
        logging.error(f"❌ 输入文件 {input_file} 不存在")
        return 0

    all_proxies = read_input_proxies(input_file)
    if not all_proxies:
        logging.warning("⚠️ 未找到任何代理，跳过测试")
        return 0

    valid_proxies = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in all_proxies}
        for future in tqdm(as_completed(future_to_proxy), total=len(all_proxies), desc="测试代理"):
            result = future.result()
            if result:
                valid_proxies.append(result)

    if valid_proxies:
        save_valid_proxies(valid_proxies, output_file)
    else:
        with open(output_file, 'w') as f:
            f.write('')
        logging.info("📁 清空输出文件（无有效代理）")

    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            content = f.read()
            logging.info(f"📄 输出文件内容 (前100字符): {content[:100]}{'...' if len(content) > 100 else ''}")
            logging.info(f"📏 文件大小: {len(content)} 字符")

    logging.info(f"✅ 测试完成 - 有效代理: {len(valid_proxies)}/{len(all_proxies)}")
    return len(valid_proxies)

if __name__ == "__main__":
    main()