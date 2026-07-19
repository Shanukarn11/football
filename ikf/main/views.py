import os
import pathlib
import shutil
import json
import glob
import subprocess
import time
import random
from tracemalloc import Statistic
from django.contrib.auth import authenticate, login
from uuid import uuid1
import PIL
import requests
from django.core import serializers
from django.contrib import messages
import razorpay
import threading
import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse

from main.admin import WinnersAdmin
from .models import IKFAchievement, HomePageClub,HomePage, SupportedByImages2526, NoticeBoardInfoBlock,TeamVideoCarousel, IWLPartner, OfficialScoutingPartner,WorkshopInternationalLogo,WorkshopNews,About_TeamAdvisors,TabelPastTrial, Calendar_Season3, Gallery_Buttons, InstaFeed, Photo_Gallery_Images,Previous_Workshop_Images, UserFlow_Season3, Winners_Season2,Winners_Workshop_Images,Testimonials, TabelSeason3,Associate_TournamentOrganizer_Right,TakeaWay2_TournamentOrganizer,TakeaWay1_TournamentOrganizer, Season3_Features,Associate_TournamentOrganizer_Images, About_TeamCore_Team, Season3_Images, Selected_Players_Season2, Clubs_Parter_Season2, Clubs_Parter_Season1,Clubs_Parter_abouttrials, Clubs_Parter_Home, About_OURTEAM_of_IkF, Associate_Clubs_Right, TakeaWay3_Clubs, TakeaWay2_Clubs, TakeaWay1_Clubs, Associate_Academy_Images, Associate_Clubs_Images, TakeaWay1_Academy, TakeaWay2_Academy, About_Us_Images, About_section1, AboutTrials_BannerPhoto, AboutTrials_Feature, AboutTrials_Images, AboutUs, Associate_Corporate_Images, Associate_Corporate_Main, Associate_Corporate_Right, Associate_PSUS_Images, Associate_PSUS_Main, Associate_PSUS_Right, Associate_Philanthropists_Images, Associate_Philanthropists_Main, Associate_Philanthropists_Right, Buttons_IKF_FOR_ALL, Clubs, Clubs_Partners1, Corporate_Images, Corporate_Partners1, IKF_Tech1, IKF_Tech2, IKF_Tech3, IKF_Tech4, IKF_Technology_Images, Initiatives, International_Images, International_Partners1, MasterLabels, National_Images, National_Partners1, NavTabs, Navbar, Lang, HomeBanner, HomeImages, News, Partners, Photos_IKF_FOR_ALL, PlayAbroad_Images, Playabroad, Playabroad_Features, Playabroad_Initiatives, Reginoal_Images, Regional_Partners1, Scouting_Features, Scouting_Initiatives, ScoutingCertification_Images, Season1_Bottom, Season1_Button, Season1_Feature, Season1_Images, Season1_Tabs, Season2_Features, Season2_Images, Selected_Players_Season1, Tab, TabelPlayabroad, TabelScoutingCertification, TabelSeason2, TabelWorkshops, TabelWorkshopsReg, TakeaWay1_Corporate, TakeaWay1_PSUS, TakeaWay1_Philanthropists, TakeaWay2_Corporate, TakeaWay2_PSUS, TakeaWay2_Philanthropists, TakeaWay3_PSUS, UpCommingMatchs, Winners, WorkShops_Images, WorkShopsButton, WorkShopsExperts, WorkShopsFeatureStrip, MasterSeason, MasterState, MasterCity, MasterPosition, MasterIkfSeasonUi, TrialsAndInitiativeType, TrialsAndInitiativeNav, ActiveStatusNav, WorkShopsReg_Images, WorkShopsRegButton, WorkShopsRegExperts, WorkShopsRegFeatureStrip, Youtube,Resources, SupportedByFinancial, SupportedBy, SupportedByImages, MoreaboutIKF,Donate_Images,DonateFeatureStrip,Donation,PaymentFeatureStrip,TabelDonate, SupportIkfFeatureStrip, PartnerSeasonSupportIKF,Calender,Finalists, Coaches, Scout

from django.db.models import Prefetch
from django.db.models.functions import Lower
from .forms import DesportzContactForm
from django.core.mail import send_mail
from django.http import JsonResponse

import pandas as pd
import plotly.express as px
from django.shortcuts import render
from django.db import connections
import plotly.graph_objects as go
import json






BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()

from django.shortcuts import render, get_object_or_404, redirect
# ... your existing imports ...

def onboarding(request):
    # renders templates/html/onboarding.html
    return render(request, "html/onboarding.html")

def rep_template(request):
    # renders templates/html/rep_template.html
    return render(request, "html/rep_template.html")

def pagelabel(lang):

    langqueryset = list(MasterLabels.objects.filter(
        lang=lang).values('keydata', 'label'))
    dictvalue = {}
    for item in langqueryset:
        dictvalue[item['keydata']] = item['label']
    return dictvalue

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.db import transaction
from django.db.models import Prefetch

from .models import RepTemplate, RepHighlight, RepPlayer, RepSocialLink
from .forms import (
    build_onboarding_form_for_rep,
    RepHighlightFormSet,
    RepPlayerFormSet,
    RepSocialLinkFormSet,
)

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.db import transaction

from .models import RepTemplate
from .forms import (
    build_onboarding_form_for_rep,
    RepHighlightFormSet,
    RepPlayerFormSet,
    RepSocialLinkFormSet,
)

@require_http_methods(["GET", "POST"])
def rep_onboarding(request, token):
    rep = get_object_or_404(RepTemplate, onboarding_token=token)
    preview_url = request.build_absolute_uri(reverse("rep_preview", args=[rep.onboarding_token]))

    # hard lock
    if request.method == "POST" and rep.is_locked:
        messages.error(request, "Editing is locked after final submission. Please contact the IKF team to reopen.")
        return redirect("rep_onboarding", token=rep.onboarding_token)  # ✅ stay on the same URL

    FormClass = build_onboarding_form_for_rep(rep)

    if request.method == "POST":
        action = request.POST.get("action", "save")
        form  = FormClass(request.POST, request.FILES, instance=rep)
        hl_fs = RepHighlightFormSet(request.POST, request.FILES, instance=rep, prefix="hl")
        pl_fs = RepPlayerFormSet   (request.POST, request.FILES, instance=rep, prefix="pl")
        sl_fs = RepSocialLinkFormSet(request.POST, request.FILES, instance=rep, prefix="sl")

        if form.is_valid() and hl_fs.is_valid() and pl_fs.is_valid() and sl_fs.is_valid():
            with transaction.atomic():
                form.save(); hl_fs.save(); pl_fs.save(); sl_fs.save()

                plan = getattr(rep, "plan", None)
                if callable(getattr(plan, "export_schema", None)):
                    rep.onboarding_schema_snapshot = plan.export_schema()
                    rep.save(update_fields=["onboarding_schema_snapshot"])

                if action == "final":
                    rep.is_submitted = True
                    rep.submitted_at = rep.submitted_at or timezone.now()
                    rep.is_locked = True
                    rep.is_approved = False
                    rep.approved_at = None
                    rep.approved_by = None
                    rep.save(update_fields=["is_submitted","submitted_at","is_locked","is_approved","approved_at","approved_by"])
                    messages.success(request, "Submitted for review. Editing is now locked.")
                else:
                    messages.success(request, "Saved draft. Use Preview to check how it looks.")

            return redirect("rep_onboarding", token=rep.onboarding_token)  # ✅ NOT "onboarding"

        messages.error(request, "Please fix the errors below and submit again.")
    else:
        form  = FormClass(instance=rep)
        hl_fs = RepHighlightFormSet(instance=rep, prefix="hl")
        pl_fs = RepPlayerFormSet   (instance=rep, prefix="pl")
        sl_fs = RepSocialLinkFormSet(instance=rep, prefix="sl")

    ctx = {
        "rep": rep,
        "form": form,
        "hl_formset": hl_fs,
        "pl_formset": pl_fs,
        "sl_formset": sl_fs,
        "preview_url": preview_url,
    }
    return render(request, "html/rep_onboarding.html", ctx)  # ✅ dedicated onboarding form template




@require_GET
def rep_preview(request, token):
    """Token-protected preview of the public page; renders even if not approved."""
    rep = get_object_or_404(RepTemplate, onboarding_token=token)
    return render(request, "html/rep_template.html", {"rep": rep, "preview": True})


@require_GET
def rep_public(request, slug):
    """Only approved pages visible publicly."""
    rep = get_object_or_404(RepTemplate, template_link=slug, is_approved=True)
    return render(request, "html/rep_template.html", {"rep": rep})


@require_GET
def rep_page(request, template_link):
    """Public page by template_link (case-insensitive)."""
    key = (template_link or "").strip()

    highlights_qs = RepHighlight.objects.only(
        "id", "rep_id", "title", "text", "order"
    ).order_by("order")
    players_qs = RepPlayer.objects.only(
        "id", "rep_id", "name", "subtitle", "photo", "order"
    ).order_by("order")
    socials_qs = RepSocialLink.objects.only(
        "id", "rep_id", "platform", "url"
    ).order_by("platform")

    base_qs = (
        RepTemplate.objects
        .filter(template_link__iexact=key, is_approved=True)
        .order_by("-id")  # latest wins if dupes
        .only(
            "id", "rep_name", "rep_num", "template_link",
            "rep_logo", "rep_banner", "players_bg",
            "content", "next_status",
            "cities_of_operation", "website_url",
            "rep_opinion", "rep_category", "rep_category_brief",
            "csr_activities", "ikf_activities", "rep_founder",
            "theme", "brand_color", "hero_bg_color", "card_color", "text_color",
            "show_pills", "show_stats", "created_at",
            "stat1_value","stat1_label","stat2_value","stat2_label",
            "stat3_value","stat3_label","stat4_value","stat4_label",
        )
        .prefetch_related(
            Prefetch("highlights", queryset=highlights_qs, to_attr="prefetched_highlights"),
            Prefetch("players",    queryset=players_qs,    to_attr="prefetched_players"),
            Prefetch("socials",    queryset=socials_qs,    to_attr="prefetched_socials"),
        )
    )

    rep = get_object_or_404(base_qs)

    context = {
        "rep": rep,
        "highlights": getattr(rep, "prefetched_highlights", []),
        "players": getattr(rep, "prefetched_players", []),
        "socials": getattr(rep, "prefetched_socials", []),
        "canonical_url": request.build_absolute_uri(),
    }
    return render(request, "html/rep_template.html", context)



# views.py
from django.shortcuts import render
from .models import RepTemplate

def rep_landing(request):
    reps = RepTemplate.objects.filter(is_approved=True).order_by("-id")[:24]
    return render(request, "html/landing.html", {"reps": reps})


def rep_become_partner(request):
    from .models import RepOpenState

    states = (
        RepOpenState.objects
        .filter(is_active=True)
        .prefetch_related('cities')
        .order_by('order', 'name')
    )

    # Build list of (state_name, [active city names]) — skip states with no active cities
    cities_by_state = [
        (s.name, [c.city for c in s.cities.filter(is_active=True).order_by('order', 'city')])
        for s in states
        if s.cities.filter(is_active=True).exists()
    ]

    return render(request, "html/rep_become_partner.html", {
        "cities_by_state": cities_by_state,
    })


from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.templatetags.static import static
from .models import Lawyer, ScoutProfile
from .scout_profiles_data import SCOUT_DETAILS_CONTEXT, SCOUT_LETTER, SCOUT_PROFILES, get_scout_profile

def lawyer_landing(request):
    lawyers = Lawyer.objects.filter(is_featured=True).only("name", "template_link", "photo")
    if not lawyers.exists():
        lawyers = Lawyer.objects.all().only("name", "template_link", "photo")[:12]
    return render(request, "html/lawyer_landing.html", {"lawyers": lawyers})

def lawyer_index(request):
    q = (request.GET.get("q") or "").strip()
    city = (request.GET.get("city") or "").strip()
    practice = (request.GET.get("practice") or "").strip()  # maps to expertise_area

    qs = Lawyer.objects.all().only("name", "template_link", "photo", "city", "expertise_area")

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(city__icontains=q) | Q(expertise_area__icontains=q))
    if city:
        qs = qs.filter(city__icontains=city)
    if practice:
        qs = qs.filter(expertise_area__icontains=practice)

    return render(request, "html/lawyer_grid.html", {
        "lawyers": qs.order_by("name"),
        "q": q, "practice": practice, "city": city,
    })

def lawyer_detail(request, template_link):
    lawyer = get_object_or_404(
        Lawyer.objects.only("name", "template_link", "photo", "city", "expertise_area", "linkedin_url"),
        template_link=template_link
    )
    return render(request, "html/lawyer_detail.html", {"lawyer": lawyer})


def _scout_card_pills(profile):
    experience = profile.get("experience", "") if isinstance(profile, dict) else profile.experience
    age_groups = profile.get("age_groups", "") if isinstance(profile, dict) else profile.age_groups
    players_assessed = profile.get("players_assessed", "") if isinstance(profile, dict) else profile.players_assessed

    pills = []
    if experience:
        pills.append(("Total scouting experience", experience))
    if len(pills) < 3 and players_assessed:
        pills.append(("Players assessed", players_assessed))
    if len(pills) < 3 and age_groups:
        pills.append(("Age groups scouted", age_groups))

    return pills[:3]


def _scout_photo_url(filename):
    if not filename:
        return ""
    return static(f"images/scouts/{filename}")


def _prepare_scout(profile):
    if isinstance(profile, dict):
        item = profile.copy()
        item["photo_url"] = _scout_photo_url(item.get("photo"))
        return item

    profile.photo_url = profile.photo.url if profile.photo else ""
    return profile


def _prepare_scout_cards(scouts):
    prepared = []
    for profile in scouts:
        item = _prepare_scout(profile)
        if isinstance(item, dict):
            item["card_pills"] = _scout_card_pills(item)
        else:
            item.card_pills = _scout_card_pills(item)
        prepared.append(item)
    return prepared


def scout_landing(request):
    active_scouts = ScoutProfile.objects.filter(is_active=True).order_by("sort_order", "name")
    if not active_scouts.exists():
        return render(request, "html/scout_landing.html", {
            "letter": SCOUT_LETTER,
            "scout_details": SCOUT_DETAILS_CONTEXT,
            "featured_scouts": _prepare_scout_cards(SCOUT_PROFILES),
            "scout_count": len(SCOUT_PROFILES),
        })

    featured_scouts = active_scouts.filter(is_featured=True)
    if not featured_scouts.exists():
        featured_scouts = active_scouts

    return render(request, "html/scout_landing.html", {
        "letter": SCOUT_LETTER,
        "scout_details": SCOUT_DETAILS_CONTEXT,
        "featured_scouts": _prepare_scout_cards(featured_scouts),
        "scout_count": active_scouts.count(),
    })


