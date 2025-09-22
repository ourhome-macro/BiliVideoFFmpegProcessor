from concurrent.futures import ThreadPoolExecutor
import threading
from Result import Result
from ErrorConstants import BV_NOT_FOUND_ERROR_MSG, GAIN_PLAYBACK_ERROR_MSG, INVALID_URL_ERROR_MSG, NETWORK_ERROR_MSG, FILE_WRITE_ERROR_MSG, VIDEO_INFO_ERROR_MSG
from flask import Flask
import requests
from flask import request
import re
#import json
import os
import subprocess
from datetime import datetime
from Constants import (
    BILIBILI_VIDEO_INFO_API,
    BILIBILI_PLAY_URL_API,
    DEFAULT_HEADERS,
    DOWNLOADS_DIR,
    INITIALIZATION_SUCCESS_MSG,
    TEMP_DIR,
    FILES_DIR,
    GIF_SIZE,
    GIF_START,
    GIF_LENGTH,
    GIF_RATE
)

# 参数验证手段 bv号+url
def is_valid_bvid(bvid):
    pattern = r'^(BV|bv)[0-9A-Za-z]{10}$'
    return re.match(pattern, bvid) is not None

def is_valid_Bilibili_url(url):
    pattern = r'^(https?|ftp)://www\.bilibili\.com/video/(BV[0-9A-Za-z]{10})(/.*)?$'
    return re.match(pattern, url) is not None

app = Flask(__name__)

executor = ThreadPoolExecutor(max_workers=4)

#单独抽取出ffmpeg的命令api
def run_ffmpeg_command(cmd):
    subprocess.run(cmd, shell=True, check=True)
    pass

#并发处理一下传入的多个url
@app.route('/handle_multiple_videos', methods=['POST'])
def handle_multiple_videos(urls):
    data = request.get_json()
    urls = data.get('urls', [])

    tasks = []
    for url in urls:
        tasks.append(executor.submit(handle_single_video, url))

    results = {}
    for url,task in zip(urls,tasks):
        res = task.result() 
        results[url] = Result(
            success=res['success'],
            data=res.get('data'),
            message=res.get('message')
        )
    return Result.success(results)
        #pass    
# 整合单个搜索框重的提取bv号、获取视频信息、获取播放地址接口
def handle_single_video(url):
    #4个接口。提取bv、获取信息、获取播放地址、下载
    bvid_result = get_bvid_from_url(url)
    if not bvid_result['success']:
        return bvid_result
    
    bvid = bvid_result['data']
    info_result = get_video_info(bvid)
    if not info_result['success']:
        return info_result
    
    info = info_result['data']
    play_result = get_video_play_url(info['bvid'], info['cid'])
    if not play_result['success']:
        return play_result
    
    download_result = download_file(play_result['data'])
    if not download_result['success']:
        return download_result
    
    merge_result = merge_video_audio(download_result['data'])
    if not merge_result['success']:
        return merge_result

# 从url里提取出bv号来
@app.route('/get_bvid/<path:url>', methods=['GET'])
def get_bvid_from_url(url):
    if not is_valid_Bilibili_url(url):
        return Result.error(INVALID_URL_ERROR_MSG)
    bv_pattern = r'(BV[0-9A-Za-z]{10})'
    bv_match = re.search(bv_pattern, url)
    if bv_match:
        return Result.success(bv_match.group(1))  
    return Result.error(BV_NOT_FOUND_ERROR_MSG)

# 拿到视频信息
@app.route('/get_video_info/<bvid>', methods=['GET'])
def get_video_info(bvid):
    #模拟客户端行为
    if not is_valid_bvid(bvid):
        return Result.error(BV_NOT_FOUND_ERROR_MSG)
    info_url = BILIBILI_VIDEO_INFO_API.format(bvid=bvid)
    res = requests.get(info_url, headers=DEFAULT_HEADERS)
    datas = res.json()
    if datas['code'] != 0:
        return Result.error(VIDEO_INFO_ERROR_MSG)
    data = datas['data']
    # 只保留 bvid、cid、title 字段
    filtered = {
        'bvid': data.get('bvid'),
        'cid': data.get('cid'),
        'title': data.get('title')
    }
    return Result.success(filtered)

