"""Killable platform credential-store worker.

The parent process supplies refs and values as JSON on stdin. This module
emits one small JSON result and never includes raw exception text.
"""

from __future__ import annotations

import contextlib
import ctypes
import importlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
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
# Test-only seam: point the macOS adapter at a throwaway keychain instead of
# the user's default. Honored only for a file named ``mbtest-*.keychain-db``
# outside ``~/Library/Keychains``; any other value refuses to run.
TEST_KEYCHAIN_ENV = "MB_CREDENTIAL_TEST_KEYCHAIN"
# Apple-signed, so its keychain identity survives Python, uv and macOS updates.
SECURITY_TOOL = "/usr/bin/security"
# `security -i` rejects input lines longer than about 4 KB; leave room for the
# command, the ref and a keychain path around the hex value.
SECURITY_HEX_LIMIT = 3600
DEFAULT_BUDGET_SECONDS = 6.0


_SAFE_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9:/._@+_-]{0,511}")


class _PromptPending(Exception):
    """A keychain operation would have to wait on a macOS dialog."""


def _emit(state: str, *, value: str | None = None, migrated: bool = False) -> int:
    payload: dict[str, Any] = {"state": state}
    if value is not None:
        payload["value"] = value
    if migrated:
        payload["migrated"] = True
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


def _denied_state(status: int, *, health: str) -> str:
    """Classify an item-level refusal once keychain health is known.

    With user interaction disabled, an item whose access list does not trust
    this interpreter fails at once instead of showing a dialog. On an unlocked
    keychain that refusal means a macOS prompt would be waiting for a click.
    """

    state = _status_state(status)
    if health == "ready" and state in {"auth-failed", "locked"}:
        return "prompt-pending"
    return state


def _denied_state_for(state: str, *, health: str) -> str:
    if health == "ready" and state in {"auth-failed", "locked"}:
        return "prompt-pending"
    return state


def _parse_security_password(text: str) -> str | None:
    """Decode the ``password:`` line that ``security find-generic-password -g`` writes.

    ``security`` prints a printable value in double quotes, unescaped, and
    any other value as ``0x`` followed by hex, so the two never collide.
    """

    for line in text.splitlines():
        if not line.startswith("password: "):
            continue
        rest = line[len("password: ") :]
        if rest == "":
            return ""
        if len(rest) >= 2 and rest.startswith('"') and rest.endswith('"'):
            return rest[1:-1]
        if rest.startswith("0x"):
            try:
                return bytes.fromhex(rest[2:].split(" ", 1)[0]).decode("utf-8")
            except ValueError:
                return None
        return None
    return None


def _test_keychain_path() -> str | None:
    """Return the throwaway keychain named by the test seam, if any.

    Absent means the user's keychain. Present means a throwaway keychain or
    nothing: an empty value, a wrong name, a path under ``~/Library/Keychains``,
    a symlink into it, or a hard-linked file all raise, so the seam can never
    fall through to, or alias, the login keychain.
    """

    if TEST_KEYCHAIN_ENV not in os.environ:
        return None
    raw = os.environ[TEST_KEYCHAIN_ENV]
    if not raw.strip():
        raise RuntimeError("refusing test keychain")
    path = Path(raw).expanduser().resolve()
    keychains = (Path.home() / "Library" / "Keychains").resolve()
    if (
        not path.name.startswith("mbtest-")
        or not path.name.endswith(".keychain-db")
        or path.is_relative_to(keychains)
        or not path.is_file()
        or path.stat().st_nlink != 1
    ):
        raise RuntimeError("refusing test keychain")
    return str(path)


