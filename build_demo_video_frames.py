from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = {
    "opening": ROOT / "static" / "video-assets" / "opening-tamsui-takeaway-ai.png",
    "qr": ROOT / "static" / "video-assets" / "scene-customer-qr.png",
    "phone": ROOT / "static" / "video-assets" / "scene-customer-ordering.png",
    "backend": ROOT / "static" / "video-assets" / "scene-staff-backend.png",
}
OUT = ROOT / "video-output"

SCENES = [
    ("安嘉之越南美食品在淡水", "Ẩm thực Việt Nam tại Tamsui", "外帶點餐系統｜Takeaway ordering system"),
    ("在淡水，想吃越南美食？", "Ở Tamsui, muốn ăn món Việt?", "拿起手機，就能開始點餐。"),
    ("掃描 QR Code", "Quét mã QR", "快速進入安嘉點餐系統。"),
    ("選擇三家店", "Chọn một trong ba cửa hàng", "河粉・越南麵包・飲品點心"),
    ("安嘉河食", "An Gia Phở", "看圖片、雙語名稱與食材介紹。"),
    ("依每一份餐點加料", "Chọn topping cho từng phần", "檸檬、辣椒、魚露、加菜或加肉。"),
    ("自由填寫備註", "Ghi chú theo sở thích", "讓每份外帶餐點更符合您的口味。"),
    ("一次點選多樣餐點", "Đặt nhiều món trong một đơn", "不同餐點可以有不同加料。"),
    ("確認送出外帶訂單", "Xác nhận đơn mang đi", "填入姓名、電話與付款方式。"),
    ("我的外帶訂單", "Đơn mang đi của tôi", "查看下單時間、餐點明細與付款狀態。"),
    ("即時查看製作進度", "Theo dõi tiến độ", "已接單 → 製作中 → 已完成可領取"),
    ("店家後台管理", "Quản lý phía cửa hàng", "集中處理每日外帶訂單。"),
    ("查看餐點、加料與備註", "Xem món, topping và ghi chú", "每份餐點資訊清楚保留。"),
    ("更新製作與付款狀態", "Cập nhật chế biến và thanh toán", "讓顧客安心等候取餐。"),
    ("菜單即時管理", "Quản lý thực đơn tức thì", "新增、修改、上傳照片或刪除餐點。"),
    ("每日餐點銷量", "Doanh số món ăn hằng ngày", "協助店家掌握受歡迎的餐點。"),
    ("安嘉之越南美食品在淡水", "Thương hiệu Tuấn An và Dịch Gia", "感謝您的光臨｜Cảm ơn quý khách"),
    ("立即開始外帶點餐", "Bắt đầu gọi món mang đi", "https://order.angiavietnam.com/"),
]


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\msjhbd.ttc" if bold else r"C:\Windows\Fonts\msjh.ttc",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_centered(draw, text, y, max_width, fnt, fill):
    words = list(text)
    lines, current = [], ""
    for char in words:
        test = current + char
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            current = test
        else:
            lines.append(current)
            current = char
    if current:
        lines.append(current)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        x = (draw.im.size[0] - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=fnt, fill=fill, stroke_width=1, stroke_fill=(0, 0, 0, 130))
        y += int(fnt.size * 1.35)
    return y


def make_frame(size, scene_no, scene):
    width, height = size
    asset_name = "opening"
    if 1 <= scene_no <= 2:
        asset_name = "qr"
    elif 3 <= scene_no <= 10:
        asset_name = "phone"
    elif 11 <= scene_no <= 15:
        asset_name = "backend"
    base = Image.open(ASSETS[asset_name]).convert("RGB")
    scale = max(width / base.width, height / base.height)
    crop_w, crop_h = int(width / scale), int(height / scale)
    max_x = max(0, base.width - crop_w)
    positions = [0.15, 0.35, 0.55, 0.72]
    x = int(max_x * positions[scene_no % len(positions)])
    y = max(0, (base.height - crop_h) // 2)
    background = base.crop((x, y, x + crop_w, y + crop_h)).resize(size, Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(1.2))
    overlay = Image.new("RGBA", size, (8, 29, 27, 110))
    canvas = Image.alpha_composite(background.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(canvas, "RGBA")
    panel = (int(width * .07), int(height * .16), int(width * .93), int(height * .84))
    draw.rounded_rectangle(panel, radius=int(min(width, height) * .035), fill=(255, 252, 247, 228), outline=(255, 255, 255, 170), width=2)
    draw.rectangle((0, 0, width, int(height * .017)), fill=(205, 62, 58, 255))
    draw.text((int(width * .10), int(height * .20)), f"AN GIA  |  {scene_no + 1:02d}/18", font=font(int(height * .035), True), fill=(30, 118, 91, 255))
    title, vietnamese, detail = scene
    y = int(height * .34)
    y = draw_centered(draw, title, y, int(width * .72), font(int(height * .075), True), (205, 62, 58, 255))
    y += int(height * .02)
    y = draw_centered(draw, vietnamese, y, int(width * .72), font(int(height * .048), True), (23, 119, 89, 255))
    y += int(height * .035)
    draw_centered(draw, detail, y, int(width * .70), font(int(height * .040)), (32, 38, 45, 255))
    draw.text((int(width * .10), int(height * .78)), "安嘉之越南美食品在淡水", font=font(int(height * .028), True), fill=(22, 105, 79, 220))
    return canvas.convert("RGB")


def main():
    for variant, size in (("landscape", (1280, 720)), ("portrait", (720, 1280))):
        target = OUT / variant
        target.mkdir(parents=True, exist_ok=True)
        for index, scene in enumerate(SCENES):
            make_frame(size, index, scene).save(target / f"scene-{index + 1:02d}.png", quality=95)
    print(f"Created {len(SCENES)} frames for each version in {OUT}")


if __name__ == "__main__":
    main()
