import pandas as pd
import folium
from PIL import Image, ImageDraw, ImageFont 
import os
import base64
from io import BytesIO
import json
import logging
import webview

# logging設定: UTF-8エンコーディングを指定し、エラーを捕捉
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', encoding='utf-8')

# --- 0. データ定義 (既存データ + 追加データ) ---

# 既存データ
EXISTING_DATA = {
    'name': [
        'ハローズ 御幸店', 'ハローズ 神辺モール店', 'ハローズ 南駅家店', 'エブリイ 駅家店',
        'エブリイ 緑町店', 'ハローズ 緑町店', 'フレスタ アイネス店', 'フジ 福山三吉店',
        'ハローズ 山手店', 'フレスタ 蔵王店', 'ラ・ムー 駅家店', 'ハローズ 伊勢丘店',
        'ハローズ 新涯店'
    ],
    'lat': [
        34.547245, 34.542857, 34.544033, 34.538313,
        34.477490, 34.476470, 34.487743, 34.493521,
        34.492559, 34.498787, 34.542412,
        34.502842,
        34.461328
    ],
    'lon': [
        133.347939, 133.363893, 133.330316, 133.331962,
        133.372590, 133.371601, 133.362712, 133.375035,
        133.333259, 133.392526, 133.326149,
        133.422737,
        133.392132
    ],
    'logo_file': [
        'logo_ハローズ.png', 'logo_ハローズ.png', 'logo_ハローズ.png', 'logo_エブリイ.png',
        'logo_エブリイ.png', 'logo_ハローズ.png', 'logo_フレスタ.png', 'logo_フジ.png',
        'logo_ハローズ.png', 'logo_フレスタ.png', 'logo_ラ・ムー.png', 'logo_ハローズ.png',
        'logo_ハローズ.png'
    ],
    'website': [
        'https://www.halows.com/', 'https://www.halows.com/', 'https://www.halows.com/', 'https://www.super-every.co.jp/',
        'https://www.super-every.co.jp/', 'https://www.halows.com/', 'https://www.fresta.co.jp/', 'https://www.the-fuji.com/',
        'https://www.halows.com/', 'https://www.fresta.co.jp/', 'https://www.e-dkt.co.jp/',
        'https://www.halows.com/',
        'https://www.halows.com/'
    ],
    'souzai_info': [
        'ハローズ: 本日の目玉は鶏の唐揚げ！', 'ハローズ: 出来立てのお好み焼きがあります！', 'ハローズ: 特製カツ丼がおすすめ！',
        'エブリイ: 地元の人気弁当が豊富です。', 'エブリイ: サラダ・デリが充実！', 'ハローズ: 特製オムライスが20%OFF！',
        'フレスタ: 自社製パンが人気です。', 'フジ: 手作りおにぎりコーナー！', 'ハローズ: ローストビーフ丼が数量限定！',
        'フレスタ: 季節のパスタフェア開催中！', 'ラ・ムー: 驚きの100円たこ焼き！', 'ハローズ: 本日の目玉は鶏の唐揚げ！',
        'ハローズ: 特製オムライスが20%OFF！'
    ],
    'sengyo_info': [
        'ハローズ: 瀬戸内産の新鮮な鯛が入荷！', 'ハローズ: お刺身盛り合わせがお得！', 'ハローズ: 週末限定マグロの解体！',
        'エブリイ: 干物が充実しています。', 'エブリイ: 本日のアジの開きがおすすめ！', 'ハローズ: マグロの刺身が半額！',
        'フレスタ: 鮮魚コーナーに産直品！', 'フジ: 新鮮なカツオのたたき！', 'ハローズ: 瀬戸内産の新鮮な鯛が入荷！',
        'フレスタ: 新鮮なブリが入荷！', 'ラ・ムー: 激安の冷凍魚介！', 'ハローズ: マグロの刺身が半額！',
        'ハローズ: 瀬戸内産の新鮮な鯛が入荷！'
    ],
    'niku_info': [
        'ハローズ: 黒毛和牛の特売セール！', 'ハローズ: 豚肉のこま切れがグラム98円！', 'ハローズ: BBQ用のお肉セット充実！',
        'エブリイ: 地元産「もみじ鶏」のフェア！', 'エブリイ: 牛すじ肉で煮込み料理はいかが？', 'ハローズ: 国産豚バラブロック半額！',
        'フレスタ: 熟成肉コーナーが自慢です。', 'フジ: 鶏むね肉まとめ買いでお得！', 'ハローズ: 黒毛和牛の特売セール！',
        'フレスタ: 特選ソーセージ・ハムが充実！', 'ラ・ムー: 鶏肉の激安パック！', 'ハローズ: 国産豚バラブロック半額！',
        'ハローズ: 黒毛和牛の特売セール！'
    ],
    'seika_info': [
        'ハローズ: 旬の地元産イチゴが入荷！', 'ハローズ: 新鮮な春キャベツがお買い得！', 'ハローズ: 広島県産レモン大特価！',
        'エブリイ: 地元農家直送の新鮮野菜！', 'エブリイ: 新玉ねぎの詰め放題を実施中！', 'ハローズ: 契約農家のトマトがお買い得！',
        'フレスタ: オーガニック野菜コーナー！', 'フジ: 大粒ぶどうの試食会開催！', 'ハローズ: 旬の地元産イチゴが入荷！',
        'フレスタ: 珍しい輸入野菜も！', 'ラ・ムー: 激安の袋入りもやし！', 'ハローズ: 契約農家のトマトがお買い得！',
        'ハローズ: 新鮮な春キャベツがお買い得！'
    ],
    'brand': [
        'ハローズ', 'ハローズ', 'ハローズ', 'エブリイ',
        'エブリイ', 'ハローズ', 'フレスタ', 'フジ',
        'ハローズ', 'フレスタ', 'ラ・ムー', 'ハローズ',
        'ハローズ'
    ]
}

