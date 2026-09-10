"""Killable platform credential-store worker.

The parent process supplies refs and values as JSON on stdin. This module
emits one small JSON result and never includes raw exception text.
"""

from __future__ import annotations

import ctypes
import importlib
import json
import platform
import sys
from typing import Any

SERVICE_NAME = "mainbranch"
ERR_SEC_SUCCESS = 0
ERR_SEC_DUPLICATE_ITEM = -25299
ERR_SEC_ITEM_NOT_FOUND = -25300
ERR_SEC_AUTH_FAILED = -25293
ERR_SEC_INTERACTION_NOT_ALLOWED = -25308
ERR_SEC_USER_CANCELED = -128
KEYCHAIN_UNLOCKED_STATUS = 1
CF_STRING_ENCODING_UTF8 = 0x08000100


def _emit(state: str, *, value: str | None = None) -> int:
    payload: dict[str, str] = {"state": state}
    if value is not None:
        payload["value"] = value
    sys.stdout.write(json.dumps(payload, separators=(",", ":")))
    return 0 if state in {"ready", "missing"} else 1


def _status_state(status: int) -> str:
    if status == ERR_SEC_ITEM_NOT_FOUND:
        return "missing"
    if status == ERR_SEC_AUTH_FAILED:
        return "auth-failed"
    if status in {ERR_SEC_INTERACTION_NOT_ALLOWED, ERR_SEC_USER_CANCELED}:
        return "locked"
    return "unavailable"


