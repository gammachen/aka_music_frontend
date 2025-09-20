import ollama
from huggingface_hub import hf_hub_download
import os

# 确保本地已安装ollama并下载了granite3.2-vision模型
# 安装命令: pip install ollama
# 下载模型: ollama pull granite3.2-vision

def main():
    # 模型名称
    model_name = "granite3.2-vision"

    # 从Hugging Face Hub下载示例图片
    model_path = "ibm-granite/granite-vision-3.2-2b"
    # img_path = hf_hub_download(repo_id=model_path, filename='example.png')
    img_path = "example.png"
    
    print(img_path)

    # 确保图片文件存在
    if not os.path.exists(img_path):
        print(f"图片文件不存在: {img_path}")
        return

    # 文本查询
    query = "What is the highest scoring model on ChartQA and what is its score?"

    try:
        # 调用本地ollama服务
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': query,
                    'images': [img_path]
                }
            ]
        )

        # 打印响应
        print("模型响应:")
        print(response['message']['content'])

    except Exception as e:
        print(f"调用ollama服务时出错: {str(e)}")
        print("请确保ollama服务正在运行，并且已下载granite3.2-vision模型。")


    img_path = "17-六种负载均衡算法.jpeg"
    query = "图中哪六种负载均衡算法？"

    try:
        # 调用本地ollama服务
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': query,
                    'images': [img_path]
                }
            ]
        )

        # 打印响应
        print("模型响应:")
        print(response['message']['content'])

    except Exception as e:
        print(f"调用ollama服务时出错: {str(e)}")
        print("请确保ollama服务正在运行，并且已下载granite3.2-vision模型。")
        
    img_path = "17-六种负载均衡算法.jpeg"
    query = "请描述这张图里面的主要内容"

    try:
        # 调用本地ollama服务
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': query,
                    'images': [img_path]
                }
            ]
        )

        # 打印响应
        print("模型响应:")
        print(response['message']['content'])

    except Exception as e:
        print(f"调用ollama服务时出错: {str(e)}")
        print("请确保ollama服务正在运行，并且已下载granite3.2-vision模型。")
        
    '''
    example.png
模型响应:

The highest scoring model on ChartQA is Molmo-E with a score of 0.87.
模型响应:

轮询、轮询+随机选择、轮询+最佳节点选择、轮询+最小路径选择、轮询+平均路径选择、轮询+最短路径选择
模型响应:

### 图片描述

The image is a colorful infographic that appears to be explaining various aspects of cloud computing services in Chinese. The infographic is divided into six sections, each depicting different types of cloud services and their respective features or benefits. Each section includes both textual information and visual representations such as icons and diagrams.

#### Section 1: Cloud Storage Services
- **Description**: This section likely discusses the storage capabilities provided by cloud computing services. It may include details about data storage options, scalability, and security measures.
- **Visual Elements**: Icons of servers or storage devices are used to represent this section.

#### Section 2: Cloud Computing Platforms
- **Description**: This section probably covers the platforms that enable users to build, deploy, and manage applications in the cloud. It might include details about different types of platforms (e.g., IaaS, PaaS, SaaS) and their use cases.
- **Visual Elements**: Icons of servers or application icons are used here.

#### Section 3: Cloud Security Services
- **Description**: This section likely focuses on the security measures and features provided by cloud computing services to protect data and applications from threats. It may include details about encryption, access controls, and disaster recovery options.
- **Visual Elements**: Icons of locks or shields are used here.

#### Section 4: Cloud Backup Services
- **Description**: This section probably discusses the backup services offered by cloud computing platforms to ensure data integrity and availability. It might include details about different types of backups (e.g., full, incremental, differential) and their frequency.
- **Visual Elements**: Icons of clouds or storage devices are used here.

#### Section 5: Cloud Migration Services
- **Description**: This section likely covers the services that help users migrate their applications and data from on-premises environments to cloud computing platforms. It might include details about different migration strategies (e.g., lift-and-shift, rehost, refactor) and tools used for this process.
- **Visual Elements**: Icons of servers or network diagrams are used here.

#### Section 6: Cloud Management Services
- **Description**: This section probably discusses the management services provided by cloud computing platforms to help users monitor, manage, and optimize their cloud resources. It might include details about monitoring tools, automation capabilities, and cost optimization strategies.
- **Visual Elements**: Icons of dashboards or control panels are used here.

### Analysis and Description

The infographic is designed to provide a comprehensive overview of various aspects of cloud computing services in Chinese. Each section uses visual elements such as icons and diagrams to enhance understanding and retention of the information presented. The use of different colors for each section helps distinguish between them, making it easier for viewers to follow along.

The infographic is structured in a logical manner, starting with general cloud computing services (storage, platforms, security) and progressing to more specific services (backup, migration, management). This structure allows viewers to build a comprehensive understanding of the various components that make up cloud computing services.

### Conclusion

The infographic is an effective educational tool for explaining different aspects of cloud computing services in Chinese. By using visual elements and structured sections, it provides a clear and concise overview of the key features and benefits of cloud computing services. This information can be valuable for individuals looking to understand or utilize cloud computing platforms effectively.
    '''
    
    img_path = "table_image.png"
    querys = [
        {
            "question_cn": "2024-05-13这一天的体重是多少？",
            "question_en": "What is the weight on May 13, 2024?"
        },
        {
            "question_cn": "数据集中所有体重数据的平均值是多少？",
            "question_en": "What is the average weight across all data entries in the dataset?"
        },
        {
            "question_cn": "哪一天的睡眠时长最长？具体时长是多少小时？",
            "question_en": "Which day had the longest sleep duration? How many hours specifically?"
        },
        {
            "question_cn": "在这些数据中，跳绳次数最多的那一天是哪一天？跳了多少次？",
            "question_en": "Among these data points, which day had the highest number of jump rope counts? How many times did they jump?"
        },
        {
            "question_cn": "2024-05-18这一天的运动总时长是多少分钟？",
            "question_en": "What was the total exercise duration in minutes on May 18, 2024?"
        },
        {
            "question_cn": "在这段时间内，睡眠质量评分最高的一天是哪一天？评分为多少？",
            "question_en": "During this period, which day had the highest sleep quality score? What was the score?"
        },
        {
            "question_cn": "数据集中体重最轻的一天是哪一天？体重是多少千克？",
            "question_en": "In the dataset, which day had the lowest weight? How many kilograms was it?"
        },
        {
            "question_cn": "2024-05-21这一天的睡眠质量和睡眠时长分别是多少？",
            "question_en": "What were the sleep quality and sleep duration on May 21, 2024?"
        },
        {
            "question_cn": "在这段时间内，哪一天没有进行任何运动（运动总时长为0）？",
            "question_en": "During this period, which day had no exercise at all (total exercise duration was 0)?"
        },
        {
            "question_cn": "数据集中睡眠时长最短的一天是哪一天？具体时长是多少小时？",
            "question_en": "In the dataset, which day had the shortest sleep duration? How many hours specifically?"
        }
    ]

    for question in querys:
        try:
            # 调用本地ollama服务
            response = ollama.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': question['question_en'],
                        'images': [img_path]
                    }
                ]
            )

            # 打印响应
            print(f"模型响应 {question['question_en']}:")
            print(response['message']['content'])
            
            # 调用本地ollama服务
            response = ollama.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': question['question_cn'],
                        'images': [img_path]
                    }
                ]
            )

            # 打印响应
            print(f"模型响应 {question['question_cn']}:")
            print(response['message']['content'])

        except Exception as e:
            print(f"调用ollama服务时出错: {str(e)}")
            print("请确保ollama服务正在运行，并且已下载granite3.2-vision模型。")
