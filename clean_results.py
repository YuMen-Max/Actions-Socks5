def clean_results(file_path):
    """
    清理 results.txt 文件：
    1. 移除所有以 "FAILED:" 开头的行。
    2. 去掉所有以 "SUCCESS:" 开头的行的前缀，只保留代理地址。
    """
    cleaned_proxies = []

    # 读取文件并处理内容
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("SUCCESS:"):
                # 去掉 SUCCESS: 前缀，仅保留代理地址
                cleaned_proxies.append(line.replace("SUCCESS: ", ""))
            elif line.startswith("FAILED:"):
                # 跳过 FAILED 条目
                continue

    # 将清理后的内容写回文件
    with open(file_path, "w") as file:
        file.write("\n".join(cleaned_proxies) + "\n")

    print(f"清理完成！已更新文件: {file_path}")


if __name__ == "__main__":
    # 指定 results.txt 文件路径
    results_file_path = "results.txt"
    clean_results(results_file_path)