# 追加データ
NEW_DATA = {
    'name': [
        'ハローズ 神辺店', 'ハローズ 戸手店', 'ハローズ 春日店', 'ハローズ 引野店', 'ハローズ 東福山店',
        'ハローズ 手城店', 'ハローズ 水呑店', 'ハローズ 南松永店', 'ハローズ 沼南店',
        'エブリイ 松永店', 'エブリイ瀬戸店', 'エブリイ御幸店', 'エブリイ神辺店', 'エブリイ本庄店',
        'エブリイ蔵王店', 'エブリイ川口店', 'エブリイ伊勢丘店',
        'フレスタ 福山三吉店', 'フレスタ 北吉津店', 'フレスタ 草戸店', 'フレスタ 多治米店',
        '業務スーパー新市店', 'ラ・ムー 松永店', 'ラ・ムー 手城店', 'ディオ 福山南店',
        'フジグラン神辺 食品館', 'オンリーワン 駅家店', 'オンリーワン 千田店', 'オンリーワン 旭ヶ丘店',
        'オンリーワン 木之庄店', 'オンリーワン 山手店', 'オンリーワン 瀬戸店',
        'ゆめタウン 蔵王', 'ゆめタウン福山', 'ザ・ビッグ 神辺店', 'ザ・ビッグ大門店',
        'ミスターマックス新神辺店',
        'なかやま牧場 ハート新徳田店', 'なかやま牧場 ハート加茂店', 'なかやま牧場［ﾊｰﾄ坪生店］', 'なかやま牧場 引野店',
        'なかやま牧場 ハート木之庄店', 'なかやま牧場 ハート新涯店',
        'マルナカ 加茂店', 'Ａ−プライス 福山店',
        'ニチエー 柳津店', 'ニチエー さんらいず店', 'ニチエー 瀬戸店', 'ニチエー 沼南店',
        '生鮮食品 おだ 春日店'
    ],
    'lat': [
        34.549238, 34.549010, 34.511183, 34.500121, 34.490001,
        34.484085, 34.446823, 34.443160, 34.387728,
        34.442332, 34.475457, 34.540975, 34.547862, 34.486838,
        34.503659, 34.468972, 34.504264,
        34.495523, 34.497068, 34.478892, 34.468429,
        34.545228, 34.446731, 34.483819, 34.465147,
        34.545245, 34.549297, 34.518545, 34.492134,
        34.496204, 34.494895, 34.471791,
        34.504926, 34.487064, 34.557168, 34.494797,
        34.540661,
        34.548747, 34.568176, 34.527446, 34.496260,
        34.498596, 34.454583,
        34.560882, 34.494565,
        34.439995, 34.453543, 34.473304, 34.386952,
        34.510628
    ],
    'lon': [
        133.377984, 133.283165, 133.415063, 133.406021, 133.410593,
        133.392729, 133.386847, 133.254940, 133.323727,
        133.251304, 133.317128, 133.348727, 133.382452, 133.350845,
        133.394152, 133.383982, 133.423391,
        133.378392, 133.365369, 133.360637, 133.370928,
        133.293464, 133.243272, 133.398270, 133.383363,
        133.357068, 133.326900, 133.365520, 133.422231,
        133.353517, 133.337047, 133.314893,
        133.400447, 133.378583, 133.389616, 133.438232,
        133.362873,
        133.371937, 133.346001, 133.439373, 133.400904,
        133.354959, 133.393429,
        133.347027, 133.397965,
        133.263470, 133.256207, 133.314423, 133.324780,
        133.413331
    ],
    'brand': [
        'ハローズ', 'ハローズ', 'ハローズ', 'ハローズ', 'ハローズ',
        'ハローズ', 'ハローズ', 'ハローズ', 'ハローズ',
        'エブリイ', 'エブリイ', 'エブリイ', 'エブリイ', 'エブリイ',
        'エブリイ', 'エブリイ', 'エブリイ',
        'フレスタ', 'フレスタ', 'フレスタ', 'フレスタ',
        '業務スーパー', 'ラ・ムー', 'ラ・ムー', 'ディオ',
        'フジ', 'オンリーワン', 'オンリーワン', 'オンリーワン',
        'オンリーワン', 'オンリーワン', 'オンリーワン',
        'ゆめタウン', 'ゆめタウン', 'ザ・ビッグ', 'ザ・ビッグ',
        'ミスターマックス',
        'なかやま牧場', 'なかやま牧場', 'なかやま牧場', 'なかやま牧場',
        'なかやま牧場', 'なかやま牧場',
        'マルナカ', 'Ａ−プライス',
        'ニチエー', 'ニチエー', 'ニチエー', 'ニチエー',
        '生鮮食品 おだ'
    ]
}

# 追加データにロゴファイルと情報を補完
def fill_info(brand, data_key):
    existing_brand_indices = [i for i, b in enumerate(EXISTING_DATA['brand']) if b == brand]
    safe_brand_name = brand.lower().replace(' ', '').replace('［', '').replace('］', '').replace('−', '')
    
    if data_key == 'logo_file':
        if existing_brand_indices:
            return EXISTING_DATA['logo_file'][existing_brand_indices[0]]
        else:
            return f"logo_{safe_brand_name}.png"
            
    elif data_key == 'website':
        return 'https://fukuyama-super-info.com/' 
    elif existing_brand_indices:
        return EXISTING_DATA[data_key][existing_brand_indices[0]]
    else:
        return f'{brand}: 本日の特売情報は店頭にて！ (ダミー情報)'