def scout_index(request):
    q_raw = (request.GET.get("q") or "").strip()
    state_raw = (request.GET.get("state") or "").strip()
    q = q_raw.lower()
    state = state_raw.lower()

    scouts = ScoutProfile.objects.filter(is_active=True)
    if not scouts.exists():
        fallback_scouts = SCOUT_PROFILES
        if q:
            fallback_scouts = [
                profile for profile in fallback_scouts
                if q in " ".join(str(value).lower() for value in profile.values())
            ]
        if state:
            fallback_scouts = [
                profile for profile in fallback_scouts
                if state in profile.get("state", "").lower()
            ]
        states = sorted({profile["state"] for profile in SCOUT_PROFILES if profile.get("state")})

        return render(request, "html/scout_grid.html", {
            "scouts": _prepare_scout_cards(list(fallback_scouts)),
            "states": states,
            "q": q_raw,
            "selected_state": state_raw,
            "total_scouts": len(SCOUT_PROFILES),
        })

    if q:
        scouts = scouts.filter(
            Q(name__icontains=q_raw)
            | Q(city__icontains=q_raw)
            | Q(state__icontains=q_raw)
            | Q(regions__icontains=q_raw)
            | Q(strengths__icontains=q_raw)
            | Q(age_groups__icontains=q_raw)
            | Q(certification__icontains=q_raw)
            | Q(email__icontains=q_raw)
            | Q(phone__icontains=q_raw)
        )
    if state:
        scouts = scouts.filter(state=state_raw)

    states = list(
        ScoutProfile.objects.filter(is_active=True)
        .exclude(state="")
        .order_by("state")
        .values_list("state", flat=True)
        .distinct()
    )
    total_scouts = ScoutProfile.objects.filter(is_active=True).count()

    return render(request, "html/scout_grid.html", {
        "scouts": _prepare_scout_cards(scouts.order_by("sort_order", "name")),
        "states": states,
        "q": q_raw,
        "selected_state": state_raw,
        "total_scouts": total_scouts,
    })


def scout_detail(request, slug):
    scout = ScoutProfile.objects.filter(slug=slug, is_active=True).first()
    if scout is None:
        scout = get_scout_profile(slug)
        if scout is None:
            raise Http404("Scout profile not found")
        scout = _prepare_scout(scout)
        related_scouts = _prepare_scout_cards([
            profile for profile in SCOUT_PROFILES
            if profile["slug"] != slug and profile.get("state") == scout.get("state")
        ][:3])

        return render(request, "html/scout_detail.html", {
            "scout": scout,
            "related_scouts": related_scouts,
        })

    scout = _prepare_scout(scout)
    related_scouts = _prepare_scout_cards(
        ScoutProfile.objects.filter(is_active=True, state=scout.state)
        .exclude(pk=scout.pk)
        .order_by("sort_order", "name")[:3]
    )

    return render(request, "html/scout_detail.html", {
        "scout": scout,
        "related_scouts": related_scouts,
    })





from .models import (
    HomeImages, HomeBanner, AboutUs, NavTabs, Initiatives,
    MoreaboutIKF, Buttons_IKF_FOR_ALL, Photos_IKF_FOR_ALL,
    InstaFeed, Tab, UpCommingMatchs, MasterCity, MasterIkfSeasonUi,
    OfficialScoutingPartner, IWLPartner, Clubs_Parter_Home,
)


def home(request):
    lang = 'en'
    context = pagelabel(lang)

    homeimages = HomeImages.objects.filter(lang=lang).values()

    dictvar = {}
    for img in homeimages:
        dictvar[img['keydata']] = img['pic']
    
    context['homeimages'] = dictvar

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['aboutus'] = AboutUs.objects.filter(lang=lang).values()
    context['Navtab'] = NavTabs.objects.filter(lang=lang).values()
    context['initiatives'] = Initiatives.objects.filter(lang=lang).values()
    context['moreaboutIKF'] = MoreaboutIKF.objects.filter(lang=lang).values()
    context['buttons'] = Buttons_IKF_FOR_ALL.objects.filter(lang=lang).values()
    context['photos'] = Photos_IKF_FOR_ALL.objects.filter(lang=lang).values()
    context['Insta'] = InstaFeed.objects.filter(lang=lang).values()
    context['tabs'] = Tab.objects.all().values()

    upcomingmatches = UpCommingMatchs.objects.filter(include=True).values()
    for match in upcomingmatches:
        d = match['matchdate']
        originalmonth = match['matchdate'].month
        modifiedmonth = originalmonth - 1
        newdate = d.replace(month=modifiedmonth)

        match['mydate'] = newdate.isoformat()

        match['Team2_pic'] = MasterCity.objects.get(
            id=match['teamname_2nd_id']
        ).pic
        match['teamname_2nd_id'] = MasterCity.objects.get(
            id=match['teamname_2nd_id']
        ).city

        match['Team1_pic'] = MasterIkfSeasonUi.objects.get(
            id=match['teamname_1st_id']
        ).pic
        match['teamname_1st_id'] = MasterIkfSeasonUi.objects.get(
            id=match['teamname_1st_id']
        ).name

    context['Matches'] = upcomingmatches

    # 🔻 Separate lists instead of one combined one
    official_scouting_clubs = []
    isl_clubs = []
    iwl_clubs = []

    # Official Scouting Partner
    for p in OfficialScoutingPartner.objects.all():
        official_scouting_clubs.append({
            "pic": p.image,
            "name": p.name,
        })

    # ISL Clubs (local)
    for c in Clubs_Parter_Home.objects.filter(is_international=False):
        isl_clubs.append({
            "pic": c.pic,
            "name": c.name,
        })

    # IWL Clubs
    for i in IWLPartner.objects.all():
        iwl_clubs.append({
            "pic": i.image,
            "name": i.name,
        })

    context['official_scouting_clubs'] = official_scouting_clubs
    context['isl_clubs'] = isl_clubs
    context['iwl_clubs'] = iwl_clubs
    context['indian_clubs_pre_second'] = Clubs_Parter_Season1.objects.order_by('keydata')

    # IKF Achievements section
    context['ikf_achievements'] = IKFAchievement.objects.filter(is_active=True).order_by('order')

    # Supported By companies for Trusted By section
    context['supported_by_companies'] = SupportedBy.objects.filter(logo_pic__isnull=False).exclude(logo_pic='').order_by('order_by')

    # (you can remove this if you no longer need the combined list)
    # context['clubs_partner_home'] = official_scouting_clubs + isl_clubs + iwl_clubs

    # ── Admin-managed home sections (fall back to hardcoded if empty) ──
    from .models import HomeHeroSlide, HomeFootprintProject, HomeBackboneCard
    context['home_hero_slides'] = list(
        HomeHeroSlide.objects.filter(is_active=True).order_by('order', 'id')
    )
    context['home_footprint_projects'] = list(
        HomeFootprintProject.objects.filter(is_active=True).order_by('order', 'id')
    )
    context['home_backbone_cards'] = list(
        HomeBackboneCard.objects.filter(is_active=True).order_by('order', 'id')
    )

    return render(request, 'html/index.html', context)