# 拿到播放地址
@app.route('/get_play_url/<bvid>/<cid>', methods=['GET'])
def get_video_play_url(bvid,cid):
    play_url = BILIBILI_PLAY_URL_API.format(bvid=bvid, cid=cid)
    res = requests.get(play_url, headers=DEFAULT_HEADERS)
    data = res.json()

    if data['code'] != 0:
        return Result.error(GAIN_PLAYBACK_ERROR_MSG)
    video_url = data['data']['dash']['video'][0]['baseUrl']
    audio_url = data['data']['dash']['audio'][0]['baseUrl']
    urls = [video_url, audio_url]
    return Result.success(urls)

def download_worker(url, filepath, headers):
    headers = DEFAULT_HEADERS
    try:
        res = requests.get(url, headers=headers, stream=True, timeout=10)
        res.raise_for_status()
        total_size = int(res.headers.get('content-length', 0))

        with open(filepath, 'wb') as f:
            downloaded = 0
            for data in res.iter_content(chunk_size=1024):
                downloaded += len(data)
                f.write(data)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    # TODO: 考虑用websocket推送下载进度
                    print(f"\r下载进度: {progress:.2f}%", end='')
    except requests.RequestException as e:
        return Result.error(NETWORK_ERROR_MSG)     
    except OSError as e:
        return Result.error(FILE_WRITE_ERROR_MSG)

# 下载视频、音频文件
# TODO：
@app.route('/download/', methods=['POST'])
def download_file():
    
    data = request.get_json()
    video_url = data.get('video_url')
    audio_url = data.get('audio_url')
    video_filepath = data.get('video_filepath')
    audio_filepath = data.get('audio_filepath')
    headers = DEFAULT_HEADERS
    # video_download = threading.Thread(target=download_worker, args=(video_url, video_filepath, headers))
    # audio_download = threading.Thread(target=download_worker, args=(audio_url, audio_filepath, headers))
    # video_download.start()
    # audio_download.start()
    # video_download.join()
    # audio_download.join()
    download_worker(video_url, video_filepath, headers)
    download_worker(audio_url, audio_filepath, headers)
    paths = [video_filepath, audio_filepath]
    return Result.success(paths)

#TODO: 应该维护个url队列再来用异步
@app.route('/merge', methods=['POST'])
def merge_video_audio():
    data = request.get_json()
    video_path = data.get('video_path')
    audio_path = data.get('audio_path')
    output_path = os.path.splitext(os.path.basename(video_path))[0]
    cmd = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c copy "{FILES_DIR}/{output_path}_final.mp4"'
    run_ffmpeg_command(cmd)
    #executor.submit(run_ffmpeg_command, cmd)
    #print("合并")
    final_path = f"{FILES_DIR}/{output_path}_final.mp4"
    return Result.success(final_path)


# 最终转码为H.264
@app.route('/final_convert', methods=['POST'])
def final_convert():
    data = request.get_json()
    final_path = data.get('final_path')
    # 转换HEVC到H.264
    filename, ext = os.path.splitext(final_path)
    output_path = f"{filename}_h264.mp4"
    cmd = f'ffmpeg -i "{final_path}" -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k "{output_path}"'
    executor.submit(run_ffmpeg_command, cmd)
    return Result.success(output_path)

@app.route('/init', methods=['POST'])
def init():
    try:
         if not os.path.exists(DOWNLOADS_DIR):
            os.makedirs(DOWNLOADS_DIR)
            os.makedirs(TEMP_DIR)
            os.makedirs(FILES_DIR)    
            return Result.success(INITIALIZATION_SUCCESS_MSG)

    except OSError as e:
        return Result.error(FILE_WRITE_ERROR_MSG)