class _MacSecurity:
    """Minimal ctypes bridge for generic-password operations."""

    def __init__(self) -> None:
        self.security = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")
        self.core = ctypes.CDLL(
            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        )
        self.core.CFStringCreateWithCString.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_uint32,
        ]
        self.core.CFStringCreateWithCString.restype = ctypes.c_void_p
        self.core.CFDataCreate.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_long,
        ]
        self.core.CFDataCreate.restype = ctypes.c_void_p
        self.core.CFDataGetLength.argtypes = [ctypes.c_void_p]
        self.core.CFDataGetLength.restype = ctypes.c_long
        self.core.CFDataGetBytePtr.argtypes = [ctypes.c_void_p]
        self.core.CFDataGetBytePtr.restype = ctypes.POINTER(ctypes.c_ubyte)
        self.core.CFDictionaryCreateMutable.argtypes = [
            ctypes.c_void_p,
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.core.CFDictionaryCreateMutable.restype = ctypes.c_void_p
        self.core.CFDictionarySetValue.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.core.CFRelease.argtypes = [ctypes.c_void_p]
        self.security.SecItemCopyMatching.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.security.SecItemCopyMatching.restype = ctypes.c_int32
        self.security.SecItemUpdate.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.security.SecItemUpdate.restype = ctypes.c_int32
        self.security.SecItemAdd.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.security.SecItemAdd.restype = ctypes.c_int32
        self.security.SecItemDelete.argtypes = [ctypes.c_void_p]
        self.security.SecItemDelete.restype = ctypes.c_int32
        self.security.SecKeychainCopyDefault.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.security.SecKeychainCopyDefault.restype = ctypes.c_int32
        self.security.SecKeychainGetStatus.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.security.SecKeychainGetStatus.restype = ctypes.c_int32

    @staticmethod
    def _constant(library: Any, name: str) -> int:
        value = ctypes.c_void_p.in_dll(library, name).value
        if value is None:
            raise RuntimeError("missing framework constant")
        return value

    def _string(self, value: str) -> int:
        result = self.core.CFStringCreateWithCString(
            None,
            value.encode("utf-8"),
            CF_STRING_ENCODING_UTF8,
        )
        if not result:
            raise RuntimeError("could not allocate string")
        return int(result)

    def _data(self, value: str) -> int:
        raw = value.encode("utf-8")
        buffer = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
        result = self.core.CFDataCreate(None, buffer, len(raw))
        if not result:
            raise RuntimeError("could not allocate data")
        return int(result)

    def _dictionary(self, pairs: list[tuple[int, int]]) -> int:
        # Null callbacks are intentional: every key/value remains alive for
        # the duration of the synchronous Security.framework call.
        result = self.core.CFDictionaryCreateMutable(None, 0, None, None)
        if not result:
            raise RuntimeError("could not allocate dictionary")
        for key, value in pairs:
            self.core.CFDictionarySetValue(result, key, value)
        return int(result)

    def _query(self, ref: str, *, return_data: bool = False) -> tuple[int, list[int]]:
        service = self._string(SERVICE_NAME)
        account = self._string(ref)
        owned = [service, account]
        pairs = [
            (
                self._constant(self.security, "kSecClass"),
                self._constant(self.security, "kSecClassGenericPassword"),
            ),
            (self._constant(self.security, "kSecAttrService"), service),
            (self._constant(self.security, "kSecAttrAccount"), account),
            (
                self._constant(self.security, "kSecUseAuthenticationUI"),
                self._constant(self.security, "kSecUseAuthenticationUIFail"),
            ),
        ]
        if return_data:
            pairs.extend(
                [
                    (
                        self._constant(self.security, "kSecMatchLimit"),
                        self._constant(self.security, "kSecMatchLimitOne"),
                    ),
                    (
                        self._constant(self.security, "kSecReturnData"),
                        self._constant(self.core, "kCFBooleanTrue"),
                    ),
                ]
            )
        return self._dictionary(pairs), owned

    def _release_all(self, values: list[int]) -> None:
        for value in values:
            self.core.CFRelease(value)

    def get(self, ref: str) -> tuple[str, str | None]:
        query, owned = self._query(ref, return_data=True)
        result = ctypes.c_void_p()
        try:
            status = int(self.security.SecItemCopyMatching(query, ctypes.byref(result)))
            if status != ERR_SEC_SUCCESS:
                return _status_state(status), None
            if not result.value:
                return "unavailable", None
            length = int(self.core.CFDataGetLength(result.value))
            pointer = self.core.CFDataGetBytePtr(result.value)
            raw = ctypes.string_at(pointer, length)
            return "ready", raw.decode("utf-8")
        finally:
            if result.value:
                self.core.CFRelease(result.value)
            self.core.CFRelease(query)
            self._release_all(owned)

    def _update(self, ref: str, value: str) -> int:
        query, query_owned = self._query(ref)
        data = self._data(value)
        update = self._dictionary([(self._constant(self.security, "kSecValueData"), data)])
        try:
            return int(self.security.SecItemUpdate(query, update))
        finally:
            self.core.CFRelease(update)
            self.core.CFRelease(query)
            self._release_all(query_owned)
            self.core.CFRelease(data)

    def set(self, ref: str, value: str) -> str:
        status = self._update(ref, value)
        if status == ERR_SEC_SUCCESS:
            return "ready"
        if status != ERR_SEC_ITEM_NOT_FOUND:
            return _status_state(status)

        service = self._string(SERVICE_NAME)
        account = self._string(ref)
        data = self._data(value)
        add = self._dictionary(
            [
                (
                    self._constant(self.security, "kSecClass"),
                    self._constant(self.security, "kSecClassGenericPassword"),
                ),
                (self._constant(self.security, "kSecAttrService"), service),
                (self._constant(self.security, "kSecAttrAccount"), account),
                (self._constant(self.security, "kSecValueData"), data),
                (
                    self._constant(self.security, "kSecUseAuthenticationUI"),
                    self._constant(self.security, "kSecUseAuthenticationUIFail"),
                ),
            ]
        )
        try:
            status = int(self.security.SecItemAdd(add, None))
        finally:
            self.core.CFRelease(add)
            self._release_all([service, account, data])
        if status == ERR_SEC_DUPLICATE_ITEM:
            # Another writer won the add race. Update in-place rather than
            # delete/re-add so the prior value survives a failed replacement.
            status = self._update(ref, value)
        return "ready" if status == ERR_SEC_SUCCESS else _status_state(status)

    def delete(self, ref: str) -> str:
        query, owned = self._query(ref)
        try:
            status = int(self.security.SecItemDelete(query))
        finally:
            self.core.CFRelease(query)
            self._release_all(owned)
        return "ready" if status == ERR_SEC_SUCCESS else _status_state(status)

    def health(self) -> str:
        keychain = ctypes.c_void_p()
        status = int(self.security.SecKeychainCopyDefault(ctypes.byref(keychain)))
        if status != ERR_SEC_SUCCESS:
            return _status_state(status)
        flags = ctypes.c_uint32()
        try:
            status = int(self.security.SecKeychainGetStatus(keychain, ctypes.byref(flags)))
        finally:
            if keychain.value:
                self.core.CFRelease(keychain.value)
        if status != ERR_SEC_SUCCESS:
            return _status_state(status)
        return "ready" if flags.value & KEYCHAIN_UNLOCKED_STATUS else "locked"


def _macos(action: str, payload: dict[str, Any]) -> tuple[str, str | None]:
    if platform.system() != "Darwin":
        return "unavailable", None
    adapter = _MacSecurity()
    ref = str(payload.get("ref") or "")
    if action == "health":
        return adapter.health(), None
    if not ref:
        return "unavailable", None
    if action == "get":
        return adapter.get(ref)
    if action == "set":
        value = payload.get("value")
        if not isinstance(value, str):
            return "unavailable", None
        return adapter.set(ref, value), None
    if action == "delete":
        return adapter.delete(ref), None
    return "unavailable", None


def _secret_service_items(collection: Any, ref: str) -> list[Any]:
    return list(collection.search_items({"service": SERVICE_NAME, "username": ref}))


def _secret_service_state(exc: BaseException) -> str:
    name = type(exc).__name__.lower()
    if "locked" in name or "prompt" in name or "cancel" in name:
        return "locked"
    return "unavailable"


def _secret_service(action: str, payload: dict[str, Any]) -> tuple[str, str | None]:
    if platform.system() != "Linux":
        return "unavailable", None
    module = importlib.import_module("secretstorage")
    connection = module.dbus_init()
    collection = module.get_collection_by_alias(connection, "default")
    if collection is None:
        return "unavailable", None
    if collection.is_locked():
        return "locked", None
    if action == "health":
        return "ready", None
    ref = str(payload.get("ref") or "")
    if not ref:
        return "unavailable", None
    items = _secret_service_items(collection, ref)
    if any(item.is_locked() for item in items):
        return "locked", None
    if action == "get":
        if not items:
            return "missing", None
        secret = items[0].get_secret()
        return "ready", bytes(secret).decode("utf-8")
    if action == "set":
        value = payload.get("value")
        if not isinstance(value, str):
            return "unavailable", None
        collection.create_item(
            f"Main Branch credential ({ref})",
            {
                "application": "mainbranch",
                "service": SERVICE_NAME,
                "username": ref,
            },
            value.encode("utf-8"),
            replace=True,
        )
        return "ready", None
    if action == "delete":
        for item in items:
            item.delete()
        return ("ready" if items else "missing"), None
    return "unavailable", None


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read(1_048_577)
    if len(raw) > 1_048_576:
        raise ValueError("payload too large")
    value = json.loads(raw or "{}")
    if not isinstance(value, dict):
        raise ValueError("payload must be an object")
    return value


def main() -> int:
    if len(sys.argv) != 3:
        return _emit("unavailable")
    backend, action = sys.argv[1:]
    if action not in {"get", "set", "delete", "health"}:
        return _emit("unavailable")
    try:
        payload = _read_payload()
        if backend == "macos-keychain":
            state, value = _macos(action, payload)
        elif backend == "secret-service":
            state, value = _secret_service(action, payload)
        else:
            state, value = "unavailable", None
    except BaseException as exc:
        state, value = _secret_service_state(exc), None
    return _emit(state, value=value)


if __name__ == "__main__":
    raise SystemExit(main())
