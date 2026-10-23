import json
import os
import re

import anthropic
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

JUMPCLOUD_KNOWLEDGE = """
JumpCloud is an open directory platform that centralizes identity, access, and device management
in a single cloud-based platform. It replaces the fragmented stack of on-premises Active
Directory + separate MDM + separate SSO tools.

KEY PRODUCTS & CAPABILITIES:
- Directory Platform: Cloud-based LDAP/AD replacement, single source of truth for all identities
- SSO (Single Sign-On): 700+ pre-built app connectors (Google Workspace, Salesforce, AWS, GitHub, Slack, etc.)
- MFA / Passwordless: TOTP, push notifications, hardware keys (YubiKey), JumpCloud Go™ (device-bound passkeys)
- MDM: Cross-OS device management — macOS, Windows, Linux, iOS, Android, ChromeOS — from one console
- Zero Trust: Conditional access policies, device trust verification, location/context-aware access
- Patch Management: Automated OS and third-party application patching across all OS types
- Password Manager: Built-in enterprise password manager
- Cloud LDAP & Cloud RADIUS: Protocol infrastructure delivered as a service
- User Lifecycle Management: Automated onboarding/offboarding with HRIS integrations (Workday, BambooHR, Rippling, Gusto)
- SCIM provisioning: Auto-provision users into any SCIM-compatible app

COMMON PAIN POINTS JUMPCLOUD SOLVES:
- Identity sprawl: 4-6 disconnected tools (AD, Okta, JAMF, Meraki, VPN, etc.) with no single view
- Mixed OS environments: Mac + Windows + Linux fleet with no unified management
- Remote/hybrid workforce: Employees outside the perimeter who still need secure, verified access
- Active Directory technical debt: On-prem AD maintenance, DC patching, licensing costs
- Compliance gaps: SOC 2, ISO 27001, HIPAA, PCI-DSS requiring unified audit trails and access control
- Shadow IT: Unmanaged personal devices accessing corporate resources
- Credential-based attacks: Phishing, credential stuffing, MFA fatigue — 80%+ of breaches start with identity
- Slow onboarding/offboarding: Manual provisioning across systems taking hours per employee
- Tool consolidation: Average JumpCloud customer replaces 4.5 point solutions

COMPETITIVE CONTEXT:
- vs. Microsoft (AD + Intune + Entra ID): JumpCloud is OS-agnostic, simpler, and significantly
  cheaper for shops that are not Microsoft-only
- vs. Okta: JumpCloud adds device management; Okta is identity-only, requires separate MDM
- vs. JAMF/Kandji: Those only manage Apple devices; JumpCloud manages ALL OS types
- vs. Google Workspace admin: JumpCloud manages non-Google resources too

IDEAL CUSTOMER PROFILE:
- 100–5,000 employees (SMB to mid-market)
- Mixed OS environment (any combo of Mac, Windows, Linux)
- Remote-first or hybrid workforce
- High growth / frequent hiring and offboarding
- Moving to cloud / reducing on-premises footprint
- Industries: SaaS/Tech, Financial Services, Healthcare, Professional Services, Education, Nonprofit

SAMPLE PROOF POINTS:
1. Tech/SaaS: Netlify (~300 employees) replaced AD + JAMF + Okta with JumpCloud. IT tool spend
   down 60%, employee onboarding time from 2 hours to 15 minutes, full Mac + Linux fleet managed.
2. FinTech/Compliance: A fintech scaled from 200 to 1,500 employees remote-first. JumpCloud
   provided Zero Trust access, unified device trust, and helped them achieve SOC 2 Type II in
   months rather than years. Every device verified before accessing financial systems.
3. Healthcare/Mixed OS: A healthcare SaaS managing HIPAA compliance replaced 3 identity tools
   with JumpCloud. Single audit trail for all user access, automated offboarding (down from 4
   hours to 10 minutes), and MFA enforced on every resource.
4. General narrative: "We had a customer in [industry] managing identity through 4 separate tools
   with a mixed Mac/Windows/Linux fleet. When an employee left, offboarding took 6+ hours across
   systems — and they weren't confident everything was truly revoked. A lost device meant calling
   multiple vendors. With JumpCloud, offboarding dropped to 8 minutes with a single action, device
   wipe works regardless of OS, and Zero Trust policies mean a compromised credential alone can't
   get in if the device isn't trusted."

KEY STATISTICS TO USE:
- 80%+ of data breaches involve compromised credentials (Verizon DBIR)
- Average cost of a data breach: $4.45M (IBM 2023)
- Companies use an average of 130+ SaaS apps — each is an identity risk
- 68% of breaches involve a human element (phishing, stolen credentials, misuse)
- Mean time to identify a breach: 204 days (IBM)
- Employee offboarding: average company takes 4+ hours to fully deprovision access
"""

