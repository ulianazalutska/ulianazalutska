"""
Готує фото до перетворення в ASCII-арт:
1. Видаляє фон (rembg)
2. Підвищує локальний контраст (CLAHE) - інакше рівномірно освітлене
   обличчя перетвориться на суцільну сіру пляму
3. Компонує результат на чистому білому тлі і переводить у відтінки сірого

Використання:
    python scripts/prep_photo.py source-photo.jpg
Результат: source-prepped.png
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def enhance_face_region(gray: np.ndarray) -> np.ndarray:
    """Додатково підсилює контраст і різкість саме в ділянці обличчя,
    щоб очі/брови/ніс/губи не губилися при подальшому даунсемплінгу
    в ASCII-сітку низької роздільності."""
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    if len(faces) == 0:
        return gray

    # Найбільше знайдене обличчя (на випадок хибних спрацювань на фоні)
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

    # Розширюємо бокс, щоб захопити брови/підборіддя/контур обличчя
    pad_x, pad_y = int(w * 0.2), int(h * 0.3)
    x0, y0 = max(0, x - pad_x), max(0, y - pad_y)
    x1, y1 = min(gray.shape[1], x + w + pad_x), min(gray.shape[0], y + h + pad_y)

    face = gray[y0:y1, x0:x1]

    # Тут навмисно НЕ застосовуємо другий CLAHE на обличчі: локальний CLAHE
    # на такій маленькій ділянці заганяє тіні під очима й ніздрі в чорне, а
    # шкіру - у майже біле, тож після квантування в ASCII-рампу це виглядає
    # як суцільні темні плями ("панда-ефект"), а не риси обличчя.
    # Лишаємо тільки легкий unsharp mask - він підкреслює контури (повіки,
    # крила носа, губи), не ламаючи баланс світлотіні.
    blurred = cv2.GaussianBlur(face, (0, 0), sigmaX=1.5)
    sharpened = cv2.addWeighted(face, 1.15, blurred, -0.15, 0)

    # Плавно змішуємо оброблену ділянку з рештою фото через розмиту маску,
    # інакше на межі прямокутника лишається помітний різкий "шов".
    mask = np.zeros(gray.shape, dtype=np.float64)
    mask[y0:y1, x0:x1] = 1.0
    feather = max(4, int(min(w, h) * 0.15))
    mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=feather)

    full_sharpened = gray.astype(np.float64).copy()
    full_sharpened[y0:y1, x0:x1] = sharpened
    result = gray.astype(np.float64) * (1 - mask) + full_sharpened * mask
    return result.clip(0, 255).astype(np.uint8)


def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    # 1. Видаляємо фон
    with open(input_path, "rb") as f:
        input_bytes = f.read()
    result_bytes = remove(input_bytes)

    # rembg повертає PNG з альфа-каналом (прозорий фон)
    rgba = Image.open(__import__("io").BytesIO(result_bytes)).convert("RGBA")

    # 2. Компонуємо на білому тлі (прозоре -> біле)
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("RGB")

    # 3. Переводимо в OpenCV-формат (BGR) для CLAHE
    cv_img = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # CLAHE - контрастно-обмежене адаптивне вирівнювання гістограми
    # дає реальні світлотіні на рівномірно освітленому обличчі
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 4. Локальне підсилення саме ділянки обличчя (детекція + CLAHE + sharpen)
    enhanced = enhance_face_region(enhanced)

    # Зберігаємо як grayscale PNG
    Image.fromarray(enhanced).save(output_path)
    print(f"OK: збережено {output_path} ({enhanced.shape[1]}x{enhanced.shape[0]})")


def main():
    if len(sys.argv) < 2:
        print("Використання: python scripts/prep_photo.py <шлях-до-фото>")
        sys.exit(1)
    prep_photo(sys.argv[1])


if __name__ == "__main__":
    main()