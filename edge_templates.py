# edge_templates.py
# UI + generator for Edge Function templates
import streamlit as st
import json
from textwrap import dedent

def _card(title: str, subtitle: str = ""):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)

def _end_card():
    st.markdown('</div>', unsafe_allow_html=True)

def _emit_generated(code: str, filename: str = "edgefunction.js"):
    st.markdown("### Generated EdgeFunction")
    st.code(code, language="javascript")
    st.download_button("Download", code, file_name=filename, mime="application/javascript")

# --------------------------
# Maintenance Hour
# --------------------------
def page_maintenance_hour(st: st.__class__):
    _card("Maintenance Hour", "Schedule downtime using 12-hour clock (AM/PM).")

    def _to24(h12: int, ampm: str) -> int:
        h = h12 % 12
        return h + (12 if ampm.upper() == "PM" else 0)

    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        start_h12 = st.selectbox("Start hour", list(range(1, 13)), index=1)  # 1..12
        start_ampm = st.selectbox("Start", ["AM", "PM"], index=0)
    with c2:
        end_h12 = st.selectbox("End hour", list(range(1, 13)), index=4)
        end_ampm = st.selectbox("End", ["AM", "PM"], index=0)
    with c3:
        gmt_offset = st.number_input("GMT offset", -12, 14, 7)

    msg = st.text_input("Maintenance message", "Service temporarily unavailable (Scheduled Maintenance)")

    if st.button("Generate Maintenance Worker"):
        start_24 = _to24(start_h12, start_ampm)
        end_24   = _to24(end_h12, end_ampm)

        if start_24 >= end_24:
            st.error("Start time must be earlier than end time.")
            _end_card(); return

        code = (
f"""addEventListener("fetch", event => {{
  event.respondWith(handleRequest(event.request));
}});

async function handleRequest(request) {{
  const now = new Date();
  const utcHour = now.getUTCHours();
  const localHour = (utcHour + ({gmt_offset}) + 24) % 24;

  const inWindow = localHour >= {start_24} && localHour < {end_24};
  if (inWindow) {{
    return new Response("{msg}", {{
      status: 503,
      headers: {{
        "Content-Type": "text/plain"
      }}
    }});
  }}
  return fetch(request);
}}"""
        ).strip()

        _emit_generated(code, "maintenance.js")
    _end_card()



# --------------------------
# Simple Bot Detection
# --------------------------
def page_simple_bot_detection(st: st.__class__):
    _card("Simple Bot Detection", "Lightweight heuristics based on headers.")
    st.caption("Select which conditions you want to block.")
    c1, c2 = st.columns(2)
    with c1:
        block_curl = st.checkbox("Block User-Agent contains 'curl'", True)
        block_wget = st.checkbox("Block User-Agent contains 'wget'", True)
        block_headless = st.checkbox("Block headless keywords (headless|puppeteer|selenium|phantom)", True)
    with c2:
        block_empty_ua = st.checkbox("Block if User-Agent is empty", False)
        block_no_accept_lang = st.checkbox("Block if no Accept-Language header", False)
        status_code = st.number_input("Status code when blocked", 400, 451, 403)

    msg = st.text_input("Block message", "Access Denied - Bot Detected")

    if st.button("Generate Bot-Detection Worker"):
        conds = []
        if block_empty_ua:
            conds.append("!ua")
        if block_curl:
            conds.append('ua.includes("curl")')
        if block_wget:
            conds.append('ua.includes("wget")')
        if block_headless:
            conds.append('ua.match(/headless|puppeteer|selenium|phantom/i)')
        if block_no_accept_lang:
            conds.append('!(request.headers.get("accept-language") || "")')

        condition = " || ".join(conds) if conds else "false"

        code = dedent(f"""
        addEventListener("fetch", event => {{
          event.respondWith(handleRequest(event.request));
        }});

        async function handleRequest(request) {{
          const ua = (request.headers.get("user-agent") || "").toLowerCase();
          const isBlocked = {condition};

          if (isBlocked) {{
            return new Response("{msg}", {{
              status: {status_code},
              headers: {{ "Content-Type": "text/plain" }}
            }});
          }}
          return fetch(request);
        }}
        """).strip()
        _emit_generated(code, "bot_detection.js")
    _end_card()

