import glob

import yt_dlp as youtube_dl

import config
import utils.tempfiles
from processing.ffprobe import *


class MyLogger(object):
    def debug(self, msg: ""):
        logger.debug(msg.replace("\r", ""))

    def warning(self, msg: ""):
        logger.warning(msg.replace("\r", ""))

    def error(self, msg: ""):
        logger.error(msg.replace("\r", ""))


def ytdownload(vid, form):
    # file extension is unknown so we have to do it weirdly
    while True:
        name = f"{utils.tempfiles.temp_dir}/{utils.tempfiles.get_random_string(12)}"
        if len(glob.glob(name + ".*")) == 0:
            break
    opts = {
        "quiet": True,
        "outtmpl": f"{name}.%(ext)s",
        "default_search": "auto",
        "merge_output_format": "mp4",
        "format": f'(bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best)'
                  f'[filesize<?{config.file_upload_limit}]',
        "max_filesize": config.file_upload_limit,
        "logger": MyLogger(),  # this is stupid but its how ytdl works
    }
    if form == "audio":
        opts['format'] = f"bestaudio[filesize<{config.file_upload_limit}]"
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    with youtube_dl.YoutubeDL(opts) as ydl:
        # manually exclude livestreams, cant find a better way to do this ¯\_(ツ)_/¯
        nfo = ydl.extract_info(vid, download=False)
        logger.debug(nfo)
        if "is_live" in nfo and nfo["is_live"]:
            raise youtube_dl.DownloadError("Livestreams cannot be downloaded.")
        ydl.download([vid])
    filename = glob.glob(name + ".*")
    if len(filename) > 0:
        return TempFile(filename[0], only_delete_in_main_process=True)
    else:
        return None


async def magickone(media, strength):
    tosave = TempFile("png")
    await run_command("magick", media, "-liquid-rescale", f"{strength}%x{strength}%", tosave)
    return tosave