def IkfTrials(request):
    lang = 'en'
    context = pagelabel(lang)

    ikftrialsimages = AboutTrials_Images.objects.filter(lang=lang).values()
    dictvar = dict()
    for img in ikftrialsimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['ikftrialsimages'] = dictvar
    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['bannerphoto'] = AboutTrials_BannerPhoto.objects.filter(
        lang=lang).values()
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(pagetype="about_trial",lang=lang).values()
    context['clubs_partner_home'] = Clubs_Parter_Home.objects.filter(
        lang=lang, is_participated=True).values()
    context['features'] = AboutTrials_Feature.objects.filter(
        lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()
    winners = Winners.objects.filter(lang=lang).values()
    for winner in winners:
        winner['category_id'] = MasterPosition.objects.get(
            id=winner['category_id']).label

    context['winners'] = winners
    return render(request, 'html/IkfTrials.html', context)


def season1(request):
    lang = 'en'
    context = pagelabel(lang)

    season1images = Season1_Images.objects.filter(lang=lang).values()
    buttons = Season1_Button.objects.filter(lang=lang).values()
    dictvar = dict()
    for img in season1images:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['season1images'] = dictvar
    context['season1_buttons'] = buttons
    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['season1_features'] = Season1_Feature.objects.filter(
        lang=lang).values()
    context['tabel_pasttrial'] = TabelPastTrial.objects.filter(lang=lang).values()
    context['clubs_partner_home'] = Clubs_Parter_Home.objects.filter(
        lang=lang).values()
    # context['clubs_partner_season1'] = Clubs_Parter_Season1.objects.filter(
    #     lang=lang).values()
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(pagetype="S01",
                                                                              lang=lang).values()
    context['season1_bottoms'] = Season1_Bottom.objects.filter(
        lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()
    context['Selected_Season1'] = Selected_Players_Season1.objects.filter(
        lang=lang).values()
    winners = Winners.objects.filter(lang=lang).values()
    for winner in winners:
        winner['category_id'] = MasterPosition.objects.get(
            id=winner['category_id']).label

    context['winners'] = winners

    return render(request, 'html/season1.html', context)

from django.shortcuts import render, get_object_or_404
from .models import MessageWeblink

from django.shortcuts import render, get_object_or_404
from .models import MessageWeblink

from django.shortcuts import render, get_object_or_404
from .models import MessageWeblink

def message_weblink(request, code):
    page = get_object_or_404(MessageWeblink, code=code.lower(), is_active=True)

    guidelines_en = [x.strip() for x in page.guidelines_en.splitlines() if x.strip()]
    guidelines_hi = [x.strip() for x in page.guidelines_hi.splitlines() if x.strip()]

    host = request.get_host().split(":")[0]
    show_download = (
        code.lower() == "national"
        and host in ["indiakhelofootball.com", "www.indiakhelofootball.com", "localhost", "127.0.0.1"]
    )

    context = {
        "page": page,
        "guidelines_en": guidelines_en,
        "guidelines_hi": guidelines_hi,
        "show_download": show_download,
    }
    return render(request, "html/message_weblink.html", context)


from django.shortcuts import render, get_object_or_404
from .models import ConsentNocWeblink


def noc_page(request, code):
    page = get_object_or_404(ConsentNocWeblink, code=code, is_active=True)
    return render(request, "html/noc_consent.html", {"page": page})

from django.shortcuts import render

def privacy(request):
    return render(request, "html/privacy.html")


def terms_and_conditions(request):
    from .models import TermsSection
    sections = TermsSection.objects.filter(is_active=True)
    return render(request, 'html/terms_and_conditions.html', {'sections': sections})


def season2(request):
    lang = 'en'
    context = pagelabel(lang)

    season2images = Season2_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in season2images:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['season2images'] = dictvar

    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(
        pagetype="S02", lang=lang).values()
    context['clubs_partner_season2'] = Clubs_Parter_Season2.objects.filter(
        lang=lang).values()
    context['tabel'] = TabelSeason2.objects.filter(lang=lang).values()
    context['Featurestrip'] = Season2_Features.objects.filter(
        lang=lang).values()
    winners_season2 = Winners_Season2.objects.filter(lang=lang).values()
    for winner in winners_season2:
        winner['category_id'] = MasterPosition.objects.get(
            id=winner['category_id']).label
    context['winners'] = winners_season2
    context['Selected_Season2'] = Selected_Players_Season2.objects.filter(
        lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()

    return render(request, 'html/season2.html', context)


def season3(request):
    lang = 'en'
    context = pagelabel(lang)

    season3images = Season3_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in season3images:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['season3images'] = dictvar

    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(
        pagetype="S03", lang=lang).values()
    context['tabel_season3'] = TabelSeason3.objects.filter(lang=lang).values()
    context['UserFlow'] = UserFlow_Season3.objects.filter(
        lang=lang).values()
    context['Information'] = Calendar_Season3.objects.filter(
        lang=lang).values()
    context['Featurestrip_Season3'] = Season3_Features.objects.filter(
        lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()

    return render(request, 'html/season3.html', context)


def scoutingcertification(request):
    lang = 'en'
    context = pagelabel(lang)

    scoutingimages = ScoutingCertification_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in scoutingimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['scoutingimages'] = dictvar
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(pagetype="scouting_certification",
                                                                              lang=lang).values()

    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()
    context['tabel_Scouting'] = TabelScoutingCertification.objects.filter(
        lang=lang).values()
    context['FeatureScouting'] = Scouting_Features.objects.filter().values()
    context['Scout_initiative'] = Scouting_Initiatives.objects.filter().values()

    return render(request, 'html/scoutingcertification.html', context)


def playabroad(request):
    lang = 'en'
    context = pagelabel(lang)

    playabroadimages = PlayAbroad_Images.objects.filter(lang=lang).values()
    buttons = Playabroad.objects.filter(lang=lang).values()
    dictvar = dict()
    for img in playabroadimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['playabroad_buttons'] = buttons
    # {'playabroad_header':pic}
    context['playabroadimages'] = dictvar
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(
        pagetype="play_abroad", lang=lang).values()
    context['tabel_Playabroad'] = TabelPlayabroad.objects.filter(
        lang=lang).values()
    context['Featurestrip_Playabroad'] = Playabroad_Features.objects.filter().values()
    context['Playabroad_initiative'] = Playabroad_Initiatives.objects.filter().values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()

    return render(request, 'html/playabroad.html', context)


def workshops(request):
    lang = 'en'
    context = pagelabel(lang)

    workshopsimages = WorkShops_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in workshopsimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Workshops'] = TabelWorkshops.objects.filter(
        lang=lang).values()
    context['buttons'] = WorkShopsButton.objects.filter(
        lang=lang).values()
    context['featurestrips'] = WorkShopsFeatureStrip.objects.filter(
        lang=lang).values()
    context['learnfromexperts'] = WorkShopsExperts.objects.filter(
        lang=lang).values()
    context['previous_workshop'] = Previous_Workshop_Images.objects.filter(
        lang=lang).values()
    
    winners = Winners.objects.filter(lang=lang).filter(attr2="int").values()
    for winner in winners:
        winner['category_id'] = MasterPosition.objects.get(
            id=winner['category_id']).label

    context['winners'] = winners
    context['testimonials'] = Testimonials.objects.filter(
        lang=lang).values()
    context['news'] = WorkshopNews.objects.filter(lang=lang).values()
    context['clubs_partner_home'] = WorkshopInternationalLogo.objects.filter(
        lang=lang).values()
    context['workshopsimages'] = dictvar
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(pagetype="workshops",
                                                                              lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()

    return render(request, 'html/workshops.html', context)

from .models import HomePage, HomePageClub
def ikftech(request,lang):
    lang= lang
    langqueryset = list(HomePage.objects.values('name', lang))
    dictvalue = {}
    for item in langqueryset:
        dictvalue[item['name']] = item[lang]
    print(dictvalue)

    clubs_partner_home = HomePageClub.objects.all()
 
   



    
    return render(request, 'html/ikf_&_tech.html', {
    **dictvalue,
    'clubs_partner_home': clubs_partner_home
})



def ikf_aboutus(request):
    lang = 'en'
    context = pagelabel(lang)

    aboutusimages = About_Us_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in aboutusimages:
        dictvar[img['keydata']] = img['pic']

    context['aboutusimages'] = dictvar

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['about_section1'] = About_section1.objects.filter(
        lang=lang).values()

    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/ikf_aboutus.html', context)

def team_behind_ikf(request):
    context = pagelabel('en')  # Assuming language is English

    aboutusimages = About_Us_Images.objects.all()
    dictvar = dict()
    for img in aboutusimages:
        dictvar[img.keydata] = img.pic

    context['aboutusimages'] = dictvar

    # Sort by 'name' column alphabetically
    context['about_team1'] = About_TeamAdvisors.objects.order_by('name').all()

    context['about_team2'] = About_TeamCore_Team.objects.order_by('name').all()
    
    context['about_team3'] = About_OURTEAM_of_IkF.objects.order_by('name').all()
    
    context['video_url'] = TeamVideoCarousel.objects.all()

    context['navbar'] = Navbar.objects.all().values()

    return render(request, 'html/team-behind-ikf.html', context)



    

def mission_and_vision(request):
    lang = 'en'
    context = pagelabel(lang)

    aboutusimages = About_Us_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in aboutusimages:
        dictvar[img['keydata']] = img['pic']

    context['aboutusimages'] = dictvar

    return render(request, 'html/mission-vision.html', context)


# views.py
# views.py
from django.shortcuts import render
from .models import RepTemplate, HomeBanner, Navbar  # remove Regional_Partners1
# from .models import Regional_Partners1  # ← delete this import

# views.py
from django.shortcuts import render
from .models import RepTemplate, HomeBanner, Navbar

def regionalpartners(request):
    context = pagelabel('en')

    context['banners'] = HomeBanner.objects.all()
    context['navbar']  = Navbar.objects.all()

    # Feed for the Owl carousel
    context['reps'] = (
        RepTemplate.objects
        .filter(is_approved=True)
        .only('rep_name', 'rep_logo', 'template_link')
        .order_by('-id')
    )

    return render(request, 'html/regionalpartners.html', context)



from django.db.models import Q
from django.shortcuts import render
from .models import RepTemplate

def rep_index(request):
    q = request.GET.get("q", "").strip()
    reps = (RepTemplate.objects
            .filter(is_approved=True)
            .only("rep_name", "rep_logo", "template_link", "cities_of_operation")
            .order_by("rep_name"))
    if q:
        reps = reps.filter(Q(rep_name__icontains=q) | Q(template_link__icontains=q))

    return render(request, "html/rep_index.html", {"reps": reps, "q": q})




def nationalpartners(request):
    lang = 'en'
    context = pagelabel(lang)

    nationalpartnersimages = National_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in nationalpartnersimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['national_partners1'] = National_Partners1.objects.filter(
        lang=lang).values()
    context['nationalpartnersimages'] = dictvar

    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/nationalpartners.html', context)


def internationalpartners(request):
    lang = 'en'
    context = pagelabel(lang)

    internationalpartnersimages = International_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in internationalpartnersimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['clubs_partner_home'] = Clubs_Parter_Home.objects.filter(
         is_international=True)
    context['internationalpartnersimages'] = dictvar

    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/internationalpartners.html', context)

 
def corporates(request):
    lang = 'en'
    context = pagelabel(lang)

    corporatesimages = Corporate_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in corporatesimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['corporate_partners1'] = Corporate_Partners1.objects.filter(
        lang=lang).values()
    context['corporatesimages'] = dictvar

    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/corporates.html', context)


from .models import OfficialScoutingPartner  # import the model

def clubs(request):
    lang = 'en'
    context = pagelabel(lang)

    clubsimages = Clubs.objects.filter(lang=lang)
    dictvar = dict()
    for img in clubsimages:
        dictvar[img.keydata] = img.pic

    context['banners'] = HomeBanner.objects.filter(lang=lang)
    context['indian_clubs1'] = Clubs_Parter_Home.objects.filter(is_international=False)
    context['indian_clubs_pre_second'] = Clubs_Parter_Season1.objects.order_by('keydata')
    context['indian_clubs_other'] = Clubs_Parter_Season2.objects.order_by('keydata')
    context['clubsimages'] = dictvar
    context['navbar'] = Navbar.objects.filter(lang=lang)

    # ✅ Add this line
    context['official_partners'] = OfficialScoutingPartner.objects.all()
    context['iwl_partners'] = IWLPartner.objects.all()



    return render(request, 'html/clubs.html', context)




# def Donate(request):
#     lang = 'en'
#     context = pagelabel(lang)

#     homeimages = HomeImages.objects.filter(lang=lang).values()

#     dictvar = dict()
#     for img in homeimages:
#         dictvar[img['keydata']] = img['pic']

#     context['banners'] = HomeBanner.objects.filter(lang=lang).values()
#     context['homeimages'] = dictvar
#     context['navbar'] = Navbar.objects.filter(lang=lang).values()

#     return render(request, 'html/conta.html', context)


def Associate_Corporates(request):
    lang = 'en'
    context = pagelabel(lang)

    Associate_Corporates_Image = Associate_Corporate_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in Associate_Corporates_Image:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Associate_Corporates_Image'] = dictvar
    context['TakeWay1'] = TakeaWay1_Corporate.objects.filter(
        lang=lang).values()
    context['TakeWay2'] = TakeaWay2_Corporate.objects.filter(
        lang=lang).values()
    context['Corporate_Right'] = Associate_Corporate_Right.objects.filter(
        lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/Associate_Corporates.html', context)


def Associate_Philanthropists(request):
    lang = 'en'
    context = pagelabel(lang)

    Associate_Philanthropists_Image = Associate_Philanthropists_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in Associate_Philanthropists_Image:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Associate_Philanthropists_Image'] = dictvar
    context['TakeWay1'] = TakeaWay1_Philanthropists.objects.filter(
        lang=lang).values()
    context['TakeWay2'] = TakeaWay2_Philanthropists.objects.filter(
        lang=lang).values()
    context['Philanthropists_Right'] = Associate_Philanthropists_Right.objects.filter(
        lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/Associate_Philanthropists.html', context)


def Associate_PSUS(request):
    lang = 'en'
    context = pagelabel(lang)

    Associate_PSUS_Image = Associate_PSUS_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in Associate_PSUS_Image:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Associate_PSUS_Image'] = dictvar
    context['Associate_PSUS'] = Associate_PSUS_Main.objects.filter(
        lang=lang).values()
    context['TakeWay1'] = TakeaWay1_PSUS.objects.filter(
        lang=lang).values()
    context['TakeWay2'] = TakeaWay2_PSUS.objects.filter(
        lang=lang).values()
    context['TakeWay3'] = TakeaWay3_PSUS.objects.filter(
        lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/Associate_PSUS.html', context)


def Associate_Academy(request):
    lang = 'en'
    context = pagelabel(lang)

    Associate_Academy_Image = Associate_Academy_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in Associate_Academy_Image:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Associate_Academy_Images'] = dictvar
    context['TakeWay1'] = TakeaWay1_Academy.objects.filter(
        lang=lang).values()
    context['TakeWay2'] = TakeaWay2_Academy.objects.filter(
        lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/Associate_Academy.html', context)

from django.shortcuts import redirect
from .forms import ContactUsForm

from django.contrib import messages

def submit_contact_form(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "submitted")  # ✅ Add this line
            return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect(request.META.get('HTTP_REFERER', '/'))


def Associate_Clubs(request):
    lang = 'en'
    context = pagelabel(lang)

    Associate_Clubs_Image = Associate_Clubs_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in Associate_Clubs_Image:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Associate_Clubs_Images'] = dictvar
    context['TakeWay1'] = TakeaWay1_Clubs.objects.filter(
        lang=lang).values()
    context['TakeWay2'] = TakeaWay2_Clubs.objects.filter(
        lang=lang).values()
    context['TakeWay3'] = TakeaWay3_Clubs.objects.filter(
        lang=lang).values()
    context['Clubs_Right'] = Associate_Clubs_Right.objects.filter(
        lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/Associate_Clubs.html', context)

def Associate_TournamentOrganizer(request):
    lang = 'en'
    context = pagelabel(lang)

    Associate_TournamentOrganizer_Image = Associate_TournamentOrganizer_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in Associate_TournamentOrganizer_Image:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Associate_TournamentOrganizer_Image'] = dictvar
    context['TakeWay1'] = TakeaWay1_TournamentOrganizer.objects.filter(
        lang=lang).values()
    context['TakeWay2'] = TakeaWay2_TournamentOrganizer.objects.filter(
        lang=lang).values()
    context['TournamentOrganizer_Right'] = Associate_TournamentOrganizer_Right.objects.filter(
        lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/Associate_TournamentOrganizer.html', context)


def workshopsReg(request):
    lang = 'en'
    context = pagelabel(lang)

    workshopsRegimages = WorkShopsReg_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in workshopsRegimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['WorkshopsRegTabel'] = TabelWorkshopsReg.objects.filter(
        lang=lang).values()
    context['buttonsReg'] = WorkShopsRegButton.objects.filter(
        lang=lang).values()
    context['featurestripsReg'] = WorkShopsRegFeatureStrip.objects.filter(
        lang=lang).values()
    context['learnfromexpertsReg'] = WorkShopsRegExperts.objects.filter(
        lang=lang).values()
    context['workshopsRegimages'] = dictvar
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(pagetype="workshopsreg",
                                                                              lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()

    return render(request, 'html/workshopreg.html', context)

def Photo_Gallery(request):
    lang = 'en'
    context = pagelabel(lang)

    Photo_Gallery_images = Photo_Gallery_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in Photo_Gallery_images:
        dictvar[img['keydata']] = img['pic']

    context['PGButtons'] = Gallery_Buttons.objects.filter(
        lang=lang).values()

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Photo_Gallery_images'] = dictvar

    context['navbar'] = Navbar.objects.filter(lang=lang).values()



    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(
        pagetype="S03", lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()

    return render(request, 'html/Photo_Gallery.html', context)

# Create your views here.

def ResourcesFun(request):
    lang = 'en'
    context = pagelabel(lang)

    ikftrialsimages = AboutTrials_Images.objects.filter(lang=lang).values()
    dictvar = dict()
    for img in ikftrialsimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['resources']= Resources.objects.filter(lang=lang)
    context['ikftrialsimages'] = dictvar

    return render(request, 'html/Resources.html', context)


# Supported By 
def supported_by(request):
    lang = 'en'
    context = pagelabel(lang)

    carousel_images = SupportedByImages.objects.all()
    context['carousel_images'] = carousel_images

    carousel_images_2526 = SupportedByImages2526.objects.all().order_by('order_by')
    context['carousel_images_2526'] = carousel_images_2526              # ← new

    supportedby_prefetch = Prefetch(
        'supportedby_set',
        queryset=SupportedBy.objects.order_by('-order_by')
    )
    financial_years = SupportedByFinancial.objects.prefetch_related(supportedby_prefetch).order_by('-id')
    context['financial_years'] = financial_years

    from .models import ImpactReport, ScoutOnWheelAndhraReportItem
    impact_reports = list(ImpactReport.objects.filter(is_active=True).order_by('order'))
    for idx, report in enumerate(impact_reports):
        report.irfb_idx = idx
    context['impact_reports'] = impact_reports
    context['side_impact_reports'] = [report for report in impact_reports if report.show_in_side_view]
    context['scout_wheel_reports'] = ScoutOnWheelAndhraReportItem.objects.filter(is_active=True).order_by('sort_order')

    return render(request, 'html/supported_by.html', context)


def international_alliance(request):
    lang = 'en'
    context = pagelabel(lang)
    context['clubs_partner_home'] = Clubs_Parter_Home.objects.filter(
        lang=lang, is_international=True).values()
    return render(request, 'html/international-alliance.html', context)

def football_education(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/football-education.html', context)

def woman_empowerment(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/woman-empowerment.html', context)

def community_development(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/community-development.html', context)

# views.py
from django.shortcuts import render
from django.db.models import Q
from .models import FAQItem  # uses the Footprint FAQs model you created

def invest_social_impact(request):
    lang = "en"
    context = pagelabel(lang)

    # Use the model constant if present; fall back to "ner"
    page_key = getattr(FAQItem, "PAGE_NER", "ner")

    context["faqs"] = (
        FAQItem.objects
        .filter(page=page_key, is_active=True, language=lang)
        .order_by("order", "id")
    )

    return render(request, "html/invest-social-impact.html", context)

# invictus/views.py

from django.shortcuts import render
from .models import TeamMember, Thought


# views.py
from django.shortcuts import render
from .models import TeamMember, Thought, InvictusCarouselImage

def invictus_home(request):
    ikf_team = TeamMember.objects.filter(category='IKF').order_by('order')
    invictus_team = TeamMember.objects.filter(category='INVICTUS').order_by('order')
    thoughts = Thought.objects.all().order_by('order')

    # ✅ Carousel images (active + ordered)
    carousel_images = InvictusCarouselImage.objects.filter(is_active=True).order_by('order')

    return render(request, 'html/invictus_home.html', {
        'ikf_team': ikf_team,
        'invictus_team': invictus_team,
        'thoughts': thoughts,
        'carousel_images': carousel_images,   # ✅ use this in template loop
    })



def invictus_donate(request):
    context = pagelabel('en')
    qr_image = Donate_Images.objects.first()
    context['qr_code'] = qr_image.pic.url if qr_image else None
    context['DonateTabel'] = TabelDonate.objects.all()
    context['Donatefeaturestrips'] = DonateFeatureStrip.objects.all()
    return render(request, 'html/invictus_donate.html', context)

def sponsorship_opportunities(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/sponsorship-opportunities.html', context)

def ikf_spotonn_en(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/spotonn-announcement-en.html', context)

def ikf_spotonn_hi(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/spotonn-announcement-hi.html', context)

def ikf_center_of_excellence(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/ikf-center-of-excellence.html', context)

def desportz_ikf_coe(request):
    lang = 'en'
    context = pagelabel(lang)

    if request.method == 'POST':
        contact_form = DesportzContactForm(request.POST)
        if contact_form.is_valid():
            # Extract form data
            name = contact_form.cleaned_data['name']
            email = contact_form.cleaned_data['email']
            message = contact_form.cleaned_data['message']

            # Prepare email
            subject = 'Desportz Program Enquiry by India Khelo Football Form'
            message_body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = ['ikfcoe@indiakhelofootball.com', 'ikfdesportz@gmail.com']

            # Send email
            try:
                send_mail(subject, message_body, from_email, recipient_list)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error_message': 'Failed to send email. Please try again later.'
                })

            # Return JSON response
            return JsonResponse({
                'success': True,
                'success_message': 'Thank you for your message. We will get back to you soon!'
            })

        else:
            # Return JSON response with form errors
            errors = contact_form.errors
            error_messages = []
            for field, error in errors.items():
                error_messages.append(f"{field}: {error[0]}")
            return JsonResponse({
                'success': False,
                'error_message': '\n'.join(error_messages)
            })

    else:
        contact_form = DesportzContactForm()

    context['contact_form'] = contact_form
    return render(request, 'html/desportz-ikf-coe.html', context)


def imt_ghaziabad_ikf_coe(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/imt-ghaziabad-ikf-coe.html', context)

def skss_ikf_coe(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/skss-ikf-coe.html', context)

def threelok_ikf_coe(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/threelok-ikf-coe.html', context)

def IKF_dual_career_pathways(request):
    lang = 'en'
    context = pagelabel(lang)

    return render(request, 'html/ikf-dual-career-pathways.html', context)

def IKF_videos(request):
    lang =  'en'
    context = pagelabel(lang)
    context['youtube'] = Youtube.objects.filter(lang=lang).values()
    return render(request, 'html/ikf-videos.html', context)

def IKF_news(request):
    lang = 'en'
    context = pagelabel(lang)
    context['news'] = News.objects.filter(lang=lang).values()
    return render(request, 'html/ikf-news.html', context)

def IKF_Partners(request):
    lang = 'en'
    context = pagelabel(lang)
    context['clubs_partner_home'] = Clubs_Parter_Home.objects.filter(
        lang=lang, is_participated=True).values()
    return render(request, 'html/ikf-partners.html', context)

def IKF_Winners(request):
    lang = 'en'
    context = pagelabel(lang)
    
    winners = Winners.objects.filter(lang=lang).order_by('-id').values()
    for winner in winners:
        winner['category_id'] = MasterPosition.objects.get(
            id=winner['category_id']).label

    context['winners'] = winners

    return render(request, 'html/ikf-winners.html', context)

def Support_IKF(request):
    lang = 'en'
    context = pagelabel(lang)

    context['featurestrips'] = SupportIkfFeatureStrip.objects.filter(
        lang=lang).values()
    context['PartnerSeasonSupportIKF'] = PartnerSeasonSupportIKF.objects.filter(
        lang=lang).values()
    
    return render(request, 'html/support-ikf.html', context)


def academy_partners(request):
    lang = 'en'
    context = pagelabel(lang)
    context['PartnerSeasonSupportIKF'] = PartnerSeasonSupportIKF.objects.all()
  # ✅ no .values()
    return render(request, 'html/academy_partners.html', context)



from django.shortcuts import render, get_object_or_404
from .models import StateAssociationPartner

def state_association_partners(request):
    lang = 'en'
    context = pagelabel(lang)

    state_partners = StateAssociationPartner.objects.filter(
        lang=lang,
        is_active=True
    ).order_by('sort_order', 'name')

    # ✅ IMPORTANT: must be exactly this key
    context['state_partners'] = state_partners

    # quick debug (remove later)
    print("STATE PARTNERS COUNT:", state_partners.count())

    return render(request, 'html/state-association-partners.html', context)


def state_association_partner_detail(request, slug):
    lang = 'en'
    context = pagelabel(lang)

    partner = get_object_or_404(StateAssociationPartner, lang=lang, is_active=True, slug=slug)
    context['partner'] = partner
    context['partner_stats'] = partner.stats.all()

    return render(request, 'html/state-association-partner-detail.html', context)







def donate_thank_you(request):
    """Confirmation page per the donate brief.
    Accepts GET params: project, amount, email, anonymous, method, pid (razorpay payment id)."""
    ctx = {
        'project':   (request.GET.get('project') or '').strip(),
        'amount':    (request.GET.get('amount') or '').strip(),
        'email':     (request.GET.get('email') or '').strip(),
        'anonymous': request.GET.get('anonymous') in ('1', 'true', 'True'),
        'method':    (request.GET.get('method') or 'razorpay').strip().lower(),
        'pid':       (request.GET.get('pid') or '').strip(),
    }
    return render(request, 'html/donate_thank_you.html', ctx)


def offline_donation_claim(request):
    """Records a donor's self-reported UPI or Bank Transfer payment.
    Team verifies via admin (OfflineDonationClaim)."""
    from .models import OfflineDonationClaim
    if request.method != 'POST':
        return JsonResponse({'error': True, 'message': 'POST required'}, status=405)

    method = (request.POST.get('method') or '').strip().lower()
    if method not in ('upi', 'bank'):
        return JsonResponse({'error': True, 'message': 'Invalid method'}, status=400)

    anonymous = request.POST.get('anonymous') in ('true', 'True', '1', 'on')

    claim = OfflineDonationClaim.objects.create(
        project      = (request.POST.get('project') or '')[:200],
        method       = method,
        name         = '' if anonymous else (request.POST.get('name') or '')[:200],
        organisation = '' if anonymous else (request.POST.get('organisation') or '')[:200],
        email        = (request.POST.get('email') or '')[:254],
        mobile       = (request.POST.get('mobile') or '')[:20],
        amount       = (request.POST.get('amount') or '')[:50],
        anonymous    = anonymous,
    )

    # Notify the team so they can reconcile against the bank statement.
    try:
        from django.core.mail import send_mail
        from django.conf import settings as dj_settings
        from .models import DonateSettings as _DS
        ds = _DS.load()
        donor = 'Anonymous' if claim.anonymous else (claim.name or '-')
        body = (
            f"A donor has reported an offline payment.\n\n"
            f"Project   : {claim.project}\n"
            f"Method    : {claim.get_method_display()}\n"
            f"Amount    : {claim.amount or '(not provided)'}\n"
            f"Donor     : {donor}\n"
            f"Org       : {claim.organisation or '-'}\n"
            f"Email     : {claim.email or '-'}\n"
            f"Mobile    : {claim.mobile or '-'}\n"
            f"Logged at : {claim.created_at:%Y-%m-%d %H:%M}\n\n"
            f"Please verify against the bank statement and mark this claim as "
            f"Verified or Not Received in the admin: /admin/main/offlinedonationclaim/{claim.id}/change/"
        )
        recipients = [ds.donate_email] if ds.donate_email else []
        if recipients:
            send_mail(
                subject=f"[Donate] {claim.get_method_display()} claim - {claim.project}",
                message=body,
                from_email=getattr(dj_settings, 'EMAIL_HOST_USER', None) or ds.donate_email,
                recipient_list=recipients,
                fail_silently=True,
            )
    except Exception as _e:
        # Notification is best-effort; never block the donor's confirmation.
        print('Offline-claim notify failed:', _e)

    return JsonResponse({'error': False, 'id': claim.id})


def Donate(request):
    context = pagelabel('en')
    qr_image = Donate_Images.objects.first()
    context['qr_code'] = qr_image.pic.url if qr_image else None

    context['DonateTabel'] = TabelDonate.objects.all()
    context['Donatefeaturestrips'] = DonateFeatureStrip.objects.all()
    context['navbar'] = Navbar.objects.all()
    context['banners'] = HomeBanner.objects.all()
    context['donors'] = Donation.objects.order_by('-created_at')[:4]  # latest 4 donors
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(pagetype="donate")
    context['RAZORPAY_KEY_ID'] = os.environ.get('RAZORPAY_KEY_ID')

    from .models import DonateProject, DonateSettings
    context['donate_projects'] = DonateProject.objects.filter(is_active=True)
    context['donate_settings'] = DonateSettings.load()

    return render(request, 'html/Donate.html', context)


def donate_project_detail(request, slug):
    from django.shortcuts import get_object_or_404
    from .models import DonateProject, DonateSettings

    project = get_object_or_404(DonateProject, slug=slug, is_active=True)

    context = pagelabel('en')
    qr_image = Donate_Images.objects.first()
    context['qr_code'] = qr_image.pic.url if qr_image else None
    context['navbar'] = Navbar.objects.all()
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(pagetype="donate")
    context['RAZORPAY_KEY_ID'] = os.environ.get('RAZORPAY_KEY_ID')
    context['donate_settings'] = DonateSettings.load()
    context['project'] = project
    context['sections'] = project.sections.all()

    return render(request, 'html/Donate_Project.html', context)







# Create your views here.

def order(request):
    if request.method == "POST":
        print('order api called')
        unique_id = uuid1()

        mobile= request.POST.getlist('mobile')[0]
        random_number = random.randint(100, 999)

        playerunique= str(unique_id) +str(random_number)


        amountinput=int(request.POST.getlist('amount')[0])
        amount = amountinput*100

        project = request.POST.get('project', '').strip()

        client = razorpay.Client(
            auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_KEY_SECRET')))
        notes = {"id": playerunique, "mobile": mobile}
        if project:
            notes["type_of_payment"] = project
        DATA = {
            "amount": amount,
            "currency": "INR",
            "receipt": playerunique,
            "notes": notes,
        }
        response = client.order.create(data=DATA)
        return HttpResponse(json.dumps({"order_id":response["id"], "ikfplayerunique":playerunique}))
    
def payment(request):
    # lang = "en"
    # langqueryset = MasterLabels.objects.filter().values('keydata', lang)
    dict = {}
    # for item in langqueryset:
    #     dict[item['keydata']] = item[lang]
    dict["RAZORPAY_KEY_ID"]=os.environ.get('RAZORPAY_KEY_ID')
    return render(request, 'html/payment.html', dict)
from django.core.mail import send_mail
from django.conf import settings

def successpayment(request):
    # Get data from sessionStorage if passed or stored
    name = request.session.get('name', 'Donor')
    email = request.session.get('email', '')
    mobile = request.session.get('mobile', '')
    amount = request.session.get('amount', 'N/A')
    purposes = request.session.get('purposes', [])

    # Format donation purpose
    formatted_purposes = ", ".join(purposes) if purposes else "General Donation"

    # Send confirmation email
    subject = "IKF Donation Confirmation"
    message_body = f"""
Dear {name},

Thank you for your generous donation of Rs. {amount} to India Khelo Football.

Donation Purpose: {formatted_purposes}
Mobile No.: {mobile}
Email ID: {email}

We truly appreciate your support in empowering grassroots football.

Warm regards,  
Team India Khelo Football
"""

    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email, 'ikfcoe@indiakhelofootball.com', 'ikfdesportz@gmail.com']

    try:
        send_mail(subject, message_body, from_email, recipient_list)
    except Exception as e:
        print("Email sending failed:", e)

    return render(request, 'html/success.html', {})



def thankyou(request):
    dict = {}
    return render(request, 'html/thanks.html', dict)

from django.shortcuts import render
from django.db.models import Q
from .models import Donation

from django.db.models import Count
from django.shortcuts import render
from .models import Donation

def invictus_donations(request):
    from datetime import date
    from django.db.models import Q
    context = pagelabel('en')

    # Invictus donations: flagged OR received on/after 17 Feb 2026
    donations = Donation.objects.filter(
        Q(invictus_icare=True) | Q(created_at__date__gte=date(2026, 2, 17))
    ).order_by("-created_at")

    # Optional: only successful payments
    # donations = donations.filter(status__iexact="success")

    total_amount = 0
    for d in donations:
        try:
            total_amount += int(float(d.amount or 0))
        except (ValueError, TypeError):
            pass

    context["donations"] = donations
    context["count"] = donations.count()
    context["total_amount"] = total_amount

    return render(request, "html/invictus_donations.html", context)



from django.db import IntegrityError
from django.http import HttpResponse
import json
import threading
from .models import Donation
 # adjust as per your project

from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse
import json, threading
from .utils import send_whatsapp_public_message


def save(request):
    if request.method == 'POST':
        datastr = request.POST.getlist('data')[0]
        dictdata  = json.loads(datastr)

        razorpay_payment_id = request.POST.getlist('razorpay_payment_id')[0] if request.POST.getlist('razorpay_payment_id')[0] else ""
        razorpay_order_id = request.POST.getlist('razorpay_order_id')[0] if request.POST.getlist('razorpay_order_id')[0] else ""
        razorpay_signature = request.POST.getlist('razorpay_signature')[0] if request.POST.getlist('razorpay_signature')[0] else ""

        # ✅ Get selected purposes from data
        selected_purposes = dictdata.get('purpose', [])
        if not isinstance(selected_purposes, list):
            selected_purposes = [selected_purposes]
        selected_purposes = set(selected_purposes)

        def has_purpose(*names):
            return any(name in selected_purposes for name in names)

        purpose_summary = ", ".join(sorted(selected_purposes))

        # Resolve FK to DonateProject by exact name match against any selected purpose.
        # Works for both seed projects and any new project the admin adds later.
        from .models import DonateProject as _DP
        _project_fk = None
        if selected_purposes:
            _project_fk = _DP.objects.filter(name__in=list(selected_purposes)).first()

        # ✅ Create Donation object with boolean flags
        player = Donation(
            project=_project_fk,
            name=dictdata.get('name', ''),
            mobile=dictdata.get('mobile', ''),
            email=dictdata.get('email', ''),
            amount=dictdata.get('amount', ''),
            address=f"Support for: {purpose_summary}" if purpose_summary else "",
            status=request.POST.getlist('status')[0],
            razorpay_unique_id=request.POST.getlist('razorpay_unique_id')[0],
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            razorpay_signature=razorpay_signature,

            # ✅ Always True — all donations show on invictus-donations page
            invictus_icare = True,
            future_champions = has_purpose(
                "Future Champions",
                "Field of Dreams - Future Champion",
                "Field of Dreams (Future champion)"
            ),
            books_and_boots = has_purpose(
                "Books & Boots",
                "Field of Dreams - Books & Boots",
                "Field of Dreams (Books & Boots)"
            ),
            heal_to_play = has_purpose("Heal to Play", "Heal To Play"),
            maidaan_ki_rani = has_purpose(
                "Maidaan Ki Rani",
                "Field of Dreams - Maidaan Ki Raani",
                "Field of Dreams (Maidaan Ki Raani)"
            ),
            that_kicks = has_purpose("That Kicks", "Artist That Kicks"),
            ikf_trials = has_purpose("IKF Trials"),
            anayas_goal = has_purpose("Anaya's Goal")
        )

        try:
            player.save()
            if dictdata.get('mobile'):
                t1 = threading.Thread(
                    target=send_whatsapp_public_message,
                    args=(dictdata.get('mobile', ''), dictdata.get('name', ''))
                )
                t1.start()

            # ✅ Response
            errordict = {
                "error": "false",
                "message": "Saved Successfully",
                "ikfuniqueid":1,
                "id": 1
            }

            return HttpResponse(json.dumps(errordict))



        except Exception as e:
            return HttpResponse(json.dumps({
                "error": "true",
                "message": str(e)
            }))





def paymentfail(request):
    if request.method=="GET":
        context = {}
        lang = "en"
        langqueryset = MasterLabels.objects.filter().values('keydata', lang)
        dict = {}
        for item in langqueryset:
            dict[item['keydata']] = item[lang]
        return render(request, 'player/paymentfail.html', dict)  
    
def paymentstatus(request):
    return 0
def paymentpass(request):
    return 0


def ikf_as_scouting_partners(request):
    lang = 'en'
    context = pagelabel(lang)

    context['indian_clubs1'] = Clubs_Parter_Home.objects.filter(
    lang=lang, attr2="IKF as Scouting Partner").values()

    return render(request, 'html/ikf-as-scouting-partners.html', context)



def anaya_goal(request):
    lang = 'en'
    context = pagelabel(lang)

    # context['indian_clubs1'] = Clubs_Parter_Home.objects.filter(
    # lang=lang, attr2="IKF as Scouting Partner").values()

    return render(request, 'html/anaya_goal.html', context)

def parent_fuelling_ikf(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/parent_fuelling_ikf.html', context)

def un_certificate(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/un_certificate.html', context)


def sponsordeck(request):
    lang = 'en'
    context = pagelabel(lang)

    workshopsimages = WorkShops_Images.objects.filter(lang=lang).values()

    dictvar = dict()
    for img in workshopsimages:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Workshops'] = TabelWorkshops.objects.filter(
        lang=lang).values()
    context['buttons'] = WorkShopsButton.objects.filter(
        lang=lang).values()
    context['featurestrips'] = WorkShopsFeatureStrip.objects.filter(
        lang=lang).values()
    context['learnfromexperts'] = WorkShopsExperts.objects.filter(
        lang=lang).values()
    context['previous_workshop'] = Previous_Workshop_Images.objects.filter(
        lang=lang).values()
    
    winners = Winners.objects.filter(lang=lang).filter(attr2="int").values()
    for winner in winners:
        winner['category_id'] = MasterPosition.objects.get(
            id=winner['category_id']).label

    context['winners'] = winners
    context['testimonials'] = Testimonials.objects.filter(
        lang=lang).values()
    context['news'] = WorkshopNews.objects.filter(lang=lang).values()
    context['clubs_partner_home'] = WorkshopInternationalLogo.objects.filter(
        lang=lang).values()
    context['workshopsimages'] = dictvar
    context['TrialsAndInitiativeNav'] = TrialsAndInitiativeNav.objects.filter(pagetype="workshops",
                                                                              lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()
    context['tabs'] = Tab.objects.filter().values()

    return render(request, 'html/sponsordeck.html', context)


from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string

# noticeboard/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView


from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404

from .models import NoticeboardBox, NoticeboardNotice, NoticeBoardInfoBlock, TrialGuidelinesPage


def noticeboard_home(request):
    quick_links = NoticeboardBox.objects.filter(is_active=True).order_by("order", "name")

    # -----------------------------
    # What's New (from API)
    # -----------------------------
    project_id = int(request.GET.get("project_id", 0))
    latest_data_limit = int(request.GET.get("limit", 20))

    api_url = "https://app.myfirstkick.com/be/api/v1/project/project-city/activity"
    payload = {"project_id": project_id, "latest_data_limit": latest_data_limit}

    notices = []
    try:
        r = requests.post(api_url, json=payload, timeout=6)
        r.raise_for_status()
        rows = r.json() if isinstance(r.json(), list) else []

        for row in rows:
            # ✅ Route URL based on column_name
            column_name = row.get("column_name") or ""
            url = (
                "https://indiakhelofootball.com/noticeboard/ikftrialresults"
                if column_name == "trial_result"
                else "https://indiakhelofootball.com/noticeboard/trialcalendar"
            )

            notices.append({
                "title": row.get("text_auto") or "",
                "url": url,
                "meta": row.get("city_name") or "",
            })

        # remove empty title rows
        notices = [n for n in notices if n["title"]]

    except Exception:
        notices = []

    info_blocks = NoticeBoardInfoBlock.objects.filter(is_active=True).order_by("order", "-created_at")

    from .models import Faq
    faqs = Faq.objects.filter(page_name='IkfTrials').order_by('priority')

    return render(
        request,
        "html/notice_board.html",
        {
            "quick_links": quick_links,
            "notices": notices,
            "info_blocks": info_blocks,
            "faqs": faqs,
        },
    )


# views.py

from .models import NoticeboardBox, PostTrialMediaPage, OfficialCircularCard, OfficialCircularItem

def official_circulars_page(request):
    cards = OfficialCircularCard.objects.filter(is_active=True).order_by('order')
    return render(request, "html/noticeboard_pages/official_circulars.html", {"cards": cards})

def official_circular_detail(request, slug):
    card  = get_object_or_404(OfficialCircularCard, slug=slug, is_active=True)
    items = card.items.filter(is_active=True).order_by('order', '-date')
    return render(request, "html/noticeboard_pages/official_circular_detail.html", {
        "card": card,
        "items": items,
    })

def noticeboard_slug_router(request, slug):
    box = NoticeboardBox.objects.filter(slug=slug, is_active=True).first()
    if box and box.url:
        return redirect(box.url)

    if slug == "officialcircularsnoticesannouncements":
        return official_circulars_page(request)

    if slug == "trialguidelinesinstructions":
      page = get_object_or_404(TrialGuidelinesPage, slug="trial-guidelines-instructions", is_active=True)
      sections = page.sections.filter(is_active=True).prefetch_related("items").order_by("order")
      return render(request, "html/noticeboard_pages/trial-guidelines-instructions.html", {"page": page, "sections": sections})

    # ✅ NEW: Post Trial Media
    if slug == "posttrialmedia":
       return post_trial_media_page(request)
    
    if slug == "ikftrialresults":
        return trial_results_page(request)
    
    if slug == "trialcalendar":
        return upcoming_trials_page(request)

    if box:
        return render(request, "html/noticeboard_pages/coming_soon.html", {"box": box})

    raise Http404("Page not found")

def post_trial_media_page(request):
    return render(request, "html/noticeboard_pages/post-trial-media.html")
import requests

from django.core.cache import cache

def get_playlist_thumbnail(playlist_url):
    cache_key = f"yt_thumb_{playlist_url}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    try:
        res = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": playlist_url, "format": "json"},
            timeout=5
        )
        if res.ok:
            thumb = res.json().get("thumbnail_url", "")
            cache.set(cache_key, thumb, 60 * 60 * 24)  # cache 24 hours
            return thumb
    except Exception:
        pass
    cache.set(cache_key, "", 60 * 60)  # cache empty result 1 hour
    return ""

# --- PAGE VIEW ---
def trial_results_page(request):
    """
    Renders the Trial Results page UI.
    Filters + cards are loaded via JS using your cities API.
    """
    return render(request, "html/noticeboard_pages/trial-results.html", {})

# main/views.py
import re
import requests
from django.conf import settings
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

# --- PAGE VIEW ---
def trial_results_page(request):
    """
    Renders the Trial Results page UI.
    Filters + cards are loaded via JS using your cities API.
    """
    return render(request, "html/noticeboard_pages/trial-results.html", {})


# --- HELPERS ---
def _gender_bucket(gender_raw: str) -> str:
    g = (gender_raw or "").strip().lower()
    if g.startswith("m"):
        return "Boys"
    if g.startswith("f"):
        return "Girls"
    return "Other"


def parse_trial_result_text(raw_text: str):
    """
    Input lines like:
      2008-2009,Khushboo,Female,01-01-2026
    Output:
      {
        "Boys": {"2008-2009":[{"name":"Vicky","dob":"01-01-2027"}], ...},
        "Girls": {"2008-2009":[...], ...}
      }
    """
    result = {"Boys": {}, "Girls": {}, "Other": {}}
    if not raw_text:
        return result

    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    for ln in lines:
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) < 4:
            continue

        age_group, name, gender, dob = parts[0], parts[1], parts[2], parts[3]
        bucket = _gender_bucket(gender)

        result.setdefault(bucket, {})
        result[bucket].setdefault(age_group, [])
        result[bucket][age_group].append({"name": name, "dob": dob})

    # sort players inside each age group
    for b in result:
        for ag in result[b]:
            result[b][ag] = sorted(result[b][ag], key=lambda x: (x["name"] or "").lower())

    return result


def _safe_get(d: dict, *keys, default=""):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return default if cur is None else cur


# --- DETAIL API (for a single city card click) ---
@require_GET
def trial_results_detail_api(request):
    """
    Frontend calls:
      /api/noticeboard/trial-results/detail/?cityId=123&projectId=1&stateId=2&statusOfTrial=City%20Confirmed

    We call the same FastAPI list endpoint (get_city_details) using your existing logic,
    then pick the matching city item and return parsed data for UI.
    """
    city_id = request.GET.get("cityId")
    if not city_id:
        return JsonResponse({"error": "cityId is required"}, status=400)

    # reuse your list API function logic by calling FastAPI directly again:
    payload = {}
    project_id = request.GET.get("projectId")
    state_id = request.GET.get("stateId")
    status = request.GET.get("statusOfTrial")

    if project_id:
        payload["projectId"] = int(project_id)
    if state_id:
        payload["stateId"] = int(state_id)
    if status:
        payload["statusOfTrial"] = status

    api_base_url = getattr(settings, "API_BASE_URL", None) or getattr(settings, "api_base_url", None)
    if not api_base_url:
        return JsonResponse({"error": "API_BASE_URL not configured in settings"}, status=500)

    try:
        res = requests.post(f"{api_base_url}/get_city_details", json=payload, timeout=20)
        data = res.json()
        if not isinstance(data, list):
            return JsonResponse({"error": "Unexpected response from FastAPI", "data": data}, status=500)

        match = None
        for item in data:
            # handle multiple possible key names defensively
            item_city_id = _safe_get(item, "cityId", default=None) or _safe_get(item, "city_id", default=None) or _safe_get(item, "id", default=None)
            if str(item_city_id) == str(city_id):
                match = item
                break

        if not match:
            return JsonResponse({"error": "City not found for given filters"}, status=404)

        # pick likely fields (adjust keys if your FastAPI uses different names)
        trial_result_raw = (
            _safe_get(match, "trialResult", default="")
            or _safe_get(match, "trial_result", default="")
            or _safe_get(match, "result_text", default="")
        )

        parsed = parse_trial_result_text(trial_result_raw)

        payload_out = {
            "cityId": city_id,
            "cityName": _safe_get(match, "cityName", default="") or _safe_get(match, "city_name", default=""),
            "projectName": _safe_get(match, "projectName", default="") or _safe_get(match, "project_name", default=""),
            "repName": _safe_get(match, "repName", default="") or _safe_get(match, "rep_name", default=""),
            "trialDate": _safe_get(match, "trialDate", default="") or _safe_get(match, "trial_date", default=""),
            "statusOfTrial": _safe_get(match, "statusOfTrial", default="") or _safe_get(match, "status_of_trial", default=""),
            "latestUpdatedOn": _safe_get(match, "latestUpdatedOn", default="") or _safe_get(match, "updated_at", default=""),
            "parsedResult": parsed,
        }
        return JsonResponse(payload_out, safe=False)

    except Exception as e:
        return JsonResponse({"error": "Failed to fetch trial result detail", "details": str(e)}, status=500)


def trial_result_detail_page(request, city_slug, project_slug):
    """
    Standalone page for a single trial result.
    URL: /noticeboard/ikftrialresults/<city_slug>/<project_slug>/
    Matches against FastAPI /get_city_details by slugified cityName + projectName.
    """
    from django.shortcuts import render
    from django.utils.text import slugify
    from django.http import Http404

    try:
        res = requests.post(f"{api_base_url}/get_city_details", json={}, timeout=20)
        data = res.json()
    except Exception:
        raise Http404("Failed to load trial results")

    if not isinstance(data, list):
        raise Http404("Unexpected API response")

    match = None
    for item in data:
        city_name    = _safe_get(item, "cityName") or _safe_get(item, "city_name") or ""
        project_name = _safe_get(item, "projectName") or _safe_get(item, "project_name") or ""
        if slugify(city_name) == city_slug and slugify(project_name) == project_slug:
            match = item
            break

    if not match:
        raise Http404("Trial result not found")

    trial_result_raw = (
        _safe_get(match, "trialResult")
        or _safe_get(match, "trial_result")
        or _safe_get(match, "result_text")
        or ""
    )
    parsed = parse_trial_result_text(trial_result_raw)

    boys  = parsed.get("Boys", {})  or {}
    girls = parsed.get("Girls", {}) or {}

    def to_columns(bucket):
        # Only include age-group columns that actually have at least one selected player.
        out = []
        for key in sorted(bucket.keys()):
            players = bucket.get(key) or []
            if players:
                out.append({"age_group": key, "players": players})
        return out

    boys_columns  = to_columns(boys)
    girls_columns = to_columns(girls)

    context = {
        "city_name":         _safe_get(match, "cityName") or _safe_get(match, "city_name") or "",
        "project_name":      _safe_get(match, "projectName") or _safe_get(match, "project_name") or "",
        "rep_name":          _safe_get(match, "repName") or _safe_get(match, "rep_name") or "",
        "trial_date":        _safe_get(match, "trialDate") or _safe_get(match, "trial_date") or _safe_get(match, "date") or "",
        "status_of_trial":   _safe_get(match, "statusOfTrial") or _safe_get(match, "status_of_trial") or "",
        "latest_updated_on": _safe_get(match, "latestUpdatedOn") or _safe_get(match, "updated_at") or "",
        "boys_columns":      boys_columns,
        "girls_columns":     girls_columns,
        "total_columns":     len(boys_columns) + len(girls_columns),
    }
    return render(request, "html/noticeboard_pages/trial-result-detail.html", context)


def calender(request):
    lang = 'en'
    context = pagelabel(lang)

    project_names = Calender.objects.filter(project__in = ["Tyger IKF S6 Trials", "IKF International Workshop"]).values_list('project', flat=True).distinct().order_by('project')
    project = request.GET.get('project', '')

    calender_data = Calender.objects.exclude(status_date='CANCELLED')
    calender_data= calender_data.filter(attr2="true")

    if project:
        calender_data = calender_data.filter(project=project)

    project_result_count = calender_data.count()
    total_trials = Calender.objects.filter(attr2="true").count()

    project_city = request.GET.get('project_city', '')
    project_state = request.GET.get('project_state', '')
    status_date = request.GET.get('status_date', '')

    if status_date:
        calender_data = calender_data.filter(status_date__icontains=status_date)

    if project_city:
        calender_data = calender_data.filter(project_city__icontains=project_city)

    if project_state:
        calender_data = calender_data.filter(project_state__icontains=project_state)

    calender_data = calender_data.order_by('project_city')

    context['Calender'] = calender_data
    context['status_choices'] = Calender.StatusChoices.choices
    context['result_count'] = calender_data.count()
    context['state_count'] = calender_data.count()
    context['current_status'] = status_date
    context['project_states'] = Calender.objects.values_list('project_state', flat=True).distinct().order_by('project_state')
    context['total_trials'] = total_trials
    context['project_names'] = project_names
    context['project_result_count'] = project_result_count

    return render(request, 'html/calender.html', context)


def calendar_partial(request):
    project = request.GET.get('project', '')
    project_state = request.GET.get('project_state', '')
    status_date = request.GET.get('status_date', '')

    calender_data = Calender.objects.exclude(status_date='CANCELLED')

    # ✅ Filter by project first to get project_result_count
    if project:
        calender_data = calender_data.filter(project=project)
    project_result_count = calender_data.count()

    # ✅ Filter by status to get result_count
    if status_date:
        calender_data = calender_data.filter(status_date__icontains=status_date)
    result_count = calender_data.count()

    # ✅ Filter by state to get state_count
    if project_state:
        calender_data = calender_data.filter(project_state__icontains=project_state)
    state_count = calender_data.count()

    calender_data = calender_data.order_by('project_city')

    html = render_to_string('html/partials/calendar_results.html', {'Calender': calender_data}, request=request)

    return JsonResponse({
        'html': html,
        'project_result_count': project_result_count,
        'result_count': result_count,
        'state_count': state_count
    })

def request_for_player(request):
    lang = 'en'
    context = pagelabel(lang)

    Associate_TournamentOrganizer_Image = Associate_TournamentOrganizer_Images.objects.filter(
        lang=lang).values()

    dictvar = dict()
    for img in Associate_TournamentOrganizer_Image:
        dictvar[img['keydata']] = img['pic']

    context['banners'] = HomeBanner.objects.filter(lang=lang).values()
    context['Associate_TournamentOrganizer_Image'] = dictvar
    context['TakeWay1'] = TakeaWay1_TournamentOrganizer.objects.filter(
        lang=lang).values()
    context['TakeWay2'] = TakeaWay2_TournamentOrganizer.objects.filter(
        lang=lang).values()
    context['TournamentOrganizer_Right'] = Associate_TournamentOrganizer_Right.objects.filter(
        lang=lang).values()
    context['navbar'] = Navbar.objects.filter(lang=lang).values()

    return render(request, 'html/Request_For_Player.html', context)


def career360(request):
    lang = 'en'
    context = pagelabel(lang)


    return render(request, 'html/career360.html', context)

def ikf_international_alliance(request):
    lang = 'en'
    context = pagelabel(lang)


    return render(request, 'html/ikf_international_alliance.html', context)

def discovery_call(request):
    lang = 'en'
    context = pagelabel(lang)


    return render(request, 'html/discovery_calls.html', context)

def student_athlete_pathway(request):
    lang = 'en'
    context = pagelabel(lang)


    return render(request, 'html/student_athlete_pathway.html', context)

from django.shortcuts import render
  # keep same as your project

from django.shortcuts import render

def myfirstkick_page(request):
    context = {}
    return render(request, "html/myfirstkick.html", context)




# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PartnerInterestForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FAQItem
# from .forms import PartnerInterestForm  # assuming you already have this
from .models import ScoutOnWheel

def professional_pathway(request):
    lang = "en"
    context = pagelabel(lang)
    page = ScoutOnWheel.objects.filter(is_active=True).first()
    if not page:
      raise Http404("ScoutOnWheel page not found")

    # FAQs for this page
    context["faqs"] = FAQItem.objects.filter(
        page=FAQItem.Page.SCOUT_ON_WHEELS,
        language=lang,
        is_active=True,
    )
    glimpses_images = page.images.filter(is_active=True)
    context["glimpses_images"] = glimpses_images
    media_articles = page.articles.filter(is_active=True)
    context["media_articles"] = media_articles
    # Only show items that actually have an image uploaded; otherwise fall back
    # to the existing images carousel.
    andhra_reports = (
        page.andhra_reports.filter(is_active=True)
        .exclude(cover_image__isnull=True)
        .exclude(cover_image__exact="")
    )
    context["andhra_reports"] = andhra_reports

    # Scout on Wheels 2026 — state route maps (between focuses + UN SDG sections)
    from .models import ScoutOnWheels2026StateMap
    context["sow2026_maps"] = ScoutOnWheels2026StateMap.objects.filter(is_active=True)

    # ----- Partner Interest form -----
    if request.method == "POST" and request.POST.get("form_name") == "partner_interest":
        partner_form = PartnerInterestForm(request.POST)
        if partner_form.is_valid():
            partner_form.save()
            messages.success(request, "Thanks! We’ve received your interest. Our team will contact you soon.")
            return redirect("professional_pathway")
        else:
            messages.error(request, "Please fix the highlighted fields and submit again.")
    else:
        partner_form = PartnerInterestForm()

    context["partner_form"] = partner_form
    return render(request, "html/professional_pathway.html", context)


def naari_shakti(request):
    from .models import NaariShakti
    lang = "en"
    context = pagelabel(lang)
    page = NaariShakti.objects.filter(is_active=True).first()
    if page:
        context["glimpses_images"] = page.images.filter(is_active=True)
        context["impact_stats"] = page.impact_stats.filter(is_active=True)
    else:
        context["glimpses_images"] = []
        context["impact_stats"] = []
    return render(request, "html/naari_shakti.html", context)


def naari_shakti_bihar(request):
    lang = "en"
    context = pagelabel(lang)
    context['RAZORPAY_KEY_ID'] = os.environ.get('RAZORPAY_KEY_ID')
    return render(request, "html/naari_shakti_bihar.html", context)


def naari_shakti_rajasthan(request):
    lang = "en"
    context = pagelabel(lang)
    context['RAZORPAY_KEY_ID'] = os.environ.get('RAZORPAY_KEY_ID')
    return render(request, "html/naari_shakti_rajasthan.html", context)


def naari_shakti_meerut(request):
    lang = "en"
    context = pagelabel(lang)
    context['RAZORPAY_KEY_ID'] = os.environ.get('RAZORPAY_KEY_ID')
    return render(request, "html/naari_shakti_meerut.html", context)


def _naari_shakti_donations_for(purpose_substring):
    donations = Donation.objects.filter(
        address__icontains=purpose_substring
    ).order_by("-created_at")
    total_amount = 0
    for d in donations:
        try:
            total_amount += int(float(d.amount or 0))
        except (ValueError, TypeError):
            pass
    return donations, total_amount


def naari_shakti_bihar_donations(request):
    context = pagelabel('en')
    donations, total_amount = _naari_shakti_donations_for("IKF Naari Shakti - Bihar Edition")
    context["donations"] = donations
    context["count"] = donations.count()
    context["total_amount"] = total_amount
    context["report_title"] = "IKF Naari Shakti – Bihar Donations"
    context["empty_label"] = "No Naari Shakti Bihar donations yet."
    return render(request, "html/naari_shakti_donations.html", context)


def naari_shakti_rajasthan_donations(request):
    context = pagelabel('en')
    donations, total_amount = _naari_shakti_donations_for("IKF Naari Shakti - Rajasthan")
    context["donations"] = donations
    context["count"] = donations.count()
    context["total_amount"] = total_amount
    context["report_title"] = "IKF Naari Shakti – Rajasthan Donations"
    context["empty_label"] = "No Naari Shakti Rajasthan donations yet."
    return render(request, "html/naari_shakti_donations.html", context)


def naari_shakti_meerut_donations(request):
    context = pagelabel('en')
    donations, total_amount = _naari_shakti_donations_for("IKF Naari Shakti - Meerut Edition")
    context["donations"] = donations
    context["count"] = donations.count()
    context["total_amount"] = total_amount
    context["report_title"] = "IKF Naari Shakti – Meerut Donations"
    context["empty_label"] = "No Naari Shakti Meerut donations yet."
    return render(request, "html/naari_shakti_donations.html", context)


def naari_shakti_india_donations(request):
    context = pagelabel('en')
    from django.db.models import Q
    donations = Donation.objects.filter(
        Q(address__icontains="Naari Shakti") &
        ~Q(address__icontains="Bihar") &
        ~Q(address__icontains="Rajasthan")
    ).order_by("-created_at")
    total_amount = 0
    for d in donations:
        try:
            total_amount += int(float(d.amount or 0))
        except (ValueError, TypeError):
            pass
    context["donations"] = donations
    context["count"] = donations.count()
    context["total_amount"] = total_amount
    context["report_title"] = "IKF Naari Shakti – India Donations"
    context["empty_label"] = "No Naari Shakti India donations yet."
    return render(request, "html/naari_shakti_donations.html", context)




questions = [
    {'id': 1, 'text': 'What is the capital of France?', 'options': ['Berlin', 'Madrid', 'Paris', 'Lisbon']},
    {'id': 2, 'text': 'Which planet is known as the Red Planet?', 'options': ['Earth', 'Mars', 'Venus', 'Jupiter']},
    {'id': 3, 'text': 'Who wrote "To Kill a Mockingbird"?', 'options': ['Harper Lee', 'J.K. Rowling', 'George Orwell', 'Ernest Hemingway']}
]
# Hardcoded questions
QUESTIONS = [
    {
        "id": 1,
        "text": "What is the capital of India?",
        "options": ["Delhi", "Mumbai", "Kolkata", "Chennai"],
        "answer": "Delhi"
    },
    {
        "id": 2,
        "text": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4"
    },
    {
        "id": 3,
        "text": "Which is a programming language?",
        "options": ["Python", "Snake", "Lizard", "Cobra"],
        "answer": "Python"
    },
]


# def anant_login(request):
#     if request.method == 'POST':
#         page = request.POST.get('page')

#         if page == 'login':
#             # Accept any email and password, move to test
#             return render(request, 'html/anant_login.html', {'page': 'test', 'questions': QUESTIONS})

#         elif page == 'test':
#             user_answers = {}
#             score = 0
#             total = len(QUESTIONS)
#             results = []

#             for question in QUESTIONS:
#                 qid = f"q{question['id']}"
#                 user_answer = request.POST.get(qid)
#                 is_correct = user_answer == question["answer"]

#                 if is_correct:
#                     score += 1

#                 results.append({
#                     "question": question["text"],
#                     "your_answer": user_answer,
#                     "correct": is_correct,
#                     "correct_answer": question["answer"]
#                 })

#             return render(request, 'html/anant_login.html', {
#                 'page': 'result',
#                 'score': score,
#                 'total': total,
#                 'results': results
#             })

#     # Default: show login page
#     return render(request, 'html/anant_login.html', {'page': 'login'})
def student_login(request):
    if request.method == "POST":
        # Capture email (password is not checked as per your requirement)
        email = request.POST.get('email')
        
        # After login, show the MCQ test page
        return render(request, 'html/anant_login.html', {'page': 'test', 'questions': questions})

    # By default, show the login form
    return render(request, 'html/anant_login.html', {'page': 'login'})

def mcq_test(request):
    if request.method == "POST":
        score = 0
        answers = request.POST
        for question in questions:
            correct_answer = question['options'][2]  # Hardcoded correct answer: 'Paris' for Q1, 'Mars' for Q2, etc.
            user_answer = answers.get(f'q{question["id"]}')
            if user_answer == correct_answer:
                score += 1

        # After submitting the test, show the result page
        return render(request, 'html/anant_login.html', {
            'page': 'result', 
            'score': score, 
            'total': len(questions), 
            'answers': answers,
            'questions': questions
        })

    # If GET request, stay on the test page
    return render(request, 'html/anant_login.html', {'page': 'test', 'questions': questions})


def anant_login(request):
    context = {}

    # Step 1: Login submitted
    if request.method == "POST" and request.POST.get("page") == "login":
        email = request.POST.get("email")
        password = request.POST.get("password")
        # Skipping validation, accepting any credentials
        context['page'] = 'test'
        context['questions'] = QUESTIONS
        return render(request, 'html/anant_login.html', context)

    # Step 2: Test submitted
    elif request.method == "POST" and request.POST.get("page") == "test":
        score = 0
        results = []

        for question in QUESTIONS:
            qid = f"q{question['id']}"
            user_answer = request.POST.get(qid)
            correct = user_answer == question["answer"]
            if correct:
                score += 1
            results.append({
                "question": question["text"],
                "your_answer": user_answer,
                "correct_answer": question["answer"],
                "correct": correct,
            })

        context['page'] = 'result'
        context['score'] = score
        context['total'] = len(QUESTIONS)
        context['results'] = results
        return render(request, 'html/anant_login.html', context)

    # Step 0: Default - show login page
    context['page'] = 'login'
    return render(request, 'html/anant_login.html', context)


def scoutingasservice(request):
    lang = 'en'
    context = pagelabel(lang)


    return render(request, 'html/scoutingasservice.html', context)

def scoutingasservice(request):
    lang = 'en'
    context = pagelabel(lang)


    return render(request, 'html/scoutingasservice.html', context)
from main.models import Scout
from django.db.models import Q

def scoutingcommunity(request):
    lang = 'en'
    context = pagelabel(lang)

    name_query = request.GET.get('name', '')
    city_query = request.GET.get('city', '')

    # scouts = Scout.objects.filter(ishidden=False)
    scouts = (
        Scout.objects.all()
        .order_by('-ishidden', Lower('full_name'))   # True first, then A→Z (case-insensitive)
    )

    if name_query:
        scouts = scouts.filter(full_name__icontains=name_query)
    if city_query:
        scouts = scouts.filter(preferred_cities__icontains=city_query)


    for scout in scouts:
        if scout.preferred_cities:
            cities = [city.strip() for city in scout.preferred_cities.split(',')]
        else:
            cities = []

        while len(cities) < 3:
            cities.append('-')
        scout.city_list_fixed = cities[:3]

    # ✅ Add all Indian cities for dropdown
    indian_cities = [
        "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata",
        "Pune", "Jaipur", "Lucknow", "Indore", "Bhopal", "Thane", "Nagpur", "Patna",
        "Chandigarh", "Surat", "Visakhapatnam", "Gurgaon", "Noida", "Kanpur", "Vadodara",
        "Rajkot", "Ranchi", "Amritsar", "Coimbatore", "Ludhiana", "Agra", "Nashik", "Faridabad"
    ]

    context['scouts'] = scouts
    context['name_query'] = name_query
    context['city_query'] = city_query
    context['indian_cities'] = indian_cities  # 👈 send to template
    return render(request, 'html/scoutingcommunity.html', context)



















def scoutingatschools(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/scoutingatschools.html', context)

def career360becomepartner(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/career360BecomePartner.html', context)

from .models import Career360Partner

def career360faq(request):
    lang = 'en'
    context = pagelabel(lang)

    partners = Career360Partner.objects.filter(is_active=True).order_by("order", "name")
    context.update({
        "partners": partners
    })

    return render(request, 'html/career360Faq.html', context)


def career360impactinaction(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/career360ImactInAction.html', context)

def career360parentsplayers(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/career360ParentsPlayers.html', context)

def ikf_for_players(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/ikf-for-players.html', context)

def ikf_for_parents(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/ikf-for-parents.html', context)

def ikf_for_donors(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/ikf-for-donors.html', context)

def ikf_for_scouts(request):
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/ikf-for-scouts.html', context)

def career360vision(request):
    from .models import IKF360PathwayPartner
    lang = 'en'
    context = pagelabel(lang)
    context['pathway_partners'] = IKF360PathwayPartner.objects.filter(is_active=True)
    return render(request, 'html/career360vision.html', context)


# ─────────────────────────────────────────────────────────────
# IKF 360 — Persona sub-pages
# ─────────────────────────────────────────────────────────────

def _ikf360_hero_image(url_name):
    """
    Return the active hero image for this IKF 360 sub-page.
    If the page has no own PageContent image, fall back to the main
    IKF 360 page (career360vision) so all sub-pages share the same
    banner until an admin uploads a page-specific one.
    """
    from .models import PageContent
    page = (
        PageContent.objects
        .prefetch_related("images")
        .filter(page_key=url_name)
        .first()
    )
    img = page.images.filter(is_active=True).first() if page else None
    if img:
        return img
    fallback_page = (
        PageContent.objects
        .prefetch_related("images")
        .filter(page_key="career360vision")
        .first()
    )
    if fallback_page:
        return fallback_page.images.filter(is_active=True).first()
    return None


def ikf360_player(request):
    context = pagelabel('en')
    context['hero_image'] = _ikf360_hero_image('ikf360_player')
    return render(request, 'html/ikf360/player.html', context)


def ikf360_parent(request):
    context = pagelabel('en')
    context['hero_image'] = _ikf360_hero_image('ikf360_parent')
    return render(request, 'html/ikf360/parent.html', context)


def ikf360_career(request):
    context = pagelabel('en')
    context['hero_image'] = _ikf360_hero_image('ikf360_career')
    return render(request, 'html/ikf360/career.html', context)


def ikf360_partner(request):
    context = pagelabel('en')
    context['hero_image'] = _ikf360_hero_image('ikf360_partner')
    return render(request, 'html/ikf360/partner.html', context)


def ikf360_supporter(request):
    context = pagelabel('en')
    context['hero_image'] = _ikf360_hero_image('ikf360_supporter')
    return render(request, 'html/ikf360/supporter.html', context)
# views.py
from django.shortcuts import render
from django.urls import reverse


from django.shortcuts import render

from django.shortcuts import render
from itertools import groupby
from .models import SitemapCategory


def sitemap_view(request):
    """
    Groups active categories by their `column` number so the template can
    render multiple stacked headings inside a single grid cell.

    `columns` passed to the template is an ordered list of lists, e.g.:
        [
            # column 1
            [{"category": <Home>, "items": [...]}, {"category": <Footprint Project>, "items": [...]}],
            # column 2
            [{"category": <Social Impact>, "items": [...]}],
            ...
        ]
    """
    categories = (
        SitemapCategory.objects
        .filter(is_active=True)
        .prefetch_related("items")
        .order_by("column", "order", "name")
    )

    # Build a flat list of (category, active_items) pairs, skipping empty ones
    active = []
    for cat in categories:
        items = [i for i in cat.items.all() if i.is_active]
        if items:
            active.append({"category": cat, "items": items})

    # Group into columns using itertools.groupby
    columns = []
    for _col_num, group in groupby(active, key=lambda x: x["category"].column):
        columns.append(list(group))

    return render(request, "html/sitemap.html", {"columns": columns})

from django.shortcuts import render

from django.shortcuts import render
from .models import SeasonReport, PlayerEntry

def scouted_players(request):
    from .models import ScoutedPlayersRoaster
    seasons = (
        SeasonReport.objects
        .all()
        .order_by("-season")
        .prefetch_related("players")
    )

    # Build a simple structure: for each season, two lists
    season_blocks = []
    for s in seasons:
        players = list(s.players.all())  # from related_name="players"

        shortlisted = [p for p in players if p.list_type == "Shortlisted"]
        scouted = [p for p in players if p.list_type == "Scouted"]

        # Ensure correct order
        shortlisted.sort(key=lambda x: x.sr_no)
        scouted.sort(key=lambda x: x.sr_no)

        season_blocks.append({
            "season": s,
            "shortlisted": shortlisted,
            "scouted": scouted,
        })

    roasters = ScoutedPlayersRoaster.objects.filter(is_active=True)

    return render(request, "html/scouted_players.html", {
        "season_blocks": season_blocks,
        "roasters": roasters,
    })




from .models import Faq

def season5landing(request):
    lang = 'en'
    context = pagelabel(lang)

    context['finalists'] = Finalists.objects.all().values()
    context['featurestrips'] = SupportIkfFeatureStrip.objects.filter(lang=lang).values()
    context['PartnerSeasonSupportIKF'] = PartnerSeasonSupportIKF.objects.filter(lang=lang).values()

    # IKF Trials season cards — pulled from the SeasonReport admin
    from .models import SeasonReport
    context['trial_seasons'] = SeasonReport.objects.filter(show_on_ikf_trials=True).order_by('season')

    # ✅ FAQs for IkfTrials page (because your url name is "IkfTrials")
    context['faqs'] = Faq.objects.filter(page_name='IkfTrials').order_by('priority')

    return render(request, 'html/season_5_landing.html', context)


def season5(request):
    lang = 'en'
    context = pagelabel(lang)

    from .models import Faq as FaqModel
    context['faqs'] = FaqModel.objects.filter(page_name='IkfTrials').order_by('priority')

    return render(request, 'html/season5.html', context)


from django.shortcuts import render
from .models import Faq, Winners, Coaches, Testimonials, Finalists, WorkshopInternationalLogo, MasterPosition
from .models import TrialSchedule
from .models import WorkshopLocation

def ikf_workshop(request):
    lang = 'en'
    context = pagelabel(lang)

    # Winners
    winners = Winners.objects.filter(workshop_scholarship=True).values()
    for winner in winners:
        winner['category_id'] = MasterPosition.objects.get(id=winner['category_id']).label
    context['winners'] = winners

    # Coaches
    coaches = Coaches.objects.filter(workshop_scholarship=True).values()
    for coach in coaches:
        coach['category_id'] = MasterPosition.objects.get(id=coach['category_id']).label
    context['coaches'] = coaches

    # Testimonials, Finalists, Partners
    context['testimonials'] = Testimonials.objects.filter().values()
    context['finalists'] = Finalists.objects.filter().values()
    context['clubs_partner_home'] = WorkshopInternationalLogo.objects.filter(lang=lang).values()

    # ✅ FAQs for the workshop page
    context['faqs'] = Faq.objects.filter(page_name='ikf_workshop').order_by('priority')
    context['trial_schedules'] = TrialSchedule.objects.all().order_by('city')
    context['workshop_locations'] = WorkshopLocation.objects.all().order_by('city')


    return render(request, 'html/ikf_workshop.html', context)




from django.http import JsonResponse
from .models import Winners, MasterPosition, Testimonials, WorkshopInternationalLogo

from django.http import JsonResponse
from .models import Winners, Testimonials, WorkshopInternationalLogo, Coaches, Faq, MasterPosition

from .models import TrialSchedule

def get_workshopinfo(request):
    lang = 'en'
    winners = list(Winners.objects.filter(workshop_scholarship=True).values())

    for winner in winners:
        try:
            winner['category_label'] = MasterPosition.objects.get(id=winner['category_id']).label
        except MasterPosition.DoesNotExist:
            winner['category_label'] = None

    testimonials = list(Testimonials.objects.all().values())
    clubs_partner_home = list(WorkshopInternationalLogo.objects.filter(lang=lang).values())
    coaches = list(Coaches.objects.filter(workshop_scholarship=True).values())
    faq = list(Faq.objects.filter(page_name='ikf_workshop').order_by('priority').values())
    workshop_locations = list(WorkshopLocation.objects.all().order_by('priority').values())

    # ✅ Trial Schedules (new)
    trial_schedules = []
    for schedule in TrialSchedule.objects.prefetch_related('days').all():
        trial_schedules.append({
            'city': schedule.city,
            'days': [
                {
                    'title': day.day_title,
                    'description': day.description
                }
                for day in schedule.days.all()
            ]
        })

     
       

    response = JsonResponse({
        'winners': winners,
        'testimonials': testimonials,
        'clubs_partner_home': clubs_partner_home,
        'coaches': coaches,
        'faq': faq,
        'workshop_locations': workshop_locations,
        'trial_schedules': trial_schedules  # ✅ new addition
    }, safe=False)

    print(response)
    return response





def career360fieldofdreams(request):
 
    context = pagelabel('en')
 
    return render(request, 'html/career360fieldofdreams.html', context)

def workshopfee(request):
 
    context = pagelabel('en')
 
    return render(request, 'html/workshopfee.html', context)


def news_homepage(request):
    context = pagelabel('en')
    context['ikfinnews_banner'] = News.objects.filter(priority=True).first()
    selected_type = request.GET.get('type', 'All')
    context['selected_type'] = selected_type

    qs = News.objects.filter(priority=False)
    if selected_type != 'All':
        qs = qs.filter(type__iexact=selected_type)

    context['ikfinnews_news'] = qs.order_by('-date')
    return render(request, 'html/ikfinnews.html', context)

def faces(request):
    lang = 'en'
    context = pagelabel('en')

    return render(request, 'html/faces.html', context)




def dashboard_view(request):
    # Use the latmfks database connection
    with connections['latmfks'].cursor() as cursor:
        df = pd.read_sql("SELECT * FROM players_who_visited", connections['latmfks'])

    unique_visitors = df.drop_duplicates(subset='id')


    ############ U13, U15, U17 PIE CHART (SEASON 4 & 5) ############

    # Load precomputed AgeGroup counts from SQL view
    df_agegroup = pd.read_sql("SELECT AgeGroup, Count FROM AgeGroupCounts_Season4_5", connections['latmfks'])

    # Plot radial (donut) pie chart
    fig = px.pie(
        df_agegroup,
        names='AgeGroup',
        values='Count',
        color_discrete_sequence=['#1769FF', '#74A5FF', '#D1E1FF'],
        hole=0.7  # creates the donut hole
    )

    fig.update_layout(
        margin=dict(t=40, b=0, l=50, r=0),
        width=400,
        height=320,
        showlegend=True,
        legend=dict(
            orientation="v",
            x=-0.2,
            y=0,
            xanchor="left",
            yanchor="bottom",
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
    )

    chart_age = fig.to_html(full_html=False, config={'displayModeBar': False})

    # ============================================
    # Scatter Plot for height and weight
    # ============================================

    # Load preconverted height-weight data from SQL view
    df = pd.read_sql("""
        SELECT Height_cm, Weight_kg, Position, Gender
        FROM ZonalPlayers_HeightWeightConverted
        WHERE Height_cm IS NOT NULL
        AND Weight_kg IS NOT NULL
        AND Position IS NOT NULL
        AND Gender IS NOT NULL
        """, connections['latmfks'])

    positions = ['All Positions'] + sorted(df['Position'].dropna().unique())

    fig = go.Figure()

    # Define blue-yellow color scheme
    gender_colors = {'Male': '#007bff', 'Female': '#ffc107'}

    # All Positions traces
    for gender in ['Male', 'Female']:
        subset = df[df['Gender'] == gender]
        fig.add_trace(go.Scatter(
            x=subset['Height_cm'],
            y=subset['Weight_kg'],
            mode='markers',
            marker=dict(color=gender_colors[gender], size=5, opacity=0.6),
            name=f"{gender} - All Positions",
            showlegend=False
        ))

    # Per-position traces (initially hidden)
    for pos in sorted(df['Position'].dropna().unique()):
        for gender in ['Male', 'Female']:
            subset = df[(df['Position'] == pos) & (df['Gender'] == gender)]
            fig.add_trace(go.Scatter(
                x=subset['Height_cm'],
                y=subset['Weight_kg'],
                mode='markers',
                marker=dict(color=gender_colors[gender], size=5, opacity=0.6),
                name=f"{gender} - {pos}",
                visible=False,
                showlegend=False
            ))

    # Dropdown buttons
    buttons = []

    # All Positions button
    vis = [True if i < 2 else False for i in range(len(fig.data))]
    buttons.append(dict(
        label='All Positions',
        method='update',
        args=[{'visible': vis},
            {'title': 'Height vs Weight: All Positions'}]
    ))

    # Per-position buttons
    for idx, pos in enumerate(sorted(df['Position'].dropna().unique())):
        vis = [False] * len(fig.data)
        male_idx = 2 + idx * 2
        female_idx = male_idx + 1
        vis[male_idx] = True
        vis[female_idx] = True

        buttons.append(dict(
            label=pos,
            method='update',
            args=[{'visible': vis},
                {'title': f"Height vs Weight: {pos}"}]
        ))

    # Layout
    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.1,
            y=1.2,
            xanchor='right',
            yanchor='top'
        )],
        xaxis=dict(
            title="Height (cm)",
            range=[85, 210],
            autorange=False,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            dtick=10
        ),
        yaxis=dict(
            title="Weight (kg)",
            range=[20, 90],
            autorange=False,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            dtick=5
        ),
        width=900,
        height=700,
        autosize=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=40, b=50),
    )

    chart_boys_girls_scatter = fig.to_html(full_html=False, config={'displayModeBar': False})

    # ============================================================
    # 📊 Bar Chart: Top 5 States by Average Player Rating (Simple)
    # =============================================================
    # Load precomputed top 5 states with average rating from SQL view
    df_state = pd.read_sql("""
        SELECT State, AvgRating
        FROM Top5States_AvgRating
        WHERE State IS NOT NULL
        AND AvgRating IS NOT NULL
    """, connections['latmfks'])

    # Sort by AvgRating descending for bar order consistency
    df_state = df_state.sort_values(by='AvgRating', ascending=False)

    # Define your provided hex codes (from highest to lowest score order)
    hex_colors = ['#FFC300', '#FFCF33', '#FFDB66', '#F6E29D', '#FFF3CC']

    # Create horizontal bar chart with reversed x-axis
    fig = go.Figure(go.Bar(
        x=df_state['AvgRating'],
        y=df_state['State'],
        orientation='h',
        marker_color=hex_colors,          # apply your colors
        text=df_state['State'],           # show state names as text on bars
        textposition='outside',           # outside bars
        insidetextanchor='start',
        textfont=dict(color='black', size=10)
    ))

    # Update layout for reversed x-axis and top x-axis
    fig.update_layout(
        xaxis=dict(
            range=[3.5, 3.0],  # reversed
            side='top',        # x-axis on top
            title='Average Rating'
        ),
        yaxis=dict(
            showticklabels=False,
            autorange='reversed'  # keeps order top-down
        ),
        margin=dict(l=20, r=20, t=40, b=0),
        width=225,
        height=310,
        plot_bgcolor='white',
        autosize=False,
    )

    chart_top5_state_avg_rating = fig.to_html(full_html=False, config={'displayModeBar': False})


    # =======================================================
    # Impact of Position Change on Scores (with short forms)
    # =======================================================

    # Load precomputed data from SQL view
    df = pd.read_sql("""
        SELECT PositionName, PositionStatus, PositionShort, AvgRating
        FROM PositionImpact_AvgRating_ShortForms
        WHERE PositionName IS NOT NULL
        AND PositionStatus IS NOT NULL
        AND PositionShort IS NOT NULL
        AND AvgRating IS NOT NULL
    """, connections['latmfks'])

    # Sort to place 'In Position' first within each position
    df['PositionStatus'] = pd.Categorical(df['PositionStatus'], categories=['In Position', 'Out of Position'], ordered=True)
    df = df.sort_values(['PositionName', 'PositionStatus'])

    # Create Plotly bar chart
    fig = go.Figure()

    for status, color in zip(['In Position', 'Out of Position'], ['#007bff', '#74A5FF']):
        subset = df[df['PositionStatus'] == status]
        fig.add_trace(go.Bar(
            x=subset['PositionShort'],
            y=subset['AvgRating'],
            name=status,
            marker_color=color
        ))

    # Update layout
    fig.update_layout(
        barmode='group',
        margin=dict(t=40, b=0, l=50, r=0),
        height=320,
        autosize=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(range=[2, 3.5], title="Average Rating"),
        xaxis=dict(tickangle=-45),
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.2,
            xanchor="center",
            font=dict(size=12)
        ),
    )

    chart_position_impact = fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})


    # =====================================================
    # 🚀 Top vs Average Performer Radar Chart (Fixed)
    # =====================================================
    # Load precomputed data from SQL view
    top_avg_stats = pd.read_sql("""
        SELECT AssignedPositionName, ReportCategoryName, TopPerformer, AvgPerformer
        FROM TopVsAvg_PerformerRadar
        WHERE AssignedPositionName IS NOT NULL
        AND ReportCategoryName IS NOT NULL
        AND TopPerformer IS NOT NULL
        AND AvgPerformer IS NOT NULL
    """, connections['latmfks'])

    # Unique positions for dropdown
    positions = top_avg_stats['AssignedPositionName'].unique()

    # Create figure
    fig = go.Figure()

    # Add a default position trace first (e.g. first position in list)
    default_position = positions[0]
    df_pos = top_avg_stats[top_avg_stats['AssignedPositionName'] == default_position]

    categories = df_pos['ReportCategoryName'].tolist()
    top_scores = df_pos['TopPerformer'].tolist()
    avg_scores = df_pos['AvgPerformer'].tolist()

    # Radar requires closed loop: append first value to end
    categories += [categories[0]]
    top_scores += [top_scores[0]]
    avg_scores += [avg_scores[0]]

    fig.add_trace(go.Scatterpolar(
        r=top_scores,
        theta=categories,
        fill='toself',
        name='Top Performer',
        marker_color='blue'
    ))

    fig.add_trace(go.Scatterpolar(
        r=avg_scores,
        theta=categories,
        fill='toself',
        name='Average Performer',
        marker_color='lightblue'
    ))

    # Create dropdown buttons for each position
    buttons = []
    for pos in positions:
        df_pos = top_avg_stats[top_avg_stats['AssignedPositionName'] == pos]
        cats = df_pos['ReportCategoryName'].tolist()
        top = df_pos['TopPerformer'].tolist()
        avg = df_pos['AvgPerformer'].tolist()

        # Close loop
        cats += [cats[0]]
        top += [top[0]]
        avg += [avg[0]]

        buttons.append(dict(
            method='update',
            label=pos,
            args=[
                {'r': [top, avg], 'theta': [cats, cats]},
            ]
        ))

    # Update layout with dropdown
    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.5,
            y=1.3,
            xanchor='right',
            yanchor='top'
        )],
        polar=dict(
            radialaxis=dict(visible=True, range=[2, 4.5])
        ),
        showlegend=True,
        autosize=True,
    )

    chart_top_vs_avg = fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})


    # ==================================
    # 🚀 Radial Foot Preference Chart
    # ==================================

    # Load precomputed foot preference counts from SQL view
    foot_counts = pd.read_sql("""
        SELECT PreferenceFoot, Count
        FROM FootPreferenceCounts
        WHERE PreferenceFoot IS NOT NULL
        AND Count IS NOT NULL
    """, connections['latmfks'])

    # Map colours (adapt as desired)
    color_map = {
        'Right': '#FFC107',  # yellow (right foot)
        'Left': '#007BFF',   # blue (left foot)
    }

    # Apply colours to data order
    colors = [color_map.get(foot, '#d9d9d9') for foot in foot_counts['PreferenceFoot']]

    # Plot radial donut chart
    fig = px.pie(
        foot_counts,
        names='PreferenceFoot',
        values='Count',
        color_discrete_sequence=colors,
        hole=0.7
    )

    # Update layout
    fig.update_layout(
        margin=dict(t=40, b=0, l=50, r=0),
        width=400,
        height=300,
        showlegend=True,
        legend=dict(
            orientation="v",
            x=-0.2,
            y=0,
            xanchor="left",
            yanchor="bottom",
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
    )

    chart_radial_foot = fig.to_html(full_html=False, config={'displayModeBar': False})

    # ==================================
    # 🚀 LINE CHART BANNER
    # ==================================
    # Load precomputed monthly cumulative registrations from SQL view
    monthly_counts = pd.read_sql("""
        SELECT Month, Registrations, Year, MonthNum
        FROM Monthly_Cumulative_Registrations
        WHERE Month IS NOT NULL
        AND Registrations IS NOT NULL
        AND Year IS NOT NULL
        AND MonthNum IS NOT NULL
        ORDER BY Month
    """, connections['latmfks'])

    monthly_counts['CumulativeRegistrations'] = monthly_counts['Registrations'].cumsum()

    # Filter for December rows for yearly summaries
    december_rows = monthly_counts[monthly_counts['MonthNum'] == 12]

    # Prepare yearly summary text
    yearly_summaries = [
        f"{int(row['Year'])}: {int(row['CumulativeRegistrations']):,}"
        for i, row in december_rows.iterrows()
    ]
    yearly_summary_text = " | ".join(yearly_summaries)

    # Calculate current total dynamically
    current_total = monthly_counts['CumulativeRegistrations'].iloc[-1]
    current_total_formatted = f"{current_total:,}"

    # Create smooth line chart with pattern fill
    fig = go.Figure()

    # Add pattern fill as area under line
    fig.add_trace(go.Scatter(
        x=monthly_counts['Month'],
        y=monthly_counts['CumulativeRegistrations'],
        mode='lines',
        line=dict(
            color='#FFC300',
            width=4,
            shape='spline',
            smoothing=1.3
        ),
        fill='tozeroy',
        fillpattern=dict(
            shape="|",
            fgcolor="#FFC300",
            bgcolor="white",
            solidity=0.1
        ),
        name='Cumulative Registrations'
    ))

    # Add vertical lines and annotations for December
    for i, row in december_rows.iterrows():
        fig.add_shape(
            type="line",
            x0=row['Month'],
            y0=0,
            x1=row['Month'],
            y1=row['CumulativeRegistrations'],
            line=dict(color="#FFC300", width=4, dash="dot"),
            layer="above"
        )
        
        fig.add_annotation(
            x=row['Month'],
            y=row['CumulativeRegistrations'] * 1.05,
            text=f"{row['Year']}:<br>{row['CumulativeRegistrations']:,}",
            showarrow=False,
            yanchor="bottom",
            font=dict(size=12, color="black")
        )

    # Update layout
    fig.update_layout(
        title={
            'text': '<b>IKF Player Growth</b> - Cumulative Month by Month',
            'x': 0.05,
            'xanchor': 'left',
            'y': 0.85,
            'yanchor': 'top',
            'font': dict(size=25, color='black')
        },
        xaxis=dict(showticklabels=False),
        yaxis=dict(
            title=dict(text="Cumulative Registrations", standoff=20),
            side='right',
        ),
        margin=dict(l=0, r=40, t=60, b=0),
        width=None,
        height=350,
        autosize=True,
        plot_bgcolor='white'
    )

    # Adjust summary annotation position below title with left alignment
    fig.add_annotation(
        x=0.05,
        y=0.78,
        xref="paper",
        yref="paper",
        text=f"Total: <b>{current_total_formatted}</b>",
        showarrow=False,
        font=dict(size=19, color="black"),
        align="left"
    )

    chart_registrations_per_month = fig.to_html(full_html=False, config={'displayModeBar': False})



    # ====================================================
    # 🚀 Secondary Position Preference Bar Chart (Final)
    # ====================================================
    # Load precomputed data from SQL view
    df = pd.read_sql("""
        SELECT PositionShort, SecondaryPositionShort, Count
        FROM SecondaryPositionPreferenceCounts
        WHERE PositionShort IS NOT NULL
        AND SecondaryPositionShort IS NOT NULL
        AND Count IS NOT NULL
        ORDER BY PositionShort, Count DESC
    """, connections['latmfks'])

    # Unique primary positions
    positions = df['PositionShort'].unique()

    # Initialize figure
    fig = go.Figure()

    # Default position = first in list
    default_pos = positions[0]
    df_pos = df[df['PositionShort'] == default_pos]

    # Add bar trace for default position
    fig.add_trace(go.Bar(
        x=df_pos['SecondaryPositionShort'],
        y=df_pos['Count'],
        marker_color='#FFCF33' 
    ))

    # Create dropdown buttons for each position
    buttons = []
    for pos in positions:
        df_pos = df[df['PositionShort'] == pos]
        buttons.append(dict(
            method='update',
            label=pos,
            args=[
                {'x': [df_pos['SecondaryPositionShort']],
                'y': [df_pos['Count']]},
                {'title': f"Secondary Position Preference for {pos}"}
            ]
        ))

    # Update layout with dropdown
    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.05,
            y=1.2
        )],
        title=f"Secondary Position Preference for {default_pos}",
        xaxis_title='Secondary Position',
        yaxis_title='Count',
        autosize=True,
        plot_bgcolor='white'
    )

    # Render to HTML
    chart_secondary_pref = fig.to_html(full_html=False, config={'responsive': True, 'displayModeBar': False})

    return render(request, 'html/dashboard.html', {
        'chart_age': chart_age,
        'chart_boys_girls_scatter': chart_boys_girls_scatter,
        'chart_top5_state_avg_rating': chart_top5_state_avg_rating,
        'chart_position_impact': chart_position_impact,
        'chart_top_vs_avg': chart_top_vs_avg,
        'chart_radial_foot':chart_radial_foot,
        'chart_registrations_per_month':chart_registrations_per_month,
        'chart_secondary_pref': chart_secondary_pref,
    })


api_base_url = "https://app.myfirstkick.com/be/api/v1/project"


def upcoming_trials_page(request):
    # IMPORTANT: your template location
    return render(request, "html/upcoming_trials.html")


def upcoming_trials_filters_api(request):
    """
    Browser calls this with GET.
    Django calls FastAPI with POST internally.
    """
    try:
        res = requests.post(
            f"{api_base_url}/get_upcoming_trials_filters",
            json={},   # both optional in FastAPI
            timeout=15
        )
        return JsonResponse(res.json(), safe=False)
    except Exception as e:
        return JsonResponse({"error": "Failed to fetch filters", "details": str(e)}, status=500)


def get_playlist_thumbnail(playlist_url):
    try:
        res = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": playlist_url, "format": "json"},
            timeout=5
        )
        if res.ok:
            return res.json().get("thumbnail_url", "")
    except Exception:
        pass
    return ""


def upcoming_trials_cities_api(request):
    payload = {}
    project_id = request.GET.get("projectId")
    state_id   = request.GET.get("stateId")
    status     = request.GET.get("statusOfTrial")

    if project_id: payload["projectId"]      = int(project_id)
    if state_id:   payload["stateId"]        = int(state_id)
    if status:     payload["statusOfTrial"]  = status

    try:
        res  = requests.post(f"{api_base_url}/get_city_details", json=payload, timeout=20)
        data = res.json()

        # ── inject videoThumbnail into each city that has a videoLink ──
        if isinstance(data, list):
            for city in data:
                video_link = city.get("videoLink") or ""
                city["videoThumbnail"] = get_playlist_thumbnail(video_link) if video_link else ""

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": "Failed to fetch cities", "details": str(e)}, status=500)
    
def upcoming_trials_city_api(request):
    """
    Browser calls this with GET params:
      projectId, stateId, statusOfTrial (all optional)
    Django calls FastAPI with POST internally.
    """
    payload = {}
    project_id = request.GET.get("projectId")
    
    
    project_city_id = request.GET.get("projectCityId")

    if project_id:
        payload["projectId"] = int(project_id)
    if project_city_id:
        payload["projectCityId"] = int(project_city_id)
    

    try:
        res = requests.post(
            f"{api_base_url}/get_city_detail",
            json=payload,
            timeout=20
        )
        return JsonResponse(res.json(), safe=False)
    except Exception as e:
        return JsonResponse({"error": "Failed to fetch cities", "details": str(e)}, status=500)


def upcoming_trials_last_modified(request):
    """
    Browser calls this with GET.
    Django calls FastAPI with GET internally.

    FastAPI endpoint:
      /be/api/v1/project/project_city_modified_at

    Response example:
      {"lastModifiedAt":"01:31 PM ,20 Feb 2026"}
    """
    try:
        res = requests.get(
            f"{api_base_url}/project_city_modified_at",
            headers={"accept": "application/json"},
            timeout=10
        )
        # keep safe=False because it's a dict anyway but consistent with your pattern
        return JsonResponse(res.json(), safe=False)
    except Exception as e:
        return JsonResponse(
            {"error": "Failed to fetch last modified", "details": str(e)},
            status=500
        )


def ikf_broadcast_page(request):
    from .models import IKFBroadcastItem
    items = IKFBroadcastItem.objects.filter(is_active=True).order_by('-date', '-created_at')
    return render(request, 'html/noticeboard_pages/ikf_broadcast.html', {'items': items})


# ─────────────────────────────────────────────────────────────
# IKF Career 360 — The Parent Conversation (Quiz)
# ─────────────────────────────────────────────────────────────
PARENT_CONVO_LABELS = {
    "q1_origin": {
        "label": "How did your child first fall in love with football?",
        "options": {
            "A": "My child just started playing one day and never stopped.",
            "B": "We introduced them to it — and they took it from there.",
            "C": "A coach or school spotted something in them.",
            "D_open": "It's a longer story — (open answer)",
        },
    },
    "q2_child_voice": {
        "label": "When your child talks about football, what do you hear most?",
        "options": {
            "A": "I want to play professionally. This is my life.",
            "B": "I love football. I don't know where it leads yet.",
            "C": "I play because it makes me happy — nothing more.",
            "D": "Honestly, I'm not sure. They haven't said.",
        },
    },
    "q3_worth_it": {
        "label": "Your child is 22. Football has given them everything it can. What would make you feel the journey was worth it?",
        "options": {
            "A": "They're playing at a professional or semi-professional level.",
            "B": "They're earning a living inside football — coaching, management, media.",
            "C": "They grew into a confident, disciplined, resilient person — football did that.",
            "D": "All three. I won't settle for less.",
        },
    },
    "q4_support": {
        "label": "On a normal week, what does your support look like?",
        "options": {
            "A": "I'm there — planning, tracking, making sure everything lines up.",
            "B": "I provide what's needed — fees, travel, kit — but day-to-day is their responsibility.",
            "C": "I show up for matches and big moments. The rest is up to them.",
            "D": "Honestly, I'm still figuring out what support should look like.",
        },
    },
    "q5_hardest_part": {
        "label": "What is the hardest part of supporting your child's football journey right now?",
        "options": None,
    },
    "q6_pro_estimate": {
        "label": "Of every 100 children who play football seriously in India — how many do you think turn professional?",
        "options": {
            "A": "Fewer than 1",
            "B": "Around 5",
            "C": "Around 10",
            "D": "More than 10",
        },
    },
    "q7_ten_years": {
        "label": "If your child gives ten years to this game and does not play professionally — what would you want football to have given them?",
        "options": {
            "A": "A career inside football — coaching, scouting, sports management, media.",
            "B": "The values. Discipline, teamwork, resilience. Those will serve them anywhere.",
            "C": "Both. A connection to the game and the character it builds.",
            "D": "Honestly — if they don't play professionally, I'll need time to think about what comes next.",
        },
    },
    "q8_ecosystem": {
        "label": "Does the every-child-has-a-pathway approach matter to you?",
        "options": {
            "A": "Yes — that's exactly the kind of programme I want my child in.",
            "B": "I hadn't thought about it this way — but yes, it matters.",
            "C": "My focus right now is on the professional pathway. We can think about the rest later.",
        },
    },
}


def _compute_parent_profile(q3, q4, q6, q7, q8):
    aligned = potential = atrisk = 0

    if q3 in ("B", "C"): aligned += 2
    if q3 == "D":        atrisk  += 1
    if q3 == "A":        potential += 1

    if q4 in ("A", "B"): aligned += 1
    if q4 == "D":        potential += 2

    if q6 == "A":         aligned += 2
    if q6 == "B":         aligned += 1
    if q6 in ("C", "D"):  atrisk += 2

    if q7 in ("B", "C"): aligned += 2
    if q7 == "A":        aligned += 1
    if q7 == "D":        atrisk  += 3

    if q8 == "A": aligned   += 2
    if q8 == "B": potential += 2
    if q8 == "C": atrisk    += 2

    if aligned >= atrisk and aligned >= potential:
        return "aligned"
    if atrisk > aligned and atrisk >= potential:
        return "atrisk"
    return "potential"


def parent_conversation_quiz(request):
    """The IKF Career 360 — Parent Conversation quiz page."""
    lang = 'en'
    context = pagelabel(lang)
    return render(request, 'html/parent_conversation_quiz.html', context)


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def parent_conversation_submit(request):
    """Accept JSON body, score the quiz, persist, return outcome JSON."""
    from .models import ParentConversation
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    try:
        age = int(payload.get("childAge") or 0)
    except (TypeError, ValueError):
        age = 0

    q3 = (payload.get("q3") or "").strip()
    q4 = (payload.get("q4") or "").strip()
    q6 = (payload.get("q6") or "").strip()
    q7 = (payload.get("q7") or "").strip()
    q8 = (payload.get("q8") or "").strip()

    profile = _compute_parent_profile(q3, q4, q6, q7, q8)

    record = ParentConversation.objects.create(
        parent_name     = (payload.get("parentName")  or "").strip()[:200],
        parent_email    = (payload.get("parentEmail") or "").strip()[:254],
        child_age       = age if 5 <= age <= 25 else 0,
        child_gender    = (payload.get("childGender") or "").strip()[:10],
        q1_origin       = (payload.get("q1")          or "").strip()[:20],
        q1_origin_open  = (payload.get("q1Open")      or "").strip(),
        q2_child_voice  = (payload.get("q2")          or "").strip()[:20],
        q3_worth_it     = q3[:20],
        q4_support      = q4[:20],
        q5_hardest_part = (payload.get("q5Open")      or "").strip(),
        q6_pro_estimate = q6[:20],
        q7_ten_years    = q7[:20],
        q8_ecosystem    = q8[:20],
        profile         = profile,
    )

    return JsonResponse({"ok": True, "id": record.id, "profile": profile})


def parent_conversation_responses(request):
    """Public-facing table of submitted Parent Conversation responses."""
    from .models import ParentConversation
    context = pagelabel('en')
    responses = ParentConversation.objects.all()
    context["responses"] = responses
    context["count"] = responses.count()
    context["q_labels"] = PARENT_CONVO_LABELS
    return render(request, "html/parent_conversation_responses.html", context)
