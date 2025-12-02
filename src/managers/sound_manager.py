import os
import platform
import subprocess
import time
from enum import Enum
import ctypes


class AudioList(Enum):
    # 테스트를 위해 경로가 정확한지 확인해주세요
    CLICK = "src/assets/audio/click_001.wav"
    BGM_01 = "src/assets/audio/bgm_01.wav"


class SoundManager:
    _instance: "SoundManager | None" = None
    _system_os: str
    _bgm_process = None
    _bgm_alias = "bgm_alias"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._system_os = platform.system()
            self.initialized = True

    def _send_mci_command(self, command: str):
        """
        [Windows 전용] MCI 명령어를 전송하고 에러가 있으면 출력하는 헬퍼 함수
        """
        # 에러 메시지를 담을 버퍼 생성
        error_buffer = ctypes.create_unicode_buffer(256)

        # 명령어 실행 (성공 시 0 반환)
        return_code = ctypes.windll.winmm.mciSendStringW(command, None, 0, None)

        if return_code != 0:
            # 에러 코드를 사람이 읽을 수 있는 문자로 변환
            ctypes.windll.winmm.mciGetErrorStringW(return_code, error_buffer, 255)
            print(f"❌ MCI Error [{return_code}]: {error_buffer.value}")
            print(f"   └ Command: {command}")
            return False
        return True

    def play_bgm(self, audio: AudioList):
        if not os.path.exists(audio.value):
            print(f"❌ 파일 없음: {audio.value}")
            return

        try:
            if self._system_os == "Windows":
                abs_path = os.path.abspath(audio.value).replace("/", "\\")

                ctypes.windll.winmm.mciSendStringW(
                    f"close {self._bgm_alias}", None, 0, None
                )

                cmd_open = f'open "{abs_path}" type mpegvideo alias {self._bgm_alias}'

                if not self._send_mci_command(cmd_open):
                    return

                # 재생 시도
                cmd_play = f"play {self._bgm_alias} repeat"

                if not self._send_mci_command(cmd_play):
                    print("⚠️ type mpegvideo로도 repeat 실패. 1회 재생합니다.")
                    self._send_mci_command(f"play {self._bgm_alias}")
                else:
                    # 성공
                    pass

            elif self._system_os == "Linux":
                self.stop_bgm()
                setsid_func = getattr(os, "setsid", None)
                cmd = f"while true; do aplay -q {audio.value}; done"
                self._bgm_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    preexec_fn=setsid_func,
                    executable="/bin/bash",
                )

        except Exception as e:
            print(f"⚠️ BGM 재생 오류: {e}")

    def play_sfx(self, audio: AudioList):
        if not os.path.exists(audio.value):
            return

        try:
            if self._system_os == "Windows":
                import winsound

                # SND_NOSTOP을 추가하여 다른 소리를 끊지 않도록 시도 (MCI와는 별개 채널이라 괜찮음)
                winsound.PlaySound(
                    audio.value, winsound.SND_FILENAME | winsound.SND_ASYNC
                )

            elif self._system_os == "Linux":
                subprocess.Popen(["aplay", "-q", audio.value])

        except Exception as e:
            print(f"⚠️ 효과음 재생 오류: {e}")

    def stop_bgm(self):
        if self._system_os == "Windows":
            self._send_mci_command(f"stop {self._bgm_alias}")
            self._send_mci_command(f"close {self._bgm_alias}")

        elif self._system_os == "Linux":
            if self._bgm_process:
                import signal

                killpg_func = getattr(os, "killpg", None)
                getpgid_func = getattr(os, "getpgid", None)
                if killpg_func and getpgid_func:
                    try:
                        killpg_func(getpgid_func(self._bgm_process.pid), signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                else:
                    self._bgm_process.terminate()
                self._bgm_process = None
