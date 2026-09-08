"""Create a current system document from the retained quality template.

The source is copied first; only documented text slots and table cells are
updated so the reference document remains untouched.
"""
from copy import deepcopy
from pathlib import Path
import shutil

from docx import Document
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "安嘉之越南美食品在淡水_系統文件書_品質強化版.docx"
OUTPUT = ROOT / "安嘉之越南美食品在淡水_系統文件書_更新版.docx"


def replace_paragraph(paragraph, text):
    """Replace visible text while retaining paragraph style and first run style."""
    first = paragraph.runs[0] if paragraph.runs else None
    rpr = deepcopy(first._r.rPr) if first is not None and first._r.rPr is not None else None
    paragraph.clear()
    run = paragraph.add_run(text)
    if rpr is not None:
        run._r.insert(0, rpr)
    return paragraph


def replace_cell(cell, text):
    p = cell.paragraphs[0]
    replace_paragraph(p, text)
    # Remove any extra source paragraphs while preserving cell formatting.
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)


def set_table(table, rows):
    if len(table.rows) != len(rows):
        raise ValueError(f"Table row mismatch: expected {len(table.rows)}, got {len(rows)}")
    for row, values in zip(table.rows, rows):
        if len(row.cells) != len(values):
            raise ValueError("Table column mismatch")
        for cell, value in zip(row.cells, values):
            replace_cell(cell, value)


