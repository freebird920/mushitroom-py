import os
import ctypes
import platform
import subprocess
from enum import Enum


class AudioList(Enum):
    CLICK = "src/assets/audio/click_001.wav"
    BGM_01 = "src/assets/audio/bgm_01.wav"
    BGM_02 = "src/assets/audio/bgm_02.wav"


class SoundManager:
    _instance: "SoundManager | None" = None
    _system_os: str
    _bgm_process = None
    _bgm_alias = "bgm_alias"
    _volume: int = 100  # 기본 볼륨 (0~100)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._system_os = platform.system()
            self._volume = 100  # 초기화
            self.initialized = True

    def _send_mci_command(self, command: str):
        """[Windows] MCI 명령어 전송 헬퍼"""
        error_buffer = ctypes.create_unicode_buffer(256)
        return_code = ctypes.windll.winmm.mciSendStringW(command, None, 0, None)

        if return_code != 0:
            ctypes.windll.winmm.mciGetErrorStringW(return_code, error_buffer, 255)
            # 볼륨 조절 실패 등은 로그가 너무 시끄러울 수 있으므로 주석 처리하거나 필요시 사용
            # print(f"❌ MCI Error [{return_code}]: {error_buffer.value} | Cmd: {command}")
            return False
        return True

    def set_volume(self, volume: int):
        """
        볼륨 조절 (0 ~ 100)
        Windows: 현재 재생 중인 BGM의 볼륨만 조절 (MCI)
        Linux: 시스템 PCM 볼륨 조절 (amixer)
        """
        # 0 ~ 100 사이 값으로 제한
        self._volume = max(0, min(100, volume))

        if self._system_os == "Windows":
            # MCI volume 범위: 0 ~ 1000
            mci_vol = self._volume * 10
            # 현재 BGM이 열려있다면 즉시 적용
            self._send_mci_command(f"setaudio {self._bgm_alias} volume to {mci_vol}")

        elif self._system_os == "Linux":
            # 라즈베리파이/리눅스는 amixer로 시스템 볼륨 조절
            # 'PCM' 혹은 'Master' (오디오 장치 설정에 따라 다름, 보통 Pi는 PCM)
            try:
                subprocess.run(
                    f"amixer set PCM {self._volume}%",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                print(f"⚠️ 리눅스 볼륨 조절 실패: {e}")

    def play_bgm(self, audio: AudioList):
        if not os.path.exists(audio.value):
            print(f"❌ 파일 없음: {audio.value}")
            return

        try:
            if self._system_os == "Windows":
                abs_path = os.path.abspath(audio.value).replace("/", "\\")

                # 기존 BGM 닫기
                self._send_mci_command(f"close {self._bgm_alias}")

                # 파일 열기
                cmd_open = f'open "{abs_path}" type mpegvideo alias {self._bgm_alias}'
                if not self._send_mci_command(cmd_open):
                    return

                # ★ 중요: 열자마자 현재 설정된 볼륨 적용
                self.set_volume(self._volume)

                # 재생
                cmd_play = f"play {self._bgm_alias} repeat"
                if not self._send_mci_command(cmd_play):
                    self._send_mci_command(f"play {self._bgm_alias}")

            elif self._system_os == "Linux":
                self.stop_bgm()

                # ★ 리눅스는 재생 전 볼륨 세팅
                self.set_volume(self._volume)

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

                # Windows winsound는 볼륨 조절 기능이 없음 (시스템 볼륨 따름)
                winsound.PlaySound(
                    audio.value, winsound.SND_FILENAME | winsound.SND_ASYNC
                )

            elif self._system_os == "Linux":
                # aplay 실행 (시스템 볼륨의 영향을 받음)
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
