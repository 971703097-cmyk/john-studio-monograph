import argparse
import base64
import datetime as dt
import hashlib
import hmac
import mimetypes
import os
import time
from pathlib import Path
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = PROJECT_ROOT / "public"


def gmt_now():
    return dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")


def sign(secret, message):
    digest = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha1).digest()
    return base64.b64encode(digest).decode("ascii")


def request_oss(method, bucket, endpoint, object_key="", body=b"", content_type="", headers=None, subresource=""):
    access_key_id = os.environ["ALIYUN_ACCESS_KEY_ID"]
    access_key_secret = os.environ["ALIYUN_ACCESS_KEY_SECRET"]
    headers = dict(headers or {})
    date = gmt_now()
    content_md5 = ""
    oss_headers = []
    for key, value in headers.items():
        lower_key = key.lower()
        if lower_key.startswith("x-oss-"):
            oss_headers.append((lower_key, " ".join(str(value).split())))
    canonicalized_headers = "".join(f"{key}:{value}\n" for key, value in sorted(oss_headers))
    canonicalized_resource = f"/{bucket}/{object_key}"
    if subresource:
        canonicalized_resource += f"?{subresource}"
    string_to_sign = "\n".join([
        method,
        content_md5,
        content_type,
        date,
        canonicalized_headers + canonicalized_resource,
    ])
    authorization = f"OSS {access_key_id}:{sign(access_key_secret, string_to_sign)}"
    host = f"{bucket}.{endpoint}"
    encoded_key = "/".join(quote(part, safe="") for part in object_key.split("/")) if object_key else ""
    url = f"https://{host}/{encoded_key}"
    if subresource:
        url += f"?{subresource}"
    headers.update({
        "Date": date,
        "Authorization": authorization,
        "Host": host,
    })
    if content_type:
        headers["Content-Type"] = content_type
    request = Request(url, data=body if method in {"PUT", "POST"} else None, headers=headers, method=method)
    with urlopen(request, timeout=60) as response:
        return response.status, response.read()


def content_type_for(path):
    guessed, _ = mimetypes.guess_type(path.name)
    if path.suffix == ".webp":
        return "image/webp"
    if path.suffix == ".js":
        return "text/javascript; charset=utf-8"
    if path.suffix in {".html", ".css", ".json", ".txt", ".xml"}:
        base = guessed or "text/plain"
        return f"{base}; charset=utf-8"
    return guessed or "application/octet-stream"


def cache_control_for(path):
    if path.suffix in {".webp", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico"}:
        return "public, max-age=31536000, immutable"
    return "public, max-age=60"


def upload_public(bucket, endpoint):
    files = [path for path in PUBLIC_DIR.rglob("*") if path.is_file()]
    failures = []
    for path in files:
        key = path.relative_to(PUBLIC_DIR).as_posix()
        body = path.read_bytes()
        content_type = content_type_for(path)
        headers = {"Cache-Control": cache_control_for(path)}
        for attempt in range(1, 5):
            try:
                request_oss("PUT", bucket, endpoint, key, body, content_type, headers)
                print(f"uploaded {key}")
                break
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                if attempt == 4:
                    failures.append((key, str(exc)))
                    print(f"failed {key}: {exc}")
                else:
                    time.sleep(attempt * 2)
    if failures:
        print(f"uploaded with {len(failures)} failures")
        for key, error in failures:
            print(f"- {key}: {error}")
        raise SystemExit(1)
    print(f"uploaded {len(files)} files")


def configure_website(bucket, endpoint):
    body = b"""<?xml version="1.0" encoding="UTF-8"?>
<WebsiteConfiguration>
  <IndexDocument>
    <Suffix>index.html</Suffix>
  </IndexDocument>
  <ErrorDocument>
    <Key>index.html</Key>
  </ErrorDocument>
</WebsiteConfiguration>
"""
    request_oss("PUT", bucket, endpoint, "", body, "application/xml", subresource="website")
    print("configured static website: index.html / index.html")


def set_public_read(bucket, endpoint):
    request_oss("PUT", bucket, endpoint, "", b"", headers={"x-oss-acl": "public-read"}, subresource="acl")
    print("bucket ACL set to public-read")


def main():
    parser = argparse.ArgumentParser(description="Deploy public/ to Alibaba Cloud OSS.")
    parser.add_argument("--bucket", default=os.environ.get("ALIYUN_OSS_BUCKET"), required=False)
    parser.add_argument("--endpoint", default=os.environ.get("ALIYUN_OSS_ENDPOINT"), required=False,
                        help="Example: oss-cn-hongkong.aliyuncs.com")
    parser.add_argument("--configure-website", action="store_true")
    parser.add_argument("--set-public-read", action="store_true")
    args = parser.parse_args()

    missing = [name for name in ["ALIYUN_ACCESS_KEY_ID", "ALIYUN_ACCESS_KEY_SECRET"] if not os.environ.get(name)]
    if not args.bucket:
        missing.append("ALIYUN_OSS_BUCKET")
    if not args.endpoint:
        missing.append("ALIYUN_OSS_ENDPOINT")
    if missing:
        raise SystemExit("Missing required settings: " + ", ".join(missing))

    if args.set_public_read:
        set_public_read(args.bucket, args.endpoint)
    if args.configure_website:
        configure_website(args.bucket, args.endpoint)
    upload_public(args.bucket, args.endpoint)


if __name__ == "__main__":
    main()
