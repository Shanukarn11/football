from __future__ import annotations
from datetime import date
from pydoc import describe
#from turtle import heading
#from turtle import heading
from unicodedata import category, name
from django.db import models
# from .storage import OverwriteStorage
from PIL import Image
from .storage import OverwriteStorage
# main/models.py (top of file)
  # optional but fine to keep
import re, secrets, string

from django.utils import timezone
from django.urls import reverse
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property   # <-- ADD/KEEP THIS ABOVE USE

# ikf/main/models.py


import re, secrets, string
from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property

# ------------ Registry of onboarding-capable fields (RepTemplate field names) ------------
# Edit this list anytime; labels are used in Admin checkboxes.
ONBOARDING_FIELDS = [
    ("rep_logo", "Rep logo"),
    ("rep_banner", "Rep banner"),
    ("players_bg", "Players background"),
    ("content", "Intro / long description (HTML)"),
    ("cities_of_operation", "Cities of operation"),
    ("website_url", "Website URL"),
    ("rep_opinion", "Rep opinion"),
    ("rep_category", "Rep category"),
    ("rep_category_brief", "Rep category brief"),
    ("csr_activities", "CSR activities"),
    ("ikf_activities", "IKF activities"),
    ("rep_founder", "Founder name"),
    ("theme", "Theme (enum)"),
    ("brand_color", "Brand color (#HEX)"),
    ("hero_bg_color", "Hero background color (#HEX)"),
    ("card_color", "Card color (#HEX)"),
    ("text_color", "Text color (#HEX)"),
    ("show_pills", "Show pills (toggle)"),
    ("show_stats", "Show stats (toggle)"),
    ("stat1_value", "Stat 1 value"),
    ("stat1_label", "Stat 1 label"),
    ("stat2_value", "Stat 2 value"),
    ("stat2_label", "Stat 2 label"),
    ("stat3_value", "Stat 3 value"),
    ("stat3_label", "Stat 3 label"),
    ("stat4_value", "Stat 4 value"),
    ("stat4_label", "Stat 4 label"),
    # Uncomment if you ever want login fields in onboarding:
    # ("username", "Username"),
    # ("password", "Password"),
]
FIELD_SLUGS = [s for s, _ in ONBOARDING_FIELDS]

# ---- Simple CSV (pipe-delimited) helpers so we don't rely on JSON ----
_DELIM = "|"

def _split_csv(s: str) -> list[str]:
    """Parse pipe-delimited string into a list, deduping while preserving order."""
    if not s:
        return []
    out, seen = [], set()
    for part in (p.strip() for p in s.split(_DELIM)):
        if part and part not in seen:
            seen.add(part)
            out.append(part)
    return out

def _split_csv_raw(s: str) -> list[str]:
    """Parse without dedup (used in validation to detect duplicates)."""
    if not s:
        return []
    return [p.strip() for p in s.split(_DELIM) if p.strip()]

def _join_csv(items) -> str:
    """Join items into pipe-delimited string, removing empties and duplicates."""
    out, seen = [], set()
    for x in (str(i).strip() for i in (items or [])):
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return _DELIM.join(out)


# =========================
# Plans / Status (no JSON)
# =========================
class Status(models.Model):
    """
    Plan config that the main admin edits: which fields are enabled and their order.
    Example names: premium / normal / basic
    """
    name = models.SlugField(
        max_length=32,
        unique=True,
        help_text="Lowercase key (e.g. premium, normal). Must match RepTemplate.next_status.",
    )
    label = models.CharField(
        max_length=64,
        default="",
        help_text="Friendly name shown to reps (how this plan appears in the UI).",
    )

    # Store enabled fields AND their order in one CSV string (pipe-delimited).
    # Example: "rep_logo|rep_banner|content"
    enabled_fields_csv = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = "Status (Plan)"
        verbose_name_plural = "Statuses (Plans)"

    def __str__(self) -> str:  # pragma: no cover
        return self.label or self.name

    # ----- properties your forms/admin use -----
    @property
    def enabled_fields(self) -> list[str]:
        return _split_csv(self.enabled_fields_csv)

    @enabled_fields.setter
    def enabled_fields(self, value) -> None:
        self.enabled_fields_csv = _join_csv(value)

    # For compatibility with previous API name:
    def ordered_enabled_fields(self) -> list[str]:
        return self.enabled_fields

    def export_schema(self) -> dict:
        ef = self.enabled_fields
        return {"enabled": list(ef), "order": list(ef)}

    # ----- validation + helpers -----
    def clean(self) -> None:
        # normalize name
        if self.name:
            self.name = (self.name or "").lower()

        raw = _split_csv_raw(self.enabled_fields_csv)

        # unknown fields?
        unknown = set(raw) - set(FIELD_SLUGS)
        if unknown:
            raise ValidationError(f"Unknown field(s): {', '.join(sorted(unknown))}")

        # duplicates?
        if len(raw) != len(set(raw)):
            raise ValidationError("enabled_fields contains duplicates; each field may appear once.")


# =========================
# Rep template + related
# =========================
class RepTemplate(models.Model):
    STATUS_CHOICES = [
        ("premium", "Premium"),
        ("normal", "Normal"),
        ("basic",  "Basic"),
        ("other",  "Other"),
    ]
    THEME_CHOICES = [
        ("yellow",  "Yellow / Navy (default)"),
        ("red",     "Red / Charcoal"),
        ("pink",    "Pink / Midnight"),
        ("emerald", "Emerald / Slate"),
        ("blue",    "Blue / Dark"),
        ("custom",  "Custom (use colors below)"),
    ]

    # identity
    rep_name      = models.CharField(max_length=100, default="Default Rep")
    rep_num       = models.CharField(max_length=100, default="0")
    template_link = models.CharField(max_length=100)

    # visuals
    rep_logo   = models.ImageField(upload_to="rep_logos/", blank=True, null=True)
    rep_banner = models.ImageField(upload_to="rep_banners/", blank=True, null=True)
    players_bg = models.ImageField(upload_to="rep_players_bg/", blank=True, null=True)

    # content / meta
    content             = models.TextField(blank=True, help_text="Intro/long description. HTML allowed.")
    next_status         = models.CharField(max_length=20, choices=STATUS_CHOICES)
    username            = models.CharField(max_length=100, blank=True, null=True)
    password            = models.CharField(max_length=100, blank=True, null=True)
    cities_of_operation = models.CharField(max_length=255, blank=True)
    website_url         = models.URLField(blank=True)
    rep_opinion         = models.TextField(blank=True)
    rep_category        = models.CharField(max_length=100, blank=True)
    rep_category_brief  = models.TextField(blank=True)
    csr_activities      = models.TextField(blank=True)
    ikf_activities      = models.TextField(blank=True)
    rep_founder         = models.CharField(max_length=120, blank=True)

    # theming / toggles
    theme        = models.CharField(max_length=20, choices=THEME_CHOICES, default="yellow")
    brand_color  = models.CharField(max_length=7, blank=True, help_text="#HEX, used when theme = custom")
    hero_bg_color= models.CharField(max_length=7, blank=True, help_text="#HEX, used when theme = custom")
    card_color   = models.CharField(max_length=7, blank=True, help_text="#HEX, used when theme = custom")
    text_color   = models.CharField(max_length=7, blank=True, help_text="#HEX, used when theme = custom")

    show_pills   = models.BooleanField(default=False)
    show_stats   = models.BooleanField(default=False)

    # editable stats
    stat1_value  = models.CharField(max_length=40, blank=True)
    stat1_label  = models.CharField(max_length=80, blank=True)
    stat2_value  = models.CharField(max_length=40, blank=True)
    stat2_label  = models.CharField(max_length=80, blank=True)
    stat3_value  = models.CharField(max_length=40, blank=True)
    stat3_label  = models.CharField(max_length=80, blank=True)
    stat4_value  = models.CharField(max_length=40, blank=True)
    stat4_label  = models.CharField(max_length=80, blank=True)

    # secure onboarding link token
    onboarding_token = models.CharField(max_length=24, blank=True, editable=False, unique=True)

    # submission & approval workflow
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(blank=True, null=True)
    is_locked    = models.BooleanField(default=False)

    is_approved = models.BooleanField(default=False, db_index=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="rep_approvals"
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # optional: keep a snapshot of the plan schema used at submit time
    onboarding_schema_snapshot = models.TextField(blank=True, null=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.rep_name} ({self.template_link})"

    @property
    def theme_class(self) -> str:
        return f"theme-{self.theme or 'yellow'}"

    @property
    def is_live(self) -> bool:
        return bool(self.is_approved)

    # Map string next_status -> Status instance
    @cached_property
    def plan(self) -> Optional["Status"]:
        try:
            return Status.objects.get(name=(self.next_status or "").lower())
        except Status.DoesNotExist:
            return None

    # token helpers
    def _gen_onboarding_token(self) -> str:
        base = re.sub(r"[^a-z0-9]", "", (self.rep_name or "rep").lower())[:4] or "rep"
        def rnd8() -> str:
            return "".join(secrets.choice(string.digits) for _ in range(8))
        token = (base + rnd8())[:24]
        Model = type(self)
        while Model.objects.filter(onboarding_token=token).exists():
            token = (base + rnd8())[:24]
        return token

    def save(self, *args, **kwargs) -> None:
        if not self.onboarding_token:
            self.onboarding_token = self._gen_onboarding_token()
        super().save(*args, **kwargs)

    # URLs (ensure you have matching urlpattern names in urls.py)
    def get_onboarding_path(self):
        return reverse("rep_onboarding", args=[self.onboarding_token])

    def get_onboarding_url(self, request):
        return request.build_absolute_uri(self.get_onboarding_path())

    def get_public_path(self):
        return reverse("rep_public", args=[self.template_link])

    def get_preview_path(self):
        return reverse("rep_preview", args=[self.onboarding_token])

    def get_preview_url(self, request):
        return request.build_absolute_uri(self.get_preview_path())

from django.db import models

class Career360Partner(models.Model):
    name = models.CharField(max_length=120, unique=True)
    logo = models.ImageField(upload_to="career360/partners/", blank=True, null=True)
    description = models.TextField()
    website_url = models.URLField(blank=True, null=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

from django.db import models
from django.urls import reverse

class MessageWeblink(models.Model):
    code = models.SlugField(max_length=60, unique=True)
    heading = models.CharField(max_length=200)
    heading_hi = models.CharField(max_length=200, blank=True)

    outro_en = models.TextField(blank=True)
    outro_hi = models.TextField(blank=True)

    message_en = models.TextField(blank=True)
    message_hi = models.TextField(blank=True)

    venue = models.TextField(blank=True)
    reporting_time = models.CharField(max_length=80, blank=True)
    event_date = models.CharField(max_length=80, blank=True)
    map_link = models.URLField(blank=True)

    guidelines_en = models.TextField(blank=True, help_text="One guideline per line.")
    guidelines_hi = models.TextField(blank=True, help_text="One guideline per line.")

    whatsapp_number = models.CharField(max_length=40, blank=True)
    consent_form_link = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.code} — {self.heading}"

    # ✅ THIS is what admin will use for "View page"
    def get_absolute_url(self):
        # If your public url is: http://localhost:8000/smseast/
        return reverse("message_weblink", kwargs={"code": self.code})

        # If your public url is: http://localhost:8000/weblink/smseast/
        # return reverse("message_weblink", kwargs={"code": self.code})

from django.db import models
from django.urls import reverse
import re


class ConsentNocWeblink(models.Model):
    # URL: /noc/<code>/
    code = models.SlugField(max_length=60, unique=True)

    # Watermark/logo (paste a full URL in admin)
    # Example: https://indiakhelofootball.com/static/images/ikf_watermark.png
    watermark_logo_url = models.URLField(blank=True)

    # Top headings
    title = models.CharField(max_length=250, default="", blank=True)

    event_name = models.CharField(max_length=250, blank=True)

    # Labels + values
    venue_label = models.CharField(max_length=50, default="Venue:")
    venue_value = models.TextField(blank=True)

    date_label = models.CharField(max_length=50, default="Date:")
    date_value = models.CharField(max_length=100, blank=True)

    # Full intro paragraph (store as one text field)
    intro_text = models.TextField(blank=True)

    # Section headings (backend controlled)
    player_details_heading = models.CharField(max_length=120, default="PLAYER DETAILS")
    declaration_heading = models.CharField(max_length=120, default="DECLARATION & CONSENT")
    guardian_heading = models.CharField(max_length=180, default="PARENT / GUARDIAN DECLARATION")

    # Player fields (backend controlled)
    # Put one per line:
    # Player Name:
    # Age / Date of Birth:
    # Parent / Guardian Name:
    player_fields = models.TextField(
        blank=True,
        help_text="One field per line. Example: Player Name:"
    )

    # Declaration lead line (backend controlled)
    declaration_lead = models.TextField(
        blank=True,
        help_text='Example: "By signing this NOC, the participant and/or parent/guardian confirms and agrees to the following:"'
    )

    # Declaration points from backend (one point per line)
    # You can paste numbered points OR non-numbered points.
    declaration_points = models.TextField(
        blank=True,
        help_text="One point per line. You can paste '1. ...' or just '...'."
    )

    # Guardian paragraph (backend controlled)
    guardian_text = models.TextField(blank=True)

    # Signature fields (backend controlled)
    signature_fields = models.TextField(
        blank=True,
        help_text="One field per line. Example: Signature of Parent/Guardian:"
    )

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.code} — {self.title}"

    def get_absolute_url(self):
        return reverse("noc_page", kwargs={"code": self.code})

    # ---------- helpers for template ----------

    def player_field_lines(self):
        return [x.strip() for x in (self.player_fields or "").splitlines() if x.strip()]

    def signature_field_lines(self):
        return [x.strip() for x in (self.signature_fields or "").splitlines() if x.strip()]

    def declaration_items(self):
        """
        Converts declaration_points text -> clean list items for <ol>.
        If admin pasted "1. text", "2) text", "3 - text" etc, we strip the numbering.
        This gives perfect PDF-like wrapping/indent.
        """
        items = []
        for raw in (self.declaration_points or "").splitlines():
            line = raw.strip()
            if not line:
                continue
            # remove common numbering prefixes: "1.", "1)", "1 -", "1:"
            line = re.sub(r"^\s*\d+\s*[\.\)\-\:]\s*", "", line)
            items.append(line)
        return items


