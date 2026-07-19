from django import forms

class DesportzContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

from django import forms
from .models import PartnerInterest

class PartnerInterestForm(forms.ModelForm):
    class Meta:
        model  = PartnerInterest
        fields = ["org_name", "contact_person", "email", "state", "city", "focus_areas", "message"]
        widgets = {
            "org_name": forms.TextInput(attrs={"placeholder":"Organization Name"}),
            "contact_person": forms.TextInput(attrs={"placeholder":"Contact Person"}),
            "email": forms.EmailInput(attrs={"placeholder":"Email"}),
            "state": forms.TextInput(attrs={"placeholder":"State"}),          # ✅ now works
            "city": forms.TextInput(attrs={"placeholder":"City / District"}),
            "focus_areas": forms.TextInput(attrs={"placeholder":"Focus Areas"}),
            "message": forms.Textarea(attrs={"rows":4, "placeholder":"How can we collaborate?"}),
        }



from django import forms
from django.core.validators import RegexValidator
from .models import ContactUs

class ContactUsForm(forms.ModelForm):
    mobile = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Enter a valid 10-digit mobile number.'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mobile no.',
            'pattern': r'\d{10}',
            'maxlength': '10',
            'title': 'Enter 10-digit mobile number'
        })
    )

    message = forms.CharField(
        required=False,  # ✅ make message optional
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '...',
            'rows': 4
        })
    )

    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'mobile', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email ID'}),
            'message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason for Contact (not compulsory)'}),
        }


# ikf/main/forms.py

# main/forms.py
# main/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import RepTemplate, RepHighlight, RepPlayer, RepSocialLink, FIELD_SLUGS

DEFAULT_FIELDS = [
    "rep_logo", "rep_banner", "players_bg",
    "theme", "show_pills", "show_stats",
    "brand_color", "hero_bg_color", "card_color", "text_color",
    "stat1_value", "stat1_label",
    "stat2_value", "stat2_label",
    "stat3_value", "stat3_label",
    "stat4_value", "stat4_label",
    "cities_of_operation", "website_url", "rep_founder",
    "content", "rep_opinion", "rep_category", "rep_category_brief",
    "csr_activities", "ikf_activities",
]

TEXTAREA_WIDGETS = {
    "content": forms.Textarea(attrs={"rows": 5}),
    "rep_opinion": forms.Textarea(attrs={"rows": 4}),
    "rep_category_brief": forms.Textarea(attrs={"rows": 3}),
    "csr_activities": forms.Textarea(attrs={"rows": 3}),
    "ikf_activities": forms.Textarea(attrs={"rows": 3}),
}

def _is_hex(val: str) -> bool:
    if not isinstance(val, str): return False
    v = val.strip()
    if not v.startswith("#"): return False
    return len(v) in (4, 7) and all(c in "0123456789abcdefABCDEF" for c in v[1:])

def build_onboarding_form_for_rep(rep: RepTemplate):
    """
    Returns a ModelForm class whose fields/order are driven by rep.plan (Status).
    """
    if rep.plan:
        enabled = rep.plan.ordered_enabled_fields()
    else:
        enabled = list(DEFAULT_FIELDS)

    # Safety: keep only valid RepTemplate fields we know about
    enabled = [f for f in enabled if hasattr(RepTemplate, f) and (f in FIELD_SLUGS or f in DEFAULT_FIELDS)]

    class _RepOnboardingForm(forms.ModelForm):
        class Meta:
            model = RepTemplate
            fields = enabled
            widgets = {k: v for k, v in TEXTAREA_WIDGETS.items() if k in enabled}

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # keep explicit order
            self.order_fields(enabled)

        def clean(self):
            cleaned = super().clean()
            # If theme is present and set to 'custom', validate HEX colors if those fields are present
            theme_val = cleaned.get("theme")
            if "theme" in self.fields and theme_val == "custom":
                for f in ("brand_color", "hero_bg_color", "card_color", "text_color"):
                    if f in self.fields:
                        v = (cleaned.get(f) or "").strip()
                        if not v:
                            self.add_error(f, "Required when theme is ‘Custom’.")
                        elif not _is_hex(v):
                            self.add_error(f, "Use #HEX (e.g. #000 or #123ABC).")
            return cleaned

    return _RepOnboardingForm


# formsets unchanged...
RepHighlightFormSet = inlineformset_factory(
    RepTemplate, RepHighlight,
    fields=["order", "title", "text"],
    extra=1, can_delete=True,
    widgets={"text": forms.Textarea(attrs={"rows": 2})},
)
RepPlayerFormSet = inlineformset_factory(
    RepTemplate, RepPlayer,
    fields=["order", "name", "subtitle", "photo", "bio"],
    extra=1, can_delete=True,
    widgets={"bio": forms.Textarea(attrs={"rows": 2})},
)
RepSocialLinkFormSet = inlineformset_factory(
    RepTemplate, RepSocialLink,
    fields=["platform", "url"],
    extra=1, can_delete=True,
)