'''
     example.png
模型响应:

The highest scoring model on ChartQA is Molmo-E with a score of 0.87.
模型响应:

轮询、轮询+随机选择、轮询+最佳节点选择、轮询+最小路径选择、轮询+平均路径选择、轮询+最短路径选择
模型响应:

### 图片描述

The image is a colorful infographic that appears to be explaining various aspects of cloud computing services in Chinese. The infographic is divided into six sections, each depicting different types of cloud services and their respective features or benefits. Each section includes both textual information and visual representations such as icons and diagrams.

#### Section 1: Cloud Storage Services
- **Description**: This section likely discusses the storage capabilities provided by cloud computing services. It may include details about data storage options, scalability, and security measures.
- **Visual Elements**: Icons of servers or storage devices are used to represent this section.

#### Section 2: Cloud Computing Platforms
- **Description**: This section probably covers the platforms that enable users to build, deploy, and manage applications in the cloud. It might include details about different types of platforms (e.g., IaaS, PaaS, SaaS) and their use cases.
- **Visual Elements**: Icons of servers or application icons are used here.

#### Section 3: Cloud Security Services
- **Description**: This section likely focuses on the security measures and features provided by cloud computing services to protect data and applications from threats. It may include details about encryption, access controls, and disaster recovery options.
- **Visual Elements**: Icons of locks or shields are used here.

#### Section 4: Cloud Backup Services
- **Description**: This section probably discusses the backup services offered by cloud computing platforms to ensure data integrity and availability. It might include details about different types of backups (e.g., full, incremental, differential) and their frequency.
- **Visual Elements**: Icons of clouds or storage devices are used here.

#### Section 5: Cloud Migration Services
- **Description**: This section likely covers the services that help users migrate their applications and data from on-premises environments to cloud computing platforms. It might include details about different migration strategies (e.g., lift-and-shift, rehost, refactor) and tools used for this process.
- **Visual Elements**: Icons of servers or network diagrams are used here.

#### Section 6: Cloud Management Services
- **Description**: This section probably discusses the management services provided by cloud computing platforms to help users monitor, manage, and optimize their cloud resources. It might include details about monitoring tools, automation capabilities, and cost optimization strategies.
- **Visual Elements**: Icons of dashboards or control panels are used here.

### Analysis and Description

The infographic is designed to provide a comprehensive overview of various aspects of cloud computing services in Chinese. Each section uses visual elements such as icons and diagrams to enhance understanding and retention of the information presented. The use of different colors for each section helps distinguish between them, making it easier for viewers to follow along.

The infographic is structured in a logical manner, starting with general cloud computing services (storage, platforms, security) and progressing to more specific services (backup, migration, management). This structure allows viewers to build a comprehensive understanding of the various components that make up cloud computing services.

### Conclusion

The infographic is an effective educational tool for explaining different aspects of cloud computing services in Chinese. By using visual elements and structured sections, it provides a clear and concise overview of the key features and benefits of cloud computing services. This information can be valuable for individuals looking to understand or utilize cloud computing platforms effectively.
模型响应 What is the weight on May 13, 2024?:

80.5 kg
模型响应 2024-05-13这一天的体重是多少？:

80.5
模型响应 What is the average weight across all data entries in the dataset?:

79.8
模型响应 数据集中所有体重数据的平均值是多少？:

根据表格中的数据，计算平均体重为：(80.5+80.3+80.6+80.2+80.0+79.8)/6=80.17。
模型响应 Which day had the longest sleep duration? How many hours specifically?:

2024-05-19 79.9
模型响应 哪一天的睡眠时长最长？具体时长是多少小时？:

2024-05-18 79.8 小时
模型响应 Among these data points, which day had the highest number of jump rope counts? How many times did they jump?:

2024-05-19.
模型响应 在这些数据中，跳绳次数最多的那一天是哪一天？跳了多少次？:

2024-05-19，1800
模型响应 What was the total exercise duration in minutes on May 18, 2024?:

79.8
模型响应 2024-05-18这一天的运动总时长是多少分钟？:

79.8
模型响应 During this period, which day had the highest sleep quality score? What was the score?:

2024-05-19, 80.0
模型响应 在这段时间内，睡眠质量评分最高的一天是哪一天？评分为多少？:

2024-05-19，80.5
模型响应 In the dataset, which day had the lowest weight? How many kilograms was it?:

2024-05-18 79.8.
模型响应 数据集中体重最轻的一天是哪一天？体重是多少千克？:

2024-05-19 79.8
模型响应 What were the sleep quality and sleep duration on May 21, 2024?:

79.5
模型响应 2024-05-21这一天的睡眠质量和睡眠时长分别是多少？:

79.5
模型响应 During this period, which day had no exercise at all (total exercise duration was 0)?:

2024-05-19.
模型响应 在这段时间内，哪一天没有进行任何运动（运动总时长为0）？:

2024-05-19
模型响应 In the dataset, which day had the shortest sleep duration? How many hours specifically?:

2024-05-16 80.2
模型响应 数据集中睡眠时长最短的一天是哪一天？具体时长是多少小时？:

2024-05-16 80.2 小时
'''   

if __name__ == "__main__":
    main()