# Comprehensive list of user-facing pages for the Sticky Page Title admin.
# Add new pages here whenever you create a new template / URL so admins can
# pick them from the dropdown.
STICKY_PAGE_CHOICES = [
    # Home
    ("home", "Home"),

    # Persona landing pages
    ("ikf_for_players", "I'm a Player"),
    ("ikf_for_parents", "I'm a Parent"),
    ("ikf_for_scouts", "I'm a Scout"),
    ("ikf_for_donors", "I'm a Donor"),

    # Social Impact
    ("supporters", "Annual Impact"),
    ("international-alliance", "Faces of Change: Human Stories"),
    ("anaya_goal", "Anaya – Goal for a Cause"),
    ("football-education", "Democratizing the Dream"),
    ("woman-empowerment", "Empowering Her Through Football"),
    ("career360vision", "Football as a Career Enabler"),
    ("Donate", "Get Involved / Donate"),
    ("community-development", "Community Development"),
    ("faces", "Faces"),
    ("dashboard", "Desi Messi Tracker"),

    # Footprint Project
    ("professional_pathway", "Scout on Wheel"),
    ("invest-social-impact", "North East Rising"),
    ("naari_shakti", "Project Naari Shakti"),

    # IKF Trials
    ("IkfTrials", "About Trials"),
    ("season5", "Season 6 (Ongoing)"),
    ("calender", "Calendar (legacy)"),
    ("upcoming_trials_page", "Upcoming Trials / Trial Calendar"),
    ("noticeboard_home", "Noticeboard Home"),
    ("ikf_broadcast", "IKF Broadcast"),
    ("scouted_players", "Scouted Players"),
    ("support-ikf", "Season 5 Finals"),
    ("season1", "Past Trials – Season 1"),
    ("season2", "Past Trials – Season 2"),

    # Global Pathways
    ("internationalpartners", "IKF Global Alliances / International Clubs & Academies"),
    ("ikf_international_alliance", "IKF International Alliance"),
    ("student_athlete_pathway", "Student-Athlete Pathway"),
    ("workshops", "International Workshops"),
    ("ikf_workshop", "IKF Workshop"),

    # IKF Scouting
    ("discovery_call", "Scouting Certification / Become IKF Scout"),
    ("scoutingasservice", "Scouting as Service"),
    ("scoutingatschools", "Session Plans by Scouts"),
    ("scoutingcommunity", "Scout Network & Community"),
    ("scoutingcertification", "Scouting Certification"),
    ("ikf-as-scouting-partners", "IKF as Scouting Partner"),
    ("scout_landing", "IKF Certified Scout Profiles"),
    ("scout_index", "Certified Scouts All"),
    ("scout_detail", "Certified Scout Profile"),

    # IKF 360
    ("career360parentsplayers", "IKF 360 – Parents SOP"),
    ("career360becomepartner", "IKF 360 – Become Partner"),
    ("career360", "IKF 360 – Field Of Dreams"),
    ("career360fieldofdreams", "IKF 360 – Field Of Dreams (alt)"),
    ("playabroad", "Job/Apprenticeship Program"),
    ("career360faq", "IKF 360 – Partner Ecosystem"),
    ("career360impactinaction", "Partnership Guidelines"),
    ("ikf-dual-career-pathways", "IKF Dual Career Pathways"),
    ("ikf360_player", "IKF 360 Player"),
    ("ikf360_parent", "IKF 360 Parent"),
    ("ikf360_career", "IKF 360 Career"),
    ("ikf360_partner", "IKF 360 Partner"),
    ("ikf360_supporter", "IKF 360 Supporter"),

    # IKF Network / Partners
    ("rep_landing", "Regional Execution Partners (REP)"),
    ("rep_become_partner", "REP – Become a Partner"),
    ("rep_index", "REP – All Partners"),
    ("regionalpartners", "Regional Partners"),
    ("academy-partners", "Academy Partners"),
    ("clubs", "Indian Clubs & Academies"),
    ("state-association-partners", "State Association Partners"),
    ("lawyer_landing", "Legal Corner / Legal Partners"),
    ("lawyer_index", "Legal Partners – All"),
    ("associate_tournamentorganizer", "Tournament Organizer / Tournament Partner"),
    ("request_for_player", "Request For Player"),
    ("nationalpartners", "National Partners"),
    ("corporates", "Corporates"),
    ("Corporate", "Associate – Corporate"),
    ("Philanthropists", "Associate – Philanthropists"),
    ("PSUS", "Associate – PSUs"),
    ("associate_academy", "Associate – Academy"),
    ("associate_clubs", "Associate – Clubs"),
    ("sponsorship-opportunities", "Sponsorship Opportunities"),

    # Centres of Excellence
    ("ikf-center-of-excellence", "IKF Centre of Excellence"),
    ("desportz-ikf-coe", "IKF COE – Desportz"),
    ("imt-ghaziabad-ikf-coe", "IKF COE – IMT Ghaziabad"),
    ("skss-ikf-coe", "IKF COE – SKSS"),
    ("threelok-ikf-coe", "IKF COE – Threelok"),

    # About Us
    ("ikf_aboutus", "About IKF"),
    ("team-behind-ikf", "Meet The Team"),
    ("mission-and-vision", "Mission & Vision"),
    ("ikfinnews", "IKF In News"),
    ("ikf-news", "IKF News"),
    ("ikf-videos", "IKF Videos"),
    ("ikf-partners", "IKF Partners"),
    ("ikf-winners", "IKF Winners"),

    # Parent / Donor focused
    ("parent-fuelling-ikf", "Parent Fuelling IKF"),

    # Invictus
    ("invictus_home", "Invictus x OP Jindal"),
    ("invictus_donations", "Invictus Donations"),
    ("invictus_donate", "Invictus Donate"),

    # Other
    ("Gallery", "Photo Gallery"),
    ("Resources", "Resources"),
    ("sponsordeck", "Sponsor Deck"),
    ("un_certificate", "UN Certificate"),
    ("ikf-spotonn-announcement-en", "IKF Spotonn Announcement (EN)"),
    ("ikf-spotonn-announcement-hi", "IKF Spotonn Announcement (HI)"),
]


PAGE_CHOICES = [
    # Home
    ("home", "Home"),

    # Social Impact
    ("dashboard", "Desi Messi Tracker"),
    ("supporters", "Annual Impact"),
    ("international-alliance", "Faces of Change: Human Stories"),
    ("football-education", "Democratizing the Dream"),
    ("woman-empowerment", "Empowering Her Through Football"),
    ("career360vision", "Football as a Career Enabler"),
    ("Donate", "Get Involved / Donate"),

    # ✅ Add this (Anaya page)
    ("anaya_goal", "Anaya – Goal for a Cause"),

    # Footprint Project
    ("professional_pathway", "Scout on Wheel"),
    ("invest-social-impact", "North East Rising"),
    ("naari_shakti", "Project Naari Shakti"),

    # IKF Trials
    ("IkfTrials", "About Trials"),
    ("season5", "Season 5 (Ongoing)"),
    ("calender", "Calendar"),
    ("support-ikf", "Season 5 Finals"),

    # Global Pathways / Clubs links
    ("internationalpartners", "IKF Global Alliances / International Clubs & Academies"),

    # IKF Scouting
    ("discovery_call", "Scouting Certification"),
    ("scoutingasservice", "Scouting as Service"),
    ("scoutingatschools", "Session Plans by Scouts"),
    ("scoutingcommunity", "Scout Network & Community"),
    ("scout_landing", "IKF Certified Scout Profiles"),
    ("scout_index", "Certified Scouts All"),

    # IKF 360
    ("career360parentsplayers", "Parents SOP"),
    ("career360becomepartner", "Become Partner"),
    ("career360", "Field Of Dreams"),
    ("playabroad", "Job/Apprenticeship Program"),
    ("career360faq", "Partner Ecosystem"),

    # IKF 360 — new persona sub-pages (banner images)
    ("ikf360_player",    "IKF 360 — Player page banner"),
    ("ikf360_parent",    "IKF 360 — Parent page banner"),
    ("ikf360_career",    "IKF 360 — Career page banner"),
    ("ikf360_partner",   "IKF 360 — Partner page banner"),
    ("ikf360_supporter", "IKF 360 — Supporter page banner"),

    # IKF Network
    ("rep_landing", "Regional Execution Partners"),
    ("academy-partners", "Academy Partners"),
    ("clubs", "Indian Clubs & Academies"),
    ("state-association-partners", "State Association Partners"),
    ("lawyer_landing", "Legal Partners"),
    ("associate_tournamentorganizer", "Tournament Organizer"),
    ("request_for_player", "Request For Player"),
    ("career360impactinaction", "Partnership Guidelines"),

    # About Us
    ("team-behind-ikf", "Meet The Team"),
    ("ikfinnews", "IKF In News"),

    # Parent Fuelling IKF
    ("parent-fuelling-ikf", "Parent Fuelling IKF"),
]


class PageContent(models.Model):
    page_key = models.CharField(
        max_length=64,
        unique=True,
        choices=PAGE_CHOICES,
        help_text="Must match the URL name, e.g. 'woman-empowerment', 'career360'."
    )

    # auto-filled so you don't have to manage it
    admin_label = models.CharField(max_length=150, blank=True)

    def save(self, *args, **kwargs):
        if not self.admin_label:
            self.admin_label = f"{self.get_page_key_display()} Images"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.admin_label} ({self.page_key})"


class PageImage(models.Model):
    page = models.ForeignKey(
        PageContent,
        related_name="images",
        on_delete=models.CASCADE,
        null=True,   # keep True if you already have old rows
        blank=True,
    )
    image = models.ImageField(upload_to="page_images/")
    caption = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["page", "created_at"]

    def __str__(self):
        label = self.page.admin_label if self.page else "No page"
        cap = self.caption[:40] if self.caption else "Image"
        return f"{label} – {cap}"

from django.db import models
from django.utils.text import slugify

class StateAssociationPartner(models.Model):
    lang = models.CharField(max_length=5, default='en', db_index=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    logo = models.ImageField(upload_to='partners/state_associations/', blank=True, null=True)

    short_description = models.TextField(blank=True)
    about = models.TextField(blank=True)

    state_name = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)

    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:240]
            slug = base
            i = 1
            while StateAssociationPartner.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
import re
from django.db import models
from django.core.exceptions import ValidationError

# If PageContent is in the same file, don't import it.
# If it's in another file, import correctly:
# from .models import PageContent

def _extract_youtube_id(url_or_id: str) -> str:
    if not url_or_id:
        return ""
    s = (url_or_id or "").strip()

    # direct id
    if "http" not in s and "/" not in s and "?" not in s and "&" not in s:
        return s

    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?&/]+)",
        r"youtube\.com/embed/([^?&/]+)",
        r"youtube\.com/shorts/([^?&/]+)",
    ]
    for p in patterns:
        m = re.search(p, s)
        if m:
            return m.group(1)
    return ""


