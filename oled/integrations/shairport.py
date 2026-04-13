"""Shairport-Sync metadata reader without external parser dependencies."""
import asyncio
import base64
import os
import re
from typing import Optional

import settings


class ShairportMetadata():
    def __init__(self, loop, eventbus=None):
        self.loop = loop
        self.eventbus = eventbus
        self.metadata_pipe = getattr(settings, "SHAIRPORT_METADATA_PIPE")
        self._info = {}
        self.connected = False
        self._last_volume: Optional[int] = None
        self.client_name = "AirPlay"
        self._task = self.loop.create_task(self._listen_pipe())

    def _ensure_pipe_exists(self):
        if os.path.exists(self.metadata_pipe):
            return
        if hasattr(os, "mkfifo"):
            try:
                os.mkfifo(self.metadata_pipe)
            except FileExistsError:
                pass

    def _worker_read_pipe(self):
        with open(self.metadata_pipe, "r", encoding="utf-8", errors="ignore") as pipe:
            print(f"Connected to Shairport metadata pipe: {self.metadata_pipe}")
            current_item = ""
            for line in pipe:
                current_item += line
                if "</item>" in line:
                    self._handle_xml_item(current_item)
                    current_item = ""

    async def _listen_pipe(self):
        pipe_not_found_logged = False
        while self.loop.is_running():
            try:
                self._ensure_pipe_exists()
                await asyncio.to_thread(self._worker_read_pipe)
                pipe_not_found_logged = False
            except FileNotFoundError:
                if not pipe_not_found_logged:
                    print(
                        f"Shairport metadata pipe not found ({self.metadata_pipe}), "
                        "AirPlay info unavailable."
                    )
                    pipe_not_found_logged = True
            except asyncio.CancelledError:
                return
            except Exception as err:  # pragma: no cover
                print(f"Error while reading Shairport metadata: {err}")

            await asyncio.sleep(1)

    def _decode_code(self, code_raw: str) -> str:
        code_raw = code_raw.strip()
        try:
            return bytes.fromhex(code_raw).decode("utf-8", errors="replace")
        except ValueError:
            return code_raw

    def _set_info(self, key: str, value: str):
        if self._info.get(key) == value:
            return
        self._info[key] = value
        self._set_connected(True)
        self._emit_nowplaying()

    def _handle_stream_code(self, code: str):
        if code in {"pbeg", "pfls", "prsm", "abeg"}:
            self._set_connected(True)
            self._emit_nowplaying()
            return

        if code in {"pend", "disc", "aend"}:
            self._set_connected(False)
            self._emit_nowplaying()

    def _decode_b64_bytes(self, data_b64: str) -> Optional[bytes]:
        try:
            return base64.b64decode(data_b64, validate=False)
        except Exception:
            return None

    def _decode_b64_text(self, data_b64: str) -> Optional[str]:
        decoded = self._decode_b64_bytes(data_b64)
        if decoded is None:
            return None
        return decoded.decode("utf-8", errors="replace").strip()

    def _parse_airplay_volume(self, payload_text: str) -> Optional[int]:
        if not payload_text:
            return None

        try:
            db_value = float(payload_text.split(",", maxsplit=1)[0])
        except ValueError:
            return None

        if db_value <= -100:
            return 0
        if db_value >= 0:
            return 100

        return max(0, min(100, round((db_value + 30.0) * (100.0 / 30.0))))

    def _handle_xml_item(self, item_xml: str):
        code_match = re.search(r"<code>(.*?)</code>", item_xml, re.DOTALL)
        data_match = re.search(r"<data encoding=\"base64\">(.*?)</data>", item_xml, re.DOTALL)
        if not code_match:
            return

        code = self._decode_code(code_match.group(1))
        data_b64 = ""
        if data_match:
            data_b64 = data_match.group(1).replace("\n", "").replace("\r", "").strip()

        if code == "PICT" and data_b64:
            self._info["cover_art"] = f"data:image/jpeg;base64,{data_b64}"
            self._set_connected(True)
            self._emit_nowplaying()
            return

        if code == "minm" and data_b64:
            title = self._decode_b64_text(data_b64)
            if title is not None:
                self._set_info("title", title)
            return

        if code == "asar" and data_b64:
            artist = self._decode_b64_text(data_b64)
            if artist is not None:
                self._set_info("artist", artist)
            return

        if code == "asal" and data_b64:
            album = self._decode_b64_text(data_b64)
            if album is not None:
                self._set_info("album", album)
            return

        if code == "snam" and data_b64:
            source_name = self._decode_b64_text(data_b64)
            if source_name:
                self.client_name = source_name
                self._emit_nowplaying()
            return

        if code == "pvol" and data_b64:
            payload = self._decode_b64_text(data_b64)
            if payload is not None:
                new_vol = self._parse_airplay_volume(payload)
                if new_vol is not None:
                    self._emit_volume(new_vol)
            return

        self._handle_stream_code(code)

    def _set_connected(self, connected: bool):
        if self.connected == connected:
            return

        self.connected = connected
        if self.eventbus is not None:
            self.eventbus.emit_threadsafe("airplay.connection", connected)

        if not connected:
            self._info = {}
            self._last_volume = None

    def _emit_nowplaying(self):
        if self.eventbus is not None:
            self.eventbus.emit_threadsafe("music.nowplaying", self.nowplaying())

    def _emit_volume(self, volume_percent: int):
        if self._last_volume == volume_percent:
            return

        self._last_volume = volume_percent
        print(f"Set volume to {volume_percent}% from AirPlay")
        if self.eventbus is not None:
            self.eventbus.emit_threadsafe("audio.volume", volume_percent)

    def nowplaying(self):
        info = {}

        # Name field is artist + album if available with fallback
        # to separate values and client name as last resort
        if 'artist' in self._info and 'album' in self._info:
            info['name'] = f"{self._info['artist']}: {self._info['album']}"
        elif 'artist' in self._info:
            info['name'] = self._info['artist']
        elif 'album' in self._info:
            info['name'] = self._info['album']
        else:
            info['name'] = self.client_name

        if 'title' in self._info:
            info['title'] = self._info['title']
        else:
            info['title'] = "AirPlay"

        if 'artist' in self._info:
            info['artist'] = self._info['artist']

        if 'cover_art' in self._info:
            info['cover_art'] = self._info['cover_art']

        return info

    def next(self):
        print("AirPlay next is not available.")

    def previous(self):
        print("AirPlay previous is not available.")

    def cleanup(self):
        if self._task is not None:
            self._task.cancel()