for data_key in ['logo_file', 'website', 'souzai_info', 'sengyo_info', 'niku_info', 'seika_info']:
    NEW_DATA[data_key] = [
        fill_info(brand, data_key) for brand in NEW_DATA['brand']
    ]

# データの結合
df = pd.concat([pd.DataFrame(EXISTING_DATA), pd.DataFrame(NEW_DATA)], ignore_index=True)


# --- 1. 設定と画像合成用フォルダの準備 ---
LOGO_FOLDER = 'logos'
PIN_BASE_IMAGE = 'pin_base.png'

os.makedirs(LOGO_FOLDER, exist_ok=True)

# PIN_COLORSを全ブランドに対応させるために更新
PIN_COLORS = {
    'ハローズ': '#FBC02D', 'エブリイ': '#00BCD4', 'フレスタ': '#673AB7',
    'フジ': '#9C27B0', 'ラ・ムー': '#E91E63',
    '業務スーパー': '#388E3C', 'ディオ': '#2196F3', 'オンリーワン': '#FF9800',
    'ゆめタウン': '#E53935', 'ザ・ビッグ': '#8D6E63', 'ミスターマックス': '#546E7A',
    'なかやま牧場': '#795548', 'マルナカ': '#4CAF50', 'Ａ−プライス': '#00BFA5',
    'ニチエー': '#D32F2F', '生鮮食品 おだ': '#FF5722',
}

# --- 1-1. PIN_BASE_IMAGE が存在しない場合の代替作成 ---
if not os.path.exists(PIN_BASE_IMAGE):
    logging.info(f"'{PIN_BASE_IMAGE}' が見つかりませんでした。代替ピンベース画像を生成します。")
    img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse((0, 0, 99, 99), fill='#CCCCCC')
    img.save(PIN_BASE_IMAGE)