class ScoutOnWheelsMedia(models.Model):
    """
    Media entries for Scout on Wheels page.
    Currently: YouTube video support.
    (You can extend later for more video links)
    """
    page = models.ForeignKey(
        PageContent,
        on_delete=models.CASCADE,
        related_name="sow_media"
    )

    title = models.CharField(max_length=200, blank=True)

    youtube_url_or_id = models.CharField(
        max_length=300,
        help_text="Paste full YouTube URL OR just the video id."
    )

    youtube_id = models.CharField(max_length=32, blank=True, editable=False)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]
        verbose_name = "Scout on Wheels Media"
        verbose_name_plural = "Scout on Wheels Media"

    def clean(self):
        vid = _extract_youtube_id(self.youtube_url_or_id)
        if not vid:
            raise ValidationError("Please enter a valid YouTube URL or video ID.")
        self.youtube_id = vid

    def save(self, *args, **kwargs):
        self.youtube_id = _extract_youtube_id(self.youtube_url_or_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.page.page_key} | {self.title or self.youtube_id}"

from django.db import models

class ScoutOnWheel(models.Model):
    """
    One parent row for the page (AP Pilot).
    Keeps things clean and grouped in admin.
    """
    title = models.CharField(max_length=120, default="Scout on Wheel – Andhra Pradesh Pilot")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ScoutOnWheelImage(models.Model):
    page = models.ForeignKey(ScoutOnWheel, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="scoutonwheel/glimpses/")
    caption = models.CharField(max_length=140, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "-created_at")

    def __str__(self):
        return f"Image #{self.id} ({self.page_id})"


class NaariShakti(models.Model):
    """
    One parent row for the Naari Shakti page.
    Keeps things clean and grouped in admin.
    """
    title = models.CharField(max_length=120, default="Project Naari Shakti")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Naari Shakti"
        verbose_name_plural = "Naari Shakti"

    def __str__(self):
        return self.title


class NaariShaktiImage(models.Model):
    page = models.ForeignKey(NaariShakti, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="naari_shakti/glimpses/")
    caption = models.CharField(max_length=140, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "-created_at")

    def __str__(self):
        return f"Image #{self.id} ({self.page_id})"


class NaariShaktiImpactStat(models.Model):
    page = models.ForeignKey(NaariShakti, on_delete=models.CASCADE, related_name="impact_stats")
    value = models.CharField(max_length=20, help_text="Big number shown on the card, e.g. 6, 346, 7+")
    title = models.CharField(max_length=80, help_text="Card heading, e.g. 'Cities Reached'")
    description = models.TextField(help_text="Supporting text shown under the heading.")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "id")
        verbose_name = "Naari Shakti — Impact stat"
        verbose_name_plural = "Naari Shakti — Impact So Far"

    def __str__(self):
        return f"{self.value} {self.title}"

# invictus/models.py

from django.db import models


class TeamMember(models.Model):
    CATEGORY_CHOICES = [
        ('IKF', 'India Khelo Football'),
        ('INVICTUS', 'Invictus – O.P. Jindal Global University'),
    ]

    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=250)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='invictus/team/', blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class InvictusCarouselImage(models.Model):
    """
    Images for the smooth carousel below the hero banner.
    Managed from Django admin.
    """
    title = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='media/ui/carousel/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f"Carousel Image #{self.id}"
    
class Thought(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=250)
    image = models.ImageField(upload_to='invictus/thoughts/')
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class ScoutOnWheelMediaArticle(models.Model):
    page = models.ForeignKey(ScoutOnWheel, on_delete=models.CASCADE, related_name="articles")
    title = models.CharField(max_length=160)
    source = models.CharField(max_length=120, blank=True)  # e.g. "Raj News Telugu"
    link = models.URLField()
    cover_image = models.ImageField(upload_to="scoutonwheel/media/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "-created_at")

    def __str__(self):
        return self.title


class ScoutOnWheelAndhraReportItem(models.Model):
    """
    Separate admin-managed report items for the
    "Scout on Wheel Andhra Pradesh Project" carousel.
    """
    page = models.ForeignKey(
        ScoutOnWheel,
        on_delete=models.CASCADE,
        related_name="andhra_reports",
    )
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=140, blank=True)
    link = models.URLField(blank=True)
    cover_image = models.ImageField(
        upload_to="scoutonwheel/andhra_reports/",
        blank=True,
        null=True,
    )
    pdf_file = models.FileField(
        upload_to="scoutonwheel/andhra_reports/pdfs/",
        blank=True,
        null=True,
        help_text="Upload PDF for direct download",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "-created_at")
        verbose_name = "Scout on Wheel Andhra Pradesh Project"
        verbose_name_plural = "Scout on Wheel Andhra Pradesh Project"

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────
# IKF 360 — Pathway Partners (logos shown on /ikf360vision)
# ─────────────────────────────────────────────────────────────
class IKF360PathwayPartner(models.Model):
    """
    Partner logos shown under the "What is IKF Pathway 360?"
    section on the /ikf360vision page.

    Recommended logo size:
      • 400 × 200 px (2 : 1 ratio) — PNG with transparent background.
      • Min width 300 px, max width 800 px.
      • File size ≤ 200 KB for fastest page load.
    """
    name = models.CharField(
        max_length=160,
        help_text="Partner name (shown as tooltip and alt text)."
    )
    logo = models.ImageField(
        upload_to="ikf360/pathway_partners/",
        help_text=(
            "Recommended size: 400 × 200 px (2:1 ratio). "
            "PNG with transparent background works best. "
            "Min 300 px wide, max 800 px wide. Keep under 200 KB."
        ),
    )
    category = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional label shown below the logo, e.g. “Nudge Sports”, "
                  "“Health Partner”. Leave blank to show nothing.",
    )
    website = models.URLField(
        blank=True,
        help_text="Optional — clicking the logo opens this link in a new tab."
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers show first."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Untick to hide without deleting."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "-created_at")
        verbose_name = "IKF 360 Pathway Partner"
        verbose_name_plural = "IKF 360 Pathway Partners"

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────
# Scout on Wheels 2026 — state route maps shown on /scouts_on_wheels
# ─────────────────────────────────────────────────────────────
class ScoutOnWheels2026StateMap(models.Model):
    """
    Route map cards (one per state) shown between
    "Scout on Wheels focuses on" and "Aligned with UN SDGs"
    on the Scouts on Wheels page.

    Recommended route map image size:
      • 1200 × 800 px (3 : 2 ratio).
      • PNG or JPG. Card crops to a fixed aspect ratio but
        the full image is shown when clicked.
      • Min width 800 px so it stays sharp on big screens.
      • File size ≤ 500 KB for fastest page load.
    """
    class State(models.TextChoices):
        MADHYA_PRADESH = "MP", "Madhya Pradesh"
        RAJASTHAN = "RJ", "Rajasthan"
        ANDHRA_PRADESH = "AP", "Andhra Pradesh"

    state = models.CharField(
        max_length=2,
        choices=State.choices,
        help_text="State this route map represents."
    )
    title = models.CharField(
        max_length=120,
        blank=True,
        help_text=(
            "Optional — overrides the default state name shown on the card. "
            "Leave blank to use the state name."
        ),
    )
    route_map_image = models.ImageField(
        upload_to="scoutonwheel/2026_route_maps/",
        help_text=(
            "Recommended size: 1200 × 800 px (3:2 ratio). "
            "The card thumbnail is cropped to a fixed size; "
            "clicking the card opens the full image at its original ratio. "
            "Keep file size under 500 KB."
        ),
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers show first."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Untick to hide without deleting."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "-created_at")
        verbose_name = "Scout on Wheels 2026 State Map"
        verbose_name_plural = "Scout on Wheels 2026 State Maps"

    def __str__(self):
        return self.title or self.get_state_display()

    @property
    def display_title(self):
        return self.title or self.get_state_display()


# ─────────────────────────────────────────────────────────────
# Scouted Players — Roaster PDF cards
# Two cards (National + International) shown above the season
# blocks on /scouted-players/. Each card shows its cover page;
# clicking opens the PDF.
# ─────────────────────────────────────────────────────────────
class ScoutedPlayersRoaster(models.Model):
    """
    A downloadable Player Roaster PDF displayed as a cover card on
    the Scouted Players page.

    Cover image recommended size:
      • 800 × 1131 px (A4 portrait at ~96 dpi, ratio 1 : √2).
      • PNG or JPG. The card crops to a fixed shape; clicking opens
        the PDF in a new tab.
      • Keep file size under 400 KB.

    PDF tips:
      • If your PDF is over ~50 MB, host it on Google Drive / S3 /
        Dropbox and paste the public link into "PDF external URL".
        That is faster than uploading to the server.
      • Otherwise upload the file directly to "PDF file".
    """
    class Roaster(models.TextChoices):
        NATIONAL = "NATIONAL", "National Player Roaster"
        INTERNATIONAL = "INTERNATIONAL", "International Player Roaster"

    roaster_type = models.CharField(
        max_length=20,
        choices=Roaster.choices,
        unique=True,
        help_text="Pick whether this is the National or International roaster card.",
    )
    title = models.CharField(
        max_length=160,
        help_text="Card title — shown on the cover card and the open-button.",
        default="Player Roaster",
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional one-line subtitle below the title.",
    )
    cover_image = models.ImageField(
        upload_to="scouted_players/roasters/covers/",
        help_text=(
            "Recommended size: 800 × 1131 px (A4 portrait, ratio 1 : √2). "
            "PNG or JPG. Cards display the cover cropped to a uniform shape; "
            "clicking opens the full PDF. Keep file size under 400 KB."
        ),
    )
    pdf_file = models.FileField(
        upload_to="scouted_players/roasters/pdfs/",
        blank=True,
        null=True,
        help_text=(
            "Upload the PDF directly. Use this if the file is under ~50 MB. "
            "If larger, leave this blank and use 'PDF external URL' instead."
        ),
    )
    pdf_external_url = models.URLField(
        blank=True,
        help_text=(
            "Public link to the PDF (Google Drive / S3 / Dropbox). "
            "If both 'PDF file' and this are set, the uploaded file wins."
        ),
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers show first (National typically before International).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Untick to hide without deleting.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "-created_at")
        verbose_name = "Scouted Players Roaster (PDF)"
        verbose_name_plural = "Scouted Players Roasters (PDFs)"

    def __str__(self):
        return f"{self.get_roaster_type_display()} — {self.title}"

    @property
    def pdf_url(self):
        """Resolve which PDF link to use on the front-end."""
        if self.pdf_file:
            return self.pdf_file.url
        return self.pdf_external_url or ""

class StateAssociationPartnerStat(models.Model):
    partner = models.ForeignKey(
        StateAssociationPartner,
        on_delete=models.CASCADE,
        related_name="stats"
    )
    label = models.CharField(max_length=120)      # e.g., "Districts Covered"
    value = models.CharField(max_length=120)      # e.g., "18"
    note = models.CharField(max_length=160, blank=True)  # optional small note
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.partner.name} - {self.label}"

# main/models.py
class Lawyer(models.Model):
    name = models.CharField(max_length=200)
    template_link = models.SlugField(unique=True, help_text="Used in the URL, e.g. /lawyer/<template_link>/")
    photo = models.ImageField(upload_to="media/ui/lawyers/", blank=True, null=True)

    # IMPORTANT: map to the existing DB column 'expertise'
    expertise_area = models.CharField(
        max_length=200,
        blank=True,
        default="",
        db_column="expertise",
    )

    city = models.CharField(max_length=100, blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    is_featured = models.BooleanField(default=False)

    from django.utils import timezone
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["name"]


class ScoutProfile(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="Used in the URL, e.g. /scout/<slug>/")
    photo = models.ImageField(upload_to="media/ui/scouts/", blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, default="")
    state = models.CharField(max_length=120, blank=True, default="")
    age_date_of_birth = models.CharField("Age / Date of birth", max_length=160, blank=True, default="")
    languages = models.CharField(max_length=240, blank=True, default="")
    willingness_to_travel = models.CharField("Willingness to travel / relocate", max_length=220, blank=True, default="")
    phone = models.CharField(max_length=40, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    experience = models.CharField(max_length=120, blank=True, default="")
    certification = models.CharField(max_length=120, blank=True, default="")
    level1_completion_date = models.CharField("IKF CFSA Level 1 completion date", max_length=80, blank=True, default="")
    level2_completion_date = models.CharField("IKF CFSA Level 2 completion date", max_length=80, blank=True, default="")
    types = models.TextField("Scouting types", blank=True, default="")
    competitions = models.TextField(blank=True, default="")
    age_groups = models.CharField(max_length=240, blank=True, default="")
    regions = models.TextField(blank=True, default="")
    players_assessed = models.CharField(max_length=120, blank=True, default="")
    shortlisted = models.CharField(max_length=120, blank=True, default="")
    events = models.TextField(blank=True, default="")
    strengths = models.TextField(blank=True, default="")
    playing = models.TextField("Football background", blank=True, default="")
    achievements = models.TextField("Achievements and recognition", blank=True, default="")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    from django.utils import timezone
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name



class RepHighlight(models.Model):
    rep   = models.ForeignKey(RepTemplate, on_delete=models.CASCADE, related_name="highlights")
    title = models.CharField(max_length=120)
    text  = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.order}. {self.title}"


class RepPlayer(models.Model):
    rep      = models.ForeignKey(RepTemplate, on_delete=models.CASCADE, related_name="players")
    order    = models.PositiveIntegerField(default=1)
    name     = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=160, blank=True)
    photo    = models.ImageField(upload_to="rep_players/", blank=True, null=True)
    # description for the modal (bio / achievements, free text)
    bio      = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class RepSocialLink(models.Model):
    PLATFORM_CHOICES = [
        ("website",   "Website"),
        ("instagram", "Instagram"),
        ("facebook",  "Facebook"),
        ("twitter",   "X/Twitter"),
        ("youtube",   "YouTube"),
        ("linkedin",  "LinkedIn"),
        ("other",     "Other"),
    ]
    rep      = models.ForeignKey(RepTemplate, on_delete=models.CASCADE, related_name="socials")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url      = models.URLField()

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_platform_display()} - {self.url}"


