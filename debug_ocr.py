import cv2
import pytesseract as pt
import pandas as pd
from PIL import Image

pt.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img_path = r"d:\MyStuff\OtherStuff\PPIT\Project\Data\WhatsApp Image 2026-01-23 at 11.10.18 AM (1).jpeg"
img = cv2.imread(img_path)

print("--- RAW IMAGE OCR ---")
df_raw = pt.image_to_data(Image.fromarray(img), output_type=pt.Output.DATAFRAME)
df_raw = df_raw[df_raw["text"].astype(str).str.strip() != ""]
print(df_raw[["conf", "text"]].head(20))

print("\n--- GRAYSCALE IMAGE OCR (PSM 3) ---")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
df_gray = pt.image_to_data(Image.fromarray(gray), output_type=pt.Output.DATAFRAME)
df_gray = df_gray[df_gray["text"].astype(str).str.strip() != ""]
print(df_gray[["conf", "text"]].head(20))

print("\n--- GRAYSCALE IMAGE OCR (PSM 11 - Sparse Text) ---")
df_psm11 = pt.image_to_data(Image.fromarray(gray), config='--psm 11', output_type=pt.Output.DATAFRAME)
df_psm11 = df_psm11[df_psm11["text"].astype(str).str.strip() != ""]
print(df_psm11[["conf", "text"]].head(20))

print("\n--- RESIZED x2 GRAYSCALE OCR (PSM 11) ---")
resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
df_res = pt.image_to_data(Image.fromarray(resized), config='--psm 11', output_type=pt.Output.DATAFRAME)
df_res = df_res[df_res["text"].astype(str).str.strip() != ""]
print(df_res[["conf", "text"]].head(20))