# --- 1-2. ロゴファイルが存在しない場合の代替作成 (ブランド名頭文字入り) ---
def create_placeholder_logo(brand_name, size=(60, 60)):
    """ブランド名の頭文字を中央に配置した代替ロゴ画像を生成"""
    
    logo_filename = df[df['brand'] == brand_name]['logo_file'].iloc[0]
    logo_path = os.path.join(LOGO_FOLDER, logo_filename)
    
    if os.path.exists(logo_path):
        return

    try:
        logging.warning(f"ロゴファイル '{logo_filename}' が見つかりませんでした。代替画像を生成します。")

        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        pin_color = PIN_COLORS.get(brand_name, '#CCCCCC')
        draw.ellipse((0, 0, size[0], size[1]), fill=pin_color)
        
        initial = brand_name[0]
        
        font = ImageFont.load_default() 
        try:
            font_path = "C:/Windows/Fonts/meiryo.ttc" if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font = ImageFont.truetype(font_path, 30)
        except Exception:
            pass
        
        fill_color = "#FFFFFF"
        
        if hasattr(draw, 'textbbox'):
            text_bbox = draw.textbbox((0, 0), initial, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            draw.text((x, y), initial, font=font, fill=fill_color)
        else:
            draw.text((size[0]//4, size[1]//4), initial, fill=fill_color, font=font)


        img.save(logo_path)
    except Exception as e:
        logging.error(f"代替ロゴファイルの生成に失敗しました (ブランド: {brand_name}): {e}")

for brand in df['brand'].unique():
    create_placeholder_logo(brand)


# --- 2. 画像合成関数 ---
def create_logo_pin_base64(logo_path, pin_base_path, pin_color='#CCCCCC', logo_size=(60, 60)):
    try:
        pin_base = Image.open(pin_base_path).convert("RGBA").resize((100, 100), Image.LANCZOS)
        logo_img = Image.open(logo_path).convert("RGBA").resize(logo_size, Image.LANCZOS)

        colored_background = Image.new('RGBA', pin_base.size, pin_color)
        pin_mask = pin_base.split()[-1]
        colored_pin_shape = Image.new('RGBA', pin_base.size, (0,0,0,0))
        colored_pin_shape.paste(colored_background, (0,0), pin_mask)

        x_offset = (colored_pin_shape.width - logo_img.width) // 2
        y_offset = (colored_pin_shape.height - logo_img.height) // 2 - 10
        final_pin = colored_pin_shape.copy()
        final_pin.paste(logo_img, (x_offset, y_offset), logo_img)

        buffered = BytesIO()
        final_pin.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        logging.error(f"ピン画像合成中にエラーが発生しました: {e}. 単色ピンを使用します。")
        try:
            img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
            ImageDraw.Draw(img).ellipse((0, 0, 99, 99), fill=pin_color)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e_fallback:
            logging.error(f"単色ピン生成に失敗しました: {e_fallback}")
            return None

# --- 3. 各店舗のピン画像を生成し、Base64として辞書に格納 ---
generated_pin_base64 = {}
for index, row in df.iterrows():
    logo_path = os.path.join(LOGO_FOLDER, row['logo_file'])
    pin_color = PIN_COLORS.get(row['brand'], '#CCCCCC')
    b64_image = create_logo_pin_base64(logo_path, PIN_BASE_IMAGE, pin_color)
    if b64_image:
        generated_pin_base64[index] = f"data:image/png;base64,{b64_image}"


# --- 4. Foliumマップの作成とマーカーの追加 ---
FUKUYAMA_CENTER = [34.50, 133.37]
map_name = "m_temp"
# 地図をクリック可能にするために、folium.Mapのデフォルトのフォールバックレイヤーを設定
m_temp = folium.Map(location=FUKUYAMA_CENTER, zoom_start=12, name=map_name)
marker_data_for_js = []

for index, row in df.iterrows():
    pin_image_base64 = generated_pin_base64.get(index)

    logo_base64_for_popup = generated_pin_base64.get(index, "").replace("data:image/png;base64,", "")
            
    popup_html = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 250px;">
        <h4 style="margin: 0 0 8px 0; color: #333; border-bottom: 2px solid {PIN_COLORS.get(row['brand'], '#ccc')}; padding-bottom: 5px;">
            <img src='data:image/png;base64,{logo_base64_for_popup}' alt='{row['brand']}ロゴ' style='height: 20px; vertical-align: middle; margin-right: 5px; background-color: {PIN_COLORS.get(row['brand'], '#ccc')}; border-radius: 5px;'>
            {row['name']}
        </h4>
        <p style="margin: 5px 0;"><a href="{row['website']}" target="_blank" style="color: #007bff; text-decoration: none;"><i class="fas fa-globe"></i> 公式ウェブサイト</a></p>
        <hr style="margin: 10px 0; border-top: 1px solid #eee;">

        <button onclick="showComparisonPanel('{row['name']}')" style="margin-top: 5px; padding: 8px 10px; background-color: #ffc107; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; color: #333; transition: background-color 0.2s;">
            <i class="fas fa-search"></i> 本日の特売を見る
        </button>

        <div onclick="alert('この機能はまだ作動しません。');" style="margin-top: 10px; text-align: center; font-size: 0.9em; color: #007bff; cursor: pointer; padding: 5px 0; border-top: 1px solid #eee;">
            詳細はこちら <i class="fas fa-chevron-right" style="font-size: 0.7em;"></i>
        </div>
    </div>
    """

    if pin_image_base64:
        icon = folium.CustomIcon(icon_image=pin_image_base64, icon_size=(40, 40), icon_anchor=(20, 40))
    else:
        icon = folium.Icon(color='gray', icon='info-sign')

    marker = folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(popup_html, max_width=300),
        icon=icon,
        tooltip=row['name']
    ).add_to(m_temp)

    marker.add_child(folium.Element(f"<div id='marker-{index}' data-brand='{row['brand']}' class='custom-marker-info'></div>"))

    marker_data_for_js.append({
        'id': f'marker-{index}',
        'name': row['name'],
        'brand': row['brand'],
        'souzai': row['souzai_info'],
        'sengyo': row['sengyo_info'],
        'niku': row['niku_info'],
        'seika': row['seika_info'],
        'layer_id': marker._id,
        'lat': row['lat'],
        'lon': row['lon'],
        'distance': 0
    })

marker_data_json = json.dumps(marker_data_for_js)
pin_colors_json = json.dumps(PIN_COLORS)
fukuyama_center_json = json.dumps(FUKUYAMA_CENTER)


# 5. UI要素の定義とJavaScriptによる動的機能の追加 (Raw String f-stringを使用)
app_ui_elements = rf"""
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<style>
    /* --- CSSスタイル --- */

    /* ホーム画面/ローディング画面の強化 */
    #loading-mask {{
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); /* グラデーション背景 */
        color: white; display: flex; justify-content: center; align-items: center;
        flex-direction: column; z-index: 1000000; font-family: 'Segoe UI', Arial, sans-serif;
        animation: fadeIn 0.5s ease-in-out;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    #loading-title {{ 
        font-size: 3.5em; 
        margin-bottom: 5px; 
        font-weight: 800; 
        color: #fff; 
        text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        animation: pulse 1.5s infinite;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    #loading-subtitle {{ 
        font-size: 1.2em; 
        margin-bottom: 40px; 
        color: #C8E6C9; 
        font-weight: 300; 
    }}
    #start-button {{ 
        padding: 18px 40px; 
        font-size: 1.4em; 
        font-weight: bold; 
        border: none; 
        border-radius: 30px; 
        background-color: #FFC107; /* マップカラーに合わせて明るく */
        color: #333; 
        cursor: pointer; 
        box-shadow: 0 6px 15px rgba(0,0,0,0.3); 
        transition: background-color 0.2s, transform 0.1s; 
    }}
    #start-button:hover {{ 
        background-color: #FFD54F; 
        transform: translateY(-3px); 
    }}
    /* --- その他のUIスタイル (変更なし) --- */

    body {{ margin: 0; overflow: hidden; }}
    #map_{map_name} {{ position: absolute; top: 0; bottom: 0; right: 0; left: 0; z-index: 1; }}

    #sidebar {{ position: fixed; top: 0; right: 0; width: 280px; height: 100%; background-color: #fff; z-index: 100000; padding: 20px; transform: translateX(100%); transition: transform 0.3s ease-out; box-shadow: -2px 0 10px rgba(0,0,0,0.3); font-family: 'Segoe UI', Arial, sans-serif; display: flex; flex-direction: column; overflow-y: auto; }}
    #sidebar.open {{ transform: translateX(0); }}
    #sidebar h2 {{ color: #333; border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }}
    #sidebar h2 .close-btn {{ background: none; border: none; font-size: 1.5em; cursor: pointer; color: #aaa; padding: 0; line-height: 1; }}
    .sidebar-item {{ display: flex; align-items: center; padding: 12px 10px; text-decoration: none; color: #333; border-bottom: 1px solid #eee; transition: background-color 0.2s; cursor: pointer; }}
    #sidebar hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
    #sidebar h3 {{ color: #555; margin-top: 30px; margin-bottom: 15px; font-size: 1.1em; }}
    .filter-item {{ display: flex; align-items: center; justify-content: space-between; padding: 10px 10px; border-bottom: 1px solid #eee; cursor: pointer; user-select: none; }}
    .filter-item:hover {{ background-color: #f0f0f0; }}

    #hamburger {{ position: fixed; top: 20px; right: 20px; z-index: 100001; cursor: pointer; width: 30px; height: 30px; background-color: #fff; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); display: flex; flex-direction: column; justify-content: space-around; padding: 5px; transition: transform 0.3s ease-out; }}
    #sidebar.open ~ #hamburger {{ display: none; }}
    .bar {{ width: 100%; height: 3px; background-color: #333; transition: 0.4s; }}

    #locate-button {{
        position: fixed; bottom: 20px; left: 20px;
        z-index: 100005; 
        background-color: #FF9800; /* オレンジに変更 */
        color: white; border: none; width: 50px; height: 50px; border-radius: 50%; font-size: 1.5em; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); cursor: pointer; transition: background-color 0.2s, transform 0.2s;
    }}
    #details-button {{ position: fixed; bottom: 20px; right: 20px; z-index: 99999; background-color: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 5px; font-size: 1em; font-weight: bold; box-shadow: 0 4px 8px rgba(0,0,0,0.2); cursor: pointer; transition: background-color 0.2s, transform 0.2s; }}

    #details-panel {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); z-index: 100002; display: none; justify-content: center; align-items: center; font-family: 'Segoe UI', Arial, sans-serif; }}
    #details-content {{ background-color: #fff; border-radius: 8px; width: 95%; max-width: 600px; height: 70%; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow-y: auto;}}
    #details-content h2 .close-btn-panel {{ background: none; border: none; font-size: 1.5em; cursor: pointer; color: #aaa; padding: 0; line-height: 1; }}

    /* リスト項目 (小型化済) */
    #super-list li {{ padding: 10px; margin-bottom: 8px; background-color: #fff; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); cursor: pointer; display: flex; align-items: center; justify-content: space-between; border-left: 5px solid #007bff; }}
    #super-list li:hover {{ background-color: #f5f5f5; transform: translateY(-1px); }}

    #super-list li .info-block {{ flex-grow: 1; margin-left: 10px; }}
    #super-list li .store-name {{ font-weight: bold; font-size: 1.0em; color: #333; display: block; }}
    #super-list li .brand-name {{ font-size: 0.75em; color: #888; display: block; margin-top: 2px; }}

    #super-list li img {{ height: 25px; width: 25px; object-fit: contain; flex-shrink: 0; }}

    #super-list li .distance-info {{ font-size: 1.0em; font-weight: bold; color: #E91E63; white-space: nowrap; }}

    /* 地図上の情報オーバーレイ */
    #map-info {{
        position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
        background: rgba(255, 255, 255, 0.9); padding: 8px 15px; border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15); z-index: 100000; font-size: 0.9em;
        text-align: center; color: #333; font-weight: 600; max-width: 90%;
    }}

    /* 比較パネルのスタイル */
    #comparison-panel {{
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.8); z-index: 100006;
        display: none; justify-content: center; align-items: center;
    }}
    #comparison-content {{
        background-color: #fff; border-radius: 8px; width: 90%; max-width: 450px;
        padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }}
    .comparison-item {{
        padding: 8px 0; border-bottom: 1px dotted #ddd;
    }}
    .comparison-item:last-child {{ border-bottom: none; }}
