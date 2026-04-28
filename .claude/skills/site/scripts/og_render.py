#!/usr/bin/env python3
"""og_render.py — deterministic OG-image rendering atom.

Subcommand:
    render <input_svg> [<output_png>]
        Renders the input SVG to a 1200x630 PNG via rsvg-convert (preferred,
        consistent text hinting) with cairosvg as a CI-tolerated fallback.
        Validates the output file exists, has the expected dimensions, and
        is within the OG-asset size budget.

Invocation: `python3 og_render.py render <input.svg> [<output.png>]`
Output: companyctx-shape envelope JSON on stdout, logs on stderr.
Exit code: 0 on ok|partial, 1 on degraded.

Why this is its own atom (per stacked-skill decision 2026-04-27):
- Site HTML/CSS/SVG generation happens via subagents inside the
  /site build --one-shot skill. That's not API work — Claude Code is
  the LLM.
- But the SVG → PNG render IS deterministic external work: shell out
  to a binary, validate output. Closed-enum errors. Companyctx envelope.
  Atom shape.
- Two render paths so the skill stays portable: rsvg-convert is the
  authoring/canonical render (consistent across machines), cairosvg
  is a CI fallback (rsvg is harder to install in some CI images).
"""

from __future__ import annotations

import os
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Literal

import click
from pydantic import BaseModel, ConfigDict, Field, model_validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _envelope import (  # noqa: E402
    SCHEMA_VERSION,
    EnvelopeStatus,
    ProviderRunMetadata,
    emit,
    log,
    validate_status_consistency,
)

# OG image canonical dimensions (Open Graph + Twitter large card baseline).
OG_WIDTH = 1200
OG_HEIGHT = 630
# Generous size cap. The atom's job is render + dimension validation; size
# budgets belong to the consuming skill. The cap here only catches obviously
# broken output (multi-MB renders from misconfigured rasters). Real-world
# OG PNGs with hand-drawn SVG illustrations land in the 400-900KB range —
# Howdy's shipped og.png is 670KB. 1MB is the "something's wrong" threshold.
OG_MAX_BYTES = 1024 * 1024


OgRenderErrorCode = Literal[
    "svg_input_missing",
    "svg_input_unreadable",
    "output_path_invalid",
    "rsvg_convert_unavailable",
    "cairosvg_unavailable",
    "no_renderer_available",
    "render_failed",
    "output_file_missing",
    "output_invalid_dimensions",
    "output_too_large",
]


class OgRenderError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: OgRenderErrorCode
    message: str
    suggestion: str | None = None


class OgRenderData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input_svg: str
    output_png: str
    renderer: Literal["rsvg-convert", "cairosvg"] | None = None
    width: int | None = None
    height: int | None = None
    output_bytes: int | None = None


class OgRenderEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["0.1.0"] = SCHEMA_VERSION
    status: EnvelopeStatus
    data: OgRenderData
    provenance: dict[str, ProviderRunMetadata] = Field(default_factory=dict)
    error: OgRenderError | None = None

    @model_validator(mode="after")
    def _v(self) -> OgRenderEnvelope:
        return validate_status_consistency(self)  # type: ignore[return-value]


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    """Read width+height from a PNG's IHDR chunk (no Pillow dependency)."""
    try:
        with path.open("rb") as fh:
            header = fh.read(24)
    except OSError:
        return None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    try:
        width, height = struct.unpack(">II", header[16:24])
    except struct.error:
        return None
    return width, height


