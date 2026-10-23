# POV Generator

A sales rep types in an account name. A few minutes later they have a full point of view on that account, ready to open a conversation with.

I built this in April 2026 while running outbound for JumpCloud in APAC. Writing a good POV for a focus account took a rep an hour or more of research. This does the research for them, live on the web, and puts it into the structure I used to coach my team on.

## What you get back

1. **Company overview.** What they do, how big they are, recent strategic moves.
2. **Key executives.** Two or three decision makers, with researched details.
3. **Industry context and risk.** Identity and security stats for their sector, and incidents at peers.
4. **Proof point.** The most relevant customer story for this account.
5. **Point of view.** A sharp two or three sentence narrative, ending in a business question.
6. **Who to target.** Eight to ten titles, and why each one should care.
7. **First email.** A personalised cold email with a subject line, under 150 words.

The POV structure comes from the one I used at Rubrik, rebuilt for JumpCloud's identity and device management product.

## How it works

A small Flask web app (Flask is a Python tool for building websites). The rep fills in a form. The app sends the account to Claude with web search turned on, so the research is current, not from memory. Claude returns structured results, and the app lays them out as a POV page.

## Run it yourself

```
pip install -r requirements.txt
cp .env.example .env        # then add your Anthropic API key
python app.py
```

Open http://localhost:5000.

Built by [Vandana Agarwal Nik](https://vandanaagarwal.in), with Claude.