def main():
    shutil.copy2(SOURCE, OUTPUT)
    doc = Document(OUTPUT)

    # Cover and executive content.
    replacements = {
        "系統名稱：安嘉之越南美食品在淡水點餐系統": "系統名稱：安嘉之越南美食品在淡水外帶點餐與營運管理系統",
        "文件摘要": "文件摘要（2026 年 8 月最新功能版）",
        "本專題建置「安嘉之越南美食品在淡水」行動化外帶點餐系統，服務安嘉河食、安嘉越南麵包及安嘉越南食世界三個品牌。系統以 Flask 與 SQLite 為核心，提供消費者選店、瀏覽雙語菜單、選擇加料與備註、購物車結帳、會員點數、訂單追蹤及每日銷量查詢；後台則支援菜單圖片與介紹維護、人工點餐、製作與付款狀態、歷史訂單及營運圖表。系統透過 Cloudflare Tunnel 提供 HTTPS 公開網址，讓手機行動網路也能連線使用。": "本專題建置「安嘉之越南美食品在淡水」行動化外帶點餐與營運管理系統，服務安嘉河食、安嘉越南麵包及安嘉越南食世界三個品牌。系統以 Flask 與 SQLite 為核心，提供消費者選店、瀏覽中越雙語菜單、選擇每道餐點專屬加料與備註、購物車結帳、會員註冊登入、點數兌換／折抵、取餐流水號、當日訂單與每日餐點銷量查詢；後台則支援三店分頁菜單管理、圖片與介紹維護、人工點餐、製作與付款狀態、供應狀態、歷史訂單及分店營運圖表。系統透過 Cloudflare Tunnel 提供 HTTPS 公開網址，讓手機行動網路也能連線使用。",
        "本系統目前聚焦外帶流程，不設桌號與內用座位。付款狀態以店家管理確認為主，尚未直接串接第三方金流；公開網址由 Cloudflare Tunnel 對接本機 Flask 服務，因此電腦、網路與背景服務需維持運作。": "本系統目前聚焦外帶流程，不設桌號與內用座位，付款方式固定為現金，付款狀態由店家管理確認。公開網址由 Cloudflare Tunnel 對接本機 Flask 服務，因此承載主機、網路、Flask 與 Tunnel 背景服務需維持運作；未來可遷移雲端主機以提升可用性。",
        "以繁體中文與越南文呈現菜名、食材、加料及文化導覽，強化越南美食辨識與溝通。": "以繁體中文與越南文呈現菜名、食材、加料、地區／起源、推薦標示與文化導覽，並保留南北越用語提示，強化越南美食辨識與溝通。",
        "提供店家即時管理菜單、圖片、訂單製作狀態、付款狀態及人工點餐的後台。": "提供店家即時管理菜單、圖片、每道餐點加料、供應狀態、訂單製作狀態、付款狀態及人工點餐的後台。",
        "整合會員點數、優惠活動、每日銷量與歷史報表，支援日常營運決策。": "整合會員點數、免費換餐點、金額折抵、優惠活動、三店每日銷量與分店歷史報表，支援日常營運決策。",
        "手機號碼與密碼登入；系統先驗證欄位與密碼規則，再查詢帳號與密碼雜湊。驗證成功後建立登入狀態並導向訂單或結帳流程；若查無帳號，則引導使用者進入註冊頁。": "會員以手機號碼與密碼登入；註冊時須再次確認密碼，且密碼至少 8 碼、包含英文大寫、小寫與特殊符號，兩個密碼欄位皆可使用眼睛圖示切換顯示。系統驗證資料與密碼雜湊後建立登入狀態；若查無帳號，則引導使用者進入註冊頁。",
        "以手機選店、選餐、逐道勾選加料與填寫備註後下單；再由後台檢視餐點明細、更新製作與付款狀態，最後從使用者歷史紀錄與管理報表確認資料可被正確追蹤。": "以手機選店、選餐、逐道勾選專屬加料與填寫備註後下單；系統產生依當日店別排序的取餐流水號。再由後台即時檢視餐點明細、更新製作與付款狀態，最後從使用者訂單及三店報表確認資料可被正確追蹤。",
        "前端由 HTML 模板、CSS 與 JavaScript 組成；Flask 負責路由、表單處理、訂單計價與資料庫存取；Cloudflare Tunnel 則把本機 127.0.0.1:5000 安全對外提供 HTTPS 公開網址。": "前端由 HTML 模板、CSS 與 JavaScript 組成；Flask 負責路由、表單處理、訂單計價、點數規則與資料庫存取；SQLite 保存營運資料；Cloudflare Tunnel 則把本機 127.0.0.1:5000 安全對外提供 HTTPS 公開網址。",
        "使用案例圖以消費者／會員及店員／管理者為主要行為者。前者以選餐與取得外帶服務為主；後者以菜單、訂單、人工點餐與營運報表管理為主，兩者共同透過同一套資料與流程協作。": "使用案例圖以消費者／會員及店員／管理者為主要行為者。前者以選餐、專屬加料、點數折抵／兌換及取得外帶服務為主；後者以三店菜單、加料、供應狀態、訂單、人工點餐與分店營運報表管理為主，兩者共同透過同一套資料與流程協作。",
        "系統依消費金額計算點數（每滿 50 元無條件進位 1 點），導向成功頁與我的外帶訂單。": "系統依消費金額計算點數（每滿 50 元無條件進位 1 點），並可使用點數兌換餐點或以後台設定之比率進行金額折抵，最後導向成功頁與我的外帶訂單。",
        "菜單管理依店別取得 menu 資料，更新文字與圖片後立即影響該店前台菜單。": "菜單管理依店別取得 menu 資料，更新中越名稱、介紹、分類、圖片、推薦、供應狀態及每道餐點的加料選項後，前台會在短時間內同步更新。",
        "訂單管理依建立日期分為當日與歷史紀錄，顯示 order_items 餐點明細並可更新狀態。": "訂單管理依建立日期分為當日與歷史紀錄，顯示每店當日流水號、顧客電話末三碼與 order_items 餐點明細，並可更新製作與付款狀態。",
        "人工點餐透過同一個訂單與明細資料結構存檔，會員手機若存在即累積點數。": "人工點餐透過同一個訂單與明細資料結構存檔，會員手機若存在即累積點數，並同樣產生該店當日取餐流水號。",
        "歷史報表彙整 order_items，依日期、店別與餐點繪製趨勢與占比。": "每日餐點銷量與歷史營運報表皆可依安嘉河食、安嘉越南麵包、安嘉越南食世界分別檢視，並依日期、店別與餐點繪製趨勢與占比。",
        "會員密碼以 password_hash 儲存，不直接保存明碼；註冊頁要求至少 8 碼、大小寫英文字與特殊符號。": "會員密碼以 password_hash 儲存，不直接保存明碼；註冊頁要求至少 8 碼、英文大寫、小寫與特殊符號，並以再次確認密碼與眼睛圖示降低輸入錯誤。",
        "Cloudflare 提供 HTTPS 與公開網址，但本機服務若電腦關機、網路中斷或 Tunnel 未執行，外部將出現 502／無法連線。": "Cloudflare 提供 HTTPS 與公開網址，但本機服務若電腦關機、網路中斷、Flask 或 Tunnel 未執行，外部將出現 502／無法連線。",
        "本專題完成一套以外帶為中心的三店越南美食點餐系統。從前台的雙語菜單、圖片、加料、購物車、會員點數與訂單查詢，到後台的菜單圖片管理、人工點餐、製作與付款狀態、歷史資料與圖表，系統已涵蓋實際門市常見的核心流程。Cloudflare Tunnel 亦讓原本僅限本機的 Flask 系統可透過 HTTPS 與自訂網域供手機行動網路使用，證明小型餐飲服務能以低成本建立可操作的數位點餐原型。": "本專題完成一套以外帶為中心的三店越南美食點餐與營運管理系統。從前台的雙語菜單、圖片、分類、專屬加料、購物車、會員點數、取餐流水號與訂單查詢，到後台的三店菜單圖片管理、加料顯示／隱藏、供應狀態、人工點餐、製作（含已領取）與付款狀態、分店銷量及歷史圖表，系統已涵蓋實際門市常見的核心流程。Cloudflare Tunnel 亦讓原本僅限本機的 Flask 系統可透過 HTTPS 與自訂網域供手機行動網路使用，證明小型餐飲服務能以低成本建立可操作的數位點餐原型。",
    }
    for p in doc.paragraphs:
        if p.text in replacements:
            replace_paragraph(p, replacements[p.text])

    # Table 2: keyword callout.
    set_table(doc.tables[1], [["關鍵字　越南美食、外帶點餐、三店整合、會員點數、取餐流水號、Flask、SQLite、Cloudflare Tunnel、HTTPS"]])

    # Table 3: consumer front-end functions.
    set_table(doc.tables[2], [
        ("功能", "內容與效益"),
        ("三店選擇", "由首頁進入安嘉河食、安嘉越南麵包或安嘉越南食世界，保留各店個別菜單、分類與當日流水號。"),
        ("雙語菜單與供應", "以繁體中文及越南文呈現菜名、食材／介紹、地區／起源、推薦、價格、圖片與供應狀態；北、南越用字差異可加註。"),
        ("專屬加料與備註", "依不同餐點提供可複選或單選的加料、冰塊、加大等選項；加料、價格與顧客備註隨該餐點明細保存。"),
        ("購物車與結帳", "可同時加入多道餐點，付款方式固定為現金；系統顯示原價、點數折抵、實付金額並產生取餐流水號。"),
        ("會員與點數", "手機號碼註冊／登入、再次確認密碼與顯示密碼；每滿 NT$50 無條件進位累積 1 點，可免費兌換餐點或金額折抵。"),
        ("我的外帶訂單", "依登入會員或手機查詢當日與歷史訂單；三家店分組顯示餐點明細、下單時間、流水號、製作與付款狀態。"),
        ("中越導覽", "提供越南美食、食材、文化與常用對話的雙語詞彙內容；不依賴自動翻譯服務即可使用基本導覽。"),
        ("每日餐點銷量", "在使用者首頁提供當日各餐點銷量資訊，讓顧客理解熱門品項。"),
    ])

    # Table 4: current administration capabilities.
    set_table(doc.tables[3], [
        ("模組", "內容"),
        ("後台首頁", "集中入口連結三店菜單管理、外帶訂單管理、人工點餐、每日銷量、歷史報表與點數設定。"),
        ("菜單即時管理", "依三家店分頁管理；可新增、編輯、下架／刪除餐點與圖片，維護中文與越文名稱、介紹、價格、分類、推薦及供應狀態。"),
        ("餐點加料管理", "每一道商品可新增、刪除、改名、調整加料價格，並設定前端顯示／隱藏；前後台選項保持一致。"),
        ("外帶訂單管理", "檢視今日或歷史訂單與餐點明細，顯示店別流水號與電話末三碼；更新已接單／製作中／已完成可領取／已領取及付款狀態。"),
        ("人工點餐與報表", "協助未攜帶手機顧客下單；會員仍可累積點數。每日銷量與歷史報表可分別檢視三家店並呈現趨勢與占比。"),
        ("點數與優惠設定", "可設定免費兌換餐點的 1 點價值，以及本次金額折抵的 1 點價值；指定日期促銷結束後自動回復原價。"),
    ])

    # Table 14 architecture callout; no external translator dependency.
    set_table(doc.tables[13], [["架構流程　手機／電腦瀏覽器　→　Cloudflare HTTPS 與 Tunnel　→　Flask 應用程式（app.py）　→　SQLite 資料庫（vietnam_food.db）。中越導覽採系統內建詞彙與內容；自動翻譯服務為未來可選擴充，不影響既有點餐流程。\n"]])

    set_table(doc.tables[14], [
        ("檔案／目錄", "責任", "關連"),
        ("app.py", "Flask 應用程式、路由、商業規則、SQLite 讀寫", "呼叫 templates、static 與 vietnam_food.db。"),
        ("templates/", "首頁、店家菜單、訂單、會員、後台、點數設定與報表 HTML 模板", "由 app.py 的 render_template() 輸出。"),
        ("static/", "CSS、JavaScript、首頁背景、菜單照片與上傳圖檔", "供 templates/ 以 url_for('static', ...) 載入。"),
        ("static/menu-images/", "依三家店分類之餐點圖片，支援 JPG、JPEG、PNG、WEBP", "菜單管理上傳後由 menu.image_url 參照；刪除商品時同步處理其上傳圖片。"),
        ("vietnam_food.db", "SQLite 營運資料庫", "儲存菜單、帳號、訂單、明細、加料設定與點數／系統設定。"),
        ("Cloudflare Tunnel", "公開 HTTPS 網址與本機服務轉送", "服務 URL 指向 http://localhost:5000。"),
    ])

    set_table(doc.tables[15], [
        ("資料表", "主要欄位", "用途／關連"),
        ("menu", "id, name, vi_name, price, category, shop, image_url, addon_config, hidden_addons", "三家店菜單、多語內容、圖片、加料、供應狀態、點數；order_items.menu_item_id 可對應來源餐點。"),
        ("orders", "id, customer_name, phone, total_price, payment_status, status, created_at, shop_name", "每筆外帶訂單表頭；一筆 orders 對多筆 order_items，並可依日期與店別編列流水號。"),
        ("order_items", "id, order_id, menu_item_id, item_name, addon_name, unit_price, quantity, line_total", "訂單逐項明細；每道餐點獨立保存加料、備註、數量及金額。"),
        ("customer_accounts", "id, display_name, phone, password_hash, points, welcome_points_claimed", "會員帳號、密碼雜湊與點數；以手機作為消費者識別。"),
        ("app_settings", "setting_key, setting_value", "保存跨功能設定，例如餐點兌換點數價值與本次金額折抵點數價值。"),
    ])

    set_table(doc.tables[17], [
        ("規則", "實作說明"),
        ("外帶限定與現金", "訂單不含桌號；取餐姓名與手機為識別資訊；付款方式固定為現金，付款狀態由後台確認。"),
        ("多餐點訂單", "一筆 orders 可對應多筆 order_items，客製加料與備註隨各餐點保存，不互相覆蓋。"),
        ("會員點數與免費換餐", "消費金額每 NT$50 無條件進位累積 1 點；110 元為 3 點，160 元為 4 點；註冊會員可領取歡迎點數。免費換餐點所需點數＝餐點價格 ÷ 後台設定之每點兌換價值，無條件進位。"),
        ("本次金額折抵", "依後台設定計算；目前預設 1 點折抵 NT$1，點數使用量以可折抵金額為上限。"),
        ("指定日促銷", "2026/08/16 全品項以 9 折計價，活動日期結束後系統自動使用原價。"),
        ("製作與供應狀態", "製作狀態為已接單、製作中、已完成可領取、已領取；供應狀態為供應中或暫停供應。"),
    ])

    set_table(doc.tables[18], [
        ("測試項目", "測試方式", "預期驗收結果"),
        ("訂單資料正確性", "同一筆訂單加入多道餐點，分別選擇不同加料、冰塊與備註。", "每筆 order_items 保留各自的品項、加料、備註、數量與金額，不互相覆蓋。"),
        ("會員與點數", "測試密碼規則、再次確認密碼、歡迎點數、消費累積、免費換餐與本次金額折抵。", "密碼欄位驗證正確；點數依規則累積，兩種兌換方式依各自後台設定正確計算。"),
        ("取餐與狀態", "建立同日、同店及不同店別訂單，後台依序更新製作與付款狀態。", "流水號依當日店別重新計數；包含已領取在內的狀態可正確保存與呈現。"),
        ("行動裝置實用性", "以不同尺寸手機瀏覽首頁、三店菜單、購物車、會員與訂單頁面。", "文字、按鈕、圖片與表單可閱讀、可操作，無需桌號即可完成外帶下單。"),
        ("菜單同步維護", "更新名稱、介紹、分類、圖片、加料、供應狀態或下架商品後，重新檢視前後台。", "更新後維持管理者操作位置；前端短時間同步，只顯示供應中且資料完整的餐點。"),
    ])

    set_table(doc.tables[20], [
        ("類別", "工具／技術", "用途"),
        ("程式語言", "Python 3.14", "撰寫後端商業規則、路由與資料處理。"),
        ("Web Framework", "Flask", "建立路由、表單處理、HTML 模板渲染與開發伺服器。"),
        ("資料庫", "SQLite 3", "以單一 vietnam_food.db 保存菜單、訂單、會員、點數、加料與設定。"),
        ("前端", "HTML5、CSS3、JavaScript", "建立 RWD 行動介面、購物車、即時時間、菜單同步與圖表。"),
        ("開發環境", "Visual Studio Code、PowerShell", "程式編輯、執行、除錯與專案管理。"),
        ("公開服務", "Cloudflare、cloudflared Tunnel、HTTPS", "將本機 Flask 的 5000 連接埠發布到自訂網域。"),
        ("雙語導覽", "系統內建中越詞彙與內容", "提供越南美食、食材、文化與常用對話的雙語資訊；不影響核心交易流程。"),
        ("媒體工具", "FFmpeg", "協助專題展示影片輸出與轉檔。"),
    ])

    set_table(doc.tables[28], [
        ("路徑", "用途"),
        ("/", "使用者首頁：三店入口、會員入口、我的外帶訂單、每日銷量與雙語導覽。"),
        ("/shop/pho", "安嘉河食菜單與外帶點餐。"),
        ("/shop/banh-mi", "安嘉越南麵包菜單與外帶點餐。"),
        ("/shop/drinks", "安嘉越南食世界飲品與點心菜單。"),
        ("/my-orders", "消費者當日與歷史外帶訂單查詢，含三店分組與取餐流水號。"),
        ("/admin", "後台管理首頁。"),
        ("/admin/menu、/admin/menu/<shop>", "三店菜單即時管理入口與各店獨立管理頁。"),
        ("/admin/orders、/admin/orders/history", "當日與歷史外帶訂單管理，可依店別檢視。"),
        ("/admin/daily-sales/<shop>、/admin/history-report/<shop>", "各店每日餐點銷量與歷史營運圖表報表。"),
        ("/admin/points-settings、/admin/manual-order", "點數兌換設定與門市人員人工點餐。"),
    ])

    # Update keywords in static reference list and ask Word to refresh fields on open.
    settings = doc.settings.element
    update_fields = settings.find(qn("w:updateFields"))
    if update_fields is None:
        update_fields = docx_elm = __import__("docx").oxml.OxmlElement("w:updateFields")
        settings.append(update_fields)
    update_fields.set(qn("w:val"), "true")
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
