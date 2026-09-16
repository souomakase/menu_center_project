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
        # 1ファイル最大 1MB、3世代まで保持
        handler = RotatingFileHandler(
            log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # コンソール出力用
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

    # 5. HTMLコンテンツ
    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Menu Center Project</title>
    <style>
        body { font-family: sans-serif; background: #f4f6f9; padding: 40px; display: flex; justify-content: center; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; width: 100%; }
        h1 { color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 menu_center_project</h1>
        <p>共通スクリプトの仕様（ログ管理・タイムスタンプ保存）を適用して生成いたしました。</p>
    </div>
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