# --------------------------
# Custom Header Injection
# --------------------------
def page_custom_header_injection(st: st.__class__):
    _card("Custom Header Injection", "Add custom headers to every response.")
    hname = st.text_input("Header name", "X-Custom-Header")
    hval = st.text_input("Header value", "Hello from Edge Function!")
    preserve = st.checkbox("Preserve existing header if already present", True)

    if st.button("Generate Header-Injection Worker"):
        set_line = (
            f'if (!newHeaders.has("{hname}")) newHeaders.set("{hname}", "{hval}");'
            if preserve else
            f'newHeaders.set("{hname}", "{hval}");'
        )
        code = dedent(f"""
        addEventListener("fetch", event => {{
          event.respondWith(handleRequest(event.request));
        }});

        async function handleRequest(request) {{
          const response = await fetch(request);
          const newHeaders = new Headers(response.headers);
          {set_line}

          return new Response(response.body, {{
            status: response.status,
            statusText: response.statusText,
            headers: newHeaders
          }});
        }}
        """).strip()
        _emit_generated(code, "custom_header.js")
    _end_card()

# --------------------------
# Remote Authentication
# --------------------------
# replace page_remote_auth in edge_templates.py with this
def page_remote_auth(st: st.__class__):
    _card("Remote Authentication", "Generate EdgeFunction for remote token introspection / defense check. Generated JS includes English usage comments at the top.")

    col1, col2 = st.columns([2,1])
    with col1:
        def_field = st.text_input("Field in defense JSON that indicates success", "valid")
        success_value = st.text_input("Success value (as string comparison)", "true")
        fail_policy = st.selectbox("If defense unreachable", ["Fail-Open (allow)", "Fail-Closed (block)"], index=1)
        pass_when_no_header = st.checkbox("If no Authorization header -> allow (full pass)", True)
        block_message = st.text_input("Message shown when blocked", "Unauthorized")
    with col2:
        st.markdown("### Quick preview")
        st.caption("Generated JS will include a top comment block that documents usage in plain English.")

    if st.button("Generate Remote-Auth EdgeFunction"):
        fail_open_bool = (fail_policy == "Fail-Open (allow)")
        code = dedent(f"""
        /*
         Remote Authentication EdgeFunction (generated)
         -----------------------
         Usage / Mechanism (English):
         1) Incoming request is inspected for the 'Authorization' header.
            - If NO Authorization header:
              -> full pass (forward to origin) if configured to allow no-header.
              -> otherwise treated as unauthorized (401).
         2) If Authorization header exists:
            -> Strip "Bearer " prefix and send token + minimal context to defense service via POST.
            -> Defense must return JSON. Expected field: "{def_field}".
            -> If String(js["{def_field}"]) === String({json.dumps(success_value)}) then token is valid.
               -> Forward original request to origin.
            -> Else respond 401 Unauthorized. If defense returns 'reason' it is appended to response body.
         3) If defense is unreachable or returns invalid JSON:
            -> Behavior depends on policy. Fail-Open = forward to origin. Fail-Closed = return 502.
         4) Forwarding preserves method, body and most headers. Hop-by-hop headers are removed.
         5) Security considerations (not enforced by this template):
            - Use TLS and mutual auth between Edge and defense.
            - Rate-limit introspection calls and consider short caching on valid tokens.
            - Do not log raw tokens.
         Replace DEFENSE_URL and ORIGIN_URL when deploying or set them as environment variables on your edge platform.
        */

        const DEFENSE_URL = "https://your-defense.example/introspect"; // replace or set as env
        const ORIGIN_URL  = "https://your-origin.example"; // replace or set as env
        const FAIL_OPEN = {str(fail_open_bool).lower()};
        const ALLOW_NO_HEADER = {str(pass_when_no_header).lower()};

        export default {{
          async fetch(request, env, ctx) {{
            // normalize headers
            const hdrObj = {{}};
            for (const [k, v] of request.headers) hdrObj[k.toLowerCase()] = v;

            const authHeader = hdrObj["authorization"];

            // No Authorization header: full pass if configured
            if (!authHeader) {{
              if (ALLOW_NO_HEADER) return forwardToOrigin(request);
              return new Response("{block_message}", {{ status: 401, headers: {{ "content-type": "text/plain; charset=utf-8" }} }});
            }}

            const token = authHeader.replace(/^Bearer\\s+/i, "");

            // Prepare payload for defense service
            const payload = {{
              token,
              method: request.method,
              path: new URL(request.url).pathname + new URL(request.url).search,
              headers: {{
                // include only minimal useful headers to avoid leakage
                "x-forwarded-for": hdrObj["x-forwarded-for"] || hdrObj["cf-connecting-ip"] || "",
                "user-agent": hdrObj["user-agent"] || ""
              }}
            }};

            let defenseResp;
            try {{
              defenseResp = await fetch(DEFENSE_URL, {{
                method: "POST",
                headers: {{ "content-type": "application/json" }},
                body: JSON.stringify(payload)
              }});
            }} catch (e) {{
              // Defense unreachable
              if (FAIL_OPEN) return forwardToOrigin(request);
              return new Response("Auth service unreachable", {{ status: 502 }});
            }}

            let js;
            try {{
              js = await defenseResp.json();
            }} catch (e) {{
              if (FAIL_OPEN) return forwardToOrigin(request);
              return new Response("Invalid response from auth service", {{ status: 502 }});
            }}

            // Interpret defense result
            if (js && String(js["{def_field}"]) === String({json.dumps(success_value)})) {{
              // allowed
              return forwardToOrigin(request);
            }}

            const bodyMsg = js && js.reason ? `Unauthorized: ${{js.reason}}` : "{block_message}";
            return new Response(bodyMsg, {{ status: 401, headers: {{ "content-type": "text/plain; charset=utf-8" }} }});
          }}
        }};

        // helper to forward request to origin preserving method, body and headers
        async function forwardToOrigin(origRequest) {{
          const url = new URL(origRequest.url);
          const originFull = ORIGIN_URL + url.pathname + url.search;

          let body = null;
          try {{
            if (origRequest.method !== "GET" && origRequest.method !== "HEAD") {{
              body = await origRequest.arrayBuffer();
            }}
          }} catch (e) {{
            body = null;
          }}

          const newHeaders = new Headers();
          for (const [k, v] of origRequest.headers) {{
            const lk = k.toLowerCase();
            if (["connection","keep-alive","proxy-authenticate","proxy-authorization","te","trailers","transfer-encoding","upgrade"].includes(lk)) continue;
            newHeaders.set(k, v);
          }}

          if (!newHeaders.has("x-forwarded-for")) {{
            const remoteIp = (origRequest.headers.get("cf-connecting-ip") || origRequest.headers.get("x-real-ip") || "");
            if (remoteIp) newHeaders.set("x-forwarded-for", remoteIp);
          }}

          const originReq = new Request(originFull, {{
            method: origRequest.method,
            headers: newHeaders,
            body: body,
            redirect: "manual"
          }});
          return fetch(originReq);
        }}
        """).strip()

        _emit_generated(code, "edgefunction-remote-auth.js")

        # also show short usage bullets in UI
        st.markdown("### Usage summary (English)")
        st.markdown("- If no Authorization header: full pass (forwarded) if enabled; otherwise 401.")
        st.markdown(f"- If Authorization header present: token is introspected by defense service. Field '{def_field}' must equal {json.dumps(success_value)} to allow.")
        st.markdown(f"- Defense unreachable -> {'allow (Fail-Open)' if fail_open_bool else 'block (Fail-Closed)'}")
        st.markdown("- Forward preserves method, headers and body. Hop-by-hop headers removed.")
    _end_card()

