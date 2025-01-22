import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import regionprops, label

def analyze_aggregates(image_path):
    # Đọc ảnh đầu vào
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Lọc nhiễu và phát hiện biên
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Phát hiện các vùng (contours)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Dữ liệu kích thước và hình dạng
    sizes = []
    shapes = []

    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Bỏ qua các hạt nhỏ không đáng kể
        if area < 10:
            continue
        
        # Tính toán kích thước tương đương (bán kính)
        equivalent_diameter = np.sqrt(4 * area / np.pi)  # Đường kính tương đương
        
        # Xác định hình dạng
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        
        if circularity > 0.8:
            shape = 'circle'
        elif 0.5 < circularity <= 0.8:
            shape = 'oval'
        else:
            shape = 'irregular'
        
        shapes.append({'area': area, 'circularity': circularity, 'shape': shape})
        sizes.append(equivalent_diameter)
    
    # Phân loại theo kích thước
    size_bins = {'5-10mm': 0, '10-15mm': 0, '15-20mm': 0}
    total = len(sizes)

    for size in sizes:
        if 5 <= size <= 10:
            size_bins['5-10mm'] += 1
        elif 10 < size <= 15:
            size_bins['10-15mm'] += 1
        elif 15 < size <= 20:
            size_bins['15-20mm'] += 1

    # Tính phần trăm
    size_percentages = {k: (v / total) * 100 for k, v in size_bins.items()}

    # Hiển thị kết quả
    print("Tỷ lệ phần trăm theo kích thước:", size_percentages)
    print("Số lượng hạt phân tích:", total)
    print("Hình dạng các hạt:", shapes)
    
    # Biểu đồ
    plt.bar(size_percentages.keys(), size_percentages.values(), color=['blue', 'orange', 'green'])
    plt.title("Phân bố kích thước hạt")
    plt.xlabel("Khoảng kích thước (mm)")
    plt.ylabel("Tỷ lệ phần trăm (%)")
    plt.show()

# Đường dẫn đến ảnh
analyze_aggregates('y.jfif')