</style>

<div id="loading-mask">
    <div id="loading-title"><i class="fas fa-map-marked-alt"></i> SMAP - Supermarket Map App</div>
    <div id="loading-subtitle">福山市内の全店舗の特売情報と、最寄り店舗をすぐに検索！ (全{df.shape[0]}店舗)</div>
    <button id="start-button" onclick="startApp()"><i class="fas fa-play-circle"></i> マップを起動する</button>
</div>

<div id="map-info">
    <i class="fas fa-search-location" style="color:#007bff;"></i> スーパーマーケット情報
    <span id="map-info-text" style="display: block; font-size: 0.8em; font-weight: normal; color: #555;">(基準点: 穴吹ビジネス専門学校)</span>
</div>

<div id="sidebar">
    <h2>
        <i class="fas fa-bars"></i> アプリメニュー
        <button class="close-btn" onclick="toggleSidebar()"><i class="fas fa-times"></i></button>
    </h2>
    <div class="sidebar-item" onclick="alert('お気に入りの店舗をハイライトする機能を開発中です！');">
        <i class="fas fa-star" style="color: #FFC107;"></i> お気に入りリスト
    </div>

    <hr>
    <h3><i class="fas fa-filter"></i> ブランドで絞り込む</h3>
    <div class="filter-item" onclick="document.getElementById('filter-all').click()">
        <label for="filter-all">
            <input type="checkbox" id="filter-all" checked onchange="filterMarkers('all', this.checked)">
            <i class="fas fa-store" style="color: #4CAF50;"></i> 全ての店舗を表示
        </label>
    </div>