# --------------------------
# Rate Limiting
# --------------------------
def page_rate_limiting(st: st.__class__):
    _card("Rate Limiting", "Implement rate limiting to prevent abuse and DDoS attacks.")
    
    col1, col2 = st.columns(2)
    with col1:
        requests_per_minute = st.number_input("Requests per minute", 1, 1000, 60)
        burst_limit = st.number_input("Burst limit", 1, 100, 10)
        block_duration = st.number_input("Block duration (seconds)", 60, 3600, 300)
    
    with col2:
        rate_limit_by = st.selectbox("Rate limit by", ["IP Address", "User-Agent", "Country", "Custom Header"])
        custom_header = st.text_input("Custom header name", "X-User-ID") if rate_limit_by == "Custom Header" else ""
        block_message = st.text_input("Block message", "Rate limit exceeded. Please try again later.")
    
    if st.button("Generate Rate Limiting Worker"):
        rate_limit_key = "request.headers.get('cf-connecting-ip')" if rate_limit_by == "IP Address" else \
                        "request.headers.get('user-agent')" if rate_limit_by == "User-Agent" else \
                        "request.cf.country" if rate_limit_by == "Country" else \
                        f"request.headers.get('{custom_header}')" if rate_limit_by == "Custom Header" else "request.headers.get('cf-connecting-ip')"
        
        code = dedent(f"""
        // Rate Limiting EdgeFunction
        const RATE_LIMIT = {requests_per_minute};
        const BURST_LIMIT = {burst_limit};
        const BLOCK_DURATION = {block_duration} * 1000; // Convert to milliseconds

        async function handleRequest(request) {{
          const key = {rate_limit_key};
          
          if (!key) {{
            return new Response("Unable to identify client", {{ status: 400 }});
          }}
          
          // Get current timestamp
          const now = Date.now();
          
          // Get stored data from KV store (you need to set up KV namespace)
          const stored = await RATE_LIMIT_KV.get(key);
          let data = stored ? JSON.parse(stored) : {{ count: 0, resetTime: now + 60000, blocked: false, blockUntil: 0 }};
          
          // Check if currently blocked
          if (data.blocked && now < data.blockUntil) {{
            return new Response("{block_message}", {{
              status: 429,
              headers: {{
                "Retry-After": Math.ceil((data.blockUntil - now) / 1000),
                "X-RateLimit-Limit": RATE_LIMIT,
                "X-RateLimit-Remaining": 0,
                "X-RateLimit-Reset": Math.ceil(data.resetTime / 1000)
              }}
            }});
          }}

          // Reset counter if time window has passed
          if (now > data.resetTime) {{
            data.count = 0;
            data.resetTime = now + 60000;
            data.blocked = false;
          }}
          
          // Check burst limit
          if (data.count >= BURST_LIMIT) {{
            data.blocked = true;
            data.blockUntil = now + BLOCK_DURATION;
            await RATE_LIMIT_KV.put(key, JSON.stringify(data));
            
            return new Response("{block_message}", {{
              status: 429,
              headers: {{
                "Retry-After": Math.ceil(BLOCK_DURATION / 1000),
                "X-RateLimit-Limit": RATE_LIMIT,
                "X-RateLimit-Remaining": 0,
                "X-RateLimit-Reset": Math.ceil(data.resetTime / 1000)
              }}
            }});
          }}
          
          // Increment counter
          data.count++;
          
          // Check rate limit
          if (data.count > RATE_LIMIT) {{
            data.blocked = true;
            data.blockUntil = now + BLOCK_DURATION;
            await RATE_LIMIT_KV.put(key, JSON.stringify(data));
            
            return new Response("{block_message}", {{
              status: 429,
              headers: {{
                "Retry-After": Math.ceil(BLOCK_DURATION / 1000),
                "X-RateLimit-Limit": RATE_LIMIT,
                "X-RateLimit-Remaining": 0,
                "X-RateLimit-Reset": Math.ceil(data.resetTime / 1000)
              }}
            }});
          }}

          // Store updated data
          await RATE_LIMIT_KV.put(key, JSON.stringify(data));
          
          // Forward request to origin
          const response = await fetch(request);
          
          // Add rate limit headers
          const newHeaders = new Headers(response.headers);
          newHeaders.set("X-RateLimit-Limit", RATE_LIMIT);
          newHeaders.set("X-RateLimit-Remaining", Math.max(0, RATE_LIMIT - data.count));
          newHeaders.set("X-RateLimit-Reset", Math.ceil(data.resetTime / 1000));
          
          return new Response(response.body, {{
            status: response.status,
            statusText: response.statusText,
            headers: newHeaders
          }});
        }}
        
        addEventListener("fetch", event => {{
          event.respondWith(handleRequest(event.request));
        }});
        """).strip()
        
        _emit_generated(code, "rate_limiting.js")
        
        st.info("**Note:** You need to set up a KV namespace named 'RATE_LIMIT_KV' in your Cloudflare Workers dashboard.")
    
    _end_card()