POV_SYSTEM_PROMPT = f"""You are an elite sales strategist for JumpCloud creating Point of View (POV)
documents for the APAC outbound sales team. A POV is a research-based account intelligence document
that helps sales reps personalize outreach and book first meetings.

{JUMPCLOUD_KNOWLEDGE}

You have access to web_search. Use it to research the target company thoroughly before writing
anything. Search for: company overview, key executives (CIO/CISO/VP IT/CTO), recent news,
industry-specific security incidents, and any public tech stack information.

Generate a POV with exactly these 7 fields as valid JSON:

{{
  "company": "3-5 sentences. What they do, how they make money, size (employees/locations/revenue
    if public), any recent strategic events (IPO, acquisition, rapid growth, new CTO hire, cloud
    migration announcement) that create a JumpCloud moment. Note any known tech stack hints.",

  "executive": "2-3 key decision makers. For each person: Name, Title, and something specific
    and personal — a quote from LinkedIn, a podcast they appeared on, an article they wrote, a
    conference they spoke at, or a stated priority. Make it feel researched, not generic.",

  "industry": "The identity and device security landscape in their specific industry. Include 1-2
    statistics about credential-based breaches or compliance requirements in this sector. Name a
    real, recent security incident at a peer/competitor company in the same industry to make it
    concrete. Explain why companies in this industry have specific needs that JumpCloud addresses.",

  "proof_point": "The most relevant JumpCloud customer proof point for this account. If there is
    a customer in the same industry, use them. Otherwise use 'We had a customer...' format. Must
    include: the pain they had, what JumpCloud solved, and a measurable outcome (time saved, tools
    replaced, compliance achieved, breach prevented).",

  "point_of_view": "2-3 sentences that weave together: company context + industry risk + JumpCloud
    fit + proof point outcome. End with a single provocative business question that connects their
    specific situation to a consequence they care about. This should be sharp enough to get a
    meeting if read aloud on a cold call.",

  "prospects": [
    "Title — Why they care about JumpCloud at this company",
    "Title — Why they care",
    "... (8-10 total, mix of C-level, VP, Director, Manager)"
  ],

  "first_email": {{
    "subject": "Subject line (under 8 words, no clickbait)",
    "body": "Email body (under 150 words). Rules: open with something specific from the executive
      section (quote, article, initiative — NOT 'I came across your profile'). One JumpCloud value
      prop tied to their situation. Reference the industry stat or proof point. Soft CTA: suggest
      a 15-minute conversation. Tone: peer-to-peer, like a fellow technology leader, not a vendor.
      No buzzwords. No 'I hope this email finds you well.' Sign off as from the rep."
  }}
}}

Return ONLY valid JSON — no markdown code blocks, no preamble, no explanation. Start with {{ and
end with }}.
"""


def call_with_continuation(messages: list, max_continuations: int = 10) -> str:
    """Call Claude with web search, handling pause_turn continuations."""
    last_text = ""
    for i in range(max_continuations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            system=POV_SYSTEM_PROMPT,
            messages=messages,
        )

        print(f"[iteration {i}] stop_reason={response.stop_reason}, blocks={[b.type for b in response.content]}")

        # Collect any text in this response
        for block in response.content:
            if block.type == "text" and block.text.strip():
                last_text = block.text
                print(f"[iteration {i}] text snippet: {block.text[:200]}")

        if response.stop_reason == "end_turn":
            return last_text

        if response.stop_reason == "pause_turn":
            # Server-side tool hit its iteration limit — append and continue
            messages.append({"role": "assistant", "content": response.content})
            continue

        # Unexpected stop reason — return whatever text we have
        return last_text

    return last_text


def extract_json(text: str) -> dict:
    """Extract and parse the first JSON object from text."""
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Find the outermost { ... }
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError("No valid JSON found in response")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    account_name = request.form.get("account_name", "").strip()
    linkedin_url = request.form.get("linkedin_url", "").strip()
    website = request.form.get("website", "").strip()
    industry_hint = request.form.get("industry_hint", "").strip()
    rep_name = request.form.get("rep_name", "Your Name").strip()

    if not account_name:
        return render_template("index.html", error="Account name is required.")

    context_parts = [f"Company: {account_name}"]
    if linkedin_url:
        context_parts.append(f"LinkedIn: {linkedin_url}")
    if website:
        context_parts.append(f"Website: {website}")
    if industry_hint:
        context_parts.append(f"Industry (hint): {industry_hint}")

    user_prompt = (
        "Research this company using web search, then generate the full POV as JSON.\n\n"
        + "\n".join(context_parts)
        + "\n\nSearch for: company overview and size, key IT/Security/Engineering executives "
        "and their public statements, industry-specific identity/security incidents and "
        "statistics, any known tech stack or cloud migration activity, recent funding or "
        "growth news. Then produce the JSON."
    )

    try:
        raw_text = call_with_continuation(
            messages=[{"role": "user", "content": user_prompt}]
        )
        pov = extract_json(raw_text)

        # Inject rep name into email sign-off if it's a placeholder
        if rep_name and rep_name != "Your Name":
            body = pov.get("first_email", {}).get("body", "")
            if body and "[rep]" in body.lower():
                pov["first_email"]["body"] = re.sub(
                    r"\[rep\]", rep_name, body, flags=re.IGNORECASE
                )

        return render_template(
            "result.html", pov=pov, account_name=account_name, rep_name=rep_name
        )

    except Exception as e:
        return render_template(
            "result.html", error=str(e), account_name=account_name, rep_name=rep_name
        )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
