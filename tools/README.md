# Tools

Most scripts in this directory are personal Linux/Python/BASH-oriented reverse-engineering helpers from the 1.00/1.05 investigation. They are retained for reproducibility.

- `ppuhash.py` — compute PPU executable hash from a decrypted ELF.
- `findf32.py` — find aligned 32-bit big-endian float occurrences in an EMAIN ELF.
- `xref_lfs.py`, `xref16.txt` — cross-reference `lfs` instructions to the 16 constants.
- `ppumem.py` — locate PPU base in an RPCS3 Linux process and read/write PPU virtual addresses.
- `pkg_extract.py` — minimal PS3 PKG extractor.
- `rtti.py`, `ppcdis.py`, `blxref.py`, `opdxref.py`, `ctx.py` — assorted reverse-engineering helpers.
- `keys2.py`, `click_yes.py` — UI automation helpers, not required for the stable patch.

Windows users should treat the Linux-only scripts (`ppumem.py`, `keys2.py`) as reference material or port them via `ctypes`. The Windows memory scanning steps are documented in `PATCH_BUILD_GUIDE.md`.