"""
# 各ブランドのチェックボックスを動的に追加
for brand, color in PIN_COLORS.items():
    safe_brand_id = brand.replace(' ', '').replace('［', '').replace('］', '').replace('−', '')
    app_ui_elements += f"""
    <div class="filter-item" onclick="document.getElementById('filter-{safe_brand_id}').checked = !document.getElementById('filter-{safe_brand_id}').checked; filterMarkers('{brand}', document.getElementById('filter-{safe_brand_id}').checked)">
        <label for="filter-{safe_brand_id}">
            <input type="checkbox" id="filter-{safe_brand_id}" onchange="filterMarkers('{brand}', this.checked)">
            <i class="fas fa-shopping-basket" style="color: {color};"></i> {brand}のみ表示
        </label>
    </div>
    """
app_ui_elements += rf"""
    <hr>
    <h3><i class="fas fa-info-circle"></i> ヘルプ・その他</h3>
    <div class="sidebar-item" onclick="alert('ピンはブランド別に色分けされています。'); toggleSidebar();">
        <i class="fas fa-question-circle"></i> お困りですか？ (FAQ)
    </div>
    <div class="sidebar-item" onclick="alert('お問い合わせありがとうございます。担当者より折り返しご連絡いたします。\n(これはダミーです)'); toggleSidebar();">
        <i class="fas fa-envelope"></i> お問い合わせ
    </div>
</div>

<div id="hamburger" onclick="toggleSidebar()">
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
</div>

<button id="locate-button" onclick="locateUser()">
    <i class="fas fa-street-view"></i>
</button>

<button id="details-button" onclick="showDetailsTable()">
    <i class="fas fa-list-ul"></i> 詳細
</button>

<div id="details-panel">
    <div id="details-content">
        <h2>
            <i class="fas fa-store"></i> マップ上の店舗一覧
            <button class="close-btn-panel" onclick="document.getElementById('details-panel').style.display='none';"><i class="fas fa-times"></i></button>
        </h2>
        <div id="table-container" style="overflow-y: auto;">
            </div>
    </div>
</div>

<div id="comparison-panel" onclick="this.style.display='none';">
    <div id="comparison-content" onclick="event.stopPropagation()">
        <h3 style="margin-top: 0; display: flex; justify-content: space-between; align-items: center;">
            <i class="fas fa-tags" style="color: #E91E63;"></i> <span id="comparison-store-name">特売情報</span>
            <button onclick="document.getElementById('comparison-panel').style.display='none';" style="background: none; border: none; font-size: 1.2em; cursor: pointer; color: #555;">&times;</button>
        </h3>
        <div id="comparison-data">
            </div>
    </div>
</div>

