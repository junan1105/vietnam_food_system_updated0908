(() => {
  const form = document.querySelector('#ai-chat-form');
  const input = document.querySelector('#ai-chat-input');
  const messages = document.querySelector('#chat-messages');
  if (!form || !input || !messages) return;

  const bilingual = (zh, vi) => `繁中：${zh}\n\nTiếng Việt: ${vi}`;
  const answer = (question) => {
    const text = question.toLowerCase();
    if (/素食|吃素|過敏|不吃|花生|海鮮|麩質|乳製品|dị ứng|ăn chay/.test(text)) {
      return bilingual('越南料理常能依需求調整，但過敏原需要特別確認。可告知店員「我不吃肉／Tôi không ăn thịt」、「我不吃花生／Tôi không ăn đậu phộng」、「我對海鮮過敏／Tôi bị dị ứng hải sản」。魚露、蝦醬、花生、蛋與乳製品常藏在醬料或配料中；若是嚴重過敏，請再次確認湯底與器具是否接觸過相關食材。', 'Món Việt thường có thể điều chỉnh theo nhu cầu, nhưng cần xác nhận kỹ dị ứng. Bạn có thể nói: “Tôi không ăn thịt”, “Tôi không ăn đậu phộng”, hoặc “Tôi bị dị ứng hải sản”. Nước mắm, mắm tôm, đậu phộng, trứng và sữa có thể có trong nước chấm hoặc topping; nếu dị ứng nặng, hãy hỏi thêm về nước dùng và dụng cụ chế biến.');
    }
    if (/會話|句子|怎麼點|點餐.*說|問價|點菜|giao tiếp|hội thoại/.test(text)) {
      return bilingual('常用點餐會話：\n1.「我要一份牛肉河粉。」＝Tôi muốn một phần phở bò.\n2.「不要香菜，少辣。」＝Không ngò rí, ít cay.\n3.「可以外帶嗎？」＝Có thể mang đi không?\n4.「請問多少錢？」＝Bao nhiêu tiền?\n5.「好吃，謝謝！」＝Ngon quá, cảm ơn!\n若在南北越遇到不同稱呼，先用清楚的食材名稱或指菜單圖片，通常最方便。', 'Câu gọi món thông dụng:\n1. “Tôi muốn một phần phở bò.”\n2. “Không ngò rí, ít cay.”\n3. “Có thể mang đi không?”\n4. “Bao nhiêu tiền?”\n5. “Ngon quá, cảm ơn!”\nNếu gặp cách gọi khác nhau giữa các vùng, hãy nói rõ nguyên liệu hoặc chỉ vào hình món ăn trên thực đơn.');
    }
    if (/香草|調味|食材|木耳|菇|魚露|rau thơm|nguyên liệu/.test(text)) {
      return bilingual('越南料理的靈魂常是香草與調味平衡。常見香草有香菜、九層塔、薄荷、紫蘇；常用調味有魚露、萊姆／檸檬、辣椒、蒜、胡椒與羅望子。食材方面，河粉和米線常搭豆芽、洋蔥、蔥花；湯品也可能含木耳、香菇、豆腐、蝦米或肉丸。建議先試原味，再依個人口味少量加入檸檬、辣椒與魚露。', 'Linh hồn của món Việt thường là sự cân bằng giữa rau thơm và gia vị. Rau thơm phổ biến gồm ngò rí, húng quế, bạc hà và tía tô; gia vị thường có nước mắm, chanh, ớt, tỏi, tiêu và me. Phở và bún thường ăn cùng giá đỗ, hành tây, hành lá; món nước cũng có thể có nấm mèo, nấm hương, đậu hũ, tôm khô hoặc bò viên. Hãy thử vị nguyên bản trước, rồi thêm chanh, ớt và nước mắm từng ít một.');
    }
    if (/套餐|搭配|前菜|主食|飲料|一套|gợi ý.*món/.test(text)) {
      return bilingual('可嘗試這三種搭配：\n• 清爽組合：鮮蝦春捲＋雞肉米線＋椰子水。\n• 經典組合：招牌牛肉河粉＋烤肉法國麵包＋越南煉乳冰咖啡。\n• 分享組合：越南煎餅或炸春捲＋海鮮粿條＋三色冰。\n喜歡酸香可多加檸檬與香草；喜歡濃郁可選牛肉河粉、叉燒或椰奶甜點。', 'Bạn có thể thử ba cách kết hợp này:\n• Nhẹ nhàng: gỏi cuốn tôm + bún gà + nước dừa.\n• Kinh điển: phở bò đặc biệt + bánh mì thịt nướng + cà phê sữa đá.\n• Dùng chung: bánh xèo hoặc chả giò + hủ tiếu hải sản + chè ba màu.\nNếu thích vị chua thơm, hãy thêm chanh và rau thơm; nếu thích đậm đà, hãy chọn phở bò, xá xíu hoặc món chè nước cốt dừa.');
    }
    if (/做法|煮|食譜|湯頭|料理|nấu|công thức/.test(text)) {
      return bilingual('越南料理常見的做法是先準備清楚的湯底或沾醬，再以新鮮香草完成最後風味。以河粉為例，牛骨、洋蔥與薑可慢熬成湯，再加入河粉、肉片與蔥花；上桌後搭配豆芽、香菜、九層塔、檸檬與辣椒。家庭做法會依地區與家人喜好調整甜、鹹、酸、辣比例，沒有唯一標準。', 'Cách nấu món Việt thường bắt đầu bằng nước dùng hoặc nước chấm trong vị, sau đó hoàn thiện bằng rau thơm tươi. Với phở, xương bò, hành tây và gừng có thể được ninh lấy nước; sau đó cho bánh phở, thịt và hành lá. Khi ăn, dùng thêm giá, ngò rí, húng quế, chanh và ớt. Mỗi gia đình và mỗi vùng sẽ điều chỉnh vị ngọt, mặn, chua, cay theo khẩu vị riêng.');
    }
    if (/河粉|phở|pho|米線|bún|bun|粿條|hủ tiếu|hu tieu|米苔目|bánh canh/.test(text)) {
      return bilingual('河粉 Phở 重視清澈香濃的湯頭、米粉與新鮮香草；米線 Bún 常見於拌麵或湯麵。越南不同地區的湯頭與配料會略有差異，可依喜好加檸檬、辣椒、魚露與香草。', 'Phở nổi bật với nước dùng thơm, bánh phở và rau thơm tươi. Bún thường dùng cho món nước hoặc món trộn. Mỗi vùng có cách nêm nếm khác nhau; bạn có thể thêm chanh, ớt, nước mắm và rau thơm theo khẩu vị.');
    }
    if (/麵包|bánh mì|banh mi/.test(text)) {
      return bilingual('越南法國麵包外皮酥脆、內部柔軟，常搭配肉類或蛋，再加上生菜、小黃瓜、醃蘿蔔與香菜。它融合了法式麵包與越南香草、醬料的風味。', 'Bánh mì có vỏ giòn, ruột mềm; thường kẹp thịt hoặc trứng cùng rau xà lách, dưa leo, đồ chua và rau mùi. Đây là sự kết hợp giữa bánh mì kiểu Pháp với rau thơm và gia vị Việt Nam.');
    }
    if (/咖啡|cà phê|ca phe|飲料|椰子|珍珠|茶/.test(text)) {
      return bilingual('越南咖啡常以滴漏方式沖煮，搭配煉乳與冰塊就是經典的 Cà phê sữa đá。越南也常見椰子水、甘蔗汁、各種水果冰沙與甜湯。', 'Cà phê Việt Nam thường pha bằng phin; Cà phê sữa đá là cà phê với sữa đặc và đá. Ngoài ra còn có nước dừa, nước mía, sinh tố trái cây và nhiều loại chè.');
    }
    if (/文化|習俗|禮儀|節日|過年|tết|tet|家庭|用餐/.test(text)) {
      return bilingual('越南飲食很重視家庭分享、新鮮香草與共同用餐。節慶如農曆新年 Tết 常會準備象徵團圓的料理；與長輩同桌時，先邀請長輩用餐是常見的禮貌。', 'Ẩm thực Việt Nam coi trọng bữa cơm gia đình, rau thơm tươi và sự sẻ chia. Dịp Tết thường có các món mang ý nghĩa sum họp; khi ăn cùng người lớn tuổi, mời người lớn dùng bữa trước là phép lịch sự phổ biến.');
    }
    if (/南北|北越|南越|中越|地區|差別/.test(text)) {
      return bilingual('一般來說，北越料理調味較清爽、重視食材本味；中越口味常較辣；南越常帶甜味，香草與配料較豐富。不過每個家庭與城市仍有自己的做法。', 'Nói chung, món miền Bắc thanh vị và chú trọng vị nguyên liệu; miền Trung thường cay hơn; miền Nam thường ngọt hơn và dùng nhiều rau thơm, đồ ăn kèm. Tuy nhiên mỗi gia đình và mỗi thành phố đều có cách nấu riêng.');
    }
    if (/語言|越南文|你好|謝謝|怎麼說|發音|xin chào|cảm ơn/.test(text)) {
      return bilingual('常用越南語：你好是「Xin chào」、謝謝是「Cảm ơn」、很好吃是「Ngon quá」、請問多少錢是「Bao nhiêu tiền?」。越南文有聲調，慢慢說、語氣友善就很好。', 'Một số câu thông dụng: “Xin chào” là chào hỏi, “Cảm ơn” là cảm ơn, “Ngon quá” là rất ngon, “Bao nhiêu tiền?” là hỏi giá. Tiếng Việt có thanh điệu nên nói chậm và thân thiện là rất tốt.');
    }
    if (/旅遊|淡水|河內|胡志明|峴港|下龍灣|越南在哪|城市|景點/.test(text)) {
      return bilingual('越南從北到南有河內、峴港、胡志明市等特色城市。河內有傳統街頭小吃，峴港鄰近海岸與古城，胡志明市生活節奏較熱鬧。旅遊時可多嘗試在地早餐與市場小吃。', 'Việt Nam có nhiều thành phố đặc sắc như Hà Nội, Đà Nẵng và Thành phố Hồ Chí Minh. Hà Nội nổi tiếng với món ăn đường phố truyền thống, Đà Nẵng gần biển và phố cổ, còn TP. Hồ Chí Minh sôi động hơn. Khi du lịch, hãy thử bữa sáng địa phương và đồ ăn ở chợ.');
    }
    if (/推薦|第一次|吃什麼|餐點|點餐|搭配/.test(text)) {
      return bilingual('第一次品嚐可選招牌牛肉河粉搭配烤雞或烤肉法國麵包，再配越南咖啡或椰子飲品。喜歡清爽口感可試米線；喜歡濃郁口感可選河粉與加肉配料。', 'Lần đầu thưởng thức, bạn có thể chọn phở bò đặc biệt cùng bánh mì gà nướng hoặc thịt nướng, rồi dùng thêm cà phê Việt Nam hoặc nước dừa. Nếu thích thanh mát, hãy thử bún; nếu thích đậm đà, hãy chọn phở và thêm thịt.');
    }
    if (/食材|香草|魚露|辣椒|檸檬|醬|素食/.test(text)) {
      return bilingual('越南料理常用魚露、萊姆或檸檬、辣椒、香菜、九層塔、薄荷與豆芽。香草與酸、辣、鹹、甜的平衡是重要特色；不吃肉或不吃辣時，可以在點餐備註中告知。', 'Món Việt thường dùng nước mắm, chanh, ớt, rau mùi, húng quế, bạc hà và giá đỗ. Sự cân bằng chua, cay, mặn, ngọt và rau thơm là điểm đặc sắc; nếu ăn chay hoặc không ăn cay, bạn có thể ghi chú khi gọi món.');
    }
    if (/歷史|國旗|國家|人口|天氣|貨幣/.test(text)) {
      return bilingual('越南位於東南亞，首都是河內，貨幣是越南盾（VND）。它有悠久的歷史與多元文化，飲食也受到地理、季節與不同族群的影響。若想深入某個主題，可以再告訴我關鍵字。', 'Việt Nam nằm ở Đông Nam Á, thủ đô là Hà Nội và tiền tệ là đồng Việt Nam (VND). Đất nước có lịch sử lâu đời và văn hóa đa dạng; ẩm thực chịu ảnh hưởng của địa lý, mùa vụ và nhiều cộng đồng khác nhau. Bạn có thể hỏi sâu hơn về một chủ đề cụ thể.');
    }
    if (/你好|哈囉|hello|xin chào/.test(text)) {
      return bilingual('你好！很高興認識你。你想先聊越南料理、越南文化、越南文，還是旅遊呢？', 'Xin chào! Rất vui được gặp bạn. Bạn muốn trò chuyện về ẩm thực, văn hóa, tiếng Việt hay du lịch Việt Nam trước?');
    }
    return bilingual('這是一個很棒的越南主題問題！我可以協助你了解：\n• 料理：河粉、米線、粿條、米苔目、法國麵包、咖啡與甜點。\n• 食材：香草、魚露、木耳、菇類、海鮮、肉類與過敏原。\n• 文化：南中北口味、家庭用餐、Tết 農曆新年與禮貌稱呼。\n• 實用：中越翻譯、點餐會話、旅遊城市與餐點搭配。\n請直接輸入一個主題或問題，我會以繁中與越南文一起回答。', 'Đây là một câu hỏi rất thú vị về Việt Nam! Tôi có thể giúp bạn tìm hiểu:\n• Món ăn: phở, bún, hủ tiếu, bánh canh, bánh mì, cà phê và chè.\n• Nguyên liệu: rau thơm, nước mắm, nấm mèo, các loại nấm, hải sản, thịt và dị ứng.\n• Văn hóa: khẩu vị ba miền, bữa cơm gia đình, Tết và cách xưng hô lịch sự.\n• Thực tế: dịch Trung - Việt, hội thoại gọi món, thành phố du lịch và gợi ý món ăn.\nHãy nhập một chủ đề hoặc câu hỏi; tôi sẽ trả lời bằng cả tiếng Hoa và tiếng Việt.');
  };

  const append = (content, type) => {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${type}`;
    bubble.textContent = content;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  };
  const askChatGPT = async (message, mode = 'chat', direction = 'zh-vi') => {
    try {
      const response = await fetch('/api/ai-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, mode, direction })
      });
      const data = await response.json();
      return data.answer || '';
    } catch (_) {
      return '';
    }
  };
  const send = async (value) => {
    const question = value.trim();
    if (!question) return;
    append(question, 'user');
    input.value = '';
    const remoteAnswer = await askChatGPT(question);
    append(remoteAnswer || answer(question), 'bot');
  };
  form.addEventListener('submit', (event) => { event.preventDefault(); send(input.value); });
  document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => send(button.dataset.prompt)));

  const direction = document.querySelector('#translation-direction');
  const translationInput = document.querySelector('#translation-input');
  const translationResult = document.querySelector('#translation-result');
  const translateButton = document.querySelector('#translate-button');
  const zhToVi = {
    '你好': 'Xin chào', '謝謝': 'Cảm ơn', '再見': 'Tạm biệt', '請問': 'Xin hỏi', '多少錢': 'Bao nhiêu tiền?', '越南': 'Việt Nam', '台灣': 'Đài Loan',
    '很好吃': 'Ngon quá', '不要辣': 'Không cay', '少辣': 'Ít cay', '加辣椒': 'Thêm ớt', '不要香菜': 'Không ngò rí (Bắc: rau mùi)',
    '不要魚露': 'Không nước mắm', '河粉': 'Phở', '米線': 'Bún', '粿條': 'Hủ tiếu', '米苔目': 'Bánh canh',
    '法國麵包': 'Bánh mì', '咖啡': 'Cà phê', '魚露': 'Nước mắm', '醬油': '南越：nước tương\n北越：xì dầu', '檸檬': 'Chanh', '辣椒': 'Ớt',
    '豬肉': '南越：thịt heo\n北越：thịt lợn', '花生醬': '南越：bơ đậu phộng\n北越：bơ lạc',
    '玉米': '南越：bắp\n北越：ngô', '鳳梨': '南越：thơm\n北越：dứa', '香菜': '南越：ngò rí\n北越：rau mùi',
    '小黃瓜': 'Dưa leo (Bắc: dưa chuột)', '醃蘿蔔': 'Đồ chua', '外帶': 'Mang đi', '內用': 'Ăn tại chỗ'
  };
  const viToZh = {
    'xin chào': '你好', 'cảm ơn': '謝謝', 'tạm biệt': '再見', 'bao nhiêu tiền': '多少錢？', 'việt nam': '越南', 'đài loan': '台灣', 'ngon quá': '很好吃',
    'không cay': '不要辣', 'ít cay': '少辣', 'thêm ớt': '加辣椒', 'không nước mắm': '不要魚露',
    'phở': '河粉', 'bún': '米線', 'hủ tiếu': '粿條', 'bánh canh': '米苔目', 'bánh mì': '越南法國麵包',
    'cà phê': '咖啡', 'nước mắm': '魚露', 'nước tương': '醬油（南越用語）', 'xì dầu': '醬油（北越用語）', 'chanh': '檸檬', 'ớt': '辣椒',
    'thịt heo': '豬肉（南越用語）', 'thịt lợn': '豬肉（北越用語）', 'đậu phộng': '花生（南越用語）',
    'lạc': '花生（北越用語）', 'bắp': '玉米（南越用語）', 'ngô': '玉米（北越用語）',
    'thơm': '鳳梨（南越用語）', 'dứa': '鳳梨（北越用語）', 'ngò rí': '香菜（南越用語）', 'rau mùi': '香菜（北越用語）',
    'mang đi': '外帶', 'ăn tại chỗ': '內用'
  };
  // Built-in vocabulary keeps common translations available even when the
  // optional AI service is not configured or temporarily unavailable.
  Object.assign(zhToVi, {
    '請': 'Làm ơn', '不好意思': 'Xin lỗi', '沒關係': 'Không sao', '對不起': 'Xin lỗi', '歡迎': 'Hoan nghênh', '請稍等': 'Vui lòng chờ một chút',
    '可以': 'Có thể', '不可以': 'Không được', '有': 'Có', '沒有': 'Không có', '我要': 'Tôi muốn', '我不要': 'Tôi không muốn', '我想要': 'Tôi muốn',
    '這個': 'Cái này', '那個': 'Cái kia', '一個': 'Một cái', '兩個': 'Hai cái', '一份': 'Một phần', '幾份': 'Mấy phần', '全部': 'Tất cả',
    '菜單': 'Thực đơn', '餐點': 'Món ăn', '主食': 'Món chính', '加料': 'Thêm món', '備註': 'Ghi chú', '推薦': 'Gợi ý', '招牌': 'Đặc biệt',
    '好吃': 'Ngon', '很辣': 'Rất cay', '不辣': 'Không cay', '微辣': 'Hơi cay', '正常辣': 'Cay vừa', '少鹽': 'Ít muối', '不要鹽': 'Không muối',
    '少糖': 'Ít đường', '半糖': 'Nửa đường', '無糖': 'Không đường', '正常糖': 'Đường bình thường', '少冰': 'Ít đá', '去冰': 'Không đá', '常溫': 'Nhiệt độ thường',
    '加大': 'Size lớn', '加麵': 'Thêm mì', '加河粉': 'Thêm bánh phở', '加米線': 'Thêm bún', '加菜': 'Thêm rau', '加肉': 'Thêm thịt', '加蛋': 'Thêm trứng',
    '打包': 'Đóng gói', '分開裝': 'Để riêng', '醬料另外放': 'Để nước chấm riêng', '餐具': 'Dụng cụ ăn', '湯匙': 'Muỗng', '筷子': 'Đũa', '吸管': 'Ống hút', '衛生紙': 'Khăn giấy',
    '現金': 'Tiền mặt', '刷卡': 'Thanh toán bằng thẻ', '付款': 'Thanh toán', '找錢': 'Tiền thối lại', '收據': 'Hóa đơn', '總共': 'Tổng cộng', '折扣': 'Giảm giá',
    '會員': 'Thành viên', '點數': 'Điểm thưởng', '累積點數': 'Tích điểm', '折抵': 'Đổi điểm', '訂單': 'Đơn hàng', '下單': 'Đặt món', '取消訂單': 'Hủy đơn hàng',
    '已接單': 'Đã nhận đơn', '製作中': 'Đang làm', '已完成可領取': 'Đã xong, có thể nhận', '已領取': 'Đã nhận món', '已付款': 'Đã thanh toán', '待付款': 'Chờ thanh toán',
    '牛肉': 'Thịt bò', '牛腩': 'Gầu bò', '牛筋': 'Gân bò', '牛肉丸': 'Bò viên', '雞肉': 'Thịt gà', '雞腿': 'Đùi gà', '火腿': 'Giăm bông',
    '叉燒': 'Xá xíu', '肉鬆': 'Chà bông', '豬排': 'Sườn heo', '豬腳': 'Giò heo', '蝦': 'Tôm', '蟹肉': 'Thịt cua', '海鮮': 'Hải sản',
    '鮪魚': 'Cá ngừ', '沙丁魚': 'Cá mòi', '魚餅': 'Chả cá', '鱸魚': 'Cá lóc', '豆腐': 'Đậu hũ', '起司': 'Phô mai', '雞蛋': 'Trứng',
    '生菜': 'Rau xà lách', '豆芽': 'Giá đỗ', '洋蔥': 'Hành tây', '青蔥': 'Hành lá', '韭菜': 'Hẹ', '高麗菜': 'Bắp cải', '紅蘿蔔': 'Cà rốt',
    '白蘿蔔': 'Củ cải trắng', '番茄': 'Cà chua', '小白菜': 'Cải thìa', '香茅': 'Sả', '薑': 'Gừng', '蒜頭': 'Tỏi', '薄荷': 'Bạc hà', '九層塔': 'Húng quế',
    '木耳': '南越：nấm mèo\n北越：mộc nhĩ', '香菇': 'Nấm hương', '金針菇': 'Nấm kim châm', '杏鮑菇': 'Nấm bào ngư', '蘑菇': 'Nấm mỡ', '菇類': 'Nấm',
    '芹菜': 'Cần tây', '空心菜': 'Rau muống', '芥蘭': 'Cải làn', '菠菜': 'Rau bina', '芥菜': 'Cải xanh', '白菜': 'Cải thảo', '玉米筍': 'Bắp non',
    '四季豆': 'Đậu que', '豌豆': 'Đậu Hà Lan', '毛豆': 'Đậu nành non', '綠豆': 'Đậu xanh', '紅豆': 'Đậu đỏ', '黃豆': 'Đậu nành', '花豆': 'Đậu pinto',
    '蓮藕': 'Củ sen', '竹筍': 'Măng', '馬鈴薯': 'Khoai tây', '地瓜': 'Khoai lang', '芋頭': 'Khoai môn', '木薯': 'Khoai mì', '南瓜': 'Bí đỏ',
    '苦瓜': 'Khổ qua', '茄子': 'Cà tím', '青椒': 'Ớt chuông xanh', '甜椒': 'Ớt chuông', '秋葵': 'Đậu bắp', '洋菇': 'Nấm mỡ', '蔥酥': 'Hành phi',
    '油蔥酥': 'Hành phi', '炸蒜': 'Tỏi phi', '蝦米': 'Tôm khô', '蝦醬': 'Mắm tôm', '沙茶醬': 'Sa tế', '甜辣醬': 'Tương ớt ngọt', '蠔油': 'Dầu hào',
    '胡椒': 'Tiêu', '白胡椒': 'Tiêu trắng', '五香粉': 'Ngũ vị hương', '咖哩': 'Cà ri', '椰糖': 'Đường thốt nốt', '醋': 'Giấm', '醬油膏': 'Tương đen',
    '豬五花': 'Ba chỉ heo', '豬絞肉': 'Thịt heo xay', '排骨': 'Sườn', '雞胸肉': 'Ức gà', '雞翅': 'Cánh gà', '鴨肉': 'Thịt vịt', '羊肉': 'Thịt dê',
    '蛤蜊': 'Nghêu', '花枝': 'Mực nang', '魷魚': 'Mực', '魚片': 'Phi lê cá', '魚丸': 'Cá viên', '蟹肉棒': 'Thanh cua', '蚵仔': 'Hàu',
    '鳳梨': '南越：thơm\n北越：dứa', '芒果': 'Xoài', '香蕉': 'Chuối', '草莓': 'Dâu tây', '百香果': 'Chanh dây', '西瓜': 'Dưa hấu', '荔枝': 'Vải',
    '龍眼': 'Nhãn', '酪梨': 'Bơ', '檸檬汁': 'Nước chanh', '甘蔗汁': 'Nước mía', '果汁': 'Nước ép trái cây', '冰沙': 'Sinh tố', '椰絲': 'Dừa sợi',
    '檸檬葉': 'Lá chanh', '萊姆': 'Chanh xanh', '羅望子': 'Me', '椰奶': 'Nước cốt dừa', '椰子水': 'Nước dừa', '椰子果凍': 'Thạch dừa',
    '珍珠': 'Trân châu', '仙草凍': 'Sương sáo', '椰果': 'Nata de coco', '布丁': 'Bánh flan', '煉乳': 'Sữa đặc', '牛奶': 'Sữa', '優格': 'Sữa chua',
    '咖啡豆': 'Hạt cà phê', '冰咖啡': 'Cà phê đá', '黑咖啡': 'Cà phê đen', '煉乳咖啡': 'Cà phê sữa', '椰子咖啡': 'Cà phê dừa', '蛋咖啡': 'Cà phê trứng',
    '春捲': 'Gỏi cuốn', '炸春捲': 'Chả giò', '煎餅': 'Bánh xèo', '粉捲': 'Bánh cuốn', '甜湯': 'Chè', '三色冰': 'Chè ba màu', '焦糖布丁': 'Bánh flan',
    '米紙': 'Bánh tráng', '米粉': 'Bánh phở', '魚露醬': 'Nước mắm', '辣椒醬': 'Tương ớt', '花生': 'Đậu phộng (Bắc: lạc)', '糖': 'Đường', '鹽': 'Muối',
    '早安': 'Chào buổi sáng', '午安': 'Chào buổi trưa', '晚安': 'Chúc ngủ ngon', '你叫什麼名字': 'Bạn tên là gì?', '我叫': 'Tôi tên là', '很高興認識你': 'Rất vui được gặp bạn',
    '請問廁所在哪裡': 'Nhà vệ sinh ở đâu?', '我聽不懂': 'Tôi không hiểu', '請說慢一點': 'Xin nói chậm một chút', '可以幫我嗎': 'Bạn có thể giúp tôi không?',
    '越南文': 'Tiếng Việt', '繁體中文': 'Tiếng Trung phồn thể', '北越': 'Miền Bắc', '中越': 'Miền Trung', '南越': 'Miền Nam', '越南文化': 'Văn hóa Việt Nam',
    '農曆新年': 'Tết Nguyên Đán', '市場': 'Chợ', '夜市': 'Chợ đêm', '旅遊': 'Du lịch', '河內': 'Hà Nội', '胡志明市': 'Thành phố Hồ Chí Minh', '峴港': 'Đà Nẵng'
  });
  Object.assign(viToZh, {
    'làm ơn': '請', 'xin lỗi': '對不起／不好意思', 'không sao': '沒關係', 'hoan nghênh': '歡迎', 'vui lòng chờ một chút': '請稍等',
    'tôi muốn': '我想要／我要', 'tôi không muốn': '我不要', 'cái này': '這個', 'cái kia': '那個', 'một phần': '一份', 'mấy phần': '幾份',
    'thực đơn': '菜單', 'món ăn': '餐點', 'món chính': '主食', 'thêm món': '加料', 'ghi chú': '備註', 'gợi ý': '推薦', 'đặc biệt': '招牌',
    'ngon': '好吃', 'rất cay': '很辣', 'hơi cay': '微辣', 'cay vừa': '正常辣', 'ít muối': '少鹽', 'không muối': '不要鹽',
    'ít đường': '少糖', 'nửa đường': '半糖', 'không đường': '無糖', 'ít đá': '少冰', 'không đá': '去冰', 'nhiệt độ thường': '常溫', 'size lớn': '加大',
    'thêm mì': '加麵', 'thêm bánh phở': '加河粉', 'thêm bún': '加米線', 'thêm rau': '加菜', 'thêm thịt': '加肉', 'thêm trứng': '加蛋',
    'đóng gói': '打包', 'để riêng': '分開裝', 'để nước chấm riêng': '醬料另外放', 'dụng cụ ăn': '餐具', 'muỗng': '湯匙', 'đũa': '筷子', 'ống hút': '吸管', 'khăn giấy': '衛生紙',
    'tiền mặt': '現金', 'thanh toán bằng thẻ': '刷卡', 'thanh toán': '付款', 'tiền thối lại': '找錢', 'hóa đơn': '收據', 'tổng cộng': '總共', 'giảm giá': '折扣',
    'thành viên': '會員', 'điểm thưởng': '點數', 'tích điểm': '累積點數', 'đổi điểm': '折抵', 'đơn hàng': '訂單', 'đặt món': '下單', 'hủy đơn hàng': '取消訂單',
    'đã nhận đơn': '已接單', 'đang làm': '製作中', 'đã xong, có thể nhận': '已完成可領取', 'đã nhận món': '已領取', 'đã thanh toán': '已付款', 'chờ thanh toán': '待付款',
    'thịt bò': '牛肉', 'gầu bò': '牛腩', 'gân bò': '牛筋', 'bò viên': '牛肉丸', 'thịt gà': '雞肉', 'đùi gà': '雞腿', 'giăm bông': '火腿',
    'xá xíu': '叉燒', 'chà bông': '肉鬆', 'sườn heo': '豬排', 'giò heo': '豬腳', 'tôm': '蝦', 'thịt cua': '蟹肉', 'hải sản': '海鮮',
    'cá ngừ': '鮪魚', 'cá mòi': '沙丁魚', 'chả cá': '魚餅', 'cá lóc': '鱸魚', 'đậu hũ': '豆腐', 'phô mai': '起司', 'trứng': '雞蛋',
    'rau xà lách': '生菜', 'giá đỗ': '豆芽', 'hành tây': '洋蔥', 'hành lá': '青蔥', 'hẹ': '韭菜', 'bắp cải': '高麗菜', 'cà rốt': '紅蘿蔔',
    'củ cải trắng': '白蘿蔔', 'cà chua': '番茄', 'sả': '香茅', 'gừng': '薑', 'tỏi': '蒜頭', 'bạc hà': '薄荷', 'húng quế': '九層塔',
    'nấm mèo': '木耳（南越用語）', 'mộc nhĩ': '木耳（北越用語）', 'nấm hương': '香菇', 'nấm kim châm': '金針菇', 'nấm bào ngư': '杏鮑菇', 'nấm mỡ': '蘑菇／洋菇', 'nấm': '菇類',
    'cần tây': '芹菜', 'rau muống': '空心菜', 'cải làn': '芥蘭', 'rau bina': '菠菜', 'cải xanh': '芥菜', 'cải thảo': '白菜', 'bắp non': '玉米筍',
    'đậu que': '四季豆', 'đậu hà lan': '豌豆', 'đậu nành non': '毛豆', 'đậu xanh': '綠豆', 'đậu đỏ': '紅豆', 'đậu nành': '黃豆', 'củ sen': '蓮藕',
    'măng': '竹筍', 'khoai tây': '馬鈴薯', 'khoai lang': '地瓜', 'khoai môn': '芋頭', 'khoai mì': '木薯', 'bí đỏ': '南瓜', 'khổ qua': '苦瓜',
    'cà tím': '茄子', 'ớt chuông': '甜椒', 'đậu bắp': '秋葵', 'hành phi': '蔥酥／油蔥酥', 'tỏi phi': '炸蒜', 'tôm khô': '蝦米', 'mắm tôm': '蝦醬',
    'sa tế': '沙茶醬', 'tương ớt ngọt': '甜辣醬', 'dầu hào': '蠔油', 'tiêu': '胡椒', 'tiêu trắng': '白胡椒', 'ngũ vị hương': '五香粉', 'cà ri': '咖哩',
    'đường thốt nốt': '椰糖', 'giấm': '醋', 'tương đen': '醬油膏', 'ba chỉ heo': '豬五花', 'thịt heo xay': '豬絞肉', 'sườn': '排骨',
    'ức gà': '雞胸肉', 'cánh gà': '雞翅', 'thịt vịt': '鴨肉', 'thịt dê': '羊肉', 'nghêu': '蛤蜊', 'mực nang': '花枝', 'mực': '魷魚',
    'phi lê cá': '魚片', 'cá viên': '魚丸', 'thanh cua': '蟹肉棒', 'hàu': '蚵仔', 'xoài': '芒果', 'chuối': '香蕉', 'dâu tây': '草莓',
    'chanh dây': '百香果', 'dưa hấu': '西瓜', 'vải': '荔枝', 'nhãn': '龍眼', 'bơ': '酪梨', 'nước chanh': '檸檬汁', 'nước mía': '甘蔗汁',
    'nước ép trái cây': '果汁', 'sinh tố': '冰沙', 'dừa sợi': '椰絲',
    'chanh xanh': '萊姆', 'me': '羅望子', 'nước cốt dừa': '椰奶', 'nước dừa': '椰子水', 'thạch dừa': '椰子果凍', 'trân châu': '珍珠',
    'sương sáo': '仙草凍', 'nata de coco': '椰果', 'sữa đặc': '煉乳', 'sữa chua': '優格', 'cà phê đá': '冰咖啡', 'cà phê đen': '黑咖啡',
    'cà phê sữa': '煉乳咖啡', 'cà phê dừa': '椰子咖啡', 'cà phê trứng': '蛋咖啡', 'gỏi cuốn': '春捲', 'chả giò': '炸春捲', 'bánh xèo': '煎餅',
    'bánh cuốn': '粉捲', 'chè': '甜湯', 'bánh tráng': '米紙', 'tương ớt': '辣椒醬', 'đường': '糖', 'muối': '鹽',
    'chào buổi sáng': '早安', 'chúc ngủ ngon': '晚安', 'bạn tên là gì': '你叫什麼名字', 'tôi tên là': '我叫', 'rất vui được gặp bạn': '很高興認識你',
    'nhà vệ sinh ở đâu': '請問廁所在哪裡', 'tôi không hiểu': '我聽不懂', 'xin nói chậm một chút': '請說慢一點', 'tiếng việt': '越南文',
    'miền bắc': '北越', 'miền trung': '中越', 'miền nam': '南越', 'văn hóa việt nam': '越南文化', 'tết nguyên đán': '農曆新年',
    'chợ': '市場', 'chợ đêm': '夜市', 'du lịch': '旅遊', 'hà nội': '河內', 'thành phố hồ chí minh': '胡志明市', 'đà nẵng': '峴港'
  });
  // Regional vocabulary: Southern Vietnamese is displayed first because it
  // is the primary wording used by this ordering system. Northern variants
  // are preserved for learning, travel and bilingual menu communication.
  Object.assign(zhToVi, {
    '木耳絲': '南越：nấm mèo thái sợi\n北越：mộc nhĩ thái sợi',
    '豬肉': '南越：thịt heo\n北越：thịt lợn', '豬絞肉': '南越：thịt heo xay\n北越：thịt lợn xay',
    '花生': '南越：đậu phộng\n北越：lạc', '花生醬': '南越：bơ đậu phộng\n北越：bơ lạc',
    '玉米': '南越：bắp\n北越：ngô', '玉米筍': '南越：bắp non\n北越：ngô non',
    '鳳梨': '南越：thơm\n北越：dứa', '香菜': '南越：ngò rí\n北越：rau mùi',
    '小黃瓜': '南越：dưa leo\n北越：dưa chuột', '青蔥': '南越：hành lá\n北越：hành hoa',
    '木薯': '南越：khoai mì\n北越：sắn', '醃菜': '南越：đồ chua\n北越：dưa góp',
    '醬油': '南越：nước tương\n北越：xì dầu', '汽水': '南越：nước ngọt\n北越：nước giải khát có ga',
    '外帶': '南越：mang đi\n北越：đem về', '湯匙': '南越：muỗng\n北越：thìa',
    '涼粉': '南越：sương sáo\n北越：thạch đen', '煎蛋': 'Trứng chiên', '荷包蛋': 'Trứng ốp la',
    '鴨蛋': 'Trứng vịt', '鵪鶉蛋': 'Trứng cút', '肉丸': 'Viên thịt', '越南火腿': 'Chả lụa',
    '豬皮': 'Bì heo', '豬耳朵': 'Tai heo', '豬血': 'Huyết heo', '牛肚': 'Sách bò',
    '牛骨湯': 'Nước dùng xương bò', '雞高湯': 'Nước dùng gà', '酸湯': 'Canh chua', '清湯': 'Nước dùng trong',
    '河粉條': 'Bánh phở', '米線條': 'Bún', '粿條': 'Hủ tiếu', '米苔目': 'Bánh canh',
    '米飯': 'Cơm', '糯米飯': 'Xôi', '炒飯': 'Cơm chiên', '白飯': 'Cơm trắng',
    '法國麵包': 'Bánh mì', '麵包皮': 'Vỏ bánh mì', '奶油': 'Bơ', '美乃滋': 'Sốt mayonnaise',
    '辣椒': 'Ớt', '辣椒片': 'Ớt lát', '辣椒粉': 'Bột ớt', '辣椒油': 'Dầu ớt', '辣椒醬': 'Tương ớt',
    '魚露': 'Nước mắm', '魚露醬': 'Nước chấm', '蠔油': 'Dầu hào', '甜醬': 'Tương đen',
    '蝦醬': 'Mắm tôm', '蝦油': 'Dầu điều', '羅望子醬': 'Sốt me', '酸甜醬': 'Nước mắm chua ngọt',
    '紅蔥頭': 'Hành tím', '香茅': 'Sả', '南薑': 'Riềng', '薑黃': 'Nghệ', '檸檬葉': 'Lá chanh',
    '紫蘇': 'Tía tô', '魚腥草': 'Rau diếp cá', '越南香菜': 'Rau răm', '香草': 'Rau thơm',
    '豆芽菜': 'Giá đỗ', '芥菜': 'Cải xanh', '高麗菜絲': 'Bắp cải thái sợi', '涼拌菜': 'Gỏi rau',
    '秋葵': 'Đậu bắp', '絲瓜': 'Mướp', '冬瓜': 'Bí xanh', '番薯葉': 'Rau khoai lang',
    '蓮子': 'Hạt sen', '白木耳': 'Nấm tuyết', '綠豆仁': 'Đậu xanh cà vỏ', '紅豆湯': 'Chè đậu đỏ',
    '椰奶': 'Nước cốt dừa', '椰糖': 'Đường thốt nốt', '煉乳': 'Sữa đặc', '鮮奶': 'Sữa tươi',
    '豆漿': 'Sữa đậu nành', '奶茶': 'Trà sữa', '檸檬茶': 'Trà chanh', '金桔茶': 'Trà tắc',
    '越南咖啡': 'Cà phê Việt Nam', '滴漏咖啡': 'Cà phê phin', '冰滴咖啡': 'Cà phê sữa đá',
    '甘蔗汁': 'Nước mía', '酪梨冰沙': 'Sinh tố bơ', '芒果冰沙': 'Sinh tố xoài', '百香果汁': 'Nước chanh dây',
    '越南春捲': 'Gỏi cuốn', '炸春捲': 'Chả giò', '越南煎餅': 'Bánh xèo', '越南粉捲': 'Bánh cuốn',
    '涼拌米紙': 'Gỏi bánh tráng', '烤肉米線': 'Bún thịt nướng', '順化牛肉米線': 'Bún bò Huế',
    '海南雞飯': 'Cơm gà', '越南燒肉飯': 'Cơm tấm sườn nướng', '乾拌粿條': 'Hủ tiếu khô',
    '不加香菜': 'Không ngò rí', '不要木耳': 'Không nấm mèo', '不要花生': 'Không đậu phộng',
    '不要洋蔥': 'Không hành tây', '不要辣椒': 'Không ớt', '加很多辣椒': 'Cho nhiều ớt',
    '醬料分開': 'Nước chấm để riêng', '湯另外裝': 'Nước dùng để riêng', '麵另外裝': 'Bún để riêng',
    '我對花生過敏': 'Tôi bị dị ứng đậu phộng', '我對海鮮過敏': 'Tôi bị dị ứng hải sản',
    '我吃素': 'Tôi ăn chay', '不要肉': 'Không thịt', '不要魚露': 'Không nước mắm',
    '可以刷卡嗎': 'Có thể thanh toán bằng thẻ không?', '可以使用點數嗎': 'Có thể dùng điểm không?',
    '取餐號碼': 'Số lấy món', '我來取餐': 'Tôi đến lấy món', '大約等多久': 'Khoảng bao lâu thì xong?',
    '請給我發票': 'Cho tôi xin hóa đơn', '不用餐具': 'Không cần dụng cụ ăn', '謝謝，很好吃': 'Cảm ơn, rất ngon',
    '家人': 'Gia đình', '朋友': 'Bạn bè', '長輩': 'Người lớn tuổi', '小朋友': 'Trẻ em',
    '敬語': 'Cách nói lịch sự', '大哥': 'Anh', '大姐': 'Chị', '叔叔': 'Chú', '阿姨': 'Cô',
    '越南新年': 'Tết Nguyên Đán', '中秋節': 'Tết Trung Thu', '端午節': 'Tết Đoan Ngọ',
    '越南盾': 'Đồng Việt Nam', '機車': 'Xe máy', '計程車': 'Taxi', '公車': 'Xe buýt',
    '胡志明市': 'Thành phố Hồ Chí Minh', '河內': 'Hà Nội', '順化': 'Huế', '會安': 'Hội An',
    '芽莊': 'Nha Trang', '大叻': 'Đà Lạt', '富國島': 'Phú Quốc', '湄公河': 'Sông Mekong'
  });
  Object.assign(viToZh, {
    'mộc nhĩ': '木耳（北越用語）', 'nấm mèo': '木耳（南越用語）',
    'thịt heo': '豬肉（南越用語）', 'thịt lợn': '豬肉（北越用語）',
    'đậu phộng': '花生（南越用語）', 'lạc': '花生（北越用語）',
    'bắp': '玉米（南越用語）', 'ngô': '玉米（北越用語）', 'thơm': '鳳梨（南越用語）', 'dứa': '鳳梨（北越用語）',
    'ngò rí': '香菜（南越用語）', 'rau mùi': '香菜（北越用語）',
    'dưa leo': '小黃瓜（南越用語）', 'dưa chuột': '小黃瓜（北越用語）',
    'hành lá': '青蔥（南越用語）', 'hành hoa': '青蔥（北越用語）',
    'khoai mì': '木薯（南越用語）', 'sắn': '木薯（北越用語）',
    'đồ chua': '醃菜（南越用語）', 'dưa góp': '醃菜（北越用語）',
    'nước tương': '醬油（南越用語）', 'xì dầu': '醬油（北越用語）',
    'mang đi': '外帶（南越用語）', 'đem về': '外帶（北越用語）',
    'muỗng': '湯匙（南越用語）', 'thìa': '湯匙（北越用語）',
    'nước dùng xương bò': '牛骨湯', 'nước dùng gà': '雞高湯', 'canh chua': '酸湯', 'nước dùng trong': '清湯',
    'cơm': '米飯', 'xôi': '糯米飯', 'cơm chiên': '炒飯', 'cơm trắng': '白飯',
    'bơ đậu phộng': '花生醬（南越用語）', 'bơ lạc': '花生醬（北越用語）', 'chả lụa': '越南火腿',
    'bì heo': '豬皮', 'tai heo': '豬耳朵', 'huyết heo': '豬血', 'sách bò': '牛肚',
    'dầu điều': '蝦油／紅木籽油', 'sốt me': '羅望子醬', 'nước mắm chua ngọt': '酸甜魚露醬',
    'hành tím': '紅蔥頭', 'riềng': '南薑', 'nghệ': '薑黃', 'tía tô': '紫蘇', 'rau răm': '越南香菜',
    'rau diếp cá': '魚腥草', 'rau thơm': '香草', 'mướp': '絲瓜', 'bí xanh': '冬瓜', 'rau khoai lang': '番薯葉',
    'hạt sen': '蓮子', 'nấm tuyết': '白木耳', 'đậu xanh cà vỏ': '綠豆仁', 'chè đậu đỏ': '紅豆湯',
    'sữa tươi': '鮮奶', 'sữa đậu nành': '豆漿', 'trà sữa': '奶茶', 'trà chanh': '檸檬茶', 'trà tắc': '金桔茶',
    'cà phê việt nam': '越南咖啡', 'cà phê phin': '滴漏咖啡', 'cà phê sữa đá': '冰滴煉乳咖啡',
    'sinh tố bơ': '酪梨冰沙', 'sinh tố xoài': '芒果冰沙', 'nước chanh dây': '百香果汁',
    'gỏi bánh tráng': '涼拌米紙', 'bún thịt nướng': '烤肉米線', 'bún bò huế': '順化牛肉米線',
    'cơm tấm sườn nướng': '越南燒肉飯', 'hủ tiếu khô': '乾拌粿條',
    'không ngò rí': '不加香菜', 'không nấm mèo': '不要木耳', 'không đậu phộng': '不要花生',
    'nước chấm để riêng': '醬料分開', 'nước dùng để riêng': '湯另外裝', 'bún để riêng': '米線另外裝',
    'tôi bị dị ứng đậu phộng': '我對花生過敏', 'tôi bị dị ứng hải sản': '我對海鮮過敏',
    'tôi ăn chay': '我吃素', 'không thịt': '不要肉', 'có thể dùng điểm không': '可以使用點數嗎',
    'số lấy món': '取餐號碼', 'tôi đến lấy món': '我來取餐', 'khoảng bao lâu thì xong': '大約等多久',
    'cảm ơn, rất ngon': '謝謝，很好吃', 'người lớn tuổi': '長輩', 'trẻ em': '小朋友',
    'tết trung thu': '中秋節', 'tết đoan ngọ': '端午節', 'đồng việt nam': '越南盾',
    'xe máy': '機車', 'xe buýt': '公車', 'huế': '順化', 'hội an': '會安', 'nha trang': '芽莊',
    'đà lạt': '大叻', 'phú quốc': '富國島', 'sông mekong': '湄公河'
  });
  // Extra vocabulary for quick on-page translation. These are intentionally
  // short terms so they also work well with the local offline fallback.
  Object.assign(zhToVi, {
    '鱈魚': 'Cá tuyết', '鯰魚': 'Cá tra', '鯖魚': 'Cá thu', '鯷魚': 'Cá cơm', '鯉魚': 'Cá chép',
    '鮭魚': 'Cá hồi', '鯛魚': 'Cá điêu hồng', '吳郭魚': 'Cá rô phi', '蝦仁': 'Tôm bóc vỏ',
    '大蝦': 'Tôm sú', '螃蟹': 'Cua', '螃蟹肉': 'Thịt cua', '扇貝': 'Sò điệp', '淡菜': 'Vẹm',
    '章魚': 'Bạch tuộc', '小卷': 'Mực ống nhỏ', '海帶': 'Rong biển', '海藻': 'Tảo biển',
    '牛排': 'Bít tết bò', '牛小排': 'Sườn bò', '牛腱': 'Bắp bò', '牛肉片': 'Thịt bò lát',
    '牛舌': 'Lưỡi bò', '羊排': 'Sườn cừu', '培根': 'Thịt xông khói', '香腸': 'Xúc xích',
    '雞絞肉': 'Thịt gà xay', '雞皮': 'Da gà', '雞胗': 'Mề gà', '雞心': 'Tim gà',
    '雞肉丸': 'Viên thịt gà', '鵝肉': 'Thịt ngỗng', '鴿肉': 'Thịt bồ câu', '內臟': 'Nội tạng',
    '青花菜': 'Bông cải xanh', '白花椰菜': 'Súp lơ trắng', '青江菜': 'Cải thìa', '油菜': 'Cải ngọt',
    '莧菜': 'Rau dền', '茼蒿': 'Rau tần ô', '菜心': 'Cải ngồng', '豌豆苗': 'Đọt đậu',
    '豆苗': 'Đọt đậu', '蘆筍': 'Măng tây', '甜豆': 'Đậu Hà Lan ngọt', '荷蘭豆': 'Đậu Hà Lan',
    '皇帝豆': 'Đậu ngự', '紅腰豆': 'Đậu đỏ thận', '黑豆': 'Đậu đen', '豆皮': 'Tàu hũ ky',
    '腐竹': 'Tàu hũ ky', '豆干': 'Đậu hũ khô', '嫩豆腐': 'Đậu hũ non', '豆腐泡': 'Đậu hũ chiên',
    '黑木耳': '南越：nấm mèo đen\n北越：mộc nhĩ đen', '雪耳': 'Nấm tuyết', '猴頭菇': 'Nấm hầu thủ',
    '舞菇': 'Nấm maitake', '鴻喜菇': 'Nấm shimeji', '蘑菇醬': 'Sốt nấm', '菇湯': 'Canh nấm',
    '芭樂': 'Ổi', '木瓜': 'Đu đủ', '火龍果': 'Thanh long', '山竹': 'Măng cụt', '榴槤': 'Sầu riêng',
    '紅毛丹': 'Chôm chôm', '柚子': 'Bưởi', '橘子': 'Quýt', '柳橙': 'Cam', '葡萄': 'Nho',
    '蘋果': 'Táo', '梨子': 'Lê', '葡萄柚': 'Bưởi chùm', '哈密瓜': 'Dưa lưới', '椰子': 'Dừa',
    '咖哩葉': 'Lá cà ri', '斑蘭葉': 'Lá dứa', '薄荷葉': 'Lá bạc hà', '檸檬草': 'Sả',
    '蒜苗': 'Tỏi tây', '大蔥': 'Hành boa-rô', '洋香菜': 'Ngò tây', '孜然': 'Thì là Ai Cập',
    '八角': 'Hoa hồi', '肉桂': 'Quế', '丁香': 'Đinh hương', '小茴香': 'Hạt thì là',
    '芝麻': 'Mè', '白芝麻': 'Mè trắng', '黑芝麻': 'Mè đen', '腰果': 'Hạt điều',
    '杏仁': 'Hạnh nhân', '核桃': 'Óc chó', '椰肉': 'Cùi dừa', '椰漿': 'Nước cốt dừa',
    '米醋': 'Giấm gạo', '辣椒醋': 'Giấm ớt', '糖醋汁': 'Sốt chua ngọt', '胡椒鹽': 'Muối tiêu',
    '調味料': 'Gia vị', '醃料': 'Gia vị ướp', '沾醬': 'Nước chấm', '湯底': 'Nước dùng',
    '熱的': 'Nóng', '冰的': 'Lạnh', '溫的': 'Ấm', '燒燙': 'Rất nóng', '新鮮': 'Tươi',
    '酥脆': 'Giòn', '軟嫩': 'Mềm', 'Q彈': 'Dai giòn', '濃郁': 'Đậm đà', '清爽': 'Thanh mát',
    '鹹': 'Mặn', '甜': 'Ngọt', '酸': 'Chua', '苦': 'Đắng', '辣': 'Cay', '香': 'Thơm',
    '太鹹': 'Quá mặn', '太甜': 'Quá ngọt', '太酸': 'Quá chua', '太辣': 'Quá cay', '不要太辣': 'Đừng quá cay',
    '煮': 'Luộc', '燙': 'Trụng', '蒸': 'Hấp', '炒': 'Xào', '煎': 'Chiên áp chảo',
    '炸': 'Chiên giòn', '烤': 'Nướng', '滷': 'Kho', '燉': 'Hầm', '涼拌': 'Trộn gỏi',
    '切片': 'Thái lát', '切絲': 'Thái sợi', '切丁': 'Cắt hạt lựu', '剁碎': 'Băm nhỏ',
    '大份': 'Phần lớn', '小份': 'Phần nhỏ', '單點': 'Gọi món lẻ', '套餐': 'Phần ăn kèm',
    '兒童餐': 'Phần ăn trẻ em', '素食': 'Món chay', '全素': 'Thuần chay', '不含麩質': 'Không gluten',
    '過敏原': 'Chất gây dị ứng', '乳製品': 'Sản phẩm từ sữa', '甲殼類': 'Động vật có vỏ',
    '我要一碗河粉': 'Tôi muốn một tô phở', '我要一份米線': 'Tôi muốn một phần bún',
    '這個有辣嗎': 'Món này có cay không?', '可以做不辣嗎': 'Có thể làm không cay không?',
    '可以少一點冰嗎': 'Có thể cho ít đá không?', '可以少一點糖嗎': 'Có thể cho ít đường không?',
    '請幫我加檸檬': 'Cho tôi thêm chanh', '請幫我加辣椒': 'Cho tôi thêm ớt',
    '請幫我加魚露': 'Cho tôi thêm nước mắm', '請幫我加蔬菜': 'Cho tôi thêm rau',
    '請幫我加肉': 'Cho tôi thêm thịt', '請幫我加蛋': 'Cho tôi thêm trứng',
    '請問哪一道最受歡迎': 'Món nào được gọi nhiều nhất?', '有沒有推薦的飲料': 'Có đồ uống nào được gợi ý không?',
    '我第一次吃越南料理': 'Đây là lần đầu tôi ăn món Việt', '可以介紹一下嗎': 'Bạn có thể giới thiệu không?',
    '我要結帳': 'Tôi muốn thanh toán', '可以用行動支付嗎': 'Có thể thanh toán điện tử không?',
    '我已經下單了': 'Tôi đã đặt món', '我的訂單好了嗎': 'Đơn của tôi xong chưa?',
    '請問可以取消嗎': 'Có thể hủy không?', '我晚一點來拿': 'Tôi sẽ đến lấy sau',
    '麻煩你了': 'Làm phiền bạn', '真的很謝謝': 'Cảm ơn rất nhiều', '下次見': 'Hẹn gặp lại',
    '請慢用': 'Chúc ngon miệng', '祝你用餐愉快': 'Chúc bạn ăn ngon miệng',
    '越南家庭料理': 'Ẩm thực gia đình Việt Nam', '街頭小吃': 'Ẩm thực đường phố',
    '早市': 'Chợ sáng', '咖啡店': 'Quán cà phê', '餐廳': 'Nhà hàng', '小吃店': 'Quán ăn',
    '老闆': 'Chủ quán', '服務生': 'Nhân viên phục vụ', '廚師': 'Đầu bếp', '顧客': 'Khách hàng'
  });
  Object.assign(viToZh, {
    'cá tra': '鯰魚', 'cá thu': '鯖魚', 'cá cơm': '鯷魚', 'cá chép': '鯉魚', 'cá hồi': '鮭魚',
    'cá điêu hồng': '鯛魚', 'cá rô phi': '吳郭魚', 'tôm bóc vỏ': '蝦仁', 'tôm sú': '大蝦',
    'cua': '螃蟹', 'sò điệp': '扇貝', 'vẹm': '淡菜', 'bạch tuộc': '章魚', 'rong biển': '海帶',
    'bít tết bò': '牛排', 'sườn bò': '牛小排', 'bắp bò': '牛腱', 'thịt bò lát': '牛肉片',
    'thịt xông khói': '培根', 'xúc xích': '香腸', 'thịt gà xay': '雞絞肉', 'da gà': '雞皮',
    'bông cải xanh': '青花菜', 'súp lơ trắng': '白花椰菜', 'cải ngọt': '油菜', 'rau dền': '莧菜',
    'măng tây': '蘆筍', 'đậu ngự': '皇帝豆', 'đậu đen': '黑豆', 'tàu hũ ky': '豆皮／腐竹',
    'đậu hũ non': '嫩豆腐', 'đậu hũ chiên': '豆腐泡', 'nấm hầu thủ': '猴頭菇', 'nấm shimeji': '鴻喜菇',
    'ổi': '芭樂', 'đu đủ': '木瓜', 'thanh long': '火龍果', 'măng cụt': '山竹', 'sầu riêng': '榴槤',
    'chôm chôm': '紅毛丹', 'bưởi': '柚子', 'quýt': '橘子', 'cam': '柳橙', 'nho': '葡萄',
    'lá dứa': '斑蘭葉', 'hoa hồi': '八角', 'quế': '肉桂', 'đinh hương': '丁香', 'hạt điều': '腰果',
    'mè': '芝麻', 'mè trắng': '白芝麻', 'mè đen': '黑芝麻', 'gia vị': '調味料', 'gia vị ướp': '醃料',
    'nóng': '熱的', 'lạnh': '冰的', 'ấm': '溫的', 'tươi': '新鮮', 'giòn': '酥脆', 'mềm': '軟嫩',
    'đậm đà': '濃郁', 'thanh mát': '清爽', 'mặn': '鹹', 'ngọt': '甜', 'chua': '酸', 'đắng': '苦',
    'luộc': '煮', 'trụng': '燙', 'hấp': '蒸', 'xào': '炒', 'chiên giòn': '炸', 'nướng': '烤', 'kho': '滷', 'hầm': '燉',
    'thái lát': '切片', 'thái sợi': '切絲', 'cắt hạt lựu': '切丁', 'băm nhỏ': '剁碎',
    'phần lớn': '大份', 'phần nhỏ': '小份', 'gọi món lẻ': '單點', 'món chay': '素食', 'thuần chay': '全素',
    'chất gây dị ứng': '過敏原', 'không gluten': '不含麩質', 'một tô phở': '一碗河粉',
    'món này có cay không': '這個有辣嗎', 'có thể làm không cay không': '可以做不辣嗎',
    'cho ít đá': '少冰', 'cho ít đường': '少糖', 'cho tôi thêm chanh': '請幫我加檸檬',
    'cho tôi thêm ớt': '請幫我加辣椒', 'cho tôi thêm nước mắm': '請幫我加魚露',
    'cho tôi thêm rau': '請幫我加蔬菜', 'cho tôi thêm thịt': '請幫我加肉', 'cho tôi thêm trứng': '請幫我加蛋',
    'món nào được gọi nhiều nhất': '哪一道最受歡迎', 'tôi muốn thanh toán': '我要結帳',
    'tôi đã đặt món': '我已經下單了', 'đơn của tôi xong chưa': '我的訂單好了嗎',
    'tôi sẽ đến lấy sau': '我晚一點來拿', 'làm phiền bạn': '麻煩你了', 'hẹn gặp lại': '下次見',
    'chúc ngon miệng': '請慢用', 'ẩm thực đường phố': '街頭小吃', 'quán cà phê': '咖啡店',
    'nhà hàng': '餐廳', 'quán ăn': '小吃店', 'chủ quán': '老闆', 'nhân viên phục vụ': '服務生',
    'đầu bếp': '廚師', 'khách hàng': '顧客'
  });
  const translate = async () => {
    const source = translationInput.value.trim();
    if (!source) { translationResult.textContent = '請先輸入要翻譯的文字。／Vui lòng nhập nội dung cần dịch.'; return; }
    translationResult.textContent = '正在翻譯…／Đang dịch…';
    const remoteTranslation = await askChatGPT(source, 'translate', direction.value);
    if (remoteTranslation) {
      translationResult.textContent = remoteTranslation;
      return;
    }
    const dictionary = direction.value === 'zh-vi' ? zhToVi : viToZh;
    const normalized = source.toLowerCase().replace(/[？?！!。,.]/g, '').trim();
    const exact = dictionary[normalized] || dictionary[source];
    if (exact) {
      translationResult.textContent = `翻譯結果／Kết quả dịch：\n${exact}`;
      return;
    }
    const matches = Object.entries(dictionary).filter(([term]) => normalized.includes(term)).map(([term, result]) => `${term} → ${result}`);
    if (matches.length) {
      translationResult.textContent = `相關翻譯／Bản dịch liên quan：\n${matches.join('\n')}`;
      return;
    }
    translationResult.textContent = direction.value === 'zh-vi'
      ? '內建詞庫已涵蓋大量美食、食材、點餐、付款、會員、服務、會話、旅遊與文化用語。請嘗試輸入較短的詞語，例如「加醬料另外放」、「椰奶」、「累積點數」或「農曆新年」。\nTừ điển tích hợp hỗ trợ nhiều từ về ẩm thực, gọi món, dịch vụ, hội thoại, du lịch và văn hóa Việt Nam.'
      : '內建詞庫已可辨識大量越南美食、點餐、服務、會話、旅遊與文化用語。請嘗試輸入較短的越南詞語，例如「Phở」、「Cảm ơn」、「thêm rau」或「Tết Nguyên Đán」。\nTừ điển tích hợp nhận diện nhiều từ Việt Nam thông dụng.';
  };
  if (translateButton) translateButton.addEventListener('click', translate);
})();
