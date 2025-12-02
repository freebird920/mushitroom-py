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

    # [수정] 볼륨 변수 분리
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
            self.initialized = True

    def _send_mci_command(self, command: str):
        """[Windows] MCI 명령어 전송 헬퍼"""
        error_buffer = ctypes.create_unicode_buffer(256)
        return_code = ctypes.windll.winmm.mciSendStringW(command, None, 0, None)

        if return_code != 0:
            ctypes.windll.winmm.mciGetErrorStringW(return_code, error_buffer, 255)
            # 디버깅 필요 시 주석 해제
            # print(f"❌ MCI Error [{return_code}]: {error_buffer.value} | Cmd: {command}")
            return False
        return True

    def set_bgm_volume(self, volume: int):
        """
        BGM 볼륨 조절 (0 ~ 100)
        Windows: MCI 명령어로 BGM만 개별 조절 가능
        Linux: 시스템 PCM 볼륨 조절 (전체 볼륨이 변함)
        """
        self._bgm_volume = max(0, min(100, volume))

        if self._system_os == "Windows":
            # MCI volume 범위: 0 ~ 1000
            mci_vol = self._bgm_volume * 10
            # 현재 BGM이 재생 중이라면 즉시 적용
            self._send_mci_command(f"setaudio {self._bgm_alias} volume to {mci_vol}")

        elif self._system_os == "Linux":
            # 주의: 리눅스 aplay는 개별 볼륨 조절 불가. 시스템 볼륨(PCM)을 변경함.
            try:
                subprocess.run(
                    f"amixer set PCM {self._bgm_volume}%",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                print(f"⚠️ 리눅스 볼륨 조절 실패: {e}")

    def set_sfx_volume(self, volume: int):
        """
        효과음 볼륨 조절 (0 ~ 100)
        주의: 현재 사용 중인 winsound(Win)와 aplay(Linux)는
        재생 시 볼륨을 지정하는 기능을 지원하지 않습니다.
        이 메서드는 값만 저장해두며, 실제 소리 크기에는 영향을 주지 못할 수 있습니다.
        """
        self._sfx_volume = max(0, min(100, volume))
        # winsound나 aplay는 play 시점에 볼륨을 조절하는 옵션이 없음.
        # 추후 pygame이나 miniaudio 같은 라이브러리로 교체 시 여기서 적용 가능.
        pass

    def play_bgm(self, audio: AudioList):
        if not os.path.exists(audio.value):
            print(f"❌ 파일 없음: {audio.value}")
            return

        try:
            if self._system_os == "Windows":
                abs_path = os.path.abspath(audio.value).replace("/", "\\")

                self._send_mci_command(f"close {self._bgm_alias}")

                cmd_open = f'open "{abs_path}" type mpegvideo alias {self._bgm_alias}'
                if not self._send_mci_command(cmd_open):
                    return

                # [수정] 저장된 BGM 볼륨값 적용
                self.set_bgm_volume(self._bgm_volume)

                cmd_play = f"play {self._bgm_alias} repeat"
                if not self._send_mci_command(cmd_play):
                    self._send_mci_command(f"play {self._bgm_alias}")

            elif self._system_os == "Linux":
                self.stop_bgm()

                # [수정] 저장된 BGM 볼륨값 적용 (시스템 볼륨 변경)
                self.set_bgm_volume(self._bgm_volume)

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

        # [참고] 효과음 볼륨을 0으로 설정했다면 재생하지 않음 (간이 음소거 구현)
        if self._sfx_volume == 0:
            return

        try:
            if self._system_os == "Windows":
                import winsound

                # winsound는 볼륨 조절 불가 (시스템 볼륨 따름)
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