# --------------------------
# Security Headers
# --------------------------
def page_security_headers(st: st.__class__):
    _card("Security Headers", "Add comprehensive security headers to protect against common web vulnerabilities.")
    
    st.markdown("### Security Headers Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        csp_enabled = st.checkbox("Content Security Policy (CSP)", True)
        hsts_enabled = st.checkbox("HTTP Strict Transport Security (HSTS)", True)
        xss_protection = st.checkbox("X-XSS-Protection", True)
        content_type_nosniff = st.checkbox("X-Content-Type-Options", True)
        frame_options = st.checkbox("X-Frame-Options", True)
    
    with col2:
        referrer_policy = st.checkbox("Referrer-Policy", True)
        permissions_policy = st.checkbox("Permissions-Policy", True)
        cross_origin_embedder = st.checkbox("Cross-Origin-Embedder-Policy", False)
        cross_origin_opener = st.checkbox("Cross-Origin-Opener-Policy", False)
        cross_origin_resource = st.checkbox("Cross-Origin-Resource-Policy", False)
    
    # CSP Configuration
    if csp_enabled:
        st.markdown("#### Content Security Policy (CSP)")
        csp_default_src = st.text_input("default-src", "self", help="Default source for resources")
        csp_script_src = st.text_input("script-src", "self 'unsafe-inline'", help="Allowed script sources")
        csp_style_src = st.text_input("style-src", "self 'unsafe-inline'", help="Allowed style sources")
        csp_img_src = st.text_input("img-src", "self data: https:", help="Allowed image sources")
        csp_connect_src = st.text_input("connect-src", "self", help="Allowed connect sources")
        csp_font_src = st.text_input("font-src", "self", help="Allowed font sources")
        csp_object_src = st.text_input("object-src", "none", help="Allowed object sources")
        csp_base_uri = st.text_input("base-uri", "self", help="Allowed base URIs")
        csp_form_action = st.text_input("form-action", "self", help="Allowed form actions")
        csp_frame_ancestors = st.text_input("frame-ancestors", "none", help="Allowed frame ancestors")
    
    # HSTS Configuration
    if hsts_enabled:
        st.markdown("#### HSTS Configuration")
        hsts_max_age = st.number_input("HSTS Max-Age (seconds)", 31536000, 63072000, 31536000, help="How long browsers should remember to use HTTPS")
        hsts_include_subdomains = st.checkbox("Include Subdomains", True)
        hsts_preload = st.checkbox("Preload", False)
    
    # Frame Options Configuration
    if frame_options:
        st.markdown("#### X-Frame-Options Configuration")
        frame_options_value = st.selectbox("Frame Options", ["DENY", "SAMEORIGIN", "ALLOW-FROM"], index=1)
        frame_options_uri = st.text_input("Allow-From URI", "https://example.com") if frame_options_value == "ALLOW-FROM" else ""
    
    if st.button("Generate Security Headers Worker"):
        headers = []
        
        # CSP
        if csp_enabled:
            csp_directives = []
            if csp_default_src: csp_directives.append(f"default-src {csp_default_src}")
            if csp_script_src: csp_directives.append(f"script-src {csp_script_src}")
            if csp_style_src: csp_directives.append(f"style-src {csp_style_src}")
            if csp_img_src: csp_directives.append(f"img-src {csp_img_src}")
            if csp_connect_src: csp_directives.append(f"connect-src {csp_connect_src}")
            if csp_font_src: csp_directives.append(f"font-src {csp_font_src}")
            if csp_object_src: csp_directives.append(f"object-src {csp_object_src}")
            if csp_base_uri: csp_directives.append(f"base-uri {csp_base_uri}")
            if csp_form_action: csp_directives.append(f"form-action {csp_form_action}")
            if csp_frame_ancestors: csp_directives.append(f"frame-ancestors {csp_frame_ancestors}")
            
            headers.append(f'    "Content-Security-Policy": "{"; ".join(csp_directives)}"')
        
        # HSTS
        if hsts_enabled:
            hsts_value = f"max-age={hsts_max_age}"
            if hsts_include_subdomains: hsts_value += "; includeSubDomains"
            if hsts_preload: hsts_value += "; preload"
            headers.append(f'    "Strict-Transport-Security": "{hsts_value}"')
        
        # Other headers
        if xss_protection: headers.append('    "X-XSS-Protection": "1; mode=block"')
        if content_type_nosniff: headers.append('    "X-Content-Type-Options": "nosniff"')
        if frame_options: 
            frame_value = frame_options_value
            if frame_options_value == "ALLOW-FROM" and frame_options_uri:
                frame_value = f"ALLOW-FROM {frame_options_uri}"
            headers.append(f'    "X-Frame-Options": "{frame_value}"')
        if referrer_policy: headers.append('    "Referrer-Policy": "strict-origin-when-cross-origin"')
        if permissions_policy: headers.append('    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"')
        if cross_origin_embedder: headers.append('    "Cross-Origin-Embedder-Policy": "require-corp"')
        if cross_origin_opener: headers.append('    "Cross-Origin-Opener-Policy": "same-origin"')
        if cross_origin_resource: headers.append('    "Cross-Origin-Resource-Policy": "same-origin"')
        
        code = dedent(f"""
        // Security Headers EdgeFunction
        async function handleRequest(request) {{
          const response = await fetch(request);
          const newHeaders = new Headers(response.headers);
          
          // Add security headers
          const securityHeaders = {{
{chr(10).join(headers)}
          }};
          
          // Apply security headers
          for (const [key, value] of Object.entries(securityHeaders)) {{
            newHeaders.set(key, value);
          }}
          
          return new Response(response.body, {{
            status: response.status,
            statusText: response.statusText,
            headers: newHeaders
          }});
        }}
        
        addEventListener("fetch", event => {{
          event.respondWith(handleRequest(event.request));
        }});
        """).strip()
        
        _emit_generated(code, "security_headers.js")
    
    _end_card()

# --------------------------
# IP Geolocation
# --------------------------
def page_ip_geolocation(st: st.__class__):
    _card("IP Geolocation", "Block or redirect traffic based on geographic location.")
    
    col1, col2 = st.columns(2)
    with col1:
        action = st.selectbox("Action", ["Block", "Redirect", "Add Header", "Log Only"])
        countries = st.multiselect("Target Countries", [
            "US", "CN", "RU", "IR", "KP", "SY", "CU", "VE", "MM", "BY"
        ], help="Select countries to apply action to")
    
    with col2:
        redirect_url = st.text_input("Redirect URL", "https://example.com/blocked") if action == "Redirect" else ""
        header_name = st.text_input("Header Name", "X-Country-Code") if action == "Add Header" else ""
        block_message = st.text_input("Block Message", "Access denied from your location") if action == "Block" else ""
    
    if st.button("Generate IP Geolocation Worker"):
        code = dedent(f"""
        // IP Geolocation EdgeFunction
        const TARGET_COUNTRIES = {countries};
        const ACTION = "{action}";
        const REDIRECT_URL = "{redirect_url}";
        const HEADER_NAME = "{header_name}";
        const BLOCK_MESSAGE = "{block_message}";
        
        async function handleRequest(request) {{
          const country = request.cf.country;
          
          if (TARGET_COUNTRIES.includes(country)) {{
            if (ACTION === "Block") {{
              return new Response(BLOCK_MESSAGE, {{
                status: 403,
                headers: {{ "Content-Type": "text/plain" }}
              }});
            }} else if (ACTION === "Redirect") {{
              return Response.redirect(REDIRECT_URL, 302);
            }} else if (ACTION === "Add Header") {{
              const response = await fetch(request);
              const newHeaders = new Headers(response.headers);
              newHeaders.set(HEADER_NAME, country);
              return new Response(response.body, {{
                status: response.status,
                statusText: response.statusText,
                headers: newHeaders
              }});
            }} else if (ACTION === "Log Only") {{
              console.log(`Request from {{country}} - {{request.url}}`);
            }}
          }}
          
          return fetch(request);
        }}
        
        addEventListener("fetch", event => {{
          event.respondWith(handleRequest(event.request));
        }});
        """).strip()
        
        _emit_generated(code, "ip_geolocation.js")
    
    _end_card()

# --------------------------
# Request Logging
# --------------------------
def page_request_logging(st: st.__class__):
    _card("Request Logging", "Log requests for monitoring, analytics, and security analysis.")
    
    col1, col2 = st.columns(2)
    with col1:
        log_level = st.selectbox("Log Level", ["All", "Errors Only", "Suspicious Only"])
        log_headers = st.checkbox("Log Headers", True)
        log_body = st.checkbox("Log Request Body", False)
        log_response = st.checkbox("Log Response", False)
    
    with col2:
        log_destination = st.selectbox("Log Destination", ["Console", "External API", "KV Store"])
        api_url = st.text_input("API URL", "https://api.example.com/logs") if log_destination == "External API" else ""
        api_key = st.text_input("API Key", "") if log_destination == "External API" else ""
        kv_namespace = st.text_input("KV Namespace", "REQUEST_LOGS") if log_destination == "KV Store" else ""
    
    # Suspicious patterns
    st.markdown("#### Suspicious Patterns")
    suspicious_patterns = st.text_area("Suspicious Patterns (one per line)", 
                                      "sqlmap\nnikto\nnmap\nmasscan\nzap\nburp", 
                                      help="Patterns to detect in User-Agent or request body")
    
    if st.button("Generate Request Logging Worker"):
        patterns = suspicious_patterns.split('\n') if suspicious_patterns else []
        
        code = dedent(f"""
        // Request Logging EdgeFunction
        const LOG_LEVEL = "{log_level}";
        const LOG_HEADERS = {str(log_headers).lower()};
        const LOG_BODY = {str(log_body).lower()};
        const LOG_RESPONSE = {str(log_response).lower()};
        const LOG_DESTINATION = "{log_destination}";
        const API_URL = "{api_url}";
        const API_KEY = "{api_key}";
        const KV_NAMESPACE = "{kv_namespace}";
        const SUSPICIOUS_PATTERNS = {patterns};
        
        async function handleRequest(request) {{
          const startTime = Date.now();
          const response = await fetch(request);
          const endTime = Date.now();
          
          // Check if request is suspicious
          const isSuspicious = checkSuspicious(request);
          
          // Determine if we should log
          let shouldLog = false;
          if (LOG_LEVEL === "All") {{
            shouldLog = true;
          }} else if (LOG_LEVEL === "Errors Only") {{
            shouldLog = response.status >= 400;
          }} else if (LOG_LEVEL === "Suspicious Only") {{
            shouldLog = isSuspicious;
          }}
          
          if (shouldLog) {{
            const logEntry = {{
              timestamp: new Date().toISOString(),
              method: request.method,
              url: request.url,
              status: response.status,
              responseTime: endTime - startTime,
              ip: request.headers.get('cf-connecting-ip'),
              userAgent: request.headers.get('user-agent'),
              country: request.cf.country,
              suspicious: isSuspicious,
              headers: LOG_HEADERS ? Object.fromEntries(request.headers) : {{}},
              body: LOG_BODY ? await request.clone().text() : null,
              response: LOG_RESPONSE ? await response.clone().text() : null
            }};
            
            await logRequest(logEntry);
          }}
          
          return response;
        }}
        
        function checkSuspicious(request) {{
          const userAgent = request.headers.get('user-agent') || '';
          const url = request.url;
          
          return SUSPICIOUS_PATTERNS.some(pattern => 
            userAgent.toLowerCase().includes(pattern.toLowerCase()) ||
            url.toLowerCase().includes(pattern.toLowerCase())
          );
        }}
        
        async function logRequest(logEntry) {{
          if (LOG_DESTINATION === "Console") {{
            console.log(JSON.stringify(logEntry));
          }} else if (LOG_DESTINATION === "External API") {{
            try {{
              await fetch(API_URL, {{
                method: 'POST',
                headers: {{
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${{API_KEY}}`
                }},
                body: JSON.stringify(logEntry)
              }});
            }} catch (error) {{
              console.error('Failed to send log to API:', error);
            }}
          }} else if (LOG_DESTINATION === "KV Store") {{
            try {{
              const key = `log-${{Date.now()}}-${{Math.random().toString(36).substr(2, 9)}}`;
              await KV_NAMESPACE.put(key, JSON.stringify(logEntry));
            }} catch (error) {{
              console.error('Failed to store log in KV:', error);
            }}
          }}
        }}
        
        addEventListener("fetch", event => {{
          event.respondWith(handleRequest(event.request));
        }});
        """).strip()
        
        _emit_generated(code, "request_logging.js")
        
        if log_destination == "KV Store":
            st.info("**Note:** You need to set up a KV namespace named 'REQUEST_LOGS' in your Cloudflare Workers dashboard.")
    
    _end_card()

# --------------------------
# A/B Testing
# --------------------------
def page_ab_testing(st: st.__class__):
    _card("A/B Testing", "Implement A/B testing to serve different content to different users.")
    
    col1, col2 = st.columns(2)
    with col1:
        test_name = st.text_input("Test Name", "homepage_redesign")
        traffic_split = st.slider("Traffic Split (%)", 0, 100, 50, help="Percentage of traffic to send to variant B")
        test_duration = st.number_input("Test Duration (days)", 1, 365, 30)
        cookie_name = st.text_input("Cookie Name", "ab_test")
    
    with col2:
        variant_a_url = st.text_input("Variant A URL", "https://example.com")
        variant_b_url = st.text_input("Variant B URL", "https://example.com/variant-b")
        fallback_url = st.text_input("Fallback URL", "https://example.com")
        sticky_sessions = st.checkbox("Sticky Sessions", True, help="Keep users in the same variant")
    
    # Advanced options
    st.markdown("#### Advanced Options")
    col1, col2 = st.columns(2)
    with col1:
        exclude_bots = st.checkbox("Exclude Bots", True)
        exclude_mobile = st.checkbox("Exclude Mobile", False)
        exclude_countries = st.multiselect("Exclude Countries", ["CN", "RU", "IR"])
    
    with col2:
        include_paths = st.text_area("Include Paths (one per line)", "/\n/about\n/contact", help="Only run test on these paths")
        exclude_paths = st.text_area("Exclude Paths (one per line)", "/admin\n/api", help="Exclude these paths from test")
    
    if st.button("Generate A/B Testing Worker"):
        include_paths_list = include_paths.split('\n') if include_paths else ['/']
        exclude_paths_list = exclude_paths.split('\n') if exclude_paths else []
        
        code = dedent(f"""
        // A/B Testing EdgeFunction
        const TEST_NAME = "{test_name}";
        const TRAFFIC_SPLIT = {traffic_split};
        const TEST_DURATION = {test_duration};
        const COOKIE_NAME = "{cookie_name}";
        const VARIANT_A_URL = "{variant_a_url}";
        const VARIANT_B_URL = "{variant_b_url}";
        const FALLBACK_URL = "{fallback_url}";
        const STICKY_SESSIONS = {str(sticky_sessions).lower()};
        const EXCLUDE_BOTS = {str(exclude_bots).lower()};
        const EXCLUDE_MOBILE = {str(exclude_mobile).lower()};
        const EXCLUDE_COUNTRIES = {exclude_countries};
        const INCLUDE_PATHS = {include_paths_list};
        const EXCLUDE_PATHS = {exclude_paths_list};
        
        async function handleRequest(request) {{
          const url = new URL(request.url);
          const path = url.pathname;
          
          // Check if path should be included/excluded
          if (!INCLUDE_PATHS.some(p => path.startsWith(p)) || EXCLUDE_PATHS.some(p => path.startsWith(p))) {{
            return fetch(request);
          }}
          
          // Check if user should be excluded
          if (shouldExcludeUser(request)) {{
            return fetch(request);
          }}
          
          // Check if user already has a variant assigned
          let variant = null;
          if (STICKY_SESSIONS) {{
            const cookie = request.headers.get('Cookie');
            if (cookie) {{
              const match = cookie.match(new RegExp(`${{COOKIE_NAME}}=([AB])`));
              if (match) {{
                variant = match[1];
              }}
            }}
          }}
          
          // Assign variant if not already assigned
          if (!variant) {{
            const random = Math.random() * 100;
            variant = random < TRAFFIC_SPLIT ? 'B' : 'A';
          }}
          
          // Determine target URL
          let targetUrl;
          if (variant === 'A') {{
            targetUrl = VARIANT_A_URL;
          }} else {{
            targetUrl = VARIANT_B_URL;
          }}
          
          // Create new request to target URL
          const newRequest = new Request(targetUrl, {{
            method: request.method,
            headers: request.headers,
            body: request.body
          }});
          
          const response = await fetch(newRequest);
          
          // Add variant cookie if sticky sessions enabled
          if (STICKY_SESSIONS) {{
            const newHeaders = new Headers(response.headers);
            newHeaders.set('Set-Cookie', `${{COOKIE_NAME}}=${{variant}}; Path=/; Max-Age=${{TEST_DURATION * 24 * 60 * 60}}`);
            return new Response(response.body, {{
              status: response.status,
              statusText: response.statusText,
              headers: newHeaders
            }});
          }}

          return response;
        }}
        
        function shouldExcludeUser(request) {{
          const userAgent = request.headers.get('user-agent') || '';
          const country = request.cf.country;
          
          // Exclude bots
          if (EXCLUDE_BOTS && isBot(userAgent)) {{
            return true;
          }}
          
          // Exclude mobile
          if (EXCLUDE_MOBILE && isMobile(userAgent)) {{
            return true;
          }}
          
          // Exclude countries
          if (EXCLUDE_COUNTRIES.includes(country)) {{
            return true;
          }}
          
          return false;
        }}
        
        function isBot(userAgent) {{
          const botPatterns = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python', 'java'];
          return botPatterns.some(pattern => userAgent.toLowerCase().includes(pattern));
        }}
        
        function isMobile(userAgent) {{
          const mobilePatterns = ['mobile', 'android', 'iphone', 'ipad', 'blackberry', 'windows phone'];
          return mobilePatterns.some(pattern => userAgent.toLowerCase().includes(pattern));
        }}
        
        addEventListener("fetch", event => {{
          event.respondWith(handleRequest(event.request));
        }});
        """).strip()
        
        _emit_generated(code, "ab_testing.js")

    _end_card()