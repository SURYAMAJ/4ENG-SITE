# Cloudflare deployment and GoDaddy domain handoff

The site is a static Cloudflare Workers project. It does not use Supabase, a database, or a server-side form endpoint.

## 1. Deploy the site

From this folder:

```powershell
npm install
npm run check
npx wrangler login
npm run deploy
```

The first deployment creates the `4eng-site` Worker and returns a temporary `*.workers.dev` URL.

## 2. Add the custom domains in Cloudflare

1. Add `4eng.tech` to the correct Cloudflare account if it is not already present.
2. In **Workers & Pages → 4eng-site → Settings → Domains & Routes**, add:
   - `4eng.tech`
   - `www.4eng.tech`
3. Make `4eng.tech` the canonical address. Create a Cloudflare Redirect Rule that permanently redirects `www.4eng.tech/*` to `https://4eng.tech/$1` while preserving the path and query string.
4. Wait for both custom-domain certificates to show as active before announcing the site.

Cloudflare will create the required DNS records for Worker custom domains. Do not invent an A-record IP address for a Worker.

## 3. Update GoDaddy

Cloudflare will show two account-specific authoritative nameservers on the **Overview** page for `4eng.tech`, for example `name.ns.cloudflare.com`. The real values cannot be known before the zone is added to Cloudflare.

Before changing anything, copy all current GoDaddy DNS records, especially MX, TXT, SPF, DKIM, DMARC, verification, and any existing subdomains, into Cloudflare DNS. This avoids interrupting email or other services.

Then in GoDaddy:

1. Open **My Products → Domains → 4eng.tech → DNS → Nameservers → Change**.
2. Choose **Enter my own nameservers**.
3. Replace the existing nameservers with the exact two nameservers assigned by Cloudflare. Remove any extras.
4. Save the change.

If DNSSEC is enabled at GoDaddy, remove the old DS record before changing nameservers. After Cloudflare reports the zone as active, enable DNSSEC in Cloudflare and add Cloudflare's new DS record at GoDaddy.

Nameserver activation can take up to 24 hours. During propagation, keep the old hosting service online and do not remove old DNS records until Cloudflare reports the zone as active.

## 4. Launch checks

- Open `https://4eng.tech` and `https://www.4eng.tech` in a private window.
- Confirm `www` redirects to the apex domain and HTTPS has no certificate warning.
- Check `/robots.txt`, `/sitemap.xml`, `/site.webmanifest`, and a deliberately missing URL.
- Submit a design-partner enquiry by confirming the button opens a pre-addressed email draft.
- Add `https://4eng.tech/sitemap.xml` to Google Search Console and Bing Webmaster Tools.
- Enable Cloudflare Web Analytics if required; the security policy already permits its beacon.