# 单纯的转化文件为mp3
@app.route('/mp3_convert', methods=['POST'])
def convert_to_mp3():
    data = request.get_json()
    input_path = data.get('input_path')
    delete_source = data.get('delete_source', False)
    output_path = os.path.splitext(os.path.basename(input_path))[0]
    cmd = f'ffmpeg -i "{input_path}" -vn -acodec libmp3lame -ar 44100 -ac 2 -ab 192k "{FILES_DIR}/{output_path}.mp3"'
    executor.submit(run_ffmpeg_command, cmd)
    #print("MP3转换完成")
    #delete_source用来判断是否删除源文件
    if delete_source:
        os.remove(input_path)
    return Result.success(output_path)
        
# gif动画转换，可做表情包
@app.route('/gif_convert', methods=['POST'])
def gif_convert():
    data = request.get_json()
    input_path = data.get('input_path')
    size = GIF_SIZE
    start = GIF_START
    length = GIF_LENGTH
    rate = GIF_RATE
    filename, ext = os.path.splitext(input_path)
    output_path = f"{filename}_{size}_{start}_{length}.gif"
    cmd = f'ffmpeg -ss {start} -t {length} -i "{input_path}" -r {rate} -s {size} "{output_path}"'
    executor.submit(run_ffmpeg_command, cmd)
    #print("GIF转换成功")
    return Result.success(output_path)


@app.route('/mp4_convert', methods=['POST'])
def to_mp4():
    data = request.get_json()
    input_path = data.get('input_path')
    filename, ext = os.path.splitext(input_path)
    now = datetime.now().strftime("%H%M%S")
    output_path = f"{filename}_{now}.mp4"
    cmd = f'ffmpeg -i "{input_path}" -y "{output_path}"'
    executor.submit(run_ffmpeg_command, cmd)
    #print("MP4转换任务完成")
    return Result.success(output_path)


##对应平台所需画质
@app.route('/bilibili_1080p_convert', methods=['POST'])
def bilibili_1080p_convert():
    data = request.get_json()
    input_path = data.get('input_path')
    output_path = f"{FILES_DIR}/{os.path.splitext(os.path.basename(input_path))[0]}_1080p.mp4"  
    cmd = (
        f'ffmpeg -i "{input_path}" '
        '-c:v libx264 '
        '-crf 23 '
        '-preset medium '
        '-profile:v high '
        '-level 4.1 '
        '-maxrate 6000k '
        '-bufsize 12000k '
        '-pix_fmt yuv420p '
        '-movflags +faststart '
        '-c:a aac '
        '-b:a 192k '
        '-ar 48000 '
        f'"{output_path}"'
    )
    executor.submit(run_ffmpeg_command, cmd)
    return Result.success(output_path)

@app.route('/douyin_vertical_convert', methods=['POST'])
def douyin_vertical_convert():
    data = request.get_json()
    input_path = data.get('input_path')
    output_path = f"{FILES_DIR}/{os.path.splitext(os.path.basename(input_path))[0]}_vertical.mp4"
    cmd = (
        f'ffmpeg -i "{input_path}" '
        '-c:v libx264 '
        '-crf 22 '
        '-preset fast '
        '-vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2" '
        '-aspect 9:16 '
        '-maxrate 3000k '
        '-bufsize 6000k '
        '-r 30 '
        '-g 60 '
        '-c:a aac '
        '-b:a 128k '
        '-ar 44100 '
        f'"{output_path}"'
    )
    executor.submit(run_ffmpeg_command, cmd)
    #print("抖音设置完成")
    return Result.success(output_path)


if __name__ == '__main__':
    app.run(debug=True)

#测试数据:
#https://www.bilibili.com/video/BV1uz421X7bg  徐佳莹 - 行走的鱼
#https://www.bilibili.com/video/BV1TY411q7zh  孙燕姿 - 开始懂了