def _render_rsvg(input_svg: Path, output_png: Path) -> tuple[bool, int, str | None]:
    binary = shutil.which("rsvg-convert")
    if not binary:
        return False, 0, "binary_missing"
    start = time.monotonic()
    try:
        proc = subprocess.run(
            [
                binary,
                "-w",
                str(OG_WIDTH),
                "-h",
                str(OG_HEIGHT),
                "-f",
                "png",
                "-o",
                str(output_png),
                str(input_svg),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return False, int((time.monotonic() - start) * 1000), "timeout"
    latency_ms = int((time.monotonic() - start) * 1000)
    if proc.returncode != 0:
        return False, latency_ms, f"exit_{proc.returncode}: {proc.stderr.strip()[:200]}"
    return True, latency_ms, None


def _render_cairosvg(input_svg: Path, output_png: Path) -> tuple[bool, int, str | None]:
    try:
        import cairosvg  # type: ignore[import-not-found]
    except ImportError:
        return False, 0, "module_missing"
    start = time.monotonic()
    try:
        cairosvg.svg2png(  # type: ignore[attr-defined]
            url=str(input_svg),
            write_to=str(output_png),
            output_width=OG_WIDTH,
            output_height=OG_HEIGHT,
        )
    except Exception as exc:  # cairosvg surfaces a wide range of internal errors
        return False, int((time.monotonic() - start) * 1000), f"{type(exc).__name__}: {exc!s}"[:200]
    return True, int((time.monotonic() - start) * 1000), None


@click.group()
def cli() -> None:
    """og_render.py — deterministic OG-image rendering atom."""


@cli.command("render")
@click.argument("input_svg", type=click.Path(path_type=Path))
@click.argument("output_png", required=False, type=click.Path(path_type=Path))
@click.option(
    "--prefer",
    type=click.Choice(["rsvg", "cairosvg"]),
    default="rsvg",
    show_default=True,
    help="Preferred renderer. The other is used as fallback if the preferred one is unavailable.",
)
def render(input_svg: Path, output_png: Path | None, prefer: str) -> None:
    """Render INPUT_SVG to OUTPUT_PNG (defaults to <input>.png) at 1200x630."""
    input_svg = input_svg.expanduser()
    if output_png is None:
        output_png = input_svg.with_suffix(".png")
    output_png = output_png.expanduser()

    provenance: dict[str, ProviderRunMetadata] = {}

    if not input_svg.exists():
        env = OgRenderEnvelope(
            status="degraded",
            data=OgRenderData(input_svg=str(input_svg), output_png=str(output_png)),
            error=OgRenderError(
                code="svg_input_missing",
                message=f"Input SVG not found: {input_svg}",
                suggestion="Pass the path to an existing og.svg file.",
            ),
        )
        sys.exit(emit(env))

    if not input_svg.is_file() or not os.access(input_svg, os.R_OK):
        env = OgRenderEnvelope(
            status="degraded",
            data=OgRenderData(input_svg=str(input_svg), output_png=str(output_png)),
            error=OgRenderError(
                code="svg_input_unreadable",
                message=f"Input SVG is not a readable file: {input_svg}",
                suggestion="Check file permissions and that the path points to a regular file.",
            ),
        )
        sys.exit(emit(env))

    output_dir = output_png.parent
    if output_dir and not output_dir.exists():
        env = OgRenderEnvelope(
            status="degraded",
            data=OgRenderData(input_svg=str(input_svg), output_png=str(output_png)),
            error=OgRenderError(
                code="output_path_invalid",
                message=f"Output directory does not exist: {output_dir}",
                suggestion="Create the directory or pass an output path inside an existing directory.",
            ),
        )
        sys.exit(emit(env))

    # Try preferred renderer first; fall through to the other.
    order = ["rsvg", "cairosvg"] if prefer == "rsvg" else ["cairosvg", "rsvg"]
    renderer_used: Literal["rsvg-convert", "cairosvg"] | None = None
    last_err: str | None = None

    for choice in order:
        if choice == "rsvg":
            log(f"Trying rsvg-convert {input_svg} -> {output_png} ({OG_WIDTH}x{OG_HEIGHT})...")
            ok, latency_ms, err = _render_rsvg(input_svg, output_png)
            provenance["rsvg_convert"] = ProviderRunMetadata(
                status="ok" if ok else ("not_configured" if err == "binary_missing" else "failed"),
                latency_ms=latency_ms,
                error=err,
                provider_version="rsvg-convert",
            )
            if ok:
                renderer_used = "rsvg-convert"
                break
            last_err = err
        else:
            log(f"Trying cairosvg {input_svg} -> {output_png} ({OG_WIDTH}x{OG_HEIGHT})...")
            ok, latency_ms, err = _render_cairosvg(input_svg, output_png)
            provenance["cairosvg"] = ProviderRunMetadata(
                status="ok" if ok else ("not_configured" if err == "module_missing" else "failed"),
                latency_ms=latency_ms,
                error=err,
                provider_version="cairosvg",
            )
            if ok:
                renderer_used = "cairosvg"
                break
            last_err = err

    if renderer_used is None:
        rsvg_present = "rsvg_convert" in provenance and provenance["rsvg_convert"].error != "binary_missing"
        cairosvg_present = "cairosvg" in provenance and provenance["cairosvg"].error != "module_missing"

        if not rsvg_present and not cairosvg_present:
            code: OgRenderErrorCode = "no_renderer_available"
            message = "Neither rsvg-convert nor cairosvg is installed."
            suggestion = "brew install librsvg (preferred) or pip install cairosvg."
        elif not rsvg_present and prefer == "rsvg":
            code = "rsvg_convert_unavailable"
            message = "rsvg-convert is not installed."
            suggestion = "brew install librsvg, or pass --prefer=cairosvg with `pip install cairosvg`."
        elif not cairosvg_present and prefer == "cairosvg":
            code = "cairosvg_unavailable"
            message = "cairosvg is not installed."
            suggestion = "pip install cairosvg, or pass --prefer=rsvg with `brew install librsvg`."
        else:
            code = "render_failed"
            message = f"Both renderers attempted; last error: {last_err}"
            suggestion = "Inspect the SVG for unsupported elements; check stderr in provenance entries."

        env = OgRenderEnvelope(
            status="degraded",
            data=OgRenderData(input_svg=str(input_svg), output_png=str(output_png)),
            provenance=provenance,
            error=OgRenderError(code=code, message=message, suggestion=suggestion),
        )
        sys.exit(emit(env))

    # Post-render validation: file present, dimensions correct, size sane.
    if not output_png.exists():
        env = OgRenderEnvelope(
            status="degraded",
            data=OgRenderData(
                input_svg=str(input_svg),
                output_png=str(output_png),
                renderer=renderer_used,
            ),
            provenance=provenance,
            error=OgRenderError(
                code="output_file_missing",
                message=f"Renderer claimed success but output file is missing: {output_png}",
                suggestion="Check disk space and write permissions on the output directory.",
            ),
        )
        sys.exit(emit(env))

    output_bytes = output_png.stat().st_size
    dimensions = _png_dimensions(output_png)
    width, height = (dimensions or (0, 0))

    if dimensions is None or (width, height) != (OG_WIDTH, OG_HEIGHT):
        env = OgRenderEnvelope(
            status="degraded",
            data=OgRenderData(
                input_svg=str(input_svg),
                output_png=str(output_png),
                renderer=renderer_used,
                width=width or None,
                height=height or None,
                output_bytes=output_bytes,
            ),
            provenance=provenance,
            error=OgRenderError(
                code="output_invalid_dimensions",
                message=f"Output PNG dimensions are {width}x{height}; expected {OG_WIDTH}x{OG_HEIGHT}.",
                suggestion="Confirm the SVG viewBox/aspect ratio; the renderer should letterbox to 1200x630.",
            ),
        )
        sys.exit(emit(env))

    if output_bytes > OG_MAX_BYTES:
        env = OgRenderEnvelope(
            status="degraded",
            data=OgRenderData(
                input_svg=str(input_svg),
                output_png=str(output_png),
                renderer=renderer_used,
                width=width,
                height=height,
                output_bytes=output_bytes,
            ),
            provenance=provenance,
            error=OgRenderError(
                code="output_too_large",
                message=f"Output PNG is {output_bytes} bytes; limit is {OG_MAX_BYTES}.",
                suggestion="Simplify the SVG (fewer paths, smaller embedded raster) and re-render.",
            ),
        )
        sys.exit(emit(env))

    env = OgRenderEnvelope(
        status="ok",
        data=OgRenderData(
            input_svg=str(input_svg),
            output_png=str(output_png),
            renderer=renderer_used,
            width=width,
            height=height,
            output_bytes=output_bytes,
        ),
        provenance=provenance,
    )
    sys.exit(emit(env))


if __name__ == "__main__":
    cli()
