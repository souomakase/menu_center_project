from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from pathlib import Path


def get_google_drive_path() -> Path:
    """OSを自動判別してGoogleドライブ（マイドライブ）のパスを返します。"""
    home = Path.home()
    if sys.platform == "win32":
        g_drive = Path("G:/マイドライブ")
        if g_drive.exists():
            return g_drive
        user_drive = home / "Google Drive" / "My Drive"
        return user_drive if user_drive.exists() else g_drive
    elif sys.platform == "darwin":
        cloud_storage = home / "Library" / "CloudStorage"
        if cloud_storage.exists():
            gd_folders = list(cloud_storage.glob("GoogleDrive-*"))
            if gd_folders:
                my_drive = gd_folders[0] / "マイドライブ"
                return (
                    my_drive
                    if my_drive.exists()
                    else gd_folders[0] / "My Drive"
                )
        return home / "Google Drive"
    else:
        return home / "GoogleDrive"


def setup_logger(log_dir: Path) -> logging.Logger:
    """logsサブフォルダの作成と容量制限付きログ管理（RotatingFileHandler）を設定します。"""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger("MenuGenerator")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


def main():
    # 1. Google Driveベースパス取得
    drive_path = get_google_drive_path()

    # 2. 作業用フォルダ (create_menu_py) の自動作成
    work_dir = drive_path / "make_menu" / "center_left_type" / "create_menu_py"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 3. ログ機能の初期化
    logger = setup_logger(work_dir / "logs")
    logger.info("--- スクリプトの実行を開始いたしました ---")

    # 4. タイムスタンプ付与（YYYYMMDD_HHMMSS）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_filename = f"index_{timestamp}.html"

    save_path_timestamped = work_dir / timestamped_filename
    save_path_latest = work_dir / "index.html"

    # 5. HTMLコンテンツ（お嬢様ご指定のOMAKASE Generator）
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Centered & Left Aligned OMAKASE Menu Generator</title>
  <!-- Mammoth.js for Word (.docx) import -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.4.2/mammoth.browser.min.js"></script>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">

  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      display: flex;
      height: 100vh;
      font-family: sans-serif;
      background-color: #e5e5e5;
    }

    /* Left Control Panel */
    .controls {
      width: 400px;
      padding: 20px;
      background: #ffffff;
      box-shadow: 2px 0 10px rgba(0,0,0,0.08);
      overflow-y: auto;
    }
    .section {
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid #eaeaea;
    }
    h2 { font-size: 16px; margin-top: 0; color: #111; }
    h3 { font-size: 13px; margin: 10px 0 6px 0; color: #444; border-left: 3px solid #222; padding-left: 8px; }
    
    label {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      font-weight: 600;
      color: #555;
      margin-top: 8px;
      text-transform: uppercase;
    }
    input[type="text"], textarea, select {
      width: 100%;
      padding: 8px;
      margin-top: 4px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 13px;
    }
    textarea { height: 130px; resize: vertical; }
    input[type="range"] { width: 100%; margin-top: 4px; }
    
    .file-input-wrapper {
      margin-top: 6px;
      padding: 10px;
      background: #f8f9fa;
      border: 1px dashed #bbb;
      border-radius: 4px;
      text-align: center;
    }

    /* Alignment Switcher Buttons */
    .btn-group {
      display: flex;
      gap: 8px;
      margin-top: 8px;
    }
    .btn-group button {
      flex: 1;
      padding: 8px;
      border: 1px solid #222;
      background: #fff;
      color: #222;
      cursor: pointer;
      font-weight: 600;
      font-size: 12px;
      border-radius: 4px;
      transition: all 0.2s;
    }
    .btn-group button.active {
      background: #222;
      color: #fff;
    }

    /* Right Preview Panel */
    .preview-container {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 30px;
      overflow: auto;
    }

    .paper {
      width: 480px;
      height: 680px;
      background-color: #dcd3c4; /* Elegant greige */
      box-shadow: 0 8px 25px rgba(0,0,0,0.12);
      padding: 50px 45px;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      font-family: 'Montserrat', sans-serif;
      color: #1a1a1a;
      transition: all 0.3s;
    }

    /* Alignment Classes */
    .paper.align-center {
      align-items: center;
      text-align: center;
    }
    .paper.align-left {
      align-items: flex-start;
      text-align: left;
    }

    /* Title */
    .menu-title {
      font-weight: 600;
      font-size: 18px;
      letter-spacing: 3px;
      text-transform: uppercase;
      margin-bottom: 25px;
    }

    /* Course Items List */
    .course-list {
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .course-item {
      display: flex;
      flex-direction: column;
    }
    .paper.align-center .course-item { align-items: center; }
    .paper.align-left .course-item { align-items: flex-start; }

    .category-name {
      font-weight: 600;
      font-size: 14px;
      letter-spacing: 1.5px;
      margin-bottom: 3px;
    }

    .dish-description {
      font-weight: 400;
      font-size: 12px;
      color: #333;
      line-height: 1.35;
      max-width: 90%;
      letter-spacing: 0.5px;
    }
  </style>
</head>
<body>

  <!-- Controls Panel -->
  <div class="controls">
    <h2>Menu Generator Control</h2>

    <!-- Word Import -->
    <div class="section">
      <h3>1. Import Word File (.docx)</h3>
      <div class="file-input-wrapper">
        <input type="file" id="wordFile" accept=".docx" />
      </div>
    </div>

    <!-- Alignment & Style -->
    <div class="section">
      <h3>2. Alignment & Style</h3>
      <label>Text Alignment Option</label>
      <div class="btn-group">
        <button id="btnCenter" class="active">Centered</button>
        <button id="btnLeft">Left Aligned</button>
      </div>

      <label>Font Family</label>
      <select id="fontSelect">
        <option value="'Montserrat', sans-serif">Montserrat (Modern Clean)</option>
        <option value="'Cormorant Garamond', serif">Cormorant Garamond (Serif)</option>
        <option value="'Playfair Display', serif">Playfair Display (Elegant)</option>
      </select>

      <label>Background Color</label>
      <select id="bgSelect">
        <option value="#dcd3c4">Warm Greige</option>
        <option value="#f5f2eb">Off-White / Cream</option>
        <option value="#ffffff">Pure White</option>
      </select>
    </div>

    <!-- Title Settings -->
    <div class="section">
      <h3>3. Course Title</h3>
      <input type="text" id="inputTitle" value="SPECIAL OMAKASE COURSE">
      
      <label>Title Size <span id="titleSizeVal">18px</span></label>
      <input type="range" id="titleSize" min="14" max="28" value="18">

      <label>Title Spacing <span id="titleSpaceVal">3px</span></label>
      <input type="range" id="titleSpace" min="0" max="10" value="3">
    </div>

    <!-- Content Settings -->
    <div class="section">
      <h3>4. Menu Items</h3>
      <p style="font-size: 11px; color: #777; margin: 2px 0 6px 0;">Format: Category | Description</p>
      <textarea id="inputMenu">Starter | A delicate tofu skin topped with succulent sea urchin
Appetizer | Cod fish milt in Butteryaki, Hotaru Ika and braised sea snail
Seasonal Soup | Fresh Wakame, Bamboo shoot, Cheese Tofu and Sword Fish
Tempura | Sharksfin, Japanese Pond smelt, Asparagus
Sashimi Moriawase | Chef selection of Mix Sashimi
Palate Refresher | Silken Foie Gras Flan
King Crab | King Crab on a Lava stone topped with velveted egg white
Main Dish | Beef Steak, Lamb Miso or Grilled Cod Fish
Sushi | Sushi served with Lobster soup
Dessert | A sweet finale on your Omakase journey</textarea>
    </div>

    <!-- Typography Fine Tuning -->
    <div class="section">
      <h3>5. Spacing & Size</h3>
      <label>Vertical Item Gap <span id="gapVal">16px</span></label>
      <input type="range" id="gapRange" min="8" max="32" value="16">

      <label>Category Size <span id="catSizeVal">14px</span></label>
      <input type="range" id="catSize" min="10" max="20" value="14">

      <label>Description Size <span id="descSizeVal">12px</span></label>
      <input type="range" id="descSize" min="8" max="18" value="12">

      <label>Letter Spacing <span id="descSpaceVal">0.5px</span></label>
      <input type="range" id="descSpace" min="-0.5" max="4" step="0.5" value="0.5">
    </div>
  </div>

  <!-- Preview Panel -->
  <div class="preview-container">
    <div class="paper align-center" id="paper">
      <div class="menu-title" id="previewTitle">SPECIAL OMAKASE COURSE</div>
      <div class="course-list" id="courseList"></div>
    </div>
  </div>

  <script>
    const paper = document.getElementById('paper');
    const btnCenter = document.getElementById('btnCenter');
    const btnLeft = document.getElementById('btnLeft');
    const fontSelect = document.getElementById('fontSelect');
    const bgSelect = document.getElementById('bgSelect');

    const gapRange = document.getElementById('gapRange');
    const courseList = document.getElementById('courseList');

    const inputTitle = document.getElementById('inputTitle');
    const titleSize = document.getElementById('titleSize');
    const titleSpace = document.getElementById('titleSpace');
    const previewTitle = document.getElementById('previewTitle');

    const inputMenu = document.getElementById('inputMenu');
    const catSize = document.getElementById('catSize');
    const descSize = document.getElementById('descSize');
    const descSpace = document.getElementById('descSpace');

    // Alignment Switcher
    btnCenter.addEventListener('click', () => {
      btnCenter.classList.add('active');
      btnLeft.classList.remove('active');
      paper.className = 'paper align-center';
    });
    btnLeft.addEventListener('click', () => {
      btnLeft.classList.add('active');
      btnCenter.classList.remove('active');
      paper.className = 'paper align-left';
    });

    // Styles
    fontSelect.addEventListener('change', () => paper.style.fontFamily = fontSelect.value);
    bgSelect.addEventListener('change', () => paper.style.backgroundColor = bgSelect.value);

    gapRange.addEventListener('input', (e) => {
      courseList.style.gap = e.target.value + 'px';
      document.getElementById('gapVal').textContent = e.target.value + 'px';
    });

    inputTitle.addEventListener('input', () => previewTitle.textContent = inputTitle.value);
    titleSize.addEventListener('input', (e) => {
      previewTitle.style.fontSize = e.target.value + 'px';
      document.getElementById('titleSizeVal').textContent = e.target.value + 'px';
    });
    titleSpace.addEventListener('input', (e) => {
      previewTitle.style.letterSpacing = e.target.value + 'px';
      document.getElementById('titleSpaceVal').textContent = e.target.value + 'px';
    });

    // Render Menu
    function renderMenu() {
      const lines = inputMenu.value.split('\\n').filter(line => line.trim() !== '');
      courseList.innerHTML = '';

      lines.forEach(line => {
        const parts = line.split('|');
        const category = parts[0] ? parts[0].trim() : '';
        const description = parts[1] ? parts[1].trim() : '';

        const itemDiv = document.createElement('div');
        itemDiv.className = 'course-item';

        const catDiv = document.createElement('div');
        catDiv.className = 'category-name';
        catDiv.textContent = category;
        catDiv.style.fontSize = catSize.value + 'px';

        const descDiv = document.createElement('div');
        descDiv.className = 'dish-description';
        descDiv.textContent = description;
        descDiv.style.fontSize = descSize.value + 'px';
        descDiv.style.letterSpacing = descSpace.value + 'px';

        itemDiv.appendChild(catDiv);
        if (description) itemDiv.appendChild(descDiv);

        courseList.appendChild(itemDiv);
      });
    }

    inputMenu.addEventListener('input', renderMenu);
    catSize.addEventListener('input', (e) => {
      document.getElementById('catSizeVal').textContent = e.target.value + 'px';
      renderMenu();
    });
    descSize.addEventListener('input', (e) => {
      document.getElementById('descSizeVal').textContent = e.target.value + 'px';
      renderMenu();
    });
    descSpace.addEventListener('input', (e) => {
      document.getElementById('descSpaceVal').textContent = e.target.value + 'px';
      renderMenu();
    });

    // Word FileReader
    document.getElementById('wordFile').addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = function(event) {
        mammoth.extractRawText({ arrayBuffer: event.target.result })
          .then(function(result) {
            const lines = result.value.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            let output = [];
            for (let i = 0; i < lines.length; i++) {
              if (lines[i].includes('|')) {
                output.push(lines[i]);
              } else if (i + 1 < lines.length && lines[i].length < 30 && lines[i+1].length >= 30) {
                output.push(`${lines[i]} | ${lines[i+1]}`);
                i++;
              } else {
                output.push(lines[i]);
              }
            }
            inputMenu.value = output.join('\\n');
            renderMenu();
          });
      };
      reader.readAsArrayBuffer(file);
    });

    renderMenu();
  </script>
</body>
</html>
"""

    # 6. 書き込み処理
    try:
        # タイムスタンプ付き保存
        with open(save_path_timestamped, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(
            f"タイムスタンプ付きHTMLを出力いたしました: {save_path_timestamped.name}"
        )

        # 最新版 (index.html) の保存
        with open(save_path_latest, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"最新版HTMLを出力いたしました: {save_path_latest.name}")

    except Exception as e:
        logger.error(f"ファイル出力中にエラーが発生いたしました: {e}")

    logger.info("--- スクリプトの実行が正常に完了いたしました ---")


if __name__ == "__main__":
    main()
