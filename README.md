# BiliVideoFFmpegProcessor 🎬

一个基于Flask + FFmpeg + Vue.js的全栈B站视频处理平台，提供专业的视频下载、格式转换和多媒体处理服务。

## ✨ 功能特性

### 🎥 核心功能

- **B站视频下载** - 支持BV号解析和高清视频下载

- **音视频分离** - 智能分离视频和音频流

- **多格式转换** - MP4、MP3、GIF等多种格式支持

- **平台优化** - B站1080P、抖音竖屏等平台专属设置

  

### 🛠 技术栈

**后端**: Python Flask + FFmpeg   
**前端**: Vue 3 + Element Plus + Axios  
**构建工具**: Vite + Webpack

## 🏗 项目结构

```
BiliVideoFFmpegProcessor/
├── backend/                # Flask后端服务
│   ├── Woker.py            # 主应用文件
│   ├─ErrorConstant.py      #异常信息
│   ├─Constant.py           #常用信息
│   ├─Result.py             #统一响应接口
├── frontend/               # Vue前端项目
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   └── api/            # API接口
│   └── package.json
├── docs/                   # 文档资料
└── README.md
```

## 🚀 快速开始

### 后端启动

```bash
# 克隆项目
git clone https://github.com/ourhome-macro/BiliVideoFFmpegProcessor.git
cd BiliVideoFFmpegProcessor/backend

# 安装依赖
pip install -r requirements.txt

# 启动Flask服务
python Woker.py
```

### 前端启动（即将开发）

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

## 📡 API接口文档

### 视频信息获取

```http
GET /get_video_info/{bvid}
```

获取B站视频基本信息

### 视频下载

```http
POST /download
Content-Type: application/json

{
  "url": "视频URL",
  "filepath": "保存路径"
}
```

### 格式转换

```http
POST /mp3_convert
POST /gif_convert  
POST /mp4_convert
```

### 平台优化

```http
POST /bilibili_1080p_convert
POST /douyin_vertical_convert
```

## 🎯 前端功能规划

### 页面模块

- **首页** - 功能概览和快速入口
- **视频下载** - URL输入和下载管理
- **格式转换** - 文件上传和转换设置
- **任务管理** - 处理进度和历史记录
- **设置** - 参数配置和系统设置

### 组件设计

```vue
<!-- 示例：任务进度组件 -->
<template>
  <div class="task-progress">
    <el-progress :percentage="progressPercentage" />
    <div class="task-info">
      <span>{{ taskName }}</span>
      <span>{{ estimatedTime }}</span>
    </div>
  </div>
</template>
```



## 📊 开发进度

- [x] Flask后端基础框架

- [x] FFmpeg集成和视频处理功能

- [x] RESTful API接口设计

- [ ] Vue 3前端界面开发

- [ ] 实时进度推送(WebSocket)

  



## 📝 更新日志

### v0.1.0 (当前)

- 基础Flask后端服务
- FFmpeg视频处理功能
- 基本API接口实现

### v0.2.0 (规划中)  

- Vue 3前端界面
- 实时任务监控
- 用户界面优化