# ── REP Open Cities ────────────────────────────────────────────────────────────
class RepOpenState(models.Model):
    """
    A state where IKF is looking for Regional Execution Partners.
    Add the state name once here, then add cities as inlines below.
    """
    name      = models.CharField(max_length=100, unique=True, verbose_name="State Name")
    order     = models.PositiveIntegerField(
        default=0,
        help_text="Lower number appears first in the listing.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering  = ["order", "name"]
        verbose_name        = "REP Open State"
        verbose_name_plural = "REP Open States"

    def __str__(self):
        return self.name

    def city_count(self):
        return self.cities.filter(is_active=True).count()
    city_count.short_description = "Active Cities"


class RepOpenCity(models.Model):
    """
    A city under a state where IKF needs a Regional Execution Partner.
    """
    state = models.ForeignKey(
        RepOpenState,
        on_delete=models.CASCADE,
        related_name="cities",
        verbose_name="State",
    )
    city  = models.CharField(max_length=100, verbose_name="City Name")
    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower number appears first within this state.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering  = ["order", "city"]
        verbose_name        = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.city

















# Create your models here.
class Lang(models.Model):
    id = models.CharField(max_length=100, primary_key=True, db_index=True)
    lang = models.CharField(max_length=100,)


class MasterSeason(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    en = models.CharField(max_length=100, null=True)
    year = models.IntegerField(null=True)
    include = models.BooleanField(null=True, default=False, db_index=True)

    def __repr__(self) -> str:
        return str(self.en)

    def __str__(self) -> str:
        return str(self.en)
    
from django.db import models

from django.db import models

from django.db import models

class FAQItem(models.Model):  # renamed earlier from FAQ
    class Page(models.TextChoices):
        SCOUT_ON_WHEELS = "sow", "Scout on Wheels"
        NORTH_EAST_RISING = "ner", "North East Rising"

    LANG_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("te", "Telugu"),
    ]

    # NEW: which page these FAQs belong to
    page = models.CharField(
        max_length=3,
        choices=Page.choices,
        default=Page.SCOUT_ON_WHEELS,
        db_index=True,
    )

    question = models.CharField(max_length=255)
    answer = models.TextField()

    language = models.CharField(
        max_length=8,
        choices=LANG_CHOICES,
        default="en",
        db_index=True,
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Footprint FAQ"            # singular in admin
        verbose_name_plural = "Footprint FAQs"    # plural in admin left nav
        indexes = [
            models.Index(fields=["page", "language", "is_active"]),
        ]

    def __str__(self):
        # helpful when scanning in admin
        return f"[{self.get_page_display()} – {self.language}] {self.question}"






class MasterState(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    name = models.CharField(max_length=200, null=True, db_index=True)
    country_id = models.CharField(max_length=300, null=True)
    include = models.BooleanField(null=True, default=False, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language", on_delete=models.SET_NULL, db_index=True)

    def __repr__(self) -> str:
        return str(self.name)

    def __str__(self) -> str:
        return str(self.name)


class MasterIkfSeasonUi(models.Model):
    id = models.CharField(primary_key=True, max_length=200, db_index=True,)
    name = models.CharField(max_length=200, null=True, db_index=True)

    include = models.BooleanField(null=True, default=False, db_index=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/masterikfseasonui', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language", on_delete=models.SET_NULL, db_index=True)

    def __repr__(self) -> str:
        return str(self.name)

    def __str__(self) -> str:
        return str(self.name)


class MasterCity(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    city = models.CharField(max_length=200, null=True, db_index=True)
    # state_id=models.IntegerField(null=True)
    state = models.ForeignKey(
        MasterState, null=True, verbose_name="State ID", on_delete=models.SET_NULL, db_index=True)
    include = models.BooleanField(null=True, default=False, db_index=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/mastercity', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language", on_delete=models.SET_NULL, db_index=True)

    def __repr__(self) -> str:
        return str(self.city)

    def __str__(self) -> str:
        return str(self.city)

    class Meta:
        verbose_name = ("Master City")
        verbose_name_plural = ("Master Cities")


class MasterPosition(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    position = models.CharField(max_length=200, null=True, db_index=True)
    label = models.CharField(max_length=200, null=True, db_index=True)
    type = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language", on_delete=models.SET_NULL, db_index=True)

    def __repr__(self) -> str:
        return str(self.label)

    def __str__(self) -> str:
        return str(self.label)


class MasterLabels(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(
        max_length=200, null=True, db_index=True, blank=True)
    label = models.TextField(null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language", on_delete=models.SET_NULL, db_index=True)

    extrainfo = models.CharField(max_length=200, null=True)


class HomeImages(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Navbar(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)

    name = models.CharField(max_length=200, null=True, blank=True,)
    urlitem = models.CharField(max_length=200, null=True, blank=True,)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

# app: partners (or any app you prefer)

from django.db import models

class PartnerInterest(models.Model):
    org_name       = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150)
    email          = models.EmailField()
    city           = models.CharField(max_length=120, blank=True)
    focus_areas    = models.CharField(max_length=200, blank=True)
    message        = models.TextField(blank=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.org_name} — {self.contact_person}"

class HomeBanner(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/homebanner', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    heading_1 = models.CharField(max_length=200, null=True, blank=True,)
    heading_2_colored = models.CharField(
        max_length=200, null=True, blank=True,)

    description = models.TextField(null=True, blank=True)
    button1_text = models.CharField(max_length=100, null=True, blank=True)
    button2_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class AboutUs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic_1 = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/aboutus', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Winners(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/winners', null=True, blank=True)
    category = models.ForeignKey(
        MasterPosition, null=True, verbose_name="masterpostion", on_delete=models.SET_NULL, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    workshop_scholarship = models.BooleanField(null=True, default=False, db_index=True)
    trials_scholarship = models.BooleanField(null=True, default=False, db_index=True)
    season = models.CharField(max_length=10, null=True, blank=True,db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Partners(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/partners', null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Initiatives(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/initiatives', null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    initiative_href = models.CharField(max_length=200, null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class MoreaboutIKF(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/initiatives', null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    initiative_href = models.CharField(max_length=200, null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Buttons_IKF_FOR_ALL(models.Model):
    id = models.CharField(max_length=200, primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Photos_IKF_FOR_ALL(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    relationkey = models.ForeignKey(
        Buttons_IKF_FOR_ALL, null=True, verbose_name="primary relation", on_delete=models.SET_NULL, db_index=True)
    relationkeysecondary = models.ForeignKey(
        Buttons_IKF_FOR_ALL, null=True, blank=True, verbose_name="secondary relation", related_name='relationkeysecondary1', on_delete=models.SET_NULL, db_index=True)
    relationkeytertiary = models.ForeignKey(
        Buttons_IKF_FOR_ALL, null=True, blank=True, verbose_name="tertiary relation", related_name='relationkeytertiary1', on_delete=models.SET_NULL, db_index=True)
    relationkeyquaternary = models.ForeignKey(
        Buttons_IKF_FOR_ALL, null=True, blank=True, verbose_name="quaternary relation", related_name='relationkeyquaternary', on_delete=models.SET_NULL, db_index=True)
    relationkeyfifth = models.ForeignKey(
        Buttons_IKF_FOR_ALL, null=True, blank=True, verbose_name="fifth relation", related_name='relationkeyfifth', on_delete=models.SET_NULL, db_index=True)
    relationkeysixth = models.ForeignKey(
        Buttons_IKF_FOR_ALL, null=True, blank=True, verbose_name="sixth relation", related_name='relationkeysixth', on_delete=models.SET_NULL, db_index=True)

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/photos', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class News(models.Model):

    class NewsType(models.TextChoices):
        Trials = 'Trials', 'Trial'
        Workshop = 'Workshop', 'Workshops'
        Social_Impact = 'Social Impact', 'SocialImpact'
        Partners = 'Partners', 'Partner'
        Career360 = 'Career360', 'Career 360'
        Scouting = 'Scouting' , 'Scoutings'

    class MediaType(models.TextChoices):
        Digital = 'digital', 'Digital Media'
        Print = 'print', 'Print Media'


    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/news', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    heading = models.TextField(max_length=200, null=True, blank=True,)
    description = models.TextField(max_length=1000, null=True, blank=True,)
    date = models.DateField(null=True, blank=True,)
    publisher = models.TextField(max_length=200, null=True, blank=True,)
    priority = models.BooleanField(default=False, verbose_name="High Priority?")
    type = models.CharField(max_length=200, null=True, blank=True, choices=NewsType.choices, default=NewsType.Trials)
    link = models.CharField(max_length=200, null=True, blank=True,)


    # year = models.IntegerField(null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    media_type = models.CharField(max_length=20, choices=MediaType.choices, default=MediaType.Digital, null=True, blank=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
    attr5 = models.CharField(max_length=200, null=True, blank=True, )

class WorkshopNews(models.Model):
    
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/news', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    heading = models.TextField(max_length=200, null=True, blank=True,)
    description = models.TextField(max_length=1000, null=True, blank=True,)
    date = models.DateField(null=True, blank=True,)

    # year = models.IntegerField(null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
    attr5 = models.CharField(max_length=200, null=True, blank=True, )

class WorkshopInternationalLogo(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Clubs_Partners', null=True, blank=True)
    button1_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
class Tab(models.Model):
    id = models.CharField(max_length=100, primary_key=True, db_index=True)
    tab = models.CharField(max_length=200, null=True, db_index=True)
    extra = models.CharField(max_length=200, null=True, db_index=True)


class SubTab(models.Model):
    id = models.CharField(max_length=100, primary_key=True, db_index=True)
    subtab = models.CharField(max_length=200, null=True, db_index=True)
    tab = models.ForeignKey(
        Tab, null=True, verbose_name="tab", on_delete=models.SET_NULL, db_index=True)


class AboutTrials_BannerPhoto(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/bannerphoto', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)


class ActiveStatusNav(models.Model):
    id = models.CharField(primary_key=True, max_length=200, db_index=True)


class TrialsAndInitiativeType(models.Model):
    id = models.CharField(primary_key=True, max_length=200, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)


class TrialsAndInitiativeNav(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=1000, null=True, blank=True,)
    href = models.CharField(max_length=100, null=True, blank=True,)
    description = models.TextField(null=True, blank=True)
    bottomtext = models.TextField(null=True, blank=True)
    listtext = models.TextField(null=True, blank=True)
    pagetype = lang = models.ForeignKey(
        TrialsAndInitiativeType, null=True, verbose_name="TrialsAndInitiativeType", on_delete=models.SET_NULL, db_index=True)
    activestatus = models.ForeignKey(
        ActiveStatusNav, null=True, verbose_name="ActiveStatusNav", on_delete=models.SET_NULL, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)

    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/TrialsAndInitiativeNavFolder', null=True, blank=True)


class AboutTrials_Feature(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Features', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season1_Feature(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Season1', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season1_Tabs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=1000, null=True, blank=True,)
    description = models.TextField(null=True, blank=True)
    bottomtext = models.TextField(null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)

    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season2_Tabs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=1000, null=True, blank=True,)
    description = models.TextField(null=True, blank=True)
    bottomtext = models.TextField(null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)

    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season1_Bottom(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class About_section1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading1 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph1 = models.TextField(null=True, blank=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph2 = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class About_TeamAdvisors(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    name = models.CharField(max_length=200, null=True, blank=True,)
    post = models.CharField(max_length=100, null=True, blank=True,)
    about = models.CharField(max_length=500, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Team1', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class About_TeamCore_Team(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    name = models.CharField(max_length=200, null=True, blank=True,)
    post = models.CharField(max_length=100, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Team2', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class About_OURTEAM_of_IkF(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    name = models.CharField(max_length=200, null=True, blank=True,)
    post = models.CharField(max_length=100, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Team3', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class IKF_Tech1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class IKF_Tech2(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class IKF_Tech3(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class IKF_Tech4(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

from django.db import models

class HomePageClub(models.Model):
    name = models.CharField(max_length=255)
    pic = models.ImageField(upload_to='home_page_clubs/', blank=True, null=True)

    def __str__(self):
        return self.name

class Regional_Partners1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.TextField( null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Regional_Partners', null=True, blank=True)
    button1_text = models.TextField(null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class National_Partners1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/National_Partners', null=True, blank=True)
    button1_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class International_Partners1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/International_Partners', null=True, blank=True)
    button1_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Corporate_Partners1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Corporate_Partners', null=True, blank=True)
    button1_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Clubs_Partners1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Clubs_Partners', null=True, blank=True)
    button1_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Playabroad(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    button_text = models.CharField(max_length=200, null=True, db_index=True)
    button_href = models.CharField(max_length=200, null=True, db_index=True)
    content_of_button = models.CharField(
        max_length=10000, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)

    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class WorkShopsButton(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    button_text = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class WorkShopsFeatureStrip(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/WorkshopRegFeatureStrip', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TabelWorkshops(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    First_Column = models.CharField(max_length=200, null=True, db_index=True)
    Second_Column = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class WorkShopsExperts(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading1 = models.CharField(max_length=100, null=True, blank=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=500, null=True, blank=True,)
    button_text = models.CharField(max_length=200, null=True, db_index=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/LearnFromExperts', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class AboutTrials_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season1_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season2_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class ScoutingCertification_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class PlayAbroad_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class WorkShops_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class IKF_Technology_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class About_Us_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Reginoal_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class National_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class International_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Corporate_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Clubs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season1_Button(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    button_text = models.CharField(max_length=200, null=True, db_index=True)
    button_href = models.CharField(max_length=200, null=True, db_index=True)
    content_of_button = models.CharField(
        max_length=10000, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)


class Associate_Corporate_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_Philanthropists_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_PSUS_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_Academy_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='academy', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_Corporate_Main(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading1 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph1 = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_Philanthropists_Main(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading1 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph1 = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_PSUS_Main(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading1 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph1 = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_Corporate_Right(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph2 = models.CharField(max_length=200, null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    href = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_Philanthropists_Right(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph2 = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_PSUS_Right(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph2 = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class UpCommingMatchs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    teamname_1st = models.ForeignKey(
        MasterIkfSeasonUi, null=True, verbose_name="masterikfseason", on_delete=models.SET_NULL, db_index=True,)
    teamname_2nd = models.ForeignKey(
        MasterCity, null=True, verbose_name="mastercity", on_delete=models.SET_NULL, db_index=True,)
    Match_Month = models.CharField(max_length=200, null=True, blank=True,)
    day_remaining = models.IntegerField(null=True, blank=True,)
    date_year = models.IntegerField(null=True, blank=True,)
    Match_Time = models.CharField(max_length=200, null=True, blank=True,)
    Match_City = models.CharField(max_length=200, null=True, blank=True,)
    Team1_pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Team1', null=True, blank=True)
    Team2_pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Team2', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
    matchdate = models.DateField(db_index=True, null=True, )
    include = models.BooleanField(null=True, default=False, db_index=True)


class TabelSeason2(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    First_Column = models.CharField(max_length=200, null=True, db_index=True)
    Second_Column = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season2_Features(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Season1', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TabelScoutingCertification(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    First_Column = models.CharField(max_length=200, null=True, db_index=True)
    Second_Column = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Scouting_Features(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Season1', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Scouting_Initiatives(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/initiatives', null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    initiative_href = models.CharField(max_length=200, null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TabelPlayabroad(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    First_Column = models.CharField(max_length=200, null=True, db_index=True)
    Second_Column = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Playabroad_Features(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Season1', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Playabroad_Initiatives(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/initiatives', null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    initiative_href = models.CharField(max_length=200, null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class NavTabs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    tab = models.CharField(max_length=200, null=True, blank=True,)
    subtab = models.CharField(max_length=200, null=True, blank=True,)
    tab_href = models.CharField(max_length=200, null=True, blank=True,)
    subtab_href = models.CharField(max_length=200, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay1_Corporate(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay2_Corporate(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay1_Philanthropists(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay2_Philanthropists(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay1_PSUS(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay2_PSUS(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay3_PSUS(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class WorkShopsReg_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TabelWorkshopsReg(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    First_Column = models.CharField(max_length=200, null=True, db_index=True)
    Second_Column = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class WorkShopsRegButton(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    button_text = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class WorkShopsRegFeatureStrip(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/WorkshopFeatureStrip', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class WorkShopsRegExperts(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading1 = models.CharField(max_length=100, null=True, blank=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=500, null=True, blank=True,)
    button_text = models.CharField(max_length=200, null=True, db_index=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/LearnFromExperts', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Selected_Players_Season1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    Name = models.CharField(max_length=100, null=True, blank=True,)
    Age = models.CharField(max_length=100, null=True, blank=True,)
    Information = models.TextField(null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Selected_players_season1', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Selected_Players_Season2(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    Name = models.CharField(max_length=100, null=True, blank=True,)
    Age = models.CharField(max_length=100, null=True, blank=True,)
    Information = models.TextField(null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Selected_players_season2', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay1_Academy(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay2_Academy(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Associate_Clubs_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='Clubs', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class TakeaWay1_Clubs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class TakeaWay2_Clubs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class TakeaWay3_Clubs(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Associate_Clubs_Right(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph2 = models.CharField(max_length=200, null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    href = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Clubs_Parter_Home(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    # ✅ Fixed ImageField path — no need for 'media/' prefix
    pic = models.ImageField(
        storage=OverwriteStorage(),
        upload_to='media/ui/Clubs',
        null=True,
        blank=True
    )

    lang = models.ForeignKey(
        Lang,
        null=True,
        verbose_name="language21",
        on_delete=models.SET_NULL,
        db_index=True
    )

    is_international = models.BooleanField(default=False)
    is_participated = models.BooleanField(default=True)

    attr1 = models.CharField(max_length=200, null=True, blank=True)
    attr2 = models.CharField(max_length=200, null=True, blank=True)
    attr3 = models.CharField(max_length=200, null=True, blank=True)
    attr4 = models.CharField(max_length=200, null=True, blank=True)


class Clubs_Parter_Season1(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Clubs_Season1', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Clubs_Parter_Season2(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Clubs_Season2', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season3_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
class TabelPastTrial(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    First_Column = models.CharField(max_length=200, null=True, db_index=True)
    Second_Column = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class TabelSeason3(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    First_Column = models.CharField(max_length=200, null=True, db_index=True)
    Second_Column = models.CharField(max_length=200, null=True, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Season3_Features(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Season1', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    description = models.CharField(max_length=1000, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Associate_TournamentOrganizer_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='Clubs', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class TakeaWay1_TournamentOrganizer(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class TakeaWay2_TournamentOrganizer(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    paragraph = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Associate_TournamentOrganizer_Right(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph2 = models.CharField(max_length=200, null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    href = models.CharField(max_length=100, null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


class Previous_Workshop_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='Previous_Worksho', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Winners_Workshop_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='Previous_Worksho', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
class Mentor(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='Previous_Worksho', null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    trials_scholarship = models.BooleanField(null=True, default=False, db_index=True)
    season = models.CharField(max_length=10, null=True, blank=True,db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
class Testimonials(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='Previous_Worksho', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    workshop_scholarship = models.BooleanField(null=True, default=False, db_index=True)
    trials_scholarship = models.BooleanField(null=True, default=False, db_index=True)
    season = models.CharField(max_length=10, null=True, blank=True,db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Clubs_Parter_abouttrials(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Clubs_AboutTrials', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

# 13/apr 
class Youtube(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/youtube', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    heading = models.TextField(max_length=200, null=True, blank=True,)
    description = models.TextField(max_length=1000, null=True, blank=True,)
    date = models.DateField(null=True, blank=True,)

    # year = models.IntegerField(null=True, blank=True,)
    button_text = models.CharField(max_length=100, null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
    attr5 = models.CharField(max_length=200, null=True, blank=True, )

class UserFlow_Season3(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading1 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph1 = models.TextField(null=True, blank=True,)
    heading2 = models.CharField(max_length=100, null=True, blank=True,)
    paragraph2 = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Calendar_Season3(models.Model):
    id=models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    Description = models.TextField(null=True, blank=True,)
    Month = models.CharField(max_length=100, null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Winners_Season2(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/winners', null=True, blank=True)
    category = models.ForeignKey(
        MasterPosition, null=True, verbose_name="masterpostion", on_delete=models.SET_NULL, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class InstaFeed(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    Link = models.TextField(null=True, blank=True,)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Photo_Gallery_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Gallery_Buttons(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    BCity = models.CharField(max_length=200, null=True, blank=True, )
    Bname = models.CharField(max_length=100, null=True, blank=True)
    BBehavior = models.CharField(max_length=100, null=True, blank=True)
    Image = models.ImageField(
        storage=OverwriteStorage(), upload_to='courses', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Resources(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    document = models.FileField(
        storage=OverwriteStorage(), upload_to='media/ui/downloads', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    link = models.CharField(max_length=300, null=True, blank=True,)
    description = models.CharField(max_length=300, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class SupportedByImages(models.Model):
    id = models.CharField(primary_key=True, db_index=True, max_length=200)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/supportedby', null=True, blank=True)


class SupportedByFinancial(models.Model):
    id = models.CharField(primary_key=True, db_index=True, max_length=200)
    financial_year = models.CharField(max_length=200, null=True, blank=True,)
    order_by = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order_by']

class SupportedBy(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    logo_pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/supportedby', null=True, blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True,)
    company_address = models.TextField(max_length=1000, null=True, blank=True,)
    project_brief = models.TextField(max_length=1000, null=True, blank=True,)
    partners = models.TextField(max_length=1000, null=True, blank=True,)
    button_link = models.TextField(max_length=1000, null=True, blank=True,)
    order_by = models.IntegerField(null=True, blank=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
    attr5 = models.CharField(max_length=200, null=True, blank=True, )

    supported_by_financial = models.ForeignKey(
        SupportedByFinancial, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)

    class Meta:
        ordering = ['order_by']

class SupportedByImages2526(models.Model):
    id = models.CharField(primary_key=True, db_index=True, max_length=200)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/supportedby2526', null=True, blank=True)
    order_by = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Impact 2025-26 Image"
        verbose_name_plural = "Impact 2025-26 Images"
        ordering = ['order_by']
        
class Donate_Images(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True, )

    size = models.CharField(max_length=100, null=True, blank=True)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='donateus', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language27", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


from django.db import models

class TabelDonate(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    First_Column = models.CharField(max_length=200, null=True, db_index=True)
    Second_Column = models.CharField(max_length=200, null=True, db_index=True)
    
    image = models.ImageField(upload_to='donate_images/', null=True, blank=True)  # ✅ NEW FIELD

    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True)
    attr2 = models.CharField(max_length=200, null=True, blank=True)
    attr3 = models.CharField(max_length=200, null=True, blank=True)
    attr4 = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.First_Column} {self.Second_Column}"




class DonateFeatureStrip(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Donate', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class PaymentFeatureStrip(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Donate', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


from django.db import models

class Donation(models.Model):
    ikfuniqueid = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    amount = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()

    photo = models.ImageField(upload_to='donors/', blank=True, null=True)

    order_id = models.CharField(max_length=300, blank=True, null=True)
    status = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    razorpay_unique_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=300, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=300, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=400, blank=True, null=True)

    error_code = models.CharField(max_length=300, blank=True, null=True)
    error_description = models.CharField(max_length=400, blank=True, null=True)
    error_source = models.CharField(max_length=300, blank=True, null=True)
    error_reason = models.CharField(max_length=300, blank=True, null=True)
    error_meta_order_id = models.CharField(max_length=300, blank=True, null=True)
    error_meta_payment_id = models.CharField(max_length=300, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    # Link to the admin-managed DonateProject so any project (existing or newly added)
    # is properly attributed without depending on per-project boolean fields.
    project = models.ForeignKey(
        'DonateProject', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='donations', db_index=True,
        help_text="Auto-linked from the donation purpose string at save time."
    )

    # ✅ Boolean fields for donation purposes
    invictus_icare = models.BooleanField(null=True, default=False, db_index=True)

    future_champions = models.BooleanField(null=True, default=False, db_index=True)
    books_and_boots = models.BooleanField(null=True, default=False, db_index=True)
    heal_to_play = models.BooleanField(null=True, default=False, db_index=True)
    maidaan_ki_rani = models.BooleanField(null=True, default=False, db_index=True)
    that_kicks = models.BooleanField(null=True, default=False, db_index=True)
    ikf_trials = models.BooleanField(null=True, default=False, db_index=True)
    anayas_goal = models.BooleanField(null=True, default=False, db_index=True)

    def __str__(self):
        return self.name


# NOTICEBOARD Models
from django.db import models
from django.core.exceptions import ValidationError


class NoticeboardBox(models.Model):
    name = models.CharField(max_length=120)

    # NEW: internal slug route like /noticeboard/<slug>/
    slug = models.SlugField(max_length=140, blank=True)

    # Optional: external link, if you want a box to go to some other page
    url = models.CharField(max_length=300, blank=True)  # can be /something/ or full https://

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        """
        Enforce: a box should have EITHER url OR slug.
        """
        if not self.url and not self.slug:
            raise ValidationError("Provide either a URL or a Slug.")
        if self.url and self.slug:
            raise ValidationError("Provide either URL or Slug, not both.")


class NoticeboardNotice(models.Model):
    title = models.CharField(max_length=240)
    url = models.CharField(max_length=300, blank=True)  # optional; can be # if blank
    meta = models.CharField(max_length=180, blank=True)
    published_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_date", "-created_at"]

    def __str__(self):
        return self.title


class NoticeBoardInfoBlock(models.Model):
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=200, blank=True)
    body = models.TextField()

    cta_text = models.CharField(max_length=40, blank=True)
    cta_url = models.URLField(blank=True)

    image = models.ImageField(upload_to="noticeboard/info_blocks/", blank=True, null=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────
# TRIAL GUIDELINES PAGE (Dedicated models because layout differs)
# ─────────────────────────────────────────────────────────────

class TrialGuidelinesPage(models.Model):
    """
    Only 1 row usually: slug = 'trial-guidelines-instructions'
    Title + kicker come from backend.
    Banner stays frontend (static image), as you asked.
    """
    slug = models.SlugField(max_length=140, unique=True)
    page_title = models.CharField(max_length=220)
    page_kicker = models.CharField(max_length=260, blank=True)

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Trial Guidelines Page"
        verbose_name_plural = "Trial Guidelines Page"

    def __str__(self):
        return self.page_title


class TrialGuidelinesSection(models.Model):
    AREA_MAIN = "main"
    AREA_SIDEBAR = "sidebar"

    AREA_CHOICES = (
        (AREA_MAIN, "Main (Left)"),
        (AREA_SIDEBAR, "Sidebar (Right)"),
    )

    page = models.ForeignKey(
        TrialGuidelinesPage,
        on_delete=models.CASCADE,
        related_name="sections"
    )
    title = models.CharField(max_length=160)

    # ✅ NEW
    area = models.CharField(max_length=10, choices=AREA_CHOICES, default=AREA_MAIN)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["area", "order"]

    def __str__(self):
        return f"{self.page.slug} • {self.title}"



class TrialGuidelinesItem(models.Model):
    NOTE = "note"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"

    ITEM_TYPES = (
        (NOTE, "Note"),
        (PARAGRAPH, "Paragraph"),
        (LIST_ITEM, "List Item"),
    )

    section = models.ForeignKey(
        TrialGuidelinesSection,
        on_delete=models.CASCADE,
        related_name="items"
    )
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default=PARAGRAPH)

    # only useful for paragraph in your UI (bold label prefix)
    bold_label = models.CharField(max_length=120, blank=True)

    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.section.title} • {self.item_type}"

# ─────────────────────────────────────────────────────────────
# MEdia Page (Dedicated models because layout differs)
# ─────────────────────────────────────────────────────────────
# models.py
from django.db import models
from django.core.exceptions import ValidationError
from urllib.parse import urlparse, parse_qs


class PostTrialMediaPage(models.Model):
    slug = models.SlugField(max_length=140, unique=True, default="post-trial-media")
    banner_image = models.ImageField(upload_to="noticeboard/banners/", blank=True, null=True)
    title = models.CharField(max_length=120, default="Post Trial Media")
    short_description = models.CharField(
        max_length=220,
        default="Get the latest updates on trial day’s match videos."
    )
    channel_url = models.URLField(default="https://www.youtube.com/@IKFShowcase")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PostTrialMediaVideo(models.Model):
    page = models.ForeignKey(PostTrialMediaPage, related_name="videos", on_delete=models.CASCADE)
    city_name = models.CharField(max_length=120)
    video_url = models.URLField(help_text="YouTube video URL (watch / youtu.be / embed)")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "city_name"]

    def __str__(self):
        return f"{self.city_name} — {self.video_url}"

    @property
    def video_id(self):
        url = (self.video_url or "").strip()

        if "youtu.be/" in url:
            return url.split("youtu.be/")[-1].split("?")[0].split("/")[0]

        if "/embed/" in url:
            return url.split("/embed/")[-1].split("?")[0].split("/")[0]

        try:
            q = parse_qs(urlparse(url).query)
            return (q.get("v") or [""])[0]
        except Exception:
            return ""

    @property
    def thumb(self):
        # best default thumbnail
        return f"https://img.youtube.com/vi/{self.video_id}/hqdefault.jpg"




class SupportIkfFeatureStrip(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/WorkshopRegFeatureStrip', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class PartnerSeasonSupportIKF(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/Clubs', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )

class Calender(models.Model):

    class StatusChoices(models.TextChoices):
        DATE_CONFIRMED = 'DATE CONFIRMED', 'Date Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CITY_CONFIRMED = 'CITY CONFIRMED', 'City Confirmed'
        COMING_SOON = 'COMING SOON', 'Coming Soon'

    id = models.BigAutoField(primary_key=True, db_index=True,)
    keydata = models.CharField(max_length=200, null=True, db_index=True,)
    date = models.DateField(null=True, blank=True)
    second_date = models.DateField(null=True, blank=True)
    third_date = models.DateField(null=True, blank=True)
    # date2 = models.DateField(null=True, blank=True)
    project_id=models.IntegerField(null=True,blank=True)
    project=models.CharField(max_length=200, null=True, db_index=True,)
    project_city_id=models.IntegerField(null=True,blank=True)
    project_city=models.CharField(max_length=200, null=True, db_index=True,)
    project_state_id=models.IntegerField(null=True,blank=True)
    project_state=models.CharField(max_length=200, null=True, db_index=True,)
    project_country_id=models.IntegerField(null=True,blank=True)
    project_country=models.CharField(max_length=200, null=True, db_index=True,)

    heading = models.CharField(max_length=100, null=True, blank=True,)
    paragraph = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/calender', null=True, blank=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True,)
    status_date = models.CharField(max_length=200, null=True, blank=True, choices=StatusChoices.choices, default=StatusChoices.DATE_CONFIRMED)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )


from django.db import models

class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"


class Finalists(models.Model):
        id = models.BigAutoField(primary_key=True, db_index=True)
      
        size = models.CharField(max_length=100, null=True, blank=True)
        pic = models.ImageField(
            storage=OverwriteStorage(), upload_to='media/ui/finalistspic', null=True, blank=True)
        name = models.CharField(max_length=200, null=True, blank=True,)
        link = models.URLField( max_length=300,
        blank=True,
        null=True,
        verbose_name='Finalists',
        help_text='Enter a full URL including http:// or https://')

class Coaches(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    keydata = models.CharField(max_length=200, null=True, db_index=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True,)
    pic = models.ImageField(
        storage=OverwriteStorage(), upload_to='media/ui/coaches', null=True, blank=True)
    category = models.ForeignKey(
        MasterPosition, null=True, verbose_name="masterpostion", on_delete=models.SET_NULL, db_index=True)
    lang = models.ForeignKey(
        Lang, null=True, verbose_name="language21", on_delete=models.SET_NULL, db_index=True)
    workshop_scholarship = models.BooleanField(null=True, default=False, db_index=True)
    trials_scholarship = models.BooleanField(null=True, default=False, db_index=True)
    season = models.CharField(max_length=10, null=True, blank=True,db_index=True)
    attr1 = models.CharField(max_length=200, null=True, blank=True,)
    attr2 = models.CharField(max_length=200, null=True, blank=True, )
    attr3 = models.CharField(max_length=200, null=True, blank=True, )
    attr4 = models.CharField(max_length=200, null=True, blank=True, )
    description = models.TextField(null=True, blank=True)

class Scout(models.Model):
    
    id = models.BigAutoField(primary_key=True, db_index=True)
      # Unique IKF Identifier
    ikf_id = models.CharField(max_length=50, unique=False, blank=True, null=True)

    full_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)

    preferred_cities = models.TextField(help_text="Comma-separated cities like 'Delhi, Mumbai'")
    mobile_number = models.TextField()



    gmail_id = models.EmailField(blank=True, null=True)


    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)

    ikf_tshirt = models.BooleanField(default=False)  # "Yes"/"No" in CSV → convert to True/False
    pan_number = models.CharField(max_length=20)
    bank_details = models.TextField()

    profile_photo = models.ImageField(upload_to='scout_images/')
    ishidden = models.BooleanField(default=False)
 
# models.py
class TeamVideoCarousel(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(blank=True, null=True)
    video_url = models.URLField()
    pic = models.ImageField(upload_to='team_thumbnails/', blank=True, null=True)  # optional fallback

    def __str__(self):
        return self.name

class OfficialScoutingPartner(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='official_scouting_partners/')
   

    class Meta:
        verbose_name = "Official Scouting Partner"
        verbose_name_plural = "Official Scouting Partners"

    def __str__(self):
        return self.name


from django.db import models

class SeasonReport(models.Model):
    season = models.PositiveIntegerField(unique=True)  # 1,2,3,4,5...
    title = models.CharField(max_length=200, blank=True)
    tab_label = models.CharField(
        max_length=60,
        blank=True,
        default="",
        help_text="Short label shown on the Scouted Players season tab pill. "
                  "Leave blank to use 'Season N' automatically."
    )
    year_range = models.CharField(max_length=50, blank=True, default="", help_text="Displayed on the IKF Trials card, e.g. '2021 - 22'")
    description = models.TextField(blank=True, default="", help_text="Short summary shown on the IKF Trials season card")
    cities = models.CharField(max_length=50, blank=True, default="", help_text="Cities count shown on the IKF Trials card")
    participants = models.CharField(max_length=50, blank=True, default="")
    shortlisted_count = models.CharField(max_length=50, blank=True, default="")
    scouted_count = models.CharField(max_length=50, blank=True, default="")
    international_scholarship_count = models.CharField(max_length=50, blank=True, default="")
    clubs = models.CharField(max_length=50, blank=True, default="", help_text="Clubs count shown on the IKF Trials card")
    remarks = models.TextField(blank=True, default="")
    show_on_ikf_trials = models.BooleanField(default=True, help_text="Show this season as a card on the IKF Trials page")
    class Meta:
        ordering = ["season"]
        verbose_name = "IKF Season (Trials & Scouted Players)"
        verbose_name_plural = "IKF Seasons (Trials & Scouted Players)"

    def __str__(self):
        return self.title or f"Season {self.season}"


class PlayerEntry(models.Model):
    class ListType(models.TextChoices):
        SHORTLISTED = "Shortlisted", "Shortlisted"
        SCOUTED = "Scouted", "Scouted"

    season = models.ForeignKey(SeasonReport, on_delete=models.CASCADE, related_name="players")
    list_type = models.CharField(max_length=20, choices=ListType.choices)
    sr_no = models.PositiveIntegerField()
    player_name = models.CharField(max_length=200)
    clubs = models.TextField(blank=True)

    class Meta:
        unique_together = ("season", "list_type", "sr_no")
        ordering = ["season__season", "list_type", "sr_no"]

    def __str__(self):
        return f"S{self.season.season} {self.list_type} #{self.sr_no} {self.player_name}"
   
from django.db import models

from django.db import models

class TrialSchedule(models.Model):
    city = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city


class WorkshopLocation(models.Model):
    city = models.CharField(max_length=100)
    dates = models.CharField(max_length=100)
    venue = models.TextField()
    maps_link = models.URLField()
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # 💰 New
    priority = models.PositiveIntegerField(default=1)  # 🏷️ New

    class Meta:
        ordering = ['priority']  # 📌 Order by priority instead of city

    def __str__(self):
        return f"{self.city} - {self.dates}"


class TrialDay(models.Model):
    schedule = models.ForeignKey(TrialSchedule, related_name='days', on_delete=models.CASCADE)
    day_title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.schedule.city} - {self.day_title}"



class HomePage(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True)
    image = models.ImageField(upload_to='media/ui/homepage',blank=True, null=True)
    en= models.TextField(blank=True, null=True)
    marathi= models.TextField(blank=True, null=True)
    hindi=models.TextField(blank=True, null=True)
   

    class Meta:
        verbose_name = "Home"
        verbose_name_plural = "Home"

    def __str__(self):
        return self.name    
    
class IWLPartner(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='iwl_partners/')

    class Meta:
        verbose_name = "IWL Partner"
        verbose_name_plural = "IWL Partners"

    def __str__(self):
        return self.name
    
    from django.db import models

from django.db import models

class Faq(models.Model):
    PAGE_CHOICES = [
        ('ikf_workshop', 'Workshop'),
        ('donate', 'Donate'),
        ('home', 'Home'),
        ('career360', 'Career360'),

        # ✅ New pages
        ('IkfTrials', 'IKF Trials'),
        ('season5', 'Season 6 Page'),  # because your urlpattern name is "season5"
    ]

    page_name = models.CharField(max_length=100, choices=PAGE_CHOICES)
    question = models.TextField()
    answer = models.TextField()
    priority = models.PositiveIntegerField(
        help_text="Lower numbers appear first (e.g., 1 = top position)"
    )

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['priority']

    def __str__(self):
        return f"{self.page_name} - Q{self.priority}: {self.question[:50]}"

from django.db import models


class SitemapCategory(models.Model):
    """
    Represents a yellow heading block on the sitemap.
    Multiple categories sharing the same `column` value are stacked
    vertically inside a single grid cell (like "Home" + "Footprint Project").
    """
    name        = models.CharField(max_length=100)
    column      = models.PositiveSmallIntegerField(
        default=1,
        help_text=(
            "Grid column this category belongs to (1-based). "
            "Two categories with the same column number are stacked "
            "in the same cell — e.g. 'Home' and 'Footprint Project' both use column 1."
        ),
    )
    order       = models.PositiveSmallIntegerField(
        default=0,
        help_text="Vertical order within the column. Lower = higher up.",
    )
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Sitemap Category"
        verbose_name_plural = "Sitemap Categories"
        ordering            = ["column", "order", "name"]

    def __str__(self):
        return f"[Col {self.column}] {self.name}"


class SitemapItem(models.Model):
    """
    A single link card within a category.
    The hover description and target URL are managed here.
    """
    category    = models.ForeignKey(
        SitemapCategory,
        on_delete=models.CASCADE,
        related_name="items",
    )
    title       = models.CharField(max_length=150)
    description = models.TextField(
        blank=True,
        default="",
        help_text="Short preview text shown on hover / tap (1–2 sentences). Optional."
    )
    url         = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Destination URL for the 'Know More' button. Optional — leave blank to hide the button.",
    )
    order       = models.PositiveSmallIntegerField(default=0, help_text="Lower = higher in the list.")
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Sitemap Item"
        verbose_name_plural = "Sitemap Items"
        ordering            = ["category__column", "category__order", "order", "title"]

    def __str__(self):
        return f"{self.category.name} → {self.title}"






class TermsSection(models.Model):
    title      = models.CharField(max_length=250, null=True, blank=True)
    content    = models.TextField(help_text="Supports HTML for bold/lists etc.", null=True, blank=True)
    order      = models.PositiveIntegerField(default=0, help_text="Lower number = appears first on the page")
    is_active  = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['order']
        verbose_name        = "Terms & Conditions Section"
        verbose_name_plural = "Terms & Conditions Sections"

    def __str__(self):
        return f"{self.order}. {self.title}"


class IKFAchievement(models.Model):
    award_name      = models.CharField(max_length=300, help_text="Name of the award or recognition")
    awarding_agency = models.CharField(max_length=300, help_text="Who gave this award")
    year            = models.CharField(max_length=50, blank=True, help_text='e.g. "2023" or "2024 and still going on"')
    details         = models.TextField(help_text="Full description shown on the card")
    image           = models.ImageField(upload_to='achievements/', blank=True, null=True,
                                        help_text="Award badge / trophy image (optional)")
    order           = models.PositiveSmallIntegerField(default=0, help_text="Lower = appears first")
    is_active       = models.BooleanField(default=True)

    class Meta:
        ordering            = ['order']
        verbose_name        = "IKF Achievement"
        verbose_name_plural = "IKF Achievements"

    def __str__(self):
        return self.award_name


class ImpactReport(models.Model):
    title       = models.CharField(max_length=300)
    year        = models.CharField(max_length=50, blank=True)
    cover_image = models.ImageField(upload_to='impact_reports/covers/', blank=True, null=True)
    pdf_file    = models.FileField(upload_to='impact_reports/pdfs/', blank=True, null=True,
                                   help_text="Upload the PDF file for direct download")
    view_link   = models.URLField(blank=True,
                                  help_text="External URL to view/embed the PDF (Google Drive, etc.)")
    show_in_side_view = models.BooleanField(
        default=False,
        help_text="Show this report as a right-side thumbnail on the Annual Impact page."
    )
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Impact Report"
        verbose_name_plural = "Impact Reports"

    def __str__(self):
        return self.title


class OfficialCircularCard(models.Model):
    """
    Admin-managed cards shown on the Official Circulars, Notices & Announcements page.
    Each card has its own detail page at /noticeboard/circular/<slug>/
    """
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Short purpose / tagline shown under the title")
    emoji       = models.CharField(max_length=10, blank=True, help_text="Emoji icon displayed on the card, e.g. 📋")
    slug        = models.SlugField(max_length=120, unique=True, blank=True,
                    help_text="Auto-used for the detail page URL, e.g. 'trial-updates'")
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Official Circular Card"
        verbose_name_plural = "Official Circular Cards"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:100] or "circular"
            candidate = base
            i = 2
            while OfficialCircularCard.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class OfficialCircularItem(models.Model):
    """
    Content item belonging to one of the Official Circular Cards (boxes).
    Used for Trial Notices, Scout Courses, and Blogs/Stories.
    """
    card        = models.ForeignKey(
                    OfficialCircularCard,
                    on_delete=models.CASCADE,
                    related_name='items',
                  )
    title       = models.CharField(max_length=300)
    body        = models.TextField(blank=True, help_text="Full description or body text")
    tag         = models.CharField(max_length=80, blank=True,
                    help_text="Short label shown as a badge, e.g. 'Notice', 'Course', 'Blog'")
    date        = models.DateField(null=True, blank=True,
                    help_text="Publication / event date")
    image       = models.ImageField(upload_to='official_circulars/images/', blank=True, null=True,
                    help_text="Cover image (used for blogs/stories)")
    attachment  = models.FileField(upload_to='official_circulars/files/', blank=True, null=True,
                    help_text="PDF or document download")
    external_link = models.URLField(blank=True,
                    help_text="External URL for 'Read More' or 'Register' button")
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-date', '-created_at']
        verbose_name = "Official Circular Item"
        verbose_name_plural = "Official Circular Items"

    def __str__(self):
        return f"{self.card.title} › {self.title}"


class IKFBroadcastItem(models.Model):
    """
    Standalone broadcast items shown on the Official Circular & Notice / IKF Broadcast page.
    All fields are optional — publish only what you have.
    Items are ordered newest-date-first.
    """
    image       = models.ImageField(upload_to='ikf_broadcast/', blank=True, null=True,
                    help_text="Cover / thumbnail image (optional)")
    date        = models.DateField(null=True, blank=True,
                    help_text="Publication or event date — used for newest-first ordering")
    heading     = models.CharField(max_length=300, blank=True,
                    help_text="Title / headline of the broadcast")
    context     = models.CharField(max_length=500, blank=True,
                    help_text="Short tagline or one-line context shown below the heading")
    body        = models.TextField(blank=True,
                    help_text="Full description or announcement body")
    cta_label   = models.CharField(max_length=100, blank=True,
                    help_text="Primary button label, e.g. 'Register Now'")
    cta_url     = models.URLField(blank=True,
                    help_text="Primary button URL")
    cta_label_2 = models.CharField(max_length=100, blank=True,
                    help_text="Secondary button label (optional)")
    cta_url_2   = models.URLField(blank=True,
                    help_text="Secondary button URL")
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "IKF Broadcast Item"
        verbose_name_plural = "IKF Broadcast Items"

    def __str__(self):
        return self.heading or f"Broadcast #{self.pk}"


# ═════════════════════════════════════════════════════════════════
# HOME PAGE — admin-managed content for the three top sections.
# Each model falls back to existing hardcoded content if no rows
# are active. Admins can add unlimited rows from Django admin.
# ═════════════════════════════════════════════════════════════════


class HomeHeroSlide(models.Model):
    """One slide in the rotating hero carousel at the very top of the home page."""

    CHARACTER_LEFT = "left"
    CHARACTER_RIGHT = "right"
    CHARACTER_NONE = "none"
    CHARACTER_CHOICES = [
        (CHARACTER_LEFT, "Left character"),
        (CHARACTER_RIGHT, "Right character"),
        (CHARACTER_NONE, "No character"),
    ]

    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")
    is_active = models.BooleanField(default=True)

    title = models.CharField(
        max_length=200,
        help_text="Big heading, e.g. 'Not a club, Not an academy, and not an agent.'",
    )
    subtitle = models.CharField(
        max_length=160,
        blank=True,
        help_text="Optional smaller text under the title, e.g. '(India Khelo Football)'.",
    )
    body = models.TextField(
        blank=True,
        help_text=(
            "Paragraph below the title. You can use <strong>bold</strong> tags. "
            "Example: 'It is a neutral platform designed to ensure that talent is discovered, evaluated, and connected to opportunity.'"
        ),
    )
    tagline = models.CharField(
        max_length=200,
        blank=True,
        default="Aap Khelo, Mauka Hum Denge",
        help_text="Yellow line at the bottom of the slide.",
    )

    background_image = models.ImageField(
        upload_to="home/hero/bg/",
        blank=True,
        null=True,
        help_text=(
            "Optional. Stadium / pitch background. "
            "Recommended size: 1920×1080 px (16:9), .jpg or .png. "
            "Leave blank to use the default."
        ),
    )
    character_image = models.ImageField(
        upload_to="home/hero/characters/",
        blank=True,
        null=True,
        help_text=(
            "Optional. Player / mascot cut-out shown on the side. "
            "Recommended size: 800×1500 px portrait, transparent .png. "
            "Leave blank for none."
        ),
    )
    character_position = models.CharField(
        max_length=10,
        choices=CHARACTER_CHOICES,
        default=CHARACTER_LEFT,
        help_text="Which side the character image sits on.",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Home – Hero Slide"
        verbose_name_plural = "Home – Hero Slides"

    def __str__(self):
        return f"Slide {self.order}: {self.title[:60]}"


class HomeFootprintProject(models.Model):
    """One row in the 'Footprint Projects' section under the hero carousel."""

    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first (1 = top).")
    is_active = models.BooleanField(default=True)

    tab_title = models.CharField(
        max_length=120,
        help_text="Short title for the left-side tab list, e.g. 'Scout on Wheel'.",
    )
    tab_subtitle = models.CharField(
        max_length=240,
        blank=True,
        help_text="One-line description shown under the tab title.",
    )

    pane_title = models.CharField(
        max_length=160,
        blank=True,
        help_text=(
            "Big title shown on the right when this tab is selected. "
            "Leave blank to use the tab title. Example: 'IKF 360 – Beyond the Field'."
        ),
    )
    pane_description = models.TextField(
        blank=True,
        help_text="Longer description shown on the right. Plain text or HTML.",
    )
    image = models.ImageField(
        upload_to="home/footprint/",
        blank=True,
        null=True,
        help_text=(
            "Image shown on the right side for this project. "
            "Recommended size: 1200×900 px (4:3), .jpg or .png. "
            "Image is cropped to fill the panel, so keep the main subject centred."
        ),
    )
    explore_url = models.CharField(
        max_length=400,
        blank=True,
        help_text="Where the 'Explore Project →' button should go. Can be a full URL.",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Home – Footprint Project"
        verbose_name_plural = "Home – Footprint Projects"

    def __str__(self):
        return f"{self.order:02d}. {self.tab_title}"


class HomeBackboneCard(models.Model):
    """One card in the 'Build the football ecosystem with IKF' (IKF Backbone) section."""

    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first (1 = leftmost).")
    is_active = models.BooleanField(default=True)

    kicker = models.CharField(
        max_length=120,
        help_text="Pill text at the top of the card, e.g. 'Host City Trials'.",
    )
    title = models.CharField(
        max_length=160,
        help_text="Main card title, e.g. 'Regional Execution Partners'.",
    )
    description = models.CharField(
        max_length=400,
        blank=True,
        help_text="Short paragraph under the title.",
    )
    arrow_label = models.CharField(
        max_length=80,
        blank=True,
        help_text="Bottom action label, e.g. 'Become REP' or 'View partnerships'.",
    )
    url = models.CharField(
        max_length=400,
        blank=True,
        help_text="Where this card links to. Can be a path like '/rep/' or a full URL.",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Home – Backbone Card"
        verbose_name_plural = "Home – Backbone Cards"

    def __str__(self):
        return f"{self.order:02d}. {self.title}"


class PageStickyTitle(models.Model):
    """
    Lets non-tech admins override the floating/sticky page title that appears
    just below the navbar on every non-home page.

    If no active entry matches the current page, the template falls back to
    the existing auto-detection (navbar link text → first H1).
    """
    url_name = models.CharField(
        max_length=120,
        unique=True,
        choices=STICKY_PAGE_CHOICES,
        help_text="Pick the page you want to update the sticky title for.",
    )
    title = models.CharField(
        max_length=120,
        help_text=(
            "The text that shows in the sticky bar when this page is scrolled. "
            "Example: 'Democratizing the Dream'."
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to temporarily disable this override (page goes back to auto-title).",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["url_name"]
        verbose_name = "Sticky Page Title"
        verbose_name_plural = "Sticky Page Titles"

    def __str__(self):
        return f"{self.get_url_name_display()} → {self.title}"


# ─────────────────────────────────────────────────────────────
# IKF Career 360 — The Parent Conversation (Quiz)
# ─────────────────────────────────────────────────────────────
class ParentConversation(models.Model):
    PROFILE_CHOICES = [
        ("aligned",   "Aligned Parent"),
        ("potential", "Potential Parent"),
        ("atrisk",    "At-Risk Parent"),
    ]
    GENDER_CHOICES = [
        ("boy",   "Boy"),
        ("girl",  "Girl"),
        ("other", "Other"),
    ]

    # Intake
    parent_name  = models.CharField(max_length=200)
    parent_email = models.EmailField()
    child_age    = models.PositiveIntegerField()
    child_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    # Q1 — How did your child first fall in love with football?
    q1_origin       = models.CharField(max_length=20, blank=True)
    q1_origin_open  = models.TextField(blank=True)
    # Q2 — When your child talks about football, what do you hear most?
    q2_child_voice  = models.CharField(max_length=20, blank=True)
    # Q3 — Worth-it outcome at 22
    q3_worth_it     = models.CharField(max_length=20, blank=True)
    # Q4 — Weekly support pattern
    q4_support      = models.CharField(max_length=20, blank=True)
    # Q5 — Hardest part right now (open)
    q5_hardest_part = models.TextField(blank=True)
    # Q6 — % of children who turn pro
    q6_pro_estimate = models.CharField(max_length=20, blank=True)
    # Q7 — If 10 years pass and no pro, what should football have given them?
    q7_ten_years    = models.CharField(max_length=20, blank=True)
    # Q8 — Does IKF's full-ecosystem approach matter?
    q8_ecosystem    = models.CharField(max_length=20, blank=True)

    profile         = models.CharField(max_length=20, choices=PROFILE_CHOICES, db_index=True)

    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Parent Conversation Response"
        verbose_name_plural = "Parent Conversation Responses"

    def __str__(self):
        return f"{self.parent_name} — {self.get_profile_display()}"


class DonateProject(models.Model):
    name             = models.CharField(max_length=200, help_text="Project name shown as the card title.")
    slug             = models.SlugField(max_length=220, unique=True, blank=True,
                          help_text="Auto-generated from the project name. Used in the URL: /donate/<slug>/. Leave blank to auto-fill.")
    description      = models.CharField(max_length=300, help_text="One-line description shown under the title on the donate page.")
    read_more_url    = models.CharField(max_length=500, blank=True,
                          help_text="Optional fallback. Used as 'Know more' link ONLY when no detail-page content (banner/intro/sections) is filled.")
    detail_banner    = models.ImageField(upload_to='donate/projects/', null=True, blank=True,
                          help_text="Detail page banner (right side of the hero). Recommended size: 1200 x 900 px (4:3 aspect ratio). Max file size 2 MB. JPG/PNG/WebP.")
    detail_intro     = models.TextField(blank=True,
                          help_text="Longer introduction shown next to the banner on the detail page. Falls back to the short description if blank.")
    display_order    = models.PositiveIntegerField(default=100, db_index=True,
                          help_text="Lower numbers appear first.")
    is_active        = models.BooleanField(default=True, db_index=True,
                          help_text="Uncheck to hide this project from the donate page.")
    razorpay_enabled = models.BooleanField(default=True,
                          help_text="Show Razorpay as a payment option for this project.")
    upi_enabled      = models.BooleanField(default=True,
                          help_text="Show UPI as a payment option for this project.")
    bank_enabled     = models.BooleanField(default=True,
                          help_text="Show Bank Transfer as a payment option for this project.")
    preset_amounts   = models.CharField(max_length=200, default="500,1000,5000,10000",
                          help_text="Comma-separated INR amounts shown as quick-select buttons. e.g. 500,1000,5000,10000")
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Donate Page Project'
        verbose_name_plural = 'Donate Page Projects'

    def __str__(self):
        return f"{self.display_order} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200] or 'project'
            candidate = base
            i = 2
            while DonateProject.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def preset_list(self):
        out = []
        for token in (self.preset_amounts or "").split(","):
            token = token.strip()
            if token.isdigit():
                out.append(int(token))
        return out

    def has_detail_content(self):
        if self.detail_banner or (self.detail_intro and self.detail_intro.strip()):
            return True
        return self.sections.exists()


class DonateProjectSection(models.Model):
    project       = models.ForeignKey(DonateProject, on_delete=models.CASCADE, related_name='sections')
    heading       = models.CharField(max_length=200)
    content       = models.TextField(help_text="Body text shown under the heading. Plain text or simple HTML.")
    image         = models.ImageField(upload_to='donate/projects/sections/', null=True, blank=True,
                        help_text="Optional. When present, image sits beside the text. When blank, text spans full width. Recommended size: 1000 x 750 px (4:3 aspect ratio). Max file size 2 MB. JPG/PNG/WebP.")
    display_order = models.PositiveIntegerField(default=100, db_index=True,
                        help_text="Lower numbers appear first.")

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Donate Project Section'
        verbose_name_plural = 'Donate Project Sections'

    def __str__(self):
        return f"{self.project.name} - {self.heading}"


class DonateSettings(models.Model):
    """Singleton: global settings for the donate page. Edit the single row in admin."""
    reg_80g             = models.CharField(max_length=100, default="AAICK4512EF20214")
    csr_number          = models.CharField(max_length=100, default="CSR00022415")
    upi_id              = models.CharField(max_length=100, default="khelofootball.123@idfcbank")
    upi_qr_image        = models.ImageField(upload_to='donateus', null=True, blank=True,
                            help_text="UPI QR shown when donor picks UPI.")
    bank_account_name   = models.CharField(max_length=200, default="KHELO FOOTBALL ECOSYSTEM DEVELOPMENT FEDERATION")
    bank_account_number = models.CharField(max_length=50,  default="10064068880")
    bank_ifsc           = models.CharField(max_length=20,  default="IDFB0040162")
    bank_swift          = models.CharField(max_length=20,  default="IDFBINBBMUM")
    bank_name           = models.CharField(max_length=100, default="IDFC FIRST")
    bank_branch         = models.CharField(max_length=200, default="Thane - Hiranandani Estate")
    whatsapp_number     = models.CharField(max_length=30,  default="+91 88501 19762")
    donate_email        = models.EmailField(default="donate@indiakhelofootball.com")
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Donate Page Settings"
        verbose_name_plural = "Donate Page Settings"

    def __str__(self):
        return "Donate Page Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OfflineDonationClaim(models.Model):
    METHOD_CHOICES = (
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending verification'),
        ('verified', 'Verified - payment received'),
        ('not_received', 'Not received'),
    )

    project      = models.CharField(max_length=200)
    method       = models.CharField(max_length=10, choices=METHOD_CHOICES, db_index=True)
    name         = models.CharField(max_length=200, blank=True)
    organisation = models.CharField(max_length=200, blank=True)
    email        = models.EmailField(blank=True)
    mobile       = models.CharField(max_length=20, blank=True)
    amount       = models.CharField(max_length=50, blank=True)
    anonymous    = models.BooleanField(default=False)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    admin_notes  = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Offline Donation Claim (UPI / Bank)'
        verbose_name_plural = 'Offline Donation Claims (UPI / Bank)'

    def __str__(self):
        who = 'Anonymous' if self.anonymous else (self.name or self.email or self.mobile or 'Unknown')
        return f"{who} - {self.project} ({self.get_method_display()}) - {self.amount or 'no amount'}"


# ─────────────────────────────────────────────────────────────
# "Explore More" side-nav (the sticky right-side rail)
#
# Lets non-tech admins build the "Explore More" rail per page:
#   • one ExploreNav = one rail configuration
#   • attach it to one or more pages (ExploreNavPage rows)
#   • add unlimited links (ExploreNavLink rows), optionally grouped
#
# If NO active ExploreNav matches the current page, the template falls
# back to the existing hardcoded rail — so nothing breaks until an admin
# starts adding entries.
# ─────────────────────────────────────────────────────────────
class ExploreNav(models.Model):
    """One 'Explore More' rail configuration, shown on the pages linked below."""

    admin_name = models.CharField(
        max_length=150,
        help_text="Internal name so you can recognise this rail in the admin list, "
                  "e.g. 'Explore More – Player pages'. Not shown on the website.",
    )
    label = models.CharField(
        max_length=40,
        default="Explore More",
        help_text="Text on the vertical tab (the little bar on the right edge). "
                  "Example: 'Explore More'.",
    )
    heading = models.CharField(
        max_length=80,
        default="Explore More",
        help_text="Heading shown at the top of the menu when it opens. "
                  "Example: 'Explore More'.",
    )
    show_home_link = models.BooleanField(
        default=True,
        help_text="Add a 'Home' link automatically at the bottom of the menu.",
    )
    apply_to_all_pages = models.BooleanField(
        default=False,
        help_text="Show this rail on EVERY page except Home. "
                  "A page that is listed under a specific rail below still uses that "
                  "specific rail instead of this site-wide one.",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="If a page is linked to more than one rail, the lowest order wins.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to disable this rail (the page falls back to the default rail).",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Side Nav – Explore More Rail"
        verbose_name_plural = "Side Nav – Explore More Rails"

    def __str__(self):
        return self.admin_name or self.label


class ExploreNavPage(models.Model):
    """A page on which a given ExploreNav rail should appear."""

    nav = models.ForeignKey(ExploreNav, related_name="pages", on_delete=models.CASCADE)
    url_name = models.CharField(
        max_length=120,
        choices=STICKY_PAGE_CHOICES,
        help_text="Pick a page where this 'Explore More' rail should show. "
                  "Add one row per page.",
    )

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Show on these pages"

    def __str__(self):
        return self.get_url_name_display()


class ExploreNavLink(models.Model):
    """One link inside an ExploreNav rail."""

    nav = models.ForeignKey(ExploreNav, related_name="links", on_delete=models.CASCADE)
    group_header = models.CharField(
        max_length=80,
        blank=True,
        help_text="Optional grey sub-heading shown above this link, e.g. 'Players:'. "
                  "Give consecutive links the same header to group them. Leave blank for none.",
    )
    label = models.CharField(
        max_length=140,
        help_text="Text shown for the link, e.g. 'Register for Trials'.",
    )
    url_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Django URL name to link to, e.g. 'season5'. "
                  "Fill this OR 'External URL' below.",
    )
    url_arg = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional argument for the URL name, e.g. 'trialcalendar' for a "
                  "noticeboard page. Leave blank if not needed.",
    )
    external_url = models.CharField(
        max_length=400,
        blank=True,
        help_text="Full link, e.g. 'https://example.com/page'. "
                  "Used only when 'URL name' is blank.",
    )
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower shows first.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Link"
        verbose_name_plural = "Links"

    def __str__(self):
        return self.label

    def get_href(self):
        """Resolve the link target: named URL (with optional arg) or the external URL."""
        if self.url_name:
            try:
                if self.url_arg:
                    return reverse(self.url_name, args=[self.url_arg])
                return reverse(self.url_name)
            except Exception:
                pass
        return self.external_url or "#"

    def matches_current(self, url_name, slug, current_path=""):
        """True when this link points at the page currently being viewed."""
        # Internal link by URL name (developer-set).
        if self.url_name:
            if self.url_name != url_name:
                return False
            if self.url_arg:
                return self.url_arg == (slug or "")
            return True
        # Full web address — compare its path to the page we're on.
        if self.external_url and current_path:
            try:
                from urllib.parse import urlparse
                link_path = urlparse(self.external_url).path.rstrip("/")
                return bool(link_path) and link_path == current_path.rstrip("/")
            except Exception:
                return False
        return False
