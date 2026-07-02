# Aliyun OSS Deployment

This site is static. Deploy the contents of `public/` to an Alibaba Cloud OSS bucket.

## Required Aliyun Settings

Set these environment variables before deploying:

```powershell
$env:ALIYUN_ACCESS_KEY_ID="your-access-key-id"
$env:ALIYUN_ACCESS_KEY_SECRET="your-access-key-secret"
$env:ALIYUN_OSS_BUCKET="your-bucket-name"
$env:ALIYUN_OSS_ENDPOINT="oss-cn-hongkong.aliyuncs.com"
```

For a no-ICP first deployment, use a Hong Kong bucket such as `cn-hongkong`.

## Deploy

```powershell
python scripts/deploy_aliyun_oss.py --configure-website --set-public-read
```

The script uploads every file in `public/`, configures `index.html` as the website index and fallback page, and sets the bucket ACL to `public-read`.

## Output URL

After deployment, the OSS website endpoint will look similar to:

```text
http://your-bucket-name.oss-cn-hongkong.aliyuncs.com/index.html
```

For a production domain, bind a custom domain in OSS or CDN. Mainland China custom domains usually require ICP filing.
