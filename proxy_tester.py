import os
import time
import re
import requests
from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, ConnectionError

def extract_proxy(line):
    """从复杂文本中提取标准代理格式 (user:password@ip:port)"""
    # 尝试匹配标准格式
    standard_match = re.search(r'([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', line)
    if standard_match:
        return standard_match.group(1)
    
    # 尝试匹配带socks5://前缀的格式
    socks5_match = re.search(r'socks5://([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', line)
    if socks5_match:
        return socks5_match.group(1)
    
    # 尝试匹配带#注释的格式
    comment_match = re.search(r'([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)#', line)
    if comment_match:
        return comment_match.group(1)
    
    return None

def test_proxy(proxy):
    """测试单个SOCKS5代理的连通性"""
    proxies = {
        'http': f'socks5://{proxy}',
        'https': f'socks5://{proxy}'
    }
    
    try:
        start = time.time()
        response = requests.get(
            'http://www.gstatic.com/generate_204',
            proxies=proxies,
            timeout=2
        )
        latency = int((time.time() - start) * 1000)
        
        if response.status_code == 204:
            print(f"✅ 有效代理: {proxy} | 延迟: {latency}ms")
            return True
    except (ProxyError, ConnectTimeout, ReadTimeout, ConnectionError):
        pass
    except Exception as e:
        print(f"⚠️ 测试异常: {proxy} | 错误: {str(e)}")
    
    print(f"❌ 无效代理: {proxy}")
    return False

def read_input_proxies(input_file):
    """从输入文件读取并提取代理"""
    if not os.path.exists(input_file):
        print(f"⚠️ 输入文件不存在: {input_file}")
        return []
    
    try:
        with open(input_file, 'r') as f:
            extracted_proxies = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                proxy = extract_proxy(line)
                if proxy:
                    extracted_proxies.append(proxy)
                else:
                    print(f"⚠️ 无法提取代理: {line}")
            
            print(f"📖 从 {input_file} 提取 {len(extracted_proxies)} 个代理")
            return extracted_proxies
    except Exception as e:
        print(f"⚠️ 读取文件 {input_file} 失败: {str(e)}")
        return []

def save_valid_proxies(valid_proxies, output_file):
    """保存有效代理到输出文件（格式为 socks5://账号:密码@ip:端口）"""
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 修改这里：添加 socks5:// 前缀
        formatted_proxies = [f"socks5://{proxy}" for proxy in valid_proxies]
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(formatted_proxies))
        print(f"📁 保存 {len(valid_proxies)} 个有效代理到 {output_file} (格式: socks5://账号:密码@ip:端口)")
        return True
    except Exception as e:
        print(f"⚠️ 保存文件 {output_file} 失败: {str(e)}")
        return False

def main():
    try:
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"📂 脚本目录: {script_dir}")
        
        # 配置输入输出文件（使用绝对路径）
        input_file = os.path.join(script_dir, "china.txt")
        output_file = os.path.join(script_dir, "telecom.txt")
        
        print(f"📝 输入文件路径: {input_file}")
        print(f"💾 输出文件路径: {output_file}")
        
        # 确保输入文件存在
        if not os.path.exists(input_file):
            print(f"❌ 错误: 输入文件 {input_file} 不存在")
            return 0
        
        # 读取并提取输入代理
        all_proxies = read_input_proxies(input_file)
        print(f"🔍 总代理数: {len(all_proxies)}")
        
        if not all_proxies:
            print("⚠️ 未找到任何代理，跳过测试")
            return 0
        
        # 测试所有代理
        valid_proxies = []
        for i, proxy in enumerate(all_proxies):
            if test_proxy(proxy):
                valid_proxies.append(proxy)
            
            # 每测试100个代理打印一次进度
            if (i + 1) % 100 == 0:
                print(f"⏳ 测试进度: {i+1}/{len(all_proxies)} | 有效代理: {len(valid_proxies)}")
        
        # 保存有效代理（格式已修改）
        if valid_proxies:
            save_valid_proxies(valid_proxies, output_file)
        else:
            # 如果没有有效代理，清空输出文件
            with open(output_file, 'w') as f:
                f.write('')
            print("📁 清空输出文件（无有效代理）")
        
        # 验证文件是否保存成功
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                content = f.read()
                print(f"📄 输出文件内容 (前100字符): {content[:100]}{'...' if len(content) > 100 else ''}")
                print(f"📏 文件大小: {len(content)} 字符")
        else:
            print("❌ 输出文件未创建")
        
        print(f"\n✅ 测试完成 - 有效代理: {len(valid_proxies)}/{len(all_proxies)}")
        return len(valid_proxies)
    
    except Exception as e:
        print(f"🔥 主函数异常: {str(e)}")
        return 0

if __name__ == "__main__":
    main()