<script>
    const mapElement = window.{map_name};
    const allMarkersData = {marker_data_json};
    const PIN_COLORS_JS = {pin_colors_json};
    const FUKUYAMA_CENTER_JS = {fukuyama_center_json};
    let currentFilteredBrands = new Set();
    const layerControl = {{}};
    const generated_pin_base64_js = {json.dumps(generated_pin_base64)};

    // --- 基準点とデモ現在地の定義 ---
    const INITIAL_REFERENCE_LAT = 34.49178298;
    const INITIAL_REFERENCE_LON = 133.3690471;
    const INITIAL_REFERENCE_NAME = "穴吹ビジネス専門学校";

    const DEMO_LOCATION_LAT = 34.485; 
    const DEMO_LOCATION_LON = 133.365;
    const DEMO_REFERENCE_NAME = "デモ現在地 (ボタン)";

    // 現在使用している基準点
    let currentReferenceLat = INITIAL_REFERENCE_LAT;
    let currentReferenceLon = INITIAL_REFERENCE_LON;
    let currentReferenceName = INITIAL_REFERENCE_NAME;
    let currentLocationMarker = null; // 現在地のマーカーを保持するための変数

    // Leaflet Layersをブランドごとにグループ化
    mapElement.eachLayer(layer => {{
        if(layer._leaflet_id && layer.options && layer.options.pane === 'markerPane') {{
            const markerData = allMarkersData.find(d => d.layer_id === layer._leaflet_id);
            if (markerData) {{
                layerControl[markerData.brand] = layerControl[markerData.brand] || [];
                layerControl[markerData.brand].push(layer);
            }}
        }}
    }});

    Object.keys(layerControl).forEach(brand => currentFilteredBrands.add(brand));

    // 緯度経度から距離(メートル)を計算する関数
    function getDistance(lat1, lon1, lat2, lon2) {{
        const R = 6371; 
        const dLat = (lat2 - lat1) * (Math.PI / 180);
        const dLon = (lon2 - lon1) * (Math.PI / 180);
        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return Math.round(R * c * 1000);
    }}

    $(document).ready(function() {{
        filterMarkers('all', true);
        // ★修正点：初期状態でマップクリックイベントを登録★
        mapElement.on('click', onMapClick); 
    }});

    function startApp() {{
        $('#loading-mask').fadeOut(500, function() {{
            $(this).remove();
            if (mapElement && typeof mapElement.invalidateSize === 'function') {{
                mapElement.invalidateSize();
            }}
        }});
    }}

    function toggleSidebar() {{
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('open');
        setTimeout(() => {{
            if (mapElement && typeof mapElement.invalidateSize === 'function') {{
                mapElement.invalidateSize();
            }}
        }}, 350);
    }}

    function filterMarkers(brandToFilter, isChecked) {{
        const filterAllCheckbox = document.getElementById('filter-all');
        const allBrands = new Set(Object.keys(layerControl));
        
        const getBrandNameFromFilterId = (id) => {{
            const filterPrefix = 'filter-';
            const safeId = id.substring(filterPrefix.length);
            for (const brand of allBrands) {{
                if (brand.replace(' ', '').replace('［', '').replace('］', '').replace('−', '') === safeId) {{
                    return brand;
                }}
            }}
            return null;
        }};

        // フィルタリングロジック (地図上のピンの表示/非表示のみを制御)
        if (brandToFilter === 'all') {{
            if (isChecked) {{
                document.querySelectorAll('.filter-item input[type="checkbox"]').forEach(cb => {{
                    if (cb.id !== 'filter-all') cb.checked = false;
                }});
                currentFilteredBrands = new Set(allBrands);
            }} else {{
                const checkedBrands = Array.from(document.querySelectorAll('.filter-item input[type="checkbox"]'))
                                         .filter(cb => cb.id !== 'filter-all' && cb.checked)
                                         .map(cb => getBrandNameFromFilterId(cb.id))
                                         .filter(b => b);

                if (checkedBrands.length === 0) {{ 
                    filterAllCheckbox.checked = true; 
                    currentFilteredBrands = new Set(allBrands);
                    return; 
                }}

                currentFilteredBrands = new Set(checkedBrands);
            }}
        }} else {{
            const originalBrandName = brandToFilter;

            if (isChecked) {{
                currentFilteredBrands.add(originalBrandName);
            }} else {{
                currentFilteredBrands.delete(originalBrandName);
            }}

            if (currentFilteredBrands.size === 0) {{
                filterAllCheckbox.checked = true;
                currentFilteredBrands = new Set(allBrands);
                document.querySelectorAll('.filter-item input[type="checkbox"]').forEach(cb => {{
                    if (cb.id !== 'filter-all') cb.checked = false;
                }});
            }} else {{
                filterAllCheckbox.checked = false;
                
                currentFilteredBrands = new Set(Array.from(document.querySelectorAll('.filter-item input[type="checkbox"]'))
                                         .filter(cb => cb.id !== 'filter-all' && cb.checked)
                                         .map(cb => getBrandNameFromFilterId(cb.id))
                                         .filter(b => b));
            }}
        }}

        // 地図上のマーカー表示/非表示を切り替え
        allBrands.forEach(brand => {{
            const opacity = currentFilteredBrands.has(brand) ? 1 : 0;
            const zIndex = currentFilteredBrands.has(brand) ? 1000 : 0;
            if (layerControl[brand]) {{
                layerControl[brand].forEach(layer => {{
                    layer.setOpacity(opacity);
                    layer.setZIndexOffset(zIndex); 
                }});
            }}
        }});
        
        // フィルタリング状態が変更された際、詳細パネルが開いていたら更新する
        if ($('#details-panel').css('display') === 'flex') {{
            showDetailsTable();
        }}
    }}

    // ★★★ 修正: locateUser() 関数 (デモ現在地の設定) ★★★
    function locateUser() {{
        alert("現在地を福山市中心付近に設定し、最寄り店舗を計算します。\n(このボタンはデモ機能です。地図上の任意の場所をクリックして基準点を設定することもできます。)");

        // 基準点をデモ現在地に切り替え
        currentReferenceLat = DEMO_LOCATION_LAT;
        currentReferenceLon = DEMO_LOCATION_LON;
        currentReferenceName = DEMO_REFERENCE_NAME;

        // マップをデモ現在地に移動
        mapElement.setView([currentReferenceLat, currentReferenceLon], 14);

        updateReferenceMarker();
        showDetailsTable();
    }}
    // ★★★ 修正: locateUser() 関数 終わり ★★★
    
    // ★★★ 新規追加: onMapClick 関数 (地図クリックで現在地設定) ★★★
    function onMapClick(e) {{
        currentReferenceLat = e.latlng.lat;
        currentReferenceLon = e.latlng.lng;
        currentReferenceName = `クリック地点 (${{currentReferenceLat.toFixed(4)}}, ${{currentReferenceLon.toFixed(4)}})`;

        updateReferenceMarker();
        showDetailsTable();
    }}

    // ★★★ 新規追加: 基準点マーカーの更新処理を共通化 ★★★
    function updateReferenceMarker() {{
        // 既存の現在地マーカーを削除
        if (currentLocationMarker) {{
            mapElement.removeLayer(currentLocationMarker);
            currentLocationMarker = null;
        }}

        // 新しい基準点マーカーを設置
        currentLocationMarker = L.marker([currentReferenceLat, currentReferenceLon], {{
            icon: L.divIcon({{
                className: 'current-location-marker',
                html: '<div style="color: #FF9800; font-size: 20px; text-align: center;"><i class="fas fa-map-marker-alt fa-2x"></i></div>', // 地図クリック用にアイコン変更
                iconSize: [40, 40],
                iconAnchor: [15, 30] // ピンの先端が座標に来るように調整
            }}),
            zIndexOffset: 2000
        }}).addTo(mapElement).bindPopup(`${{currentReferenceName}}`).openPopup();
        
        // 地図上の情報オーバーレイを更新
        $('#map-info-text').html(`(基準点: ${{currentReferenceName}} Lat: ${{currentReferenceLat.toFixed(4)}}, Lon: ${{currentReferenceLon.toFixed(4)}})`);
    }}

    function openMarkerPopup(lat, lon, layerId) {{
        const currentZoom = mapElement.getZoom();
        const targetZoom = Math.max(currentZoom, 14);

        mapElement.setView([lat, lon], targetZoom);

        mapElement.eachLayer(layer => {{
            if (layer._leaflet_id === layerId) {{
                if (layer.openPopup) {{
                    layer.openPopup();
                    document.getElementById('details-panel').style.display = 'none';
                    return;
                }}
            }}
        }});
    }}


    // ★★★ 修正: showDetailsTable() 関数 (フィルタリング状態を反映させる) ★★★
    function showDetailsTable() {{
        const panel = document.getElementById('details-panel');
        const tableContainer = document.getElementById('table-container');

        // ★修正点1: 地図でチェックされているブランドのみをフィルタリング★
        let dataForList = allMarkersData.filter(d => currentFilteredBrands.has(d.brand));

        let closestStore = null;
        let minDistance = Infinity;

        dataForList.forEach(data => {{
            // 現在設定されている基準点 (currentReferenceLat/Lon) を使用して距離を計算
            const distanceMeters = getDistance(
                currentReferenceLat, currentReferenceLon,
                data.lat, data.lon
            );
            data.distance = distanceMeters;

            if (distanceMeters < minDistance) {{
                minDistance = distanceMeters;
                closestStore = data;
            }}
        }});

        // 距離順でソート
        dataForList.sort((a, b) => a.distance - b.distance);

        let distanceStatus = `<span style="color: #007bff;"><i class="fas fa-route"></i> <strong>${{currentReferenceName}}</strong>からの距離順に表示しています。</span>`;
        let closestStoreMessage = '';

        if (dataForList.length === 0) {{
             distanceStatus = `<span style="color: #dc3545;"><i class="fas fa-times-circle"></i> フィルター条件に一致する店舗がありません。</span>`;
        }} else if (closestStore) {{
            const formattedDistance = (closestStore.distance / 1000).toFixed(2) + ' km';
            closestStoreMessage = `<p style="margin: 5px 0 0 0; font-weight: bold; color: #E91E63;"><i class="fas fa-map-pin"></i> 最寄りの店舗は「${{closestStore.name}}」で、約 ${{formattedDistance}} です！</p>`;
        }}

        const infoTextHTML = `
            <div style="padding: 10px; margin-bottom: 15px; background-color: #f0f8ff; border: 1px solid #cceeff; border-radius: 5px; color: #333; font-size: 0.9em;">
                <p style="margin: 0;">${{distanceStatus}}</p>
                ${{closestStoreMessage}}
            </div>
        `;

        let listHTML = infoTextHTML;
        listHTML += `<ul id="super-list">`;

        // フィルタリングされたデータ（表示中のブランドのみ）を表示
        dataForList.forEach(data => {{
            const brandColor = PIN_COLORS_JS[data.brand] || '#333';
            const distanceKm = (data.distance / 1000).toFixed(2);

            const dataIndex = allMarkersData.findIndex(d => d.id === data.id);
            const logoBase64Url = generated_pin_base64_js[dataIndex];


            listHTML += `
                <li onclick="openMarkerPopup(${{data.lat}}, ${{data.lon}}, ${{data.layer_id}})" style="border-left: 5px solid ${{brandColor}};">
                    <img src="${{logoBase64Url}}"
                         onerror="this.style.display='none'"
                         style="height: 25px; width: 25px; object-fit: contain; flex-shrink: 0; background-color: ${{brandColor}}; border-radius: 50%;">
                    <div class="info-block">
                        <span class="store-name">${{data.name}}</span>
                        <span class="brand-name">ブランド: ${{data.brand}}</span>
                    </div>
                    <span class="distance-info">${{distanceKm}} km</span>
                </li>
            `;
        }});

        listHTML += `</ul>`;
        tableContainer.innerHTML = listHTML;

        panel.style.display = 'flex';
    }}

    function showComparisonPanel(storeName) {{
        const store = allMarkersData.find(d => d.name === storeName);
        if (!store) return;

        $('#comparison-store-name').text(storeName + ' の特売情報');
        let detailHtml = '';

        const categories = [
            {{ key: 'souzai', icon: 'fas fa-drumstick-bite', label: '惣菜' }},
            {{ key: 'sengyo', icon: 'fas fa-fish', label: '鮮魚' }},
            {{ key: 'niku', icon: 'fas fa-cow', label: '精肉' }},
            {{ key: 'seika', icon: 'fas fa-carrot', label: '青果' }}
        ];

        categories.forEach(cat => {{
            detailHtml += `
                <div class="comparison-item">
                    <p style="margin: 0; font-weight: bold; color: #673AB7;"><i class="${{cat.icon}}"></i> ${{cat.label}}:</p>
                    <p style="margin: 3px 0 0 20px; font-size: 0.9em;">${{store[cat.key]}}</p>
                </div>
            `;
        }});

        $('#comparison-data').html(detailHtml);
        $('#comparison-panel').fadeIn(200);

        mapElement.closePopup();
    }}

</script>
"""

# 5-2. マップをHTMLファイルとして保存し、UIを挿入
file_path = "supermarket_app_map_clickable_list.html"
m_temp.save(file_path)

with open(file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# <body>タグの直後にUIコードを挿入
insertion_point = html_content.find('<body>') + len('<body>')
modified_html_content = html_content[:insertion_point] + app_ui_elements + html_content[insertion_point:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(modified_html_content)

print(f"\n✅ 処理が完了しました！全{df.shape[0]}店舗の情報を地図に組み込みました。")
print("🔥 新機能: 地図上の任意の場所をクリックすると、そこが現在地(基準点)となり、詳細リストが更新されます。")

# --- 生成したHTMLをアプリのウィンドウで開く ---
webview.create_window(
    f"SMAP - Supermarket Map App (全{df.shape[0]}店舗)", 
    file_path,               
    width=1200, height=800,  
    resizable=True           
)
webview.start()