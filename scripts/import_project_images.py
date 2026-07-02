import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageOps


SOURCE_ROOT = Path(r"D:\JOHN设计工作室\06_品牌资产\做网页资料\项目图片")
PUBLIC_ROOT = Path(__file__).resolve().parents[1] / "public"
ASSET_ROOT = PUBLIC_ROOT / "assets" / "projects"
DATA_PATH = PUBLIC_ROOT / "data.json"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

PROJECTS = [
    {
        "folder": "A东莞新世界（室内）",
        "slug": "dongguan-new-world-interior",
        "title": {"en": "Dongguan New World Residence", "cn": "东莞新世界"},
        "year": "2025",
        "location": "Dongguan, China",
        "locationCn": "中国 · 东莞",
        "scale": "Interior residence",
        "scaleCn": "住宅室内",
        "category": {"en": "Interior Design", "cn": "室内设计"},
    },
    {
        "folder": "B南京秦双线淮河码头（建筑）",
        "slug": "nanjing-huaihe-wharf",
        "title": {"en": "Huaihe Wharf, Nanjing Qinshuang Line", "cn": "南京秦双线淮河码头"},
        "year": "2025",
        "location": "Nanjing, China",
        "locationCn": "中国 · 南京",
        "scale": "Public waterfront architecture",
        "scaleCn": "滨水公共建筑",
        "category": {"en": "Architecture", "cn": "建筑设计"},
    },
    {
        "folder": "C酒吧（室内）",
        "slug": "bar-interior",
        "title": {"en": "Bar Interior", "cn": "酒吧室内"},
        "year": "2024",
        "location": "China",
        "locationCn": "中国",
        "scale": "Hospitality interior",
        "scaleCn": "商业空间室内",
        "category": {"en": "Interior Design", "cn": "室内设计"},
    },
    {
        "folder": "D福建利水温泉游客中心（建筑）",
        "slug": "fujian-lishui-hot-spring-visitor-center",
        "title": {"en": "Lishui Hot Spring Visitor Center", "cn": "福建利水温泉游客中心"},
        "year": "2024",
        "location": "Fujian, China",
        "locationCn": "中国 · 福建",
        "scale": "Visitor center",
        "scaleCn": "游客中心",
        "category": {"en": "Architecture", "cn": "建筑设计"},
    },
    {
        "folder": "E桑植，陈家河村 贺龙希望小学扩建（建筑）",
        "slug": "helong-hope-primary-school-extension",
        "title": {"en": "He Long Hope Primary School Extension", "cn": "贺龙希望小学扩建"},
        "year": "2024",
        "location": "Sangzhi, China",
        "locationCn": "中国 · 桑植",
        "scale": "Educational architecture",
        "scaleCn": "教育建筑",
        "category": {"en": "Architecture", "cn": "建筑设计"},
    },
    {
        "folder": "F东莞·万科山境（室内）",
        "slug": "dongguan-vanke-mountain-realm",
        "title": {"en": "Dongguan Vanke Mountain Realm", "cn": "东莞 · 万科山境"},
        "year": "2024",
        "location": "Dongguan, China",
        "locationCn": "中国 · 东莞",
        "scale": "Residential interior",
        "scaleCn": "住宅室内",
        "category": {"en": "Interior Design", "cn": "室内设计"},
    },
    {
        "folder": "H广州·南沙逸涛半岛（室内）",
        "slug": "guangzhou-nansha-yitao-peninsula",
        "title": {"en": "Guangzhou Nansha Yitao Peninsula", "cn": "广州 · 南沙逸涛半岛"},
        "year": "2024",
        "location": "Guangzhou, China",
        "locationCn": "中国 · 广州",
        "scale": "Residential interior",
        "scaleCn": "住宅室内",
        "category": {"en": "Interior Design", "cn": "室内设计"},
    },
]


def natural_key(path: Path):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.stem)]


def pick_images(files):
    lower = {file.name.lower(): file for file in files}
    hero = lower.get("hero.jpg") or lower.get("hero.png") or lower.get("hero.jpeg") or files[0]
    closing = (
        lower.get("closing.jpg")
        or lower.get("closing.png")
        or lower.get("closing.jpeg")
        or files[-1]
    )
    gallery = [file for file in files if file not in {hero, closing}]
    return hero, gallery[:4], closing


def save_webp(source: Path, target: Path, max_long_edge: int):
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((max_long_edge, max_long_edge), Image.Resampling.LANCZOS)
        if image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        image.save(target, "WEBP", quality=82, method=6)


def narrative_text(project):
    is_architecture = project["category"]["en"] == "Architecture"
    if is_architecture:
        return {
            "desc": {
                "en": "A restrained architectural project shaped by site, movement, and public spatial sequence.",
                "cn": "一个由场地、动线与公共空间序列共同塑造的克制建筑项目。"
            },
            "detail": {
                "en": "The project is presented as a spatial chapter: arrival, pause, transition, and enclosure are organized through measured proportion and a quiet architectural order.",
                "cn": "项目被呈现为一个空间章节：到达、停顿、转换与围合通过克制的比例和安静的建筑秩序被组织起来。"
            },
            "concept": {
                "en": "Rather than treating architecture as an isolated object, the design frames it as a sequence of views, thresholds, and material transitions.",
                "cn": "设计并不把建筑视为孤立物体，而是将其组织为视线、界面与材料转换构成的连续序列。"
            },
            "notes": [
                ("Site", "场地", "The layout responds to orientation, approach, and the rhythm of the surrounding context.", "布局回应朝向、进入路径与周边环境的节奏。"),
                ("Order", "秩序", "Openings, edges, and circulation are calibrated as one continuous architectural system.", "开口、边界与动线被校准为一个连续的建筑系统。"),
                ("Material", "材料", "The material expression remains quiet, allowing light and proportion to define the spatial atmosphere.", "材料表达保持克制，让光线与比例成为空间气质的主要来源。"),
            ],
        }
    return {
        "desc": {
            "en": "A calm interior sequence shaped by material restraint, light, and spatial rhythm.",
            "cn": "一个由材料克制、光线与空间节奏共同塑造的安静室内序列。"
        },
        "detail": {
            "en": "The interior is edited like an architectural monograph. Each view becomes a page, and each transition is used to build a slower reading of the project.",
            "cn": "室内空间像一本建筑专辑般被编辑。每个视角成为一页，每次转换都用于建立更缓慢的项目阅读。"
        },
        "concept": {
            "en": "The project uses controlled surfaces, layered light, and a clear circulation rhythm to create a composed everyday spatial experience.",
            "cn": "项目通过受控的表面、层次化光线与清晰动线节奏，构成一种克制而日常的空间体验。"
        },
        "notes": [
            ("Material", "材料", "Neutral surfaces, tactile finishes, and indirect light form a restrained material hierarchy.", "中性表面、触感饰面与间接光共同形成克制的材料层级。"),
            ("Atmosphere", "氛围", "The visual temperature is kept quiet so furniture, proportion, and light can define the room.", "视觉温度被控制得更安静，让家具、比例与光线共同定义空间。"),
            ("Sequence", "序列", "Views are arranged as a progression from openness to detail, creating a monograph-like rhythm.", "视角从开敞到细部逐步展开，形成接近建筑专辑的阅读节奏。"),
        ],
    }


def build_project(config):
    source_dir = SOURCE_ROOT / config["folder"]
    files = sorted(
        [file for file in source_dir.rglob("*") if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS],
        key=natural_key,
    )
    if not files:
        raise RuntimeError(f"No images found in {source_dir}")

    target_dir = ASSET_ROOT / config["slug"]
    if target_dir.exists():
        shutil.rmtree(target_dir)

    hero, gallery_sources, closing = pick_images(files)
    save_webp(hero, target_dir / "hero.webp", 2400)
    save_webp(hero, target_dir / "card.webp", 1200)
    gallery = []
    for index, source in enumerate(gallery_sources, 1):
        target_name = f"{index:02d}.webp"
        save_webp(source, target_dir / target_name, 1900)
        gallery.append({
            "src": f"assets/projects/{config['slug']}/{target_name}",
            "alt": f"{config['title']['en']} view {index}",
        })
    save_webp(closing, target_dir / "closing.webp", 2400)

    narrative = narrative_text(config)
    project = {
        "title": config["title"],
        "desc": narrative["desc"],
        "detail": narrative["detail"],
        "concept": narrative["concept"],
        "year": config["year"],
        "location": config["location"],
        "locationCn": config["locationCn"],
        "scale": config["scale"],
        "scaleCn": config["scaleCn"],
        "category": config["category"],
        "image": f"assets/projects/{config['slug']}/card.webp",
        "imageFull": f"assets/projects/{config['slug']}/hero.webp",
        "gallery": gallery,
        "technicalNotes": [
            {
                "label": {"en": label_en, "cn": label_cn},
                "value": {"en": value_en, "cn": value_cn},
            }
            for label_en, label_cn, value_en, value_cn in narrative["notes"]
        ],
        "closingImage": f"assets/projects/{config['slug']}/closing.webp",
        "specs": [
            {"label": "Scope", "value": config["scale"]},
            {"label": "Type", "value": config["category"]["en"]},
            {"label": "Location", "value": config["location"]},
        ],
    }
    return project, len(files)


def main():
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    projects = []
    counts = {}
    for config in PROJECTS:
        project, count = build_project(config)
        projects.append(project)
        counts[config["slug"]] = count

    data["projects"] = projects
    data["heroImage"] = projects[0]["imageFull"]
    data["bgLayer"] = projects[0]["image"]
    data["openingStatement"] = {
        "en": "We design architecture and interiors as spatial narratives, each project unfolding like a quiet monograph.",
        "cn": "我们将建筑与室内设计为一种空间叙事，让每个项目像安静的专辑章节般展开。"
    }
    data["philosophyStatement"] = {
        "en": "Each project is not a portfolio item. It is a sequence of atmosphere, material, and movement.",
        "cn": "每一个项目都不是作品集条目，而是由氛围、材料与动线构成的空间序列。"
    }
    data["aboutText"] = {
        "en": "John Studio works across architecture, interiors, and spatial visual systems. The studio organizes each project through site, proportion, material, and narrative sequence.",
        "cn": "约翰工作室工作于建筑、室内与空间视觉系统之间，以场地、比例、材料和叙事序列组织每一个项目。"
    }
    data["aboutStatement"] = {
        "en": "Space is read slowly: one image, one threshold, one material decision at a time.",
        "cn": "空间需要被缓慢阅读：一张图、一个界面、一次材料判断。"
    }

    with DATA_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
