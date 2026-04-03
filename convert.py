
from pathlib import Path
import argparse
import os
import sys
from PIL import Image
import ffmpeg

def get_ffmpeg_executable() -> str:
    """Return path to ffmpeg binary, bundled or system."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
        ffmpeg_path = base / "ffmpeg-bin" / "ffmpeg"
    else:
        ffmpeg_path = Path(__file__).resolve().parent / "ffmpeg"

    if ffmpeg_path.exists():
        return str(ffmpeg_path)
    return "ffmpeg"  


FFMPEG_BIN = get_ffmpeg_executable()

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico', '.ppm', '.pgm', '.pbm'}
VIDEO_EXTS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
AUDIO_EXTS = {'.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'}

SUPPORTED_IMAGE = 'JPG, JPEG, PNG, BMP, GIF, TIFF, TIF, WEBP, ICO, PPM, PGM, PBM'
SUPPORTED_VIDEO = 'MP4, AVI, MKV, MOV, WMV, FLV, WEBM'
SUPPORTED_AUDIO = 'MP3, WAV, AAC, FLAC, OGG, M4A'


def print_supported_formats():
    print(
        f"Supported Image formats: {SUPPORTED_IMAGE}\n"
        f"Supported Video formats: {SUPPORTED_VIDEO}\n"
        f"Supported Audio formats: {SUPPORTED_AUDIO}"
    )

def build_output_path(input_path: Path, output_arg: str | None, output_format: str) -> Path:
    """Construct output file path."""
    output_format = output_format.lstrip('.').lower()
    if output_arg is None:
        return Path.cwd() / f"{input_path.stem}.{output_format}"

    output_path = Path(output_arg)
    if output_path.suffix:
        return output_path

    return output_path / f"{input_path.stem}.{output_format}"

def convert_image(input_path: Path, output_path: Path, quality: int = 95):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_kwargs = {}
    if output_path.suffix.lower() in {'.jpg', '.jpeg', '.webp'}:
        save_kwargs['quality'] = quality

    with Image.open(input_path) as img:
        img.save(output_path, format=output_path.suffix.lstrip('.').upper(), **save_kwargs)

    print(f"Saved: {output_path}")

def convert_ffmpeg(input_path: Path, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        ffmpeg.input(str(input_path)).output(str(output_path)).overwrite_output().run(cmd=[FFMPEG_BIN], capture_stdout=True, capture_stderr=True)
        print(f"Saved: {output_path}")
    except ffmpeg.Error as e:
        stderr = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else str(e)
        print(f"FFmpeg failed:\n{stderr}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Simple file converter")
    parser.add_argument('input', nargs='?', help="Input file path")
    parser.add_argument('output_format', nargs='?', help="Output format (extension)")
    parser.add_argument('output', nargs='?', help="Output file or directory")
    parser.add_argument('--quality', type=int, default=95, help="Image quality (1-100)")
    parser.add_argument('--formats', action='store_true', help="Show supported formats")
    parser.add_argument('--version', action='version', version='FileConvert 1.0')

    args = parser.parse_args()

    if args.formats or (args.input and args.input.lower() == 'formats'):
        print_supported_formats()
        return

    if not args.input or not args.output_format:
        parser.print_help()
        return

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_format = args.output_format.lstrip('.').lower()
    extension = input_path.suffix.lower()

    if extension in IMAGE_EXTS:
        target_path = build_output_path(input_path, args.output, output_format)
        convert_image(input_path, target_path, args.quality)
    elif extension in VIDEO_EXTS or extension in AUDIO_EXTS:
        target_path = build_output_path(input_path, args.output, output_format)
        convert_ffmpeg(input_path, target_path)
    else:
        print(f"Unsupported input format: {extension}", file=sys.stderr)
        print_supported_formats()
        sys.exit(1)

if __name__ == "__main__":
    main()