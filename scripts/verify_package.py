"""Verify that the delivered EXE embeds the final application source."""

import argparse
import hashlib
import json
import marshal
from pathlib import Path
import types

import pefile
from PyInstaller.archive.readers import CArchiveReader


def normalized(code):
    if isinstance(code, types.CodeType):
        return code.replace(co_filename="<verified-source>", co_consts=tuple(normalized(item) for item in code.co_consts))
    if isinstance(code, tuple):
        return tuple(normalized(item) for item in code)
    return code


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--desktop", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    exe = root / "YaoguangQt.exe"
    archive = CArchiveReader(str(exe))
    pyz = archive.open_embedded_archive("PYZ.pyz")
    checks = {}
    for name in ["yaoguang_qt", "yaoguang_native", "yaoguang_devices", "yaoguang_watchdog"]:
        source = root / (name + ".py")
        embedded = marshal.loads(archive.extract(name)) if name == "yaoguang_qt" else pyz.extract(name)
        expected = compile(source.read_text(encoding="utf-8"), str(source), "exec", dont_inherit=True)
        checks[name] = normalized(embedded) == normalized(expected)
    forbidden = {"yaoguang_acceptance", "yaoguang_idle_acceptance", "unittest", "tests"}
    bundled_test_modules = sorted(name for name in pyz.toc if name in forbidden or name.startswith("tests.") or name.startswith("unittest."))
    manifests = []
    pe = pefile.PE(str(exe), fast_load=False)
    for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if entry.id == 24:
            for kind in entry.directory.entries:
                for language in kind.directory.entries:
                    data = language.data.struct
                    manifests.append(pe.get_data(data.OffsetToData, data.Size).decode("utf-8"))
    pe.close()
    report = {
        "exe_sha256": sha256(exe), "desktop_sha256": sha256(args.desktop),
        "bytes": exe.stat().st_size, "embedded_code_matches_final_source": checks,
        "administrator_manifest": any("requireAdministrator" in value for value in manifests),
        "source_sha256": {name + ".py": sha256(root / (name + ".py")) for name in checks},
        "bundled_test_modules": bundled_test_modules,
    }
    assert all(checks.values()), "EXE source does not match workspace source"
    assert report["exe_sha256"] == report["desktop_sha256"], "Desktop EXE differs from the project deliverable"
    assert report["administrator_manifest"], "Missing required administrator manifest"
    assert not bundled_test_modules, "Test or acceptance modules are bundled in the EXE"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