class _MacSecurity:
    """Minimal ctypes bridge for generic-password operations."""

    def __init__(
        self, *, interactive: bool = False, budget: float = DEFAULT_BUDGET_SECONDS
    ) -> None:
        self.deadline = time.monotonic() + budget
        self.migrated = False
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
        self.security.SecKeychainSetUserInteractionAllowed.argtypes = [ctypes.c_bool]
        self.security.SecKeychainSetUserInteractionAllowed.restype = ctypes.c_int32
        self.security.SecKeychainOpen.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.security.SecKeychainOpen.restype = ctypes.c_int32
        self.core.CFArrayCreate.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_long,
            ctypes.c_void_p,
        ]
        self.core.CFArrayCreate.restype = ctypes.c_void_p
        self.core.CFArrayGetCount.argtypes = [ctypes.c_void_p]
        self.core.CFArrayGetCount.restype = ctypes.c_long
        self.core.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]
        self.core.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
        self.security.SecKeychainItemCopyAccess.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.security.SecKeychainItemCopyAccess.restype = ctypes.c_int32
        self.security.SecAccessCopyMatchingACLList.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.security.SecAccessCopyMatchingACLList.restype = ctypes.c_void_p
        self.security.SecACLCopyContents.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_uint16),
        ]
        self.security.SecACLCopyContents.restype = ctypes.c_int32
        self.security.SecTrustedApplicationCopyData.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.security.SecTrustedApplicationCopyData.restype = ctypes.c_int32
        if not interactive:
            # kSecUseAuthenticationUIFail does not suppress the file-keychain
            # access dialog; this does. It must run before any keychain call,
            # so an untrusted read fails at once instead of waiting on a click.
            status = int(self.security.SecKeychainSetUserInteractionAllowed(False))
            if status != ERR_SEC_SUCCESS:
                raise RuntimeError("could not disable keychain interaction")
        self.keychain: int | None = None
        self.search_list: int | None = None
        test_path = _test_keychain_path()
        self.keychain_path = test_path
        if test_path is not None:
            keychain = ctypes.c_void_p()
            status = int(
                self.security.SecKeychainOpen(test_path.encode("utf-8"), ctypes.byref(keychain))
            )
            if status != ERR_SEC_SUCCESS or not keychain.value:
                raise RuntimeError("could not open test keychain")
            self.keychain = int(keychain.value)
            items = (ctypes.c_void_p * 1)(self.keychain)
            search_list = self.core.CFArrayCreate(None, items, 1, None)
            if not search_list:
                raise RuntimeError("could not allocate search list")
            self.search_list = int(search_list)

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

    def _query(
        self, ref: str, *, return_data: bool = False, return_ref: bool = False
    ) -> tuple[int, list[int]]:
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
        if self.search_list is not None:
            pairs.append((self._constant(self.security, "kSecMatchSearchList"), self.search_list))
        if return_data or return_ref:
            pairs.extend(
                [
                    (
                        self._constant(self.security, "kSecMatchLimit"),
                        self._constant(self.security, "kSecMatchLimitOne"),
                    ),
                    (
                        self._constant(
                            self.security, "kSecReturnData" if return_data else "kSecReturnRef"
                        ),
                        self._constant(self.core, "kCFBooleanTrue"),
                    ),
                ]
            )
        return self._dictionary(pairs), owned

    def _release_all(self, values: list[int]) -> None:
        for value in values:
            self.core.CFRelease(value)

    # -- Legacy items: created by a Python interpreter through SecItem ------

    def _ctypes_get(self, ref: str, *, health: str) -> tuple[str, str | None]:
        query, owned = self._query(ref, return_data=True)
        result = ctypes.c_void_p()
        try:
            status = int(self.security.SecItemCopyMatching(query, ctypes.byref(result)))
            if status != ERR_SEC_SUCCESS:
                return _denied_state(status, health=health), None
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

    def _ctypes_add(self, ref: str, value: str) -> int:
        service = self._string(SERVICE_NAME)
        account = self._string(ref)
        data = self._data(value)
        pairs = [
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
        if self.keychain is not None:
            pairs.append((self._constant(self.security, "kSecUseKeychain"), self.keychain))
        add = self._dictionary(pairs)
        try:
            return int(self.security.SecItemAdd(add, None))
        finally:
            self.core.CFRelease(add)
            self._release_all([service, account, data])

    def _ctypes_delete(self, ref: str) -> int:
        query, owned = self._query(ref)
        try:
            return int(self.security.SecItemDelete(query))
        finally:
            self.core.CFRelease(query)
            self._release_all(owned)

    # -- Which code an item trusts (non-secret, never prompts) --------------

    def _item_owner(self, ref: str) -> str:
        """Return ``security``, ``legacy`` or ``absent`` for one item, or a failure state.

        Reads the item's access list, never its data, so it cannot prompt. An
        item counts as ``security`` only when ``/usr/bin/security`` is the
        first application its decrypt rule trusts, which is how macOS records
        the creating tool. Only those items are ever read through ``security``:
        it has no way to refuse a dialog, so any other item could block on one.
        """

        query, owned = self._query(ref, return_ref=True)
        item = ctypes.c_void_p()
        access = ctypes.c_void_p()
        acls: int | None = None
        apps = ctypes.c_void_p()
        description = ctypes.c_void_p()
        try:
            status = int(self.security.SecItemCopyMatching(query, ctypes.byref(item)))
            if status == ERR_SEC_ITEM_NOT_FOUND:
                return "absent"
            if status != ERR_SEC_SUCCESS or not item.value:
                return _status_state(status) if status != ERR_SEC_SUCCESS else "unavailable"
            status = int(self.security.SecKeychainItemCopyAccess(item, ctypes.byref(access)))
            if status != ERR_SEC_SUCCESS or not access.value:
                return "legacy"
            acls = self.security.SecAccessCopyMatchingACLList(
                access, self._constant(self.security, "kSecACLAuthorizationDecrypt")
            )
            if not acls or int(self.core.CFArrayGetCount(acls)) < 1:
                return "legacy"
            acl = self.core.CFArrayGetValueAtIndex(acls, 0)
            selector = ctypes.c_uint16()
            status = int(
                self.security.SecACLCopyContents(
                    acl, ctypes.byref(apps), ctypes.byref(description), ctypes.byref(selector)
                )
            )
            if status != ERR_SEC_SUCCESS or not apps.value:
                # No application list means any application; still not proof
                # that `security` can read it without a partition prompt.
                return "legacy"
            if int(self.core.CFArrayGetCount(apps.value)) < 1:
                return "legacy"
            first = self.core.CFArrayGetValueAtIndex(apps.value, 0)
            data = ctypes.c_void_p()
            status = int(self.security.SecTrustedApplicationCopyData(first, ctypes.byref(data)))
            if status != ERR_SEC_SUCCESS or not data.value:
                return "legacy"
            try:
                length = int(self.core.CFDataGetLength(data.value))
                path = ctypes.string_at(self.core.CFDataGetBytePtr(data.value), length)
            finally:
                self.core.CFRelease(data.value)
            return "security" if path.rstrip(b"\0") == SECURITY_TOOL.encode() else "legacy"
        finally:
            for value in (description.value, apps.value, acls, access.value, item.value):
                if value:
                    self.core.CFRelease(value)
            self.core.CFRelease(query)
            self._release_all(owned)

    # -- Items created by Apple-signed /usr/bin/security ---------------------

    def _security_tool(self, args: list[str], *, stdin: str | None = None) -> Any:
        """Run ``/usr/bin/security`` within the remaining budget.

        ``security`` cannot be told to fail instead of showing a dialog, so the
        caller must already have proved the item trusts it; this deadline is
        the last guard, and expiry reports a pending prompt.
        """

        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise _PromptPending
        try:
            if stdin is None:
                return subprocess.run(
                    [SECURITY_TOOL, *args],
                    check=False,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=remaining,
                )
            return subprocess.run(
                [SECURITY_TOOL, *args],
                check=False,
                input=stdin,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=remaining,
            )
        except subprocess.TimeoutExpired as exc:
            raise _PromptPending from exc

    def _keychain_args(self) -> list[str]:
        return [self.keychain_path] if self.keychain_path is not None else []

    def _security_get(self, ref: str) -> tuple[str, str | None]:
        completed = self._security_tool(
            ["find-generic-password", "-s", SERVICE_NAME, "-a", ref, "-g", *self._keychain_args()]
        )
        if completed.returncode != 0:
            return ("missing" if completed.returncode == 44 else "unavailable"), None
        value = _parse_security_password(completed.stderr or "")
        if value is None:
            return "unavailable", None
        return "ready", value

    def _security_put(self, ref: str, value: str, *, exists: bool) -> str:
        """Write ``value`` so that ``/usr/bin/security`` owns the item.

        The value goes over stdin as hex (``security -i``), never in argv. A
        value too long for one ``security -i`` line is written as an empty
        item by ``security`` and then filled in through the Security
        framework, which leaves the item's access list unchanged.
        """

        encoded = value.encode("utf-8").hex()
        fits = len(encoded) <= SECURITY_HEX_LIMIT
        keychain = f' "{self.keychain_path}"' if self.keychain_path is not None else ""
        if exists and not fits:
            status = self._update(ref, value)
            return "ready" if status == ERR_SEC_SUCCESS else _status_state(status)
        flag = "-U " if exists else ""
        hex_value = encoded if fits else ""
        command = (
            f'add-generic-password {flag}-s {SERVICE_NAME} -a "{ref}" -X "{hex_value}"{keychain}\n'
        )
        completed = self._security_tool(["-i"], stdin=command)
        if completed.returncode != 0 or "returned -" in (completed.stderr or ""):
            return "unavailable"
        if not fits:
            status = self._update(ref, value)
            if status != ERR_SEC_SUCCESS:
                return _status_state(status)
        return "ready"

    def _security_delete(self, ref: str) -> str:
        completed = self._security_tool(
            ["delete-generic-password", "-s", SERVICE_NAME, "-a", ref, *self._keychain_args()]
        )
        if completed.returncode == 0:
            return "ready"
        return "missing" if completed.returncode == 44 else "unavailable"

    def _verified(self, ref: str, value: str) -> bool:
        if self._item_owner(ref) != "security":
            return False
        state, stored = self._security_get(ref)
        return state == "ready" and stored == value

    def _migrate(self, ref: str, value: str) -> bool:
        """Re-create a legacy item under ``/usr/bin/security``; never lose it.

        The value is already in memory. Delete the legacy item, add it back
        through ``security`` and read it back the same way. If any step
        fails, put the legacy item back exactly as this Python can read it.
        """

        if self._ctypes_delete(ref) != ERR_SEC_SUCCESS:
            return False
        try:
            if self._security_put(ref, value, exists=False) == "ready" and self._verified(
                ref, value
            ):
                return True
        except _PromptPending:
            pass
        with contextlib.suppress(_PromptPending):
            if self._item_owner(ref) == "security":
                self._security_delete(ref)
        if self._ctypes_add(ref, value) != ERR_SEC_SUCCESS:
            # Last resort: keep the value somewhere this Python can read it.
            self._update(ref, value)
        return False

    # -- Public operations ---------------------------------------------------

    def get(self, ref: str) -> tuple[str, str | None]:
        health = self.health()
        if health != "ready":
            # A locked keychain would need an unlock dialog: fail fast.
            return health, None
        owner = self._item_owner(ref)
        if owner == "absent":
            return "missing", None
        if owner == "security":
            return self._security_get(ref)
        if owner != "legacy":
            return _denied_state_for(owner, health=health), None
        state, value = self._ctypes_get(ref, health=health)
        if state == "ready" and value is not None:
            self.migrated = self._migrate(ref, value)
        return state, value

    def set(self, ref: str, value: str) -> str:
        health = self.health()
        if health != "ready":
            return health
        owner = self._item_owner(ref)
        if owner == "security":
            return self._security_put(ref, value, exists=True)
        if owner == "legacy":
            # Replace the value in place first, so a failure never loses the
            # previous credential, then move the item exactly as a read would.
            # If this Python may not remove the old item, it stays legacy and a
            # later read reports the pending prompt for the keychain repair.
            status = self._update(ref, value)
            if status != ERR_SEC_SUCCESS:
                return _denied_state(status, health=health)
            self._migrate(ref, value)
            return "ready"
        if owner != "absent":
            return _denied_state_for(owner, health=health)
        state = self._security_put(ref, value, exists=False)
        if state != "ready":
            # Never leave a write undone: fall back to the legacy store.
            status = self._ctypes_add(ref, value)
            if status == ERR_SEC_DUPLICATE_ITEM:
                status = self._update(ref, value)
            return "ready" if status == ERR_SEC_SUCCESS else _denied_state(status, health=health)
        return "ready"

    def delete(self, ref: str) -> str:
        health = self.health()
        if health != "ready":
            return health
        owner = self._item_owner(ref)
        if owner == "absent":
            return "missing"
        if owner == "security":
            return self._security_delete(ref)
        status = self._ctypes_delete(ref)
        return "ready" if status == ERR_SEC_SUCCESS else _denied_state(status, health=health)

    def health(self) -> str:
        flags = ctypes.c_uint32()
        if self.keychain is not None:
            status = int(self.security.SecKeychainGetStatus(self.keychain, ctypes.byref(flags)))
        else:
            keychain = ctypes.c_void_p()
            status = int(self.security.SecKeychainCopyDefault(ctypes.byref(keychain)))
            if status != ERR_SEC_SUCCESS:
                return _status_state(status)
            try:
                status = int(self.security.SecKeychainGetStatus(keychain, ctypes.byref(flags)))
            finally:
                if keychain.value:
                    self.core.CFRelease(keychain.value)
        if status != ERR_SEC_SUCCESS:
            return _status_state(status)
        return "ready" if flags.value & KEYCHAIN_UNLOCKED_STATUS else "locked"


def _macos(action: str, payload: dict[str, Any]) -> tuple[str, str | None, bool]:
    if platform.system() != "Darwin":
        return "unavailable", None, False
    budget = payload.get("budget_seconds")
    adapter = _MacSecurity(
        interactive=payload.get("interactive") is True,
        budget=float(budget) if isinstance(budget, (int, float)) else DEFAULT_BUDGET_SECONDS,
    )
    ref = str(payload.get("ref") or "")
    if action == "health":
        return adapter.health(), None, False
    if not ref or not _SAFE_REF.fullmatch(ref):
        # Refs are generated by mb; anything else could break `security -i` quoting.
        return "unavailable", None, False
    try:
        if action == "get":
            state, value = adapter.get(ref)
            return state, value, adapter.migrated
        if action == "set":
            value = payload.get("value")
            if not isinstance(value, str):
                return "unavailable", None, False
            return adapter.set(ref, value), None, False
        if action == "delete":
            return adapter.delete(ref), None, False
    except _PromptPending:
        return "prompt-pending", None, False
    return "unavailable", None, False


def _secret_service_items(collection: Any, ref: str) -> list[Any]:
    return list(collection.search_items({"service": SERVICE_NAME, "username": ref}))


def _secret_service_item(items: list[Any]) -> Any | None:
    """Choose one compatible item without depending on service search order."""

    if not items:
        return None
    if len(items) == 1:
        return items[0]
    by_application: dict[str, list[Any]] = {}
    for item in items:
        attributes = item.get_attributes()
        application = str(attributes.get("application") or "")
        by_application.setdefault(application, []).append(item)
    for application in ("mainbranch", "Python keyring library"):
        matches = by_application.get(application, [])
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise RuntimeError("ambiguous credential items")
    raise RuntimeError("ambiguous credential items")


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
    item = _secret_service_item(items)
    if action == "get":
        if item is None:
            return "missing", None
        secret = item.get_secret()
        return "ready", bytes(secret).decode("utf-8")
    if action == "set":
        value = payload.get("value")
        if not isinstance(value, str):
            return "unavailable", None
        if item is not None:
            # Update the matched item in place. In particular, preserve the
            # attributes on legacy Python keyring items instead of creating a
            # second record whose application attribute differs.
            item.set_secret(value.encode("utf-8"))
            return "ready", None
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
        migrated = False
        if backend == "macos-keychain":
            state, value, migrated = _macos(action, payload)
        elif backend == "secret-service":
            state, value = _secret_service(action, payload)
        else:
            state, value = "unavailable", None
    except BaseException as exc:
        state, value, migrated = _secret_service_state(exc), None, False
    return _emit(state, value=value, migrated=migrated)


if __name__ == "__main__":
    raise SystemExit(main())
