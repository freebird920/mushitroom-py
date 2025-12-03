import os
import ctypes
import platform
import subprocess
from enum import Enum


class AudioList(Enum):
    CLICK = "src/assets/audio/click_001.wav"
    BGM_00 = "src/assets/audio/bgm_00.wav"
    BGM_01 = "src/assets/audio/bgm_01.wav"
    BGM_02 = "src/assets/audio/bgm_02.wav"


class AudioManager:
    _instance: "AudioManager | None" = None
    _system_os: str
    _bgm_process = None
    _bgm_alias = "bgm_alias"

    # 오디오 기능 활성화 여부 플래그
    is_audio_enabled: bool = True

    _main_volume: int = 100
    _bgm_volume: int = 100
    _sfx_volume: int = 100

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._system_os = platform.system()
            self._bgm_volume = 100
            self._sfx_volume = 100
            self._main_volume = 100

            # [안전장치] 초기화 시 오디오 장치 점검
            self.is_audio_enabled = self._check_audio_availability()
            self.initialized = True

    def _check_audio_availability(self) -> bool:
        """오디오 장치가 실제로 사용 가능한지 확인"""
        if self._system_os == "Linux":
            try:
                # aplay -l 명령어로 재생 가능한 카드가 있는지 확인
                result = subprocess.run(
                    ["aplay", "-l"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                # 'card'라는 단어가 출력에 없으면 장치가 없는 것으로 간주
                if "card" not in result.stdout:
                    print("🚫 오디오 장치 없음: 오디오 기능을 비활성화합니다.")
                    return False
            except Exception:
                print("🚫 오디오 점검 실패: 오디오 기능을 비활성화합니다.")
                return False
        return True

    def _send_mci_command(self, command: str):
        if not self.is_audio_enabled:
            return False

        error_buffer = ctypes.create_unicode_buffer(256)
        return_code = ctypes.windll.winmm.mciSendStringW(command, None, 0, None)
        if return_code != 0:
            return False
        return True

    def set_main_volume(self, volume: int):
        self._main_volume = max(0, min(100, volume))
        self.set_bgm_volume(round(self._bgm_volume * (self._main_volume / 100)))

    def set_bgm_volume(self, volume: int):
        if not self.is_audio_enabled:
            return

        self._bgm_volume = max(0, min(100, volume))

        if self._system_os == "Windows":
            mci_vol = self._bgm_volume * 10
            self._send_mci_command(f"setaudio {self._bgm_alias} volume to {mci_vol}")

        elif self._system_os == "Linux":
            try:
                subprocess.run(
                    f"amixer set PCM {self._bgm_volume}%",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except:
                pass

    def set_sfx_volume(self, volume: int):
        self._sfx_volume = max(0, min(100, volume))

    def play_bgm(self, audio: AudioList):
        # [안전장치] 오디오 비활성화 상태면 즉시 리턴
        if not self.is_audio_enabled:
            return

        # 경로 절대경로로 변환
        abs_path = os.path.abspath(audio.value)
        if not os.path.exists(abs_path):
            return

        try:
            if self._system_os == "Windows":
                abs_path_win = abs_path.replace("/", "\\")
                self._send_mci_command(f"close {self._bgm_alias}")
                cmd_open = (
                    f'open "{abs_path_win}" type mpegvideo alias {self._bgm_alias}'
                )
                if self._send_mci_command(cmd_open):
                    self.set_bgm_volume(self._bgm_volume)
                    cmd_play = f"play {self._bgm_alias} repeat"
                    if not self._send_mci_command(cmd_play):
                        self._send_mci_command(f"play {self._bgm_alias}")

            elif self._system_os == "Linux":
                self.stop_bgm()

                # [핵심 수정]
                # 무한 루프(while true) 제거 -> 한 번 재생 후 끝나게 하거나
                # 에러 발생 시( || break ) 루프를 탈출하도록 수정하여 도배 방지
                setsid_func = getattr(os, "setsid", None)

                # "aplay 실행하다 실패하면(||) 즉시 루프 탈출(break)"
                cmd = f"while true; do aplay -q '{abs_path}' || break; done"

                self._bgm_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    preexec_fn=setsid_func,
                    executable="/bin/bash",
                    stderr=subprocess.DEVNULL,  # 에러 메시지도 화면에 안 뜨게 숨김
                )

        except Exception as e:
            print(f"⚠️ BGM 오류(무시함): {e}")
            self.is_audio_enabled = False  # 에러 나면 그냥 꺼버림

    def play_sfx(self, audio: AudioList):
        if not self.is_audio_enabled:
            return

        if not os.path.exists(audio.value):
            return

        try:
            if self._system_os == "Windows":
                import winsound

                winsound.PlaySound(
                    audio.value, winsound.SND_FILENAME | winsound.SND_ASYNC
                )
            elif self._system_os == "Linux":
                # 에러 메시지 숨김 (stderr=subprocess.DEVNULL)
                subprocess.Popen(
                    ["aplay", "-q", audio.value], stderr=subprocess.DEVNULL
                )
        except:
            pass

    def stop_bgm(self):
        if not self.is_audio_enabled:
            return

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
                    except:
                        pass
                else:
                    try:
                        self._bgm_process.terminate()
                    except:
                        pass
                self._bgm_process = None
