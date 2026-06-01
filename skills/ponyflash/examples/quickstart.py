"""PonyFlash SDK — end-to-end quickstart.

Run:
    pip install ponyflash
    export PONYFLASH_API_KEY="rk_xxx"
    python quickstart.py
"""

from ponyflash import PonyFlash, InsufficientCreditsError

pony_flash = PonyFlash()

# ── Check balance ──
balance = pony_flash.account.credits()
print(f"Credit balance: {balance.balance} {balance.currency}")

# ── List models ──
page = pony_flash.models.list()
for m in page.items:
    print(f"  {m.id} ({m.type})")

# ── Generate an image ──
try:
    gen = pony_flash.images.generate(
        model="nanobanana-pro",
        prompt="A magical forest with glowing mushrooms",
        size="2K",
    )
    print(f"Image URL: {gen.url}")
    print(f"Credits used: {gen.credits}")
except InsufficientCreditsError as e:
    print(f"Not enough credits (balance={e.balance}, required={e.required})")
    link = pony_flash.account.recharge()
    print(f"Recharge at: {link.recharge_url}")

# ── Generate a video ──
try:
    gen = pony_flash.video.generate(
        model="seedance-1.5-pro",
        prompt="A timelapse of clouds moving over a mountain",
        duration=5,
    )
    print(f"Video URL: {gen.url}")
    print(f"Credits used: {gen.credits}")
except InsufficientCreditsError as e:
    print(f"Not enough credits: {e}")

# ── Generate speech ──
try:
    gen = pony_flash.speech.generate(
        model="speech-2.8-hd",
        input="Welcome to PonyFlash, the AI media generation platform.",
        voice="English_Graceful_Lady",
    )
    print(f"Speech URL: {gen.url}")
except InsufficientCreditsError as e:
    print(f"Not enough credits: {e}")

# ── Generate music ──
try:
    gen = pony_flash.music.generate(
        model="music-2.5",
        prompt="A calm acoustic guitar melody",
        instrumental=True,
        duration=30,
    )
    print(f"Music URL: {gen.url}")
except InsufficientCreditsError as e:
    print(f"Not enough credits: {e}")
