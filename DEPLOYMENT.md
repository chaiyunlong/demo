# 部署指南

## 项目根目录

项目根目录是包含 `package.json` 的目录：

```text
/workspace/demo
```

## 本地启动

先安装依赖：

```bash
npm install
```

启动开发服务：

```bash
npm run dev
```

默认访问地址：

```text
http://localhost:3000
```

如需指定端口：

```bash
PORT=4173 npm run dev
```

## 本地构建

```bash
npm run build
```

构建脚本会把 `public/` 静态资源复制到 `dist/`，`dist/` 是部署输出目录。


## 当前验证状态

已在项目根目录执行并验证通过：

```bash
npm run build
```

构建输出目录为 `dist/`，该目录由构建过程生成，不提交到 Git。

## Vercel 部署配置

本项目可以部署到 Vercel。推荐配置如下：

```text
Framework Preset: Other
Root Directory: ./
Install Command: npm install
Build Command: npm run build
Output Directory: dist
```

仓库已经提供 `vercel.json`，声明了相同的构建命令和输出目录，并配置 `/api/analyze` Python Serverless Function。

## 环境变量

### 必需环境变量

默认确定性 Agent 不需要任何环境变量。

### 可选环境变量

如果要启用 OpenAI GPT 增强模式，需要配置：

```text
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_MODEL=gpt-5.2
```

`OPENAI_MODEL` 可选，不填时使用代码中的默认模型。

## 验证命令

```bash
npm install
npm run build
npm test
PORT=4173 npm run dev
```

开发服务启动后，可以验证页面和 API：

```bash
curl -sf http://localhost:4173/ | head -5
curl -sf -X POST http://localhost:4173/api/analyze \
  -H 'Content-Type: application/json' \
  --data '{"target_role":"用户运营","experience_materials":"维护20个社群，每个约200人。"}'
```
