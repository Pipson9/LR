# 企业知识库 RAG 检索问答

基于 **LangChain + Chroma + BGE Embedding + 通义千问** 搭建的企业内部知识库问答系统。把公司制度、产品手册、客服话术等文档灌入本地向量库，用户用自然语言提问，系统检索相关片段后交给大模型作答，并**返回答案出处**（文件名 + 页码 + 分类）以便核对。

## 核心特性

- **多格式文档接入**：支持 `.txt` / `.md` / `.pdf` / `.docx`，按目录自动打分类标签
- **本地向量化**：使用 BGE 中文模型（`bge-small-zh-v1.5`）本地计算 embedding，数据不出内网
- **分块策略可调**：基于中文标点（`。！？；，`）递归切分，保留语义边界
- **答案可溯源**：回答下方列出资料来源，去重展示文件名、页码、所属分类
- **抗幻觉提示词**：系统提示明确要求"资料不足时回答无法确定"，禁止编造制度与数字
- **链式 / 非链式双实现**：同时提供 LCEL 链式写法和显式调用写法，便于对比学习

## 技术架构

```
用户提问
   │
   ▼
Retriever 向量检索（Chroma + BGE Embedding，Top-K = 3）
   │
   ▼
format_documents()  把召回片段拼成带编号和来源的 context
   │
   ▼
ChatPromptTemplate  组装 Prompt（系统约束 + context + question）
   │
   ▼
通义千问 qwen-turbo（OpenAI 兼容接口）
   │
   ▼
StrOutputParser  取出纯文本 answer
   │
   ▼
build_sources()  去重整理资料来源
   │
   ▼
返回 { answer, sources }
```

## 目录结构

```
建设知识库检索/
├── main.py                  # 入口：命令行交互式问答
├── rag_service.py           # 核心服务：封装完整 RAG 链路
├── build_db_index.py        # 构建向量库索引
├── doc_load_split.py        # 文档加载 + 文本切分
├── search_knowledge.py      # 纯检索调试脚本（不调用大模型）
├── RAG问答链式.py            # 练习：LCEL 链式写法
├── RAG问答非链式.py          # 练习：显式调用写法
├── utils/
│   ├── get_model.py             # 初始化对话模型
│   ├── get_embedding_model.py   # 初始化 Embedding 模型
│   └── fromat_documents.py      # 文档拼接工具
├── knowledge_base/          # 示例知识库
│   ├── hr/                  #   人事制度
│   ├── product/             #   产品资料
│   └── customer_service/    #   客服手册
├── .env.example             # 配置模板
└── requirements.txt
```

## 快速开始

### 1. 环境要求

- Python 3.11
- 阿里云百炼（DashScope）API Key：[获取地址](https://bailian.console.aliyun.com/)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> `torch` 体积较大，CPU 版安装可参考 [PyTorch 官方指引](https://pytorch.org/get-started/locally/)。

### 3. 下载 Embedding 模型

下载 `bge-small-zh-v1.5` 并放到以下任一位置：

- 项目根目录的 `models/bge-small-zh-v1.5/`
- 任意路径，然后在 `.env` 中指定 `EMBEDDING_MODEL_PATH`

模型地址：https://huggingface.co/BAAI/bge-small-zh-v1.5

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少填入：

```ini
BAILIAN_APIKEY=你的APIKey
BAILIAN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_MODEL_PATH=models/bge-small-zh-v1.5
```

### 5. 构建向量库

```bash
python build_db_index.py
```

把 `knowledge_base/` 下的文档切分并写入 `chroma_db/`（集合名 `knowledge_base`）。终端会打印原始文档数与分块数。

> 更换知识库内容后需重新执行本步骤。

### 6. 启动问答

```bash
python main.py
```

```
企业知识库助手已启动，输入 exit 退出。

请输入问题：快递已经发出还能退款吗？

回答：根据现有资料，快递发出后仍可申请退款，但需符合以下条件……
资料来源：
1. refund_policy.md，分类：product
2. product_manual.pdf，第 12 页，分类：customer_service
```

### 7. 仅调试检索效果

不消耗大模型额度，直接查看召回片段与距离分数：

```bash
python search_knowledge.py
```

## 配置说明

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `BAILIAN_APIKEY` | 通义千问 API Key | 必填 |
| `BAILIAN_BASE_URL` | OpenAI 兼容接口地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `EMBEDDING_MODEL_PATH` | 本地 BGE 模型路径 | `models/bge-small-zh-v1.5` |
| `EMBEDDING_DEVICE` | 推理设备 | `cpu` |
| `LANGSMITH_TRACING` | 是否开启链路追踪 | `false` |

## 关键参数

改这些地方可以调节效果，都在代码顶部集中定义：

| 参数 | 位置 | 当前值 | 作用 |
| --- | --- | --- | --- |
| `chunk_size` | `doc_load_split.py` | `100` | 分块字符数，太小会切断语义 |
| `chunk_overlap` | `doc_load_split.py` | `20` | 相邻块重叠，避免边界信息丢失 |
| `search_kwargs.k` | `rag_service.py` | `3` | 召回片段数量 |
| `temperature` | `rag_service.py` | `0.2` | 越低越贴近原文，减少发挥 |
| `collection_metadata` | `build_db_index.py` | `cosine` | 相似度算法 |

> ⚠️ `build_db_index.py` 与 `rag_service.py` 中的 `COLLECTION_NAME` **必须一致**（当前均为 `knowledge_base`），否则检索结果恒为空。

## 安全说明

- `.env` 已被 `.gitignore` 排除，**不会提交到仓库**，请勿强行 `git add -f`
- 若密钥曾经外泄，务必到控制台立即吊销并重新生成
- 知识库文档随仓库公开时，请先确认内容不含商业机密或个人信息

## License

未声明，如需开源建议补充 MIT 或 Apache-2.0 协议。
