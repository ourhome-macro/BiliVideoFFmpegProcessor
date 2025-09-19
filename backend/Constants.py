# 项目常量池

# B站API相关
BILIBILI_VIDEO_INFO_API = "https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
BILIBILI_PLAY_URL_API = "https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=112&fnval=16"

# 请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com"
}

# 文件路径
DOWNLOADS_DIR = "downloads"
TEMP_DIR = "downloads/temp"
FILES_DIR = "downloads/files"
UPLOADS_DIR = "uploads"
OUTPUTS_DIR = "outputs"

# ffmpeg参数默认值
GIF_SIZE = "640x360"
GIF_START = 2
GIF_LENGTH = 10
GIF_RATE = 15

INITIALIZATION_SUCCESS_MSG = "初始化成功"
