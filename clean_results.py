def clean_results(file_path):
    """
    清理 results.txt 文件，移除 FAILED 条目并去掉 SUCCESS 前缀
    """
    cleaned_proxies = []

    # 读取文件并处理内容
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("SUCCESS:"):
                # 去掉 SUCCESS: 前缀，保留原始代理格式
                cleaned_proxies.append(line.replace("SUCCESS: ", ""))
            elif line.startswith("FAILED:"):
                # 跳过 FAILED 条目
                continue

    # 清理后的内容写回文件
    with open(file_path, "w") as file:
        file.write("\n".join(cleaned_proxies))

    print(f"清理完成！已保存到 {file_path}")


if __name__ == "__main__":
    # 指定 results.txt 文件路径
    results_file_path = "results.txt"
    clean_results(results_file_path)