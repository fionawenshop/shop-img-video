import re
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    try:
        creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print("❌ service_account.json error:", e)
        return None

def extract_folder_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def get_file_name(service, file_id):
    return service.files().get(fileId=file_id, fields='name').execute()['name']

def list_all_files(service, parent_id):
    files = []
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields="files(id, name, mimeType), nextPageToken",
            pageToken=page_token,
            pageSize=1000
        ).execute()
        files.extend(resp.get('files', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return files

def generate_html(products):
    product_list = list(products.items())
    json_data = json.dumps(product_list, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>FionaWen</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:Arial,sans-serif;background:#fff}}
.container{{max-width:1000px;margin:0 auto;padding:20px}}
.main-title{{text-align:center;font-size:28px;margin:30px 0;color:#222}}

.product{{margin-bottom:50px;padding-bottom:20px;border-bottom:1px solid #eee}}
.product-title{{
    text-align:center;
    font-size:18px;
    margin:15px 0;
    color:#000;
    cursor:pointer;
    font-weight:bold;
    text-decoration:underline;
}}

.grid{{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:8px;
}}
.grid-item{{
    aspect-ratio:1;
    background:#000;
    border-radius:6px;
    overflow:hidden;
    position:relative;
    cursor:pointer;
}}
.grid-item img{{
    width:100%;height:100%;object-fit:cover
}}
.grid-item .more{{
    position:absolute;
    inset:0;
    background:rgba(0,0,0,0.6);
    color:#fff;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:26px;
    font-weight:bold;
}}

.modal{{
    display:none;
    position:fixed;
    top:0;left:0;
    width:100%;height:100%;
    background:rgba(0,0,0,0.95);
    z-index:9999;
    padding:10px;
    overflow-y:auto;
}}
.modal-close{{
    position:fixed;
    top:15px;right:15px;
    color:#fff;
    font-size:36px;
    cursor:pointer;
    z-index:9999
}}
.modal-content{{
    max-width:500px;
    margin:40px auto;
}}
.modal-media{{
    margin-bottom:12px;
    border-radius:8px;
    overflow:hidden;
    background:#000;
    width:100%;
}}
.modal-media img{{
    width:100%;
    height:auto;
    display:block;
}}

/* 竖屏 9:16 手机专用 */
.video-wrapper {{
    position: relative;
    width: 100%;
    padding-top: 177.77%;
    background: #000;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom:12px;
}}
.video-wrapper iframe {{
    position: absolute;
    top:0; left:0;
    width:100%; height:100%;
    border:none;
}}

.pagination{{
    text-align:center;
    margin:40px 0;
}}
.pagination button{{
    padding: 10px 20px;
    font-size:15px;
    margin:0 8px;
    border:none;
    background:#222;
    color:#fff;
    border-radius:8px;
    cursor:pointer;
}}
.pagination button:disabled{{
    background:#ccc;
}}
#pageInfo{{
    font-size:16px;
}}
</style>
</head>
<body>

<div class="container">
        <div style="text-align:center; margin:15px 0;">
    <a href="https://wa.me/message/44E5ERX6L7IDG1" target="_blank" style="
        display:inline-block;
        background:#25D366;
        color:#fff;
        font-size:14px;
        font-weight:bold;
        padding:10px 22px;
        border-radius:6px;
        text-decoration:none;
    ">Wholesale - Contact WhatsApp</a>
</div>
    <div id="productList"></div>

    <div class="pagination">
        <button id="prev">Previous</button>
        <span id="pageInfo">Page 1 / 0</span>
        <button id="next">Next</button>
    </div>
</div>

<div class="modal" id="modal">
    <div class="modal-close" onclick="closeModal()">×</div>
    <div class="modal-content" id="modalContent"></div>
</div>

<script>
const allProducts = {json_data};
const perPage = 10;
let currentPage = 1;
let currentPageProducts = [];

function renderProducts(){{
    const container = document.getElementById('productList');
    container.innerHTML = '';
    
    const start = (currentPage-1)*perPage;
    const end = currentPage*perPage;
    currentPageProducts = allProducts.slice(start, end);
    
    currentPageProducts.forEach((item, idx) => {{
        const [prodName, medias] = item;
        let gridHTML = '';
        const showItems = medias.slice(0,9);
        const extraCount = medias.length - 9;

        showItems.forEach((m, idx2) => {{
            if (!m.mimeType.includes('video')) {{
                gridHTML += `
                <div class="grid-item" onclick="openModal(${{idx}})">
                    <img src="https://lh3.googleusercontent.com/d/${{m.id}}">
                    ${{extraCount > 0 && idx2 === 8 ? '<div class="more">+'+extraCount+'</div>' : ''}}
                </div>`;
            }}
        }});

        container.innerHTML += `
        <div class="product">
            <div class="product-title" onclick="openModal(${{idx}})">${{prodName}}</div>
            <div class="grid">${{gridHTML}}</div>
        </div>`;
    }});

    document.getElementById('pageInfo').innerText = `Page ${{currentPage}} / ${{Math.ceil(allProducts.length / perPage)}}`;
    document.getElementById('prev').disabled = currentPage === 1;
    document.getElementById('next').disabled = currentPage === Math.ceil(allProducts.length/perPage);
}}

function openModal(idx){{
    const [name, medias] = currentPageProducts[idx];
    const content = document.getElementById('modalContent');
    content.innerHTML = `<h2 style="color:#fff;text-align:center;margin-bottom:20px">${{name}}</h2>`;

    medias.forEach(m => {{
        if(m.mimeType.includes('video')){{
            // 一键播放 + 正确封面比例
            content.innerHTML += `
            <div class="video-wrapper">
                <iframe 
                    src="https://drive.google.com/file/d/${{m.id}}/preview?autoplay=0&rel=0" 
                    allow="autoplay"
                    allowfullscreen>
                </iframe>
            </div>`;
        }}
    }});

    medias.forEach(m => {{
        if(!m.mimeType.includes('video')){{
            content.innerHTML += `
            <div class="modal-media">
                <img src="https://lh3.googleusercontent.com/d/${{m.id}}">
            </div>`;
        }}
    }});

    document.getElementById('modal').style.display = 'block';
}}

function closeModal(){{
    document.getElementById('modal').style.display = 'none';
    document.getElementById('modalContent').innerHTML = '';
}}

document.getElementById('prev').onclick = () => {{
    if(currentPage>1){{
        currentPage--;
        renderProducts();
        window.scrollTo({{top:0, behavior:'smooth'}});
    }}
}}
document.getElementById('next').onclick = () => {{
    if(currentPage<Math.ceil(allProducts.length/perPage)){{
        currentPage++;
        renderProducts();
        window.scrollTo({{top:0, behavior:'smooth'}});
    }}
}}

renderProducts();
</script>
</body>
</html>'''
    return html

def main():
    print("=== FionaWen ===")
    url = input("Drive Folder URL: ").strip()
    fid = extract_folder_id(url)
    if not fid:
        print("Invalid URL"); return

    service = get_drive_service()
    if not service: return

    print("Loading products...")
    folders = list_all_files(service, fid)
    print(f"Total products: {len(folders)}")

    name_map = {f['name']: f for f in folders}
    all_names = [f['name'] for f in folders]

    priority = input("\nPriority order (comma separated): ").strip()
    pri_list = [n.strip() for n in priority.split(',') if n.strip()]
    pri_list = [n for n in pri_list if n in name_map]
    rest = [n for n in all_names if n not in pri_list]
    final = pri_list + rest

    products = {}
    for name in final:
        products[name] = list_all_files(service, name_map[name]['id'])

    html = generate_html(products)
    with open("FionaWen.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\n✅ Done! Open FionaWen.html")

if __name__ == '__main__':
    main()