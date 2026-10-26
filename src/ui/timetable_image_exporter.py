from __future__ import annotations

from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont

from PIL import Image, ImageDraw, ImageFont


class TimetableImageExporter:
    """Tkinter Canvasの描画内容をPNG画像として出力する。"""

    @staticmethod
    def export(
        canvas: tk.Canvas,
        output_path: Path,
    ) -> None:
        """Canvas全体の描画内容をPNG画像として保存する。"""

        bbox = canvas.bbox("all")

        if bbox is None:
            raise ValueError("出力する時刻表がありません。")

        x1, y1, x2, y2 = bbox

        # Canvasの描画範囲に余白を設ける。
        padding = 2
        origin_x = x1 - padding
        origin_y = y1 - padding

        width = max(1, x2 - x1 + padding * 2)
        height = max(1, y2 - y1 + padding * 2)

        background = canvas.cget("background") or "white"

        image = Image.new(
            "RGB",
            (width, height),
            background,
        )
        draw = ImageDraw.Draw(image)

        for item_id in canvas.find_all():
            item_type = canvas.type(item_id)
            coords = canvas.coords(item_id)

            if not coords:
                continue

            # Canvas座標を画像座標に変換する。
            points = [
                (
                    coords[index] - origin_x,
                    coords[index + 1] - origin_y,
                )
                for index in range(0, len(coords) - 1, 2)
            ]

            if item_type == "rectangle":
                TimetableImageExporter._draw_rectangle(
                    canvas,
                    draw,
                    item_id,
                    points,
                )

            elif item_type == "line":
                TimetableImageExporter._draw_line(
                    canvas,
                    draw,
                    item_id,
                    points,
                )

            elif item_type == "text":
                TimetableImageExporter._draw_text(
                    canvas,
                    draw,
                    item_id,
                    points[0],
                )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(
            output_path,
            format="PNG",
        )

    @staticmethod
    def _draw_rectangle(
        canvas: tk.Canvas,
        draw: ImageDraw.ImageDraw,
        item_id: int,
        points: list[tuple[float, float]],
    ) -> None:
        """Canvasの矩形を描画する。"""

        if len(points) < 2:
            return

        options = canvas.itemconfigure(item_id)

        fill = options["fill"][-1]
        outline = options["outline"][-1]
        width = max(1, int(float(options["width"][-1] or 1)))

        draw.rectangle(
            (
                points[0][0],
                points[0][1],
                points[1][0],
                points[1][1],
            ),
            fill=fill or None,
            outline=outline or None,
            width=width,
        )

    @staticmethod
    def _draw_line(
        canvas: tk.Canvas,
        draw: ImageDraw.ImageDraw,
        item_id: int,
        points: list[tuple[float, float]],
    ) -> None:
        """Canvasの線を描画する。"""

        if len(points) < 2:
            return

        options = canvas.itemconfigure(item_id)

        color = options["fill"][-1] or "black"
        width = max(1, int(float(options["width"][-1] or 1)))
        dash = options["dash"][-1]
        capstyle = options["capstyle"][-1]

        coordinates = [
            coordinate
            for point in points
            for coordinate in point
        ]

        if not dash:
            draw.line(
                coordinates,
                fill=color,
                width=width,
                joint="curve",
            )
            return

        # Canvasのdash指定をPillowの線分に変換する。
        dash_pattern = (
            tuple(int(value) for value in dash)
            if isinstance(dash, (tuple, list))
            else (4, 3)
        )

        if not dash_pattern or all(value <= 0 for value in dash_pattern):
            draw.line(
                coordinates,
                fill=color,
                width=width,
            )
            return

        TimetableImageExporter._draw_dashed_line(
            draw,
            points,
            color,
            width,
            dash_pattern,
        )

    @staticmethod
    def _draw_dashed_line(
        draw: ImageDraw.ImageDraw,
        points: list[tuple[float, float]],
        color: str,
        width: int,
        pattern: tuple[int, ...],
    ) -> None:
        """指定したパターンで線を描画する。"""

        import math

        pattern = tuple(max(1, value) for value in pattern)
        pattern_index = 0
        remaining = pattern[0]
        draw_segment = True

        for start, end in zip(points, points[1:]):
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = math.hypot(dx, dy)

            if length == 0:
                continue

            position = 0.0

            while position < length:
                segment_length = min(remaining, length - position)

                if draw_segment:
                    start_ratio = position / length
                    end_ratio = (position + segment_length) / length

                    draw.line(
                        (
                            start[0] + dx * start_ratio,
                            start[1] + dy * start_ratio,
                            start[0] + dx * end_ratio,
                            start[1] + dy * end_ratio,
                        ),
                        fill=color,
                        width=width,
                    )

                position += segment_length
                remaining -= segment_length

                if remaining <= 0:
                    pattern_index = (pattern_index + 1) % len(pattern)
                    remaining = pattern[pattern_index]
                    draw_segment = not draw_segment

    @staticmethod
    def _draw_text(
        canvas: tk.Canvas,
        draw: ImageDraw.ImageDraw,
        item_id: int,
        position: tuple[float, float],
    ) -> None:
        """Canvasの文字を描画する。"""

        text = canvas.itemcget(item_id, "text")

        if not text:
            return

        color = canvas.itemcget(item_id, "fill") or "black"
        anchor = canvas.itemcget(item_id, "anchor") or "center"
        font_spec = canvas.itemcget(item_id, "font")

        font = TimetableImageExporter._load_font(
            canvas,
            font_spec,
        )

        anchor_map = {
            "center": "mm",
            "w": "lm",
            "e": "rm",
            "n": "mt",
            "s": "mb",
            "nw": "lt",
            "ne": "rt",
            "sw": "lb",
            "se": "rb",
        }

        draw.text(
            position,
            text,
            fill=color,
            font=font,
            anchor=anchor_map.get(anchor, "mm"),
        )

    @staticmethod
    def _load_font(
        canvas: tk.Canvas,
        font_spec: str,
    ) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Tkinterのフォント設定をWindowsのフォントファイルへ変換する。"""

        try:
            font = tkfont.Font(
                root=canvas,
                font=font_spec,
            )

            family = font.actual("family")
            size = max(
                1,
                abs(int(font.actual("size"))),
            )
            weight = font.actual("weight")
            slant = font.actual("slant")

            candidates = TimetableImageExporter._font_candidates(
                family,
                weight,
                slant,
            )

            for candidate in candidates:
                try:
                    return ImageFont.truetype(
                        candidate,
                        size=size,
                    )
                except OSError:
                    continue

        except (tk.TclError, ValueError, TypeError):
            pass

        return ImageFont.load_default()

    @staticmethod
    def _font_candidates(
        family: str,
        weight: str,
        slant: str,
    ) -> list[str]:
        """フォント名からWindowsのフォントファイル候補を生成する。"""

        import os

        font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        normalized = family.lower().replace(" ", "")

        font_map = {
            "meiryo": ["meiryo.ttc", "meiryob.ttc"],
            "yugothic": ["YuGothR.ttc", "YuGothB.ttc"],
            "msgothic": ["msgothic.ttc"],
            "msmincho": ["msmincho.ttc"],
            "arial": ["arial.ttf", "arialbd.ttf"],
            "segoeui": ["segoeui.ttf", "segoeuib.ttf"],
        }

        filenames = list(font_map.get(normalized, []))

        if weight == "bold":
            filenames = [
                "meiryob.ttc",
                "YuGothB.ttc",
                *filenames,
            ]

        # 日本語表示に対応したフォントを最後の候補として追加する。
        filenames.extend([
            "meiryo.ttc",
            "msgothic.ttc",
        ])

        # 順序を維持して重複を除去する。
        unique_filenames = list(dict.fromkeys(filenames))

        return [
            str(font_dir / filename)
            for filename in unique_filenames